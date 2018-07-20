from scrapy import signals
from scrapy.exceptions import DontCloseSpider
from scrapy.spiders import Spider, CrawlSpider

from . import connection, defaults


class KafkaMixin(object):
    consumer = None
    kafka_topic = None
    kafka_batch_size = None

    def start_requests(self):
        """Returns a batch of start requests from redis."""
        return self.next_requests()

    def setup_kafka(self, crawler=None):
        """Setup redis connection and idle signal.

        This should be called after the spider has set its crawler object.
        """
        if self.consumer is not None:
            return

        if crawler is None:
            # We allow optional crawler argument to keep backwards
            # compatibility.
            # XXX: Raise a deprecation warning.
            crawler = getattr(self, 'crawler', None)

        if crawler is None:
            raise ValueError("crawler is required")

        settings = crawler.settings

        if self.kafka_topic is None:
            self.kafka_topic = settings.get(
                'KAFKA_START_URLS_KEY', defaults.START_URLS_TOPIC,
            )

        self.kafka_topic = self.kafka_topic % {'name': self.name}

        if self.kafka_batch_size is None:
            self.kafka_batch_size = settings.getint('CONCURRENT_REQUESTS')

        try:
            self.kafka_batch_size = int(self.kafka_batch_size)
        except (TypeError, ValueError):
            raise ValueError("redis_batch_size must be an integer")

        if not self.kafka_topic.strip():
            raise ValueError("kafka topic must not be empty")

        self.logger.info("Reading start URLs from kafka topic '%(kafka_topic)s' "
                         "(batch size: %(kafka_batch_size)s",
                         self.__dict__)

        self.consumer = connection.get_start_urls_consumer_from_settings(crawler.settings)
        self.consumer.subscribe(self.kafka_topic)
        # The idle signal is called when the spider has no requests left,
        # that's when we will schedule new requests from redis queue
        crawler.signals.connect(self.spider_idle, signal=signals.spider_idle)

    def fetch_one(self):
        """Pop a request"""
        msgs = self.consumer.poll(max_records=1)
        data = None
        partitions = self.consumer.assignment()
        for part in partitions:
            records = msgs.get(part)
            if records:
                data = records[0].value
                break
        return data

    def next_requests(self):
        found = 0
        while found < self.kafka_batch_size:
            data = self.fetch_one()
            if not data:
                # Queue empty.
                break
            req = self.make_request_from_data(data)
            if req:
                yield req
                found += 1
            else:
                self.logger.debug("Request not made from data: %r", data)

        if found:
            self.logger.debug("Read %s requests from '%s'", found, self.kafka_topic)

    def make_request_from_data(self, url):
        """Returns a Request instance from data coming from Redis.

        By default, ``data`` is an encoded URL. You can override this method to
        provide your own message decoding.

        Parameters
        ----------
        data : bytes
            Message from redis.

        """
        return self.make_requests_from_url(url)

    def schedule_next_requests(self):
        """Schedules a request if available"""
        # TODO: While there is capacity, schedule a batch of redis requests.
        for req in self.next_requests():
            self.crawler.engine.crawl(req, spider=self)

    def spider_idle(self):
        """Schedules a request if available, otherwise waits."""
        # XXX: Handle a sentinel to close the spider.
        self.schedule_next_requests()
        raise DontCloseSpider


class KafkaSpider(KafkaMixin, Spider):

    @classmethod
    def from_crawler(self, crawler, *args, **kwargs):
        obj = super(KafkaSpider, self).from_crawler(crawler, *args, **kwargs)
        obj.setup_kafka(crawler)
        return obj


class RedisCrawlSpider(KafkaMixin, CrawlSpider):

    @classmethod
    def from_crawler(self, crawler, *args, **kwargs):
        obj = super(RedisCrawlSpider, self).from_crawler(crawler, *args, **kwargs)
        obj.setup_redis(crawler)
        return obj

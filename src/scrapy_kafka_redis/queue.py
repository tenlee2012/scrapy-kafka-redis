# encoding=utf-8

from scrapy.utils.reqser import request_to_dict, request_from_dict
from kafka import KafkaProducer, KafkaConsumer


class Base(object):
    """Per-spider base queue class"""

    def __init__(self, producer: KafkaProducer, consumer: KafkaConsumer,
                 spider, topic):
        self.producer = producer
        self.consumer = consumer
        self.consumer.subscribe(topic)
        self.spider = spider
        self.topic = topic % {'spider': spider.name}

    def _encode_request(self, request):
        """Encode a request object"""
        obj = request_to_dict(request, self.spider)
        return obj

    def _decode_request(self, obj):
        """Decode an request previously encoded"""
        return request_from_dict(obj, self.spider)

    def __len__(self):
        """Return the length of the queue"""
        raise NotImplementedError

    def push(self, request):
        """Push a request"""
        raise NotImplementedError

    def pop(self, timeout=0):
        """Pop a request"""
        raise NotImplementedError

    def close(self):
        self.consumer.close()
        self.producer.close()


class KafkaQueue(Base):
    """Per-spider FIFO queue"""

    def __len__(self):
        """Return the length of the queue"""
        return 0

    def push(self, request):
        """Push a request"""
        self.producer.send(self.topic, value=self._encode_request(request))
        self.producer.flush()

    def pop(self, timeout=0):
        """Pop a request"""
        msgs = self.consumer.poll(timeout_ms=timeout, max_records=1)
        data = None
        partitions = self.consumer.assignment()
        for part in partitions:
            records = msgs.get(part)
            if records:
                data = records[0].value
                break

        if data:
            return self._decode_request(data)

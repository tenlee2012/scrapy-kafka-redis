import redis
from .picklecompat import loads, dumps

# For standalone use.
DUPEFILTER_KEY = 'dupefilter:%(timestamp)s'

PIPELINE_TOPIC = '%(spider)s-items'

REDIS_CLS = redis.StrictRedis
REDIS_ENCODING = 'utf-8'
# Sane connection defaults.
REDIS_PARAMS = {
    'socket_timeout': 30,
    'socket_connect_timeout': 30,
    'retry_on_timeout': True,
    'encoding': REDIS_ENCODING,
}

SCHEDULER_QUEUE_TOPIC = '%(spider)s-requests'
SCHEDULER_QUEUE_CLASS = 'scrapy_kafka_redis.queue.KafkaQueue'
SCHEDULER_DUPEFILTER_KEY = '%(spider)s:dupefilter'
SCHEDULER_DUPEFILTER_CLASS = 'scrapy_kafka_redis.dupefilter.BloomFilter'


START_URLS_TOPIC = '%(name)s-start_urls'
BLOOM_BLOCK_NUM = 1

KAFKA_BOOTSTRAP_SERVERS = None
KAFKA_REQUEST_PRODUCER_PARAMS = {
    'api_version': (0, 10, 1),
    'value_serializer': dumps
}
KAFKA_REQUEST_CONSUMER_PARAMS = {
    'group_id': 'requests',
    'api_version': (0, 10, 1),
    'value_deserializer': loads
}
KAFKA_START_URLS_CONSUMER_PARAMS = {
    'group_id': 'start_url',
    'api_version': (0, 10, 1),
    'value_deserializer': lambda m: m.decode('utf-8'),
}

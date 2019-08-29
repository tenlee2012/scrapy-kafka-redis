[中文文档](README_zh.md) | 
[English](README.md)
# Scrpay-Kafka-Redis
In the case of a large number of requests, even using the `Bloomfilter` algorithm, but using [scrapy-redis] (https://github.com/rmax/scrapy-redis) still consumes a lot of memory. This project refers to `scrapy- Redis`.
### Features
 - Support for distributed
 - Use Redis as a deduplication queue, Simultaneous use of Bloomfilter to reduce the memory footprint, but increased the amount of deduplication
 - Use Kafka as a request queue, Can support a large number of request stacks, capacity and disk size related, rather than running memory
 - Due to the feature of Kafka, priority queues are not supported, only FIFO queues are supported.
 
### 依赖
 - Python 3.0+
 - Redis >= 2.8
 - Scrapy >= 1.5
 - kafka-python >= 1.4.0
 - kafka <= 1.1.0 (Since [kafka-python](https://github.com/dpkp/kafka-python) only supports kafka-1.1.0 version)

### 使用
  - `pip install scrapy-kafka-redis`
  - Configuration `settings.py` file
Must add param in `settings.py` file
```
# Enable Kafka scheduling storage request queue
SCHEDULER = "scrapy_kafka_redis.scheduler.Scheduler"

# Use BloomFilter as a deduplication queue
DUPEFILTER_CLASS = "scrapy_kafka_redis.dupefilter.BloomFilter"
```

Default values for other optional parameters
```
# the key of the deduplication queue stored in redis
DUPEFILTER_KEY = 'dupefilter:%(timestamp)s'

REDIS_CLS = redis.StrictRedis
REDIS_ENCODING = 'utf-8'
REDIS_URL = 'redis://localhost:6378/1'

REDIS_PARAMS = {
    'socket_timeout': 30,
    'socket_connect_timeout': 30,
    'retry_on_timeout': True,
    'encoding': REDIS_ENCODING,
}

KAFKA_BOOTSTRAP_SERVERS=['localhost:9092']
# Default TOPIC for the dispatch queue
SCHEDULER_QUEUE_TOPIC = '%(spider)s-requests'
# Scheduled queue used by default
SCHEDULER_QUEUE_CLASS = 'scrapy_kafka_redis.queue.KafkaQueue'
# The name of the key stored in the redis queue in redis
SCHEDULER_DUPEFILTER_KEY = '%(spider)s:dupefilter'
# Deduplication algorithm used by the scheduler
SCHEDULER_DUPEFILTER_CLASS = 'scrapy_kafka_redis.dupefilter.BloomFilter'
# Number of blocks in the BloomFilter algorithm
BLOOM_BLOCK_NUM = 1

# TOPIC used by start urls
START_URLS_TOPIC = '%(name)s-start_urls'

KAFKA_BOOTSTRAP_SERVERS = None
# Kafka producer constructing the request queue
KAFKA_REQUEST_PRODUCER_PARAMS = {
    'api_version': (0, 10, 1),
    'value_serializer': dumps
}
# Constructing a Kafka consumer of the request queue
KAFKA_REQUEST_CONSUMER_PARAMS = {
    'api_version': (0, 10, 1),
    'value_deserializer': loads
}
# Constructing a Kafka consumer in the start queue
KAFKA_START_URLS_CONSUMER_PARAMS = {
    'api_version': (0, 10, 1),
    'value_deserializer': lambda m: m.decode('utf-8'),
}
```
- how to use in `spiders`
```
import scrapy
from scrapy_kafka_redis.spiders import KafkaSpider

class DemoSpider(KafkaSpider):
    name = "demo"
    def parse(self, response):
        pass
```
- Create Kafka `Topic`
Set the number of partitions for the topic based on the distributed scrapy instance you need to create.
```
./bin/kafka-topics.sh --create --zookeeper localhost:2181 --partitions 3 --replication-factor 1 --topic demo-start_urls

./bin/kafka-topics.sh --create --zookeeper localhost:2181 --partitions 3 --replication-factor 1 --topic demo-requests
```
- Send Msg
```
./bin/kafka-console-producer.sh --broker-list localhost:9092 --topic demo-start_urls
```
It is recommended to manually create a Topic and specify the number of partitions.

- run scrapy

### Reference:
[scrapy-redis](https://github.com/rmax/scrapy-redis)
[Bloomfilter](https://github.com/LiuXingMing/Scrapy_Redis_Bloomfilter)

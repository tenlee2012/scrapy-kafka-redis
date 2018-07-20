# Scrpay-Kafka
在有大量请求堆积的情况下，即使用了`Bloomfilter`算法，使用[scrapy-redis](https://github.com/rmax/scrapy-redis)仍然会占用大量内存，本项目参考`scrapy-redis`，
### 特点
 - 支持分布式
 - 使用Redis作为去重队列
   同时使用Bloomfilter去重算法，降低了内存占用，但是增加了可去重数量
 - 使用Kafka作为请求队列
   可支持大量请求堆积，容量和磁盘大小相关，而不是和运行内存相关
 - 由于Kafka的特性，不支持优先队列，只支持先进先出队列
 
### 依赖
 - Python 3.0+
 - Redis >= 2.8
 - Scrapy >= 1.5
 - kafka-python >= 1.4.0

### 使用
  - `pip install scrapy-kafka-redis`
  - 配置`settings.py`
必须要添加在`settings.py`的内容
```
# 启用Kafka调度存储请求队列
SCHEDULER = "scrapy_kafka_redis.scheduler.Scheduler"

# 使用BloomFilter作为去重队列
DUPEFILTER_CLASS = "scrapy_kafka_redis.dupefilter.BloomFilter"
```

其他可选参数的默认值
```
# 单独使用情况下，去重队列在redis中存储的key
DUPEFILTER_KEY = 'dupefilter:%(timestamp)s'

REDIS_CLS = redis.StrictRedis
REDIS_ENCODING = 'utf-8'

REDIS_PARAMS = {
    'socket_timeout': 30,
    'socket_connect_timeout': 30,
    'retry_on_timeout': True,
    'encoding': REDIS_ENCODING,
}

# 调度队列的默认TOPIC
SCHEDULER_QUEUE_TOPIC = '%(spider)s-requests'
# 默认使用的调度队列
SCHEDULER_QUEUE_CLASS = 'scrapy_kafka.queue.KafkaQueue'
# 去重队列在redis中存储的key名
SCHEDULER_DUPEFILTER_KEY = '%(spider)s:dupefilter'
# 调度器使用的去重算法
SCHEDULER_DUPEFILTER_CLASS = 'scrapy_kafka.dupefilter.BloomFilter'
# BloomFilter的块个数
BLOOM_BLOCK_NUM = 1

# start urls使用的TOPIC
START_URLS_TOPIC = '%(name)s-start_urls'

KAFKA_BOOTSTRAP_SERVERS = None
# 构造请求队列的Kafka生产者
KAFKA_REQUEST_PRODUCER_PARAMS = {
    'api_version': (0, 10, 1),
    'value_serializer': dumps
}
# 构造请求队列的Kafka消费者
KAFKA_REQUEST_CONSUMER_PARAMS = {
    'group_id': 'requests',
    'api_version': (0, 10, 1),
    'value_deserializer': loads
}
# 构造开始队列的Kafka消费者
KAFKA_START_URLS_CONSUMER_PARAMS = {
    'group_id': 'start_url',
    'api_version': (0, 10, 1),
    'value_deserializer': loads
}
```
- `spiders` 使用
```
import scrapy
from scrapy_kafka.spiders import KafkaSpider

class DemoSpider(KafkaSpider):
    name = "demo"
    def parse(self, response):
        pass
```
- 创建`Topic`
根据需要创建的分布式scrapy实例，设置topic的分区数,比如
```
./bin/kafka-topics.sh --create --zookeeper localhost:2181 --partitions 3 --replication-factor 1 --topic demo-start_urls

./bin/kafka-topics.sh --create --zookeeper localhost:2181 --partitions 3 --replication-factor 1 --topic demo-requests
```
建议手动创建Topic并指定分区数

- 运行分布式scrapy

### 参考:
[scrapy-redis](https://github.com/rmax/scrapy-redis)
[Bloomfilter](https://github.com/LiuXingMing/Scrapy_Redis_Bloomfilter)

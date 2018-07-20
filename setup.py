#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup


setup(
    name='scrapy-kafka-redis',
    version='0.0.3',
    description="Kafka and Redis based components for Scrapy.",
    author="tenlee",
    author_email='tenlee2012@163.com',
    url='https://github.com/tenlee2012/scrapy-kafka-redis',
    packages=['scrapy_kafka_redis'],
    package_dir={'': 'src'},
    install_requires=['Scrapy>=1.0', 'redis>=2.10', 'kafka-python>=1.4.0'],
    include_package_data=True,
    license="MIT",
    keywords='scrapy-kafka-redis',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
)

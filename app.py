#!/usr/bin/env python3

from aws_cdk import core

from redis_to_elasticache.redis_to_elasticache_stack import RedisToElasticacheStack


app = core.App()
RedisToElasticacheStack(app, "redis-to-elasticache")

app.synth()

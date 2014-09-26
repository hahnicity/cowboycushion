"""
cowboycushion.tests.test_limiter
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
from time import sleep, time

from mock import Mock, patch
from mockredis import mock_strict_redis_client
from nose.tools import assert_less_equal, eq_

from cowboycushion.limiter import RedisLimiter, SimpleLimiter
from cowboycushion.tests.constants import *


def _call_many_apis(limited_client, mock_client, sleep_between_calls=False):
    start = time()
    for _ in range(0, CALLS_PER_BATCH + 1):
        if sleep_between_calls:
            sleep(SLEEP_DURATION)
        limited_client.do_stuff()
    end = time()
    eq_(mock_client.do_stuff.call_count, CALLS_PER_BATCH + 1)
    assert_less_equal(end - start - TIMEOUT, SECONDS_PER_BATCH)
    assert_less_equal(SECONDS_PER_BATCH, end - start + TIMEOUT)
    eq_(limited_client.call_count, CALLS_PER_BATCH)


class TestSimpleLimiter(object):
    def setup(self):
        self.client = Mock()
        self.limited_client = SimpleLimiter(
            self.client, TIMEOUT, CALLS_PER_BATCH, SECONDS_PER_BATCH
        )

    def test_calling_many_apis(self):
        _call_many_apis(self.limited_client, self.client)


class TestRedisLimiter(object):
    @patch("cowboycushion.limiter.StrictRedis", mock_strict_redis_client)
    def setup(self):
        self.client = Mock()
        self.limited_client = RedisLimiter(
            self.client,
            TIMEOUT,
            CALLS_PER_BATCH,
            SECONDS_PER_BATCH,
            REDIS_HOSTNAME,
            REDIS_PORT,
            REDIS_DB
        )

    def test_calling_many_apis(self):
        _call_many_apis(self.limited_client, self.client, sleep_between_calls=True)

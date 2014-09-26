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
    calls_made = CALLS_PER_BATCH + 1
    if sleep_between_calls:
        call_duration = SLEEP_DURATION
    else:
        call_duration = 0
    for _ in range(calls_made):
        sleep(call_duration)
        limited_client.do_stuff()
    end = time()
    eq_(mock_client.do_stuff.call_count, CALLS_PER_BATCH + 1)
    if call_duration * CALLS_PER_BATCH >= SECONDS_PER_BATCH:
        expected_time = call_duration * calls_made
    else:
        expected_time = (
            SECONDS_PER_BATCH * (calls_made / CALLS_PER_BATCH) +
            (calls_made - calls_made / CALLS_PER_BATCH) * call_duration
        )
    assert_less_equal(end - start - TIMEOUT, expected_time)
    assert_less_equal(expected_time, end - start + TIMEOUT)
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

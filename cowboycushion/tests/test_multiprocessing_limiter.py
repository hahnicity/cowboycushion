from time import time

from mock import patch
from mockredis import mock_strict_redis_client
from nose.tools import assert_greater_equal, assert_less_equal, assert_true, eq_

from cowboycushion.multiprocessing_limiter import RedisMultiprocessingLimiter, SimpleMultiprocessingLimiter
from cowboycushion.tests.constants import *

CALL_EXECUTION_TIME = 2


def _multiprocessing_api_calls(limited_client, mock_client):
    calls_made = CALLS_PER_BATCH * 3 + 1
    jobs = []
    start = time()
    for i in range(calls_made):
        job_start = time()
        jobs.append(limited_client.do_stuff())
        job_end = time()
        if i > 0 and i % CALLS_PER_BATCH == 0:
            assert_greater_equal(job_end - job_start, SECONDS_PER_BATCH)
    limited_client.close()
    limited_client.join()
    end = time()
    eq_(len(jobs), calls_made)
    assert_less_equal(end - start - TIMEOUT, SECONDS_PER_BATCH * 3)
    assert_less_equal(SECONDS_PER_BATCH * 3, end - start + TIMEOUT)
    eq_(limited_client.call_count, CALLS_PER_BATCH)


class MultiprocessingMockClient(object):
    def do_stuff(self):
        return True


class TestSimpleMultiprocessingLimiter(object):
    def setup(self):
        self.client = MultiprocessingMockClient()
        self.limited_client = SimpleMultiprocessingLimiter(
            self.client, TIMEOUT, CALLS_PER_BATCH, SECONDS_PER_BATCH, POOL_SIZE
        )

    def test_calling_many_apis(self):
        _multiprocessing_api_calls(self.limited_client, self.client)


class TestRedisMultiprocessingLimiter(object):
    @patch("cowboycushion.multiprocessing_limiter.StrictRedis", mock_strict_redis_client)
    def test_setup(self):
        self.client = MultiprocessingMockClient()
        self.limited_client = RedisMultiprocessingLimiter(
            self.client,
            TIMEOUT,
            CALLS_PER_BATCH,
            SECONDS_PER_BATCH,
            REDIS_HOSTNAME,
            REDIS_PORT,
            REDIS_DB,
            POOL_SIZE
        )
        job = self.limited_client.do_stuff()
        assert_true(job.get())
        eq_(self.limited_client.call_count, 1)
        assert_true(self.limited_client._verify_we_can_make_call())
        self.limited_client.close()
        self.limited_client.join()

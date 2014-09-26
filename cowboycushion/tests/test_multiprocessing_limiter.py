from time import time

from nose.tools import assert_greater_equal, assert_less_equal, eq_

from cowboycushion.multiprocessing_limiter import SimpleMultiprocessingLimiter
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
        pass


class TestSimpleMultiprocessingLimiter(object):
    def setup(self):
        self.client = MultiprocessingMockClient()
        self.limited_client = SimpleMultiprocessingLimiter(
            self.client, TIMEOUT, CALLS_PER_BATCH, SECONDS_PER_BATCH, POOL_SIZE
        )

    def test_calling_many_apis(self):
        _multiprocessing_api_calls(self.limited_client, self.client)

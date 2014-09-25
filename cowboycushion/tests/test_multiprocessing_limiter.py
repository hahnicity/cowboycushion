from multiprocessing import Pool
from time import time

from nose.tools import assert_less_equal, eq_

from cowboycushion.multiprocessing_limiter import SimpleLimiter
from cowboycushion.tests.constants import *


def _multiprocessing_api_calls(limited_client, mock_client):
    start = time()
    pool = Pool(POOL_SIZE)
    jobs = []
    for _ in range(CALLS_PER_BATCH + 5):
        jobs.append(pool.apply_async(limited_client.do_stuff, args=()))
    results = [job.get() for job in jobs]
    pool.close()
    pool.join()
    end = time()
    eq_(len(results), CALLS_PER_BATCH + 5)
    assert_less_equal(end - start - TIMEOUT, SECONDS_PER_BATCH)
    assert_less_equal(SECONDS_PER_BATCH, end - start + TIMEOUT)
    eq_(limited_client.call_count, CALLS_PER_BATCH)


class MultiprocessingMockClient(object):
    def do_stuff(self):
        pass


class TestSimpleMultiprocessingLimiter(object):
    def setup(self):
        self.client = MultiprocessingMockClient()
        self.limited_client = SimpleLimiter(
            self.client, TIMEOUT, CALLS_PER_BATCH, SECONDS_PER_BATCH
        )

    def test_calling_many_apis(self):
        _multiprocessing_api_calls(self.limited_client, self.client)

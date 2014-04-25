"""
discourse.tests.test_limiter
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
from time import time

from mock import Mock
from nose.tools import assert_less_equal, eq_

from discourse.limiter import Limiter


CALLS_PER_BATCH = 10
SECONDS_PER_BATCH = 1
TIMEOUT = .5


class TestLimiter(object):
    def setup(self):
        self.client = Mock()
        self.limited_client = Limiter(self.client, TIMEOUT, CALLS_PER_BATCH, SECONDS_PER_BATCH)

    def test_calling_many_apis(self):
        start = time()
        for _ in range(0, CALLS_PER_BATCH + 1):
            self.limited_client.do_stuff()
        end = time()
        eq_(self.client.do_stuff.call_count, CALLS_PER_BATCH + 1)
        assert_less_equal(end - start - TIMEOUT, SECONDS_PER_BATCH)
        assert_less_equal(SECONDS_PER_BATCH, end - start + TIMEOUT)
        eq_(len(self.limited_client.calls), CALLS_PER_BATCH)

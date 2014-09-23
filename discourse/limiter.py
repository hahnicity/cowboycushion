"""
discourse.limiter
~~~~~~~~~~~~~~~~~

A really dumb rate limiter that makes the assumption that each time we call it we are making an
API call. Is based off of the disqus API limitations that you can only make 1000 calls every
10 minutes.
"""
from time import sleep, time


class Limiter(object):
    def __init__(self, client, timeout, calls_per_batch, seconds_per_batch):
        self.client = client
        self._timeout = timeout
        self._calls_per_batch = calls_per_batch
        self._seconds_per_batch = seconds_per_batch
        self._calls = []

    def __getattr__(self, attr):
        if self._verify_we_can_make_call():
            return self._call_api(attr)
        else:
            self._wait_to_make_call()
            return self._call_api(attr)

    @property
    def calls(self):
        """
        A list of times that the disqus API was called.
        """
        return self._calls

    @property
    def calls_per_batch(self):
        return self._calls_per_batch

    @property
    def seconds_per_batch(self):
        return self._seconds_per_batch

    @property
    def timeout(self):
        return self._timeout

    def _call_api(self, attr):
        self._record_call()
        return getattr(self.client, attr)

    def _record_call(self):
        self.calls.append(time())

    def _verify_we_can_make_call(self):
        if len(self.calls) >= self.calls_per_batch:
            if self.calls[0] < time() - self.seconds_per_batch:
                del self.calls[0]
                return True
            else:
                return False
        else:
            return True

    def _wait_to_make_call(self):
        while self.calls[0] >= time() - self.seconds_per_batch:
            sleep(self.timeout)
        del self.calls[0]

"""
cowboycushion.limiter
~~~~~~~~~~~~~~~~~~~~~

A really dumb rate limiter that makes the assumption that each time we call it we are
making an API call.
"""
from time import sleep, time

from redis import StrictRedis


class SingleProcessLimiter(object):
    def _call_api(self, attr):
        self._record_call()
        return getattr(self.client, attr)


class Limiter(object):
    def __getattr__(self, attr):
        if self._verify_we_can_make_call():
            return self._call_api(attr)
        else:
            self._wait_to_make_call()
            return self._call_api(attr)

    @property
    def calls_per_batch(self):
        return self._calls_per_batch

    @property
    def seconds_per_batch(self):
        return self._seconds_per_batch

    @property
    def timeout(self):
        return self._timeout

    def _verify_we_can_make_call(self):
        if self.call_count >= self.calls_per_batch:
            if self._get_first_call() < time() - self.seconds_per_batch:
                self._remove_first_call()
                return True
            else:
                return False
        else:
            return True

    def _wait_to_make_call(self):
        while self._get_first_call() >= time() - self.seconds_per_batch:
            sleep(self.timeout)
        self._remove_first_call()


class RedisStorage(Limiter):
    @property
    def call_count(self):
        return self._redis.zcard(self._calls_key)

    def _get_first_call(self):
        return float(self._redis.zrange(self._calls_key, 0, 0)[0])

    def _record_call(self):
        self._redis.zadd(self._calls_key, time(), time())

    def _remove_first_call(self):
        self._redis.zremrangebyrank(self._calls_key, 0, 0)


class SimpleStorage(Limiter):
    @property
    def calls(self):
        """
        A list of times that our client API was called.
        """
        return self._calls

    @property
    def call_count(self):
        return len(self.calls)

    def _get_first_call(self):
        return self.calls[0]

    def _record_call(self):
        self.calls.append(time())

    def _remove_first_call(self):
        del self.calls[0]


class SimpleLimiter(SingleProcessLimiter, SimpleStorage):
    def __init__(self, client, timeout, calls_per_batch, seconds_per_batch):
        self.client = client
        self._timeout = timeout
        self._calls_per_batch = calls_per_batch
        self._seconds_per_batch = seconds_per_batch
        self._calls = []


class RedisLimiter(SingleProcessLimiter, RedisStorage):
    def __init__(self,
                 client,
                 timeout,
                 calls_per_batch,
                 seconds_per_batch,
                 redis_host,
                 redis_port,
                 redis_db):
        self.client = client
        self._timeout = timeout
        self._calls_per_batch = calls_per_batch
        self._seconds_per_batch = seconds_per_batch
        self._redis = StrictRedis(host=redis_host, port=redis_port, db=redis_db)
        self._calls_key = "redis_limiter_api_call_times"

from copy_reg import pickle
from multiprocessing import Pool
from types import MethodType

from redis import StrictRedis

from cowboycushion.limiter import Limiter, RedisStorage, SimpleStorage


class MultiprocessingLimiter(object):
    def close(self):
        self.pool.close()

    def join(self):
        self.pool.join()

    def _call_api(self, attr):
        self._record_call()
        return lambda *args, **kwargs: self.pool.apply_async(getattr(self.client, attr), args, kwargs)


class SimpleMultiprocessingLimiter(MultiprocessingLimiter, SimpleStorage, Limiter):
    def __init__(self, client, timeout, calls_per_batch, seconds_per_batch, pool_size):
        self.pool = Pool(pool_size)
        self.client = client
        self._timeout = timeout
        self._calls_per_batch = calls_per_batch
        self._seconds_per_batch = seconds_per_batch
        self._calls = []


class RedisMultiprocessingLimiter(MultiprocessingLimiter, RedisStorage, Limiter):
    def __init__(self,
                 client,
                 timeout,
                 calls_per_batch,
                 seconds_per_batch,
                 redis_host,
                 redis_port,
                 redis_db,
                 pool_size):
        self.client = client
        self._timeout = timeout
        self._calls_per_batch = calls_per_batch
        self._seconds_per_batch = seconds_per_batch
        self._redis = StrictRedis(host=redis_host, port=redis_port, db=redis_db)
        self.pool = Pool(pool_size)
        self._calls_key = "redis_limiter_api_call_times"


def _pickle_method(method):
    func_name = method.im_func.__name__
    obj = method.im_self
    cls = method.im_class
    return _unpickle_method, (func_name, obj, cls)


def _unpickle_method(func_name, obj, cls):
    for cls in cls.mro():
        try:
            func = cls.__dict__[func_name]
        except KeyError:
            pass
        else:
            break
    return func.__get__(obj, cls)


pickle(MethodType, _pickle_method, _unpickle_method)

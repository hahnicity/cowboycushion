# cowboycushion
Rate limiting libraries for making API calls with python clients

## Installation

    pip install cowboycushion

## Usage
### Limiting the rate of API calls
We have multiple different ways of limiting API calls. One using a simple python wrapper
that stores all call times within the python object, and the other that stores call times
inside a Redis DB.

#### Pure Python Wrapper

    from cowboycushion.limiter import SimpleLimiter
    from clientapi import MyAPIClient
    
    client = MyAPIClient(...)
    limited_client = SimpleLimiter(client, <timeout for polling to call API>, 1000, 60 * 10)

Now we can call the client like we normally would call the `client` object

    limited_client.my_client_method(...)

The `SimpleLimiter` will keep track of all the API calls that we make and only attempt to
make an API call when possible. Since `SimpleLimiter` is a pure python construct all call
times will be lost when our program stops execution. For this reason we have created a 
`RedisLimiter` to add persistence of call time storage

#### Redis Limiter

    from cowboycushion.limiter import RedisLimiter
    from clientapi import MyAPIClient

    client = MyAPIClient
    limited_client = RedisLimiter(client, <timeout for polling>, 1000, 60 * 10, "localhost", 6379, 0)
    limited_client.my_client_method(...)

If our program halts execution then redis will maintain our list of the times we called 
the API. When we reinstantiate the limiter then our client will pick up the list of these 
calls and be able to know whether/not we should make an API call.

### MultiprocessingLimiter
We can use our limiter in a similar way if we want to use multiprocessing as well. In this case however
we are using an implementation of `multiprocessing.Pool` inside the multiprocessing limiter. Each function
call we make will return an asynchronous job.

    from cowboycushion.multiprocess_limiter import SimpleMultiprocessingLimiter
    from clientapi import MyAPIClient
    
    client = MyAPIClient(...)
    limited_client = SimpleMultiprocessingLimiter(client, <timeout for polling to call API>, 1000, 60 * 10, <pool size>)
    async_job = limited_client.my_client_method(...)
    result = async_job.get()
    limited_client.close()
    limited_client.join()

*Disclaimer* since we cannot actually pickle methods (only functions) we had to make some modifications to the
way python pickles objects in `cowboycushion.multiprocessing_limiter`. The method we used is described in this
[stackoverflow post][1]. As a result of these modifications *only* import cowboycushion.multiprocessing_pool if you
need it.


[1]: http://stackoverflow.com/questions/1816958/cant-pickle-type-instancemethod-when-using-pythons-multiprocessing-pool-ma

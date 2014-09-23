# discourse
A data analysis package using the Disqus API.

## Installation
    git clone git@github.com:hahnicity/discourse.git
    cd discourse
	python setup.py develop

## Usage
### Limiting the rate of API calls
As of this moment we only have a tool that limits the rate of the API calls we 
make to the Disqus API. So given our rate of calls (1000 calls every 10 minutes)
we can input this logic into the limiter.

    from discourse.limiter import Limiter
    from disqusapi import DisqusAPI
    
    disqus = DisqusAPI(secret_key=secret, public_key=public)
    client = Limiter(disqus, <timeout>, 1000, 60 * 10)

Now we can call the client like we normally would call the `disqus` object

    client.posts.details(post=1, version="3.0")

The only difference is the limiter will keep track of the time we are making
API calls to the Disqus API. If we go over our quota, the rate limiter will
wait until the next time we are available to make a call, checking at interval,
`<timeout>` that we have specified.

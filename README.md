# cowboycushion
Rate limiting libraries for making API calls with python clients

## Installation

    pip install cowboycushion

## Usage
### Limiting the rate of API calls
As of this moment we only have a tool that limits the rate of the API calls we 
make for a discrete client. So given our rate of calls (1000 calls every 10 minutes)
we can input this logic into the limiter.

    from cowboycushion.limiter import Limiter
    from clientapi import MyAPIClient
    
    client = MyAPIClient(secret_key=secret, public_key=public)
    limited_client = Limiter(client, <timeout>, 1000, 60 * 10)

Now we can call the client like we normally would call the `client` object

    limited_client.my_client_method(...)

The Limiter will keep track of all the API calls that we make and only attempt to
make an API call when possible.

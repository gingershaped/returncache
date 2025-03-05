# returncache

A very, very small Python utility library for caching the return value of a function until a given `datetime` has passed.

## example

```python
from time import sleep
from datetime import datetime, timedelta

from returncache import returncache

# This only has to be recomputed every ten minutes
@returncache()
def cached_square(value) -> tuple[datetime, float]:
    print("squaring!!")
    return datetime.now() + timedelta(minutes=10), value ** 2


# only the first call will cause the body of cached_square() to run
first = cached_square(42)  # prints "squaring!!"
second = cached_square(42) # does not print anything

# wait for a bit...
sleep(60 * 15)
third = cached_square(42)  # prints "squaring!!"

# by default, the internal cache is keyed by a hash of the parameters.
# this does require all parameters to be hashable.
# you can opt out of this behavior by passing keyed_by_parameters=False to @returncache()
# because the parameter is different, cached_square() _will_ run here!
fourth = cached_square(69) # prints "squaring!!"
```

Coroutines are also supported:
```py
from asyncio import run
from aiohttp import ClientSession
from returncache import returncache
from datetime import datetime, timedelta

@returncache()
async def cached_network_request(url) -> bytes:
    async with ClientSession() as session:
        async with session.get(url) as response:
            return datetime.now() + timedelta(minutes=10), await response.json()

async def main():
    # only makes one network request
    first = await cached_network_request("https://httpbin.org/get")
    second = await cached_network_request("https://httpbin.org/get")

asyncio.run(main())
```
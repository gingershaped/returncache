from datetime import datetime
import unittest

from returncache import returncache

now = lambda: datetime.fromtimestamp(1)

class TestReturncache(unittest.TestCase):

    def test_sync_cached(self):
        invocations = 0

        @returncache(now)
        def foo():
            nonlocal invocations
            invocations += 1
            return (datetime.fromtimestamp(2), ":3")

        self.assertEqual(foo(), ":3")
        self.assertEqual(foo(), ":3")
        self.assertEqual(invocations, 1)

    def test_sync_cache_miss(self):
        invocations = 0

        @returncache(now)
        def foo():
            nonlocal invocations
            invocations += 1
            return (datetime.fromtimestamp(0), ":3")

        self.assertEqual(foo(), ":3")
        self.assertEqual(foo(), ":3")
        self.assertEqual(invocations, 2)

class TestAsyncReturncache(unittest.IsolatedAsyncioTestCase):
    async def test_async_cached(self):
        invocations = 0

        @returncache(now)
        async def foo():
            nonlocal invocations
            invocations += 1
            return (datetime.fromtimestamp(2), ":3")

        self.assertEqual(await foo(), ":3")
        self.assertEqual(await foo(), ":3")
        self.assertEqual(invocations, 1)

    async def test_async_cache_miss(self):
        invocations = 0

        @returncache(now)
        async def foo():
            nonlocal invocations
            invocations += 1
            return (datetime.fromtimestamp(0), ":3")

        self.assertEqual(await foo(), ":3")
        self.assertEqual(await foo(), ":3")
        self.assertEqual(invocations, 2)

if __name__ == "__main__":
    unittest.main()
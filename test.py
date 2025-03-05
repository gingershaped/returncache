# SPDX-License-Identifier: MPL-2.0

from datetime import datetime
import unittest

from returncache import returncache

now = lambda: datetime.fromtimestamp(1)


class TestReturncache(unittest.TestCase):

    def test_sync_cached(self):
        invocations = 0

        @returncache(now=now)
        def foo(value):
            nonlocal invocations
            invocations += 1
            return (datetime.fromtimestamp(2), value)

        self.assertEqual(foo(":3"), ":3")
        self.assertEqual(foo(":3"), ":3")
        self.assertEqual(foo(":3c"), ":3c")
        self.assertEqual(invocations, 2)

    def test_sync_no_parameter_keying(self):
        invocations = 0

        @returncache(keyed_by_parameters=False, now=now)
        def foo(value):
            nonlocal invocations
            invocations += 1
            return (datetime.fromtimestamp(2), value)

        self.assertEqual(foo(":3"), ":3")
        self.assertEqual(foo(":3c"), ":3")
        self.assertEqual(invocations, 1)

    def test_sync_cache_miss(self):
        invocations = 0

        @returncache(now=now)
        def foo(value):
            nonlocal invocations
            invocations += 1
            return (datetime.fromtimestamp(0), value)

        self.assertEqual(foo(":3"), ":3")
        self.assertEqual(foo(":3"), ":3")
        self.assertEqual(foo(":3c"), ":3c")
        self.assertEqual(invocations, 3)


class TestAsyncReturncache(unittest.IsolatedAsyncioTestCase):
    async def test_async_cached(self):
        invocations = 0

        @returncache(now=now)
        async def foo(value):
            nonlocal invocations
            invocations += 1
            return (datetime.fromtimestamp(2), value)

        self.assertEqual(await foo(":3"), ":3")
        self.assertEqual(await foo(":3"), ":3")
        self.assertEqual(await foo(":3c"), ":3c")
        self.assertEqual(invocations, 2)

    async def test_async_no_parameter_keying(self):
        invocations = 0

        @returncache(keyed_by_parameters=False, now=now)
        async def foo(value):
            nonlocal invocations
            invocations += 1
            return (datetime.fromtimestamp(2), value)

        self.assertEqual(await foo(":3"), ":3")
        self.assertEqual(await foo(":3c"), ":3")
        self.assertEqual(invocations, 1)

    async def test_async_cache_miss(self):
        invocations = 0

        @returncache(now=now)
        async def foo(value):
            nonlocal invocations
            invocations += 1
            return (datetime.fromtimestamp(0), value)

        self.assertEqual(await foo(":3"), ":3")
        self.assertEqual(await foo(":3"), ":3")
        self.assertEqual(await foo(":3c"), ":3c")
        self.assertEqual(invocations, 3)


if __name__ == "__main__":
    unittest.main()

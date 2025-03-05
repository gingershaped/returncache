from asyncio import iscoroutinefunction
from functools import partial, wraps
import inspect
from datetime import datetime
from typing import Any, Awaitable, Callable, Coroutine, overload

type SynchronousCacheable[**P, R] = Callable[P, tuple[datetime, R]]
type AsynchronousCacheable[**P, R] = Callable[
    P, Coroutine[Any, Any, tuple[datetime, R]]
]
type Cacheable[**P, R] = SynchronousCacheable[P, R] | AsynchronousCacheable[P, R]
type AnyCoroutine[R] = Coroutine[Any, Any, R]
type Now = Callable[[], datetime]

NOW = lambda: datetime.now()


@overload
def _returncache_inner[
    **P, R
](now: Now, method: SynchronousCacheable[P, R]) -> Callable[P, R]: ...


@overload
def _returncache_inner[
    **P, R
](now: Now, method: AsynchronousCacheable[P, R]) -> Callable[P, AnyCoroutine[R]]: ...


def _returncache_inner[
    **P, R
](now: Now, method: Cacheable[P, R]) -> Callable[P, R | AnyCoroutine[R]]:
    value: tuple[datetime, R] | None = None

    async def _async_store(ret: Awaitable[tuple[datetime, R]]) -> R:
        nonlocal value
        value = await ret
        return value[1]

    async def _dummy(value):
        return value

    @wraps(method)
    def _wrapper(*args: P.args, **kwargs: P.kwargs):
        nonlocal value
        if value is None or value[0] < now():
            ret = method(*args, **kwargs)
            if inspect.isawaitable(ret):
                return _async_store(ret)
            value = ret
        if inspect.iscoroutinefunction(method):
            return _dummy(value[1])
        return value[1]

    return _wrapper


def returncache(now: Now = NOW):
    return partial(_returncache_inner, now)

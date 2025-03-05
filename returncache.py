# SPDX-License-Identifier: MPL-2.0

import inspect
from datetime import datetime
from functools import partial, wraps
from typing import Any, Awaitable, Callable, Coroutine, overload

type SynchronousCacheable[**P, R] = Callable[P, tuple[datetime, R]]
type AsynchronousCacheable[**P, R] = Callable[
    P, Coroutine[Any, Any, tuple[datetime, R]]
]
type Cacheable[**P, R] = SynchronousCacheable[P, R] | AsynchronousCacheable[P, R]
type AnyCoroutine[R] = Coroutine[Any, Any, R]
type Now = Callable[[], datetime]

_NOW = lambda: datetime.now()
_DEFAULT_CACHE_KEY = 0


@overload
def _returncache_inner[
    **P, R
](keyed_by_parameters: bool, now: Now, method: SynchronousCacheable[P, R]) -> Callable[
    P, R
]: ...


@overload
def _returncache_inner[
    **P, R
](keyed_by_parameters: bool, now: Now, method: AsynchronousCacheable[P, R]) -> Callable[
    P, AnyCoroutine[R]
]: ...


def _returncache_inner[
    **P, R
](keyed_by_parameters: bool, now: Now, method: Cacheable[P, R]) -> Callable[
    P, R | AnyCoroutine[R]
]:
    values: dict[int, tuple[datetime, R]] = {}

    async def _async_store(ret: Awaitable[tuple[datetime, R]], key: int) -> R:
        nonlocal values
        values[key] = await ret
        return values[key][1]

    async def _dummy(value):
        return value

    @wraps(method)
    def _wrapper(*args: P.args, **kwargs: P.kwargs):
        nonlocal values
        if keyed_by_parameters:
            try:
                key = hash((args, tuple(kwargs.items()))) # it's probably fine...
            except TypeError as error:
                raise ValueError(
                    "All parameters to a returncached method with keyed_by_parameters = True must be hashable"
                ) from error
        else:
            key = _DEFAULT_CACHE_KEY
        value = values.get(key)
        if value is None or value[0] < now():
            ret = method(*args, **kwargs)
            if inspect.isawaitable(ret):
                return _async_store(ret, key)
            value = ret
            values[key] = value
        if inspect.iscoroutinefunction(method):
            return _dummy(value[1])
        return value[1]

    return _wrapper

def returncache(*, keyed_by_parameters: bool = True, now: Now = _NOW):
    """Cache the return value of a function for some amount of time.
    
    Parameters:
        keyed_by_parameters: If True, passing different parameters to the function will
            store its return value in a different cache. The parameters are hashed to achieve this.
        now: A function which will be called with no arguments to determine when "now" is
            for the purpose of checking cache expiration. Defaults to `lambda: datetime.now()`.
    
    Returns:
        A wrapper function which, when called, wraps its callable argument in an expiring cache.
    """
    return partial(_returncache_inner, keyed_by_parameters, now)

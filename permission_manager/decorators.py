from collections.abc import Callable
from functools import wraps

from .exceptions import PermissionManagerDenied
from .result import PermissionResult


def catch_denied_exception(fn: Callable) -> Callable:
    """Decorator that catches PermissionManagerDenied exception.

    This decorator catches `PermissionManagerDenied` exception and returns a
    `PermissionResult` instead.

    Args:
        fn (Callable): The function to be decorated.

    Returns:
        Callable: The decorated function.
    """
    fn.catch_denied_exception = True

    @wraps(fn)
    def wrapper(self) -> Callable | PermissionResult:
        try:
            return fn(self)
        except PermissionManagerDenied as e:
            return PermissionResult(str(e) or None)

    return wrapper


def cache_permission(fn: Callable) -> Callable:
    """Decorator that caches the permission result.

    This decorator caches the result of the decorated permission function to
    optimize repeated permission checks.

    Args:
        fn (Callable): The function to be decorated.

    Returns:
        Callable: The decorated function.
    """
    fn.cache_permission = True

    @wraps(fn)
    def wrapper(self) -> Callable:
        if not self.cache:
            return fn(self)

        try:
            return self._cache[fn.__name__]
        except KeyError:
            self._cache[fn.__name__] = fn(self)
            return self._cache[fn.__name__]

    return wrapper


def alias(names: list[str]) -> Callable:
    """Decorator that adds aliases to a permission function.

    This decorator allows you to define alternative names (aliases) for the
    decorated permission function.

    Args:
        names (list[str]): The alias name(s) to be added to the permission
            function.

    Returns:
        Callable: The decorated function.
    """

    def decorator(fn) -> Callable:
        fn.aliases = getattr(fn, 'aliases', set()) | set(names)
        return fn

    return decorator

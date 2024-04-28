from collections.abc import Callable
from functools import wraps

from .exceptions import PermissionManagerDenied
from .result import PermissionResult


def catch_denied_exception(fn: Callable) -> Callable:
    """Decorator that catches PermissionManagerDenied exception.

    Catch `PermissionManagerDenied` exception and return
    PermissionResult instead
    """

    @wraps(fn)
    def wrapper(self) -> Callable | PermissionResult:
        try:
            return fn(self)
        except PermissionManagerDenied as e:
            return PermissionResult(str(e) or None)

    return wrapper


def cache_permission(fn: Callable) -> Callable:
    """Decorator that cache permission result."""

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


def alias(name: str) -> Callable:
    """Decorator that add alias to permission."""

    def decorator(fn) -> Callable:
        fn.permission_manager_alias = name
        return fn

    return decorator

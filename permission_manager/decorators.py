from functools import wraps

from .exceptions import PermissionManagerDenied
from .result import PermissionResult


def catch_denied_exception(fn):
    """
    Catch `PermissionManagerDenied` exception and return
    PermissionResult instead
    """

    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except PermissionManagerDenied as e:
            return PermissionResult(str(e) or None)

    return wrapper


def cache_permission(fn):
    """Cache permission result"""

    @wraps(fn)
    def wrapper(self, *args, **kwargs):
        if not self.cache:
            return fn(self, *args, **kwargs)

        try:
            return self._cache[fn.__name__]
        except KeyError:
            self._cache[fn.__name__] = fn(self, *args, **kwargs)
            return self._cache[fn.__name__]

    return wrapper

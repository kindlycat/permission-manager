import re
from collections.abc import Iterable
from contextlib import suppress
from functools import cached_property
from typing import Any

from .decorators import cache_permission, catch_denied_exception
from .exceptions import PermissionManagerError
from .result import PermissionResult


permission_re = re.compile(r'^has_(\w+)_permission$')


class BasePermissionMeta(type):
    """Metaclass for bind permission actions."""

    def __new__(cls, *args, **kwargs) -> type:
        new_cls = super().__new__(cls, *args, **kwargs)
        new_cls._actions = {}
        new_cls._aliases = {}
        new_cls.bind_actions()
        return new_cls

    def bind_actions(cls) -> None:
        """Collect all actions, add decorators."""
        for attr_name in dir(cls):
            if action_name := permission_re.match(attr_name):
                permission_fn = cache_permission(
                    catch_denied_exception(getattr(cls, attr_name))
                )
                setattr(cls, attr_name, permission_fn)
                cls._actions[action_name.group(1)] = permission_fn

                if alias := getattr(
                    permission_fn, 'permission_manager_alias', None
                ):
                    cls._aliases[alias] = permission_fn


class BasePermissionManager(metaclass=BasePermissionMeta):
    """Base permission manager class."""

    def __init__(
        self,
        *,
        user: Any | None = None,
        instance: Any | None = None,
        cache: bool = False,
        **context,
    ) -> None:
        self.user = user
        self.instance = instance
        self.context = context
        self.cache = cache
        self._cache = {}

    @classmethod
    def create(
        cls: type['BasePermissionManager'],
        name: str,
        **type_dict,
    ) -> type:
        """Create new manager dynamically."""
        return type(name, (cls,), type_dict)

    def has_permission(self, action: str) -> bool:
        """Check permission."""
        with suppress(KeyError):
            return self._actions[action](self)

        try:
            return self._aliases[action](self)
        except KeyError as exc:
            raise ValueError(
                f'"{self.__class__.__name__}" doesn\'t have "{action}" action.'
            ) from exc

    def get_result_value(
        self,
        *,
        value: bool | dict | PermissionResult,
        with_messages: bool = False,
    ) -> bool | dict:
        """Serialize result value."""
        if isinstance(value, dict):
            return {
                k: self.get_result_value(
                    value=v,
                    with_messages=with_messages,
                )
                for k, v in value.items()
            }

        result = bool(value)

        if with_messages:
            result = {
                'allow': result,
                'messages': getattr(value, 'returned_message', None),
            }
        return result

    def resolve(
        self,
        *,
        actions: Iterable | None = None,
        with_messages: bool = False,
    ) -> dict:
        """Resolve list of actions."""
        if actions is None:
            actions = self._actions.keys()

        return {
            action: self.get_result_value(
                value=self.has_permission(action),
                with_messages=with_messages,
            )
            for action in actions
        }


class PermissionManager(BasePermissionManager):
    """Permission manager class.

    Permission manager class with additional functionality
    to check parent permissions.
    """

    parent_attr: str | None = None

    @cached_property
    def parent(self) -> Any:
        """Get parent object."""
        if parent := self.context.get('parent'):
            return parent
        return self.get_parent_from_instance()

    def get_parent_from_instance(self) -> Any:
        """Get parent object from instance."""
        if not self.instance:
            raise PermissionManagerError('Instance is missing.')

        if not self.parent_attr:
            raise PermissionManagerError(
                'Attribute `parent_attr` is not defined.'
            )

        return getattr(self.instance, self.parent_attr)

    @property
    def has_parent(self) -> bool:
        """Check if object has parent."""
        try:
            return bool(self.parent)
        except PermissionManagerError:
            return False

    @cached_property
    def parent_permission_manager(self) -> 'PermissionManager':
        """Get parent permission manager."""
        if from_context := self.context.get('parent_permission_manager'):
            return from_context

        return self.parent.permission_manager(
            user=self.user,
            instance=self.parent,
            context=self.context,
        )

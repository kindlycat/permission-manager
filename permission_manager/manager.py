import re
from functools import cached_property
from typing import Any, Dict, Iterable, Optional, Union

from .result import PermissionResult
from .decorators import cache_permission, catch_denied_exception
from .exceptions import PermissionManagerException


permission_re = re.compile(r'^has_(\w+)_permission$')


class BasePermissionMeta(type):
    """Metaclass for bind permission actions"""

    def __new__(cls, *args, **kwargs) -> type:
        new_cls = super().__new__(cls, *args, **kwargs)
        new_cls._actions = {}
        new_cls.bind_actions()
        return new_cls

    def bind_actions(cls) -> None:
        """Collect all actions, add decorators"""
        for attr_name in dir(cls):
            if action_name := permission_re.match(attr_name):
                permission_fn = cache_permission(
                    catch_denied_exception(getattr(cls, attr_name))
                )
                setattr(cls, attr_name, permission_fn)
                cls._actions[action_name.group(1)] = permission_fn


class BasePermissionManager(metaclass=BasePermissionMeta):
    """Base permission manager class"""

    def __init__(
        self,
        user: Optional[Any] = None,
        instance: Optional[Any] = None,
        cache: bool = False,
        **context,
    ) -> None:
        self.user = user
        self.instance = instance
        self.context = context
        self.cache = cache
        self._cache = {}

    @classmethod
    def create(cls, name: str, **type_dict) -> type:
        """Create new manager dynamically"""

        return type(name, (cls,), type_dict)

    def has_permission(self, action: str) -> bool:
        """Check permission"""

        try:
            return self._actions[action](self)
        except KeyError as exc:
            raise ValueError(
                f'"{self.__class__.__name__}" doesn\'t have "{action}" action.'
            ) from exc

    def get_result_value(
        self,
        value: Union[bool, dict, PermissionResult],
        with_messages: bool = False,
    ) -> Union[bool, dict]:
        """Serialize result value"""

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
                'message': getattr(value, 'message', None),
            }
        return result

    def resolve(
        self,
        actions: Optional[Iterable] = None,
        with_messages: bool = False,
    ) -> Dict:
        """Resolve list of actions"""

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
    """Permission manager class with additional functionality to check parent permissions"""

    parent_attr: Optional[str] = None

    @cached_property
    def parent(self) -> Any:
        """Get parent object"""

        if parent := self.context.get('parent'):
            return parent
        return self.get_parent_from_instance()

    def get_parent_from_instance(self) -> Any:
        """Get parent object from instance"""

        if not self.instance:
            raise PermissionManagerException('Instance is missing.')

        if not self.parent_attr:
            raise PermissionManagerException(
                'Attribute `parent_attr` is not defined.'
            )

        return getattr(self.instance, self.parent_attr)

    @property
    def has_parent(self) -> bool:
        """Check if object has parent"""

        try:
            return bool(self.parent)
        except PermissionManagerException:
            return False

    @cached_property
    def parent_permission_manager(self) -> 'PermissionManager':
        """Get parent permission manager"""

        return self.parent.permission_manager(
            user=self.user,
            instance=self.parent,
            context=self.context,
        )

# Permission Manager

A simple way to manage object permissions.

## Install

```bash
pip install permission-manager
```

## Example

Use `BasePermissionManager`

```python
import dataclasses
from permission_manager import BasePermissionManager, PermissionResult


@dataclasses.dataclass
class User:
    name: str


@dataclasses.dataclass
class Person:
    first_name: str
    last_name: str
    status: str


class PersonPermissionManager(BasePermissionManager):
    instance: Person

    def has_create_permission(self):
        return True
    
    def has_delete_permission(self):
        return self.user.name == 'admin'

    def has_access_permission(self):
        if self.instance.status == 'excommunicado':
            return PermissionResult('Due status')
        return True


manager = PersonPermissionManager()
manager.has_permission('create')
# same as 
# manager.has_create_permission()
# > True

manager = PersonPermissionManager(
    instance=Person(
        first_name='John',
        last_name='Wick',
        status='excommunicado',
    ),
    user=User(name='Ms. Perkins'),
)
manager.has_permission('delete')
# > False
manager.has_permission('access')
# > PermissionResult(value=False, message=['Due status'])

manager.resolve()
# > {'access': False, 'create': True, 'delete': False}
manager.resolve(with_messages=True)
# > {'access': {'allow': False, 'messages': ['Due status']},
#    'create': {'allow': True, 'messages': None},
#    'delete': {'allow': False, 'messages': None}}
```

Also, it's include `PermissionManager`, which add additional functionality to check parent permissions

```python
import dataclasses
from permission_manager import PermissionManager


class PostPermissionManager(PermissionManager):
    instance: 'Post'

    def has_update_permission(self):
        return self.instance.status == 'draft'


@dataclasses.dataclass
class Post:
    title: str
    status: str = 'draft'

    permission_manager = PostPermissionManager

    
class ImagePermissionManager(PermissionManager):
    parent_attr = 'post'
    instance: 'Image'
    
    def has_update_permission(self):
        return self.parent_permission_manager.has_permission('update')


@dataclasses.dataclass
class Image:
    post: Post
    file: str

post = Post(title='Test')
manager = ImagePermissionManager(
    instance=Image(
        post=post,
        file='/path/to/file',
    ),
)
manager.has_permission('update')
# > True
post.status = 'published'
manager.has_permission('update')
# > False
```

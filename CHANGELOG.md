# Changelog

### 0.3.0
- Get a parent_permission_manager from the `context` in the `PermissionManager` if it's passed.
- Add `message_if_false` that indicating whether to include the `message` when the `value` is False.
- Rename `message` -> `messages` in the `resolve` method if `with_messages` is passed.
- Rename `PermissionManagerException` -> `PermissionManagerError`

### 0.2.0
- Add `alias` decorator

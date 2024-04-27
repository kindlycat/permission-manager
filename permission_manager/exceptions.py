class PermissionManagerError(Exception):
    """Base permission manager exception."""


class PermissionManagerDenied(PermissionManagerError):  # noqa: N818
    """Exception for negative result."""

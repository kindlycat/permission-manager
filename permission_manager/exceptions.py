class PermissionManagerException(Exception):
    """Base permission manager exception"""


class PermissionManagerDenied(PermissionManagerException):
    """Exception for negative result"""

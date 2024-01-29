from dataclasses import dataclass
from typing import List, Optional, Union


@dataclass
class PermissionResult:
    """Class for storing permission value and message"""

    message: Optional[Union[str, List]] = None
    value: bool = False

    def __post_init__(self):
        if self.message and not isinstance(self.message, list):
            self.message = [self.message]

    def __bool__(self):
        return self.value

    def __repr__(self):
        return (
            f'PermissionResult(value={self.value!r}, message={self.message!r})'
        )

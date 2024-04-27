from dataclasses import dataclass


@dataclass
class PermissionResult:
    """Class for storing permission value and message."""

    message: str | list | None = None
    value: bool = False

    def __post_init__(self) -> None:
        """Ensure the value is a list."""
        if self.message and not isinstance(self.message, list):
            self.message = [self.message]

    def __bool__(self) -> bool:
        """Return the boolean value of the PermissionResult object."""
        return self.value

    def __repr__(self) -> str:
        """Return a string representation of the PermissionResult object."""
        return (
            f'PermissionResult(value={self.value!r}, message={self.message!r})'
        )

from dataclasses import dataclass


@dataclass
class PermissionResult:
    """Class for storing permission values and messages.

    Attributes:
        message (str | list | None): The message associated with the
            permission result.
        value (bool): The boolean value indicating the permission result.
        message_if_false (bool): A flag indicating whether to include the
            message when the value is False.
    """

    message: str | list | None = None
    value: bool = False
    message_if_false: bool = True

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

    @property
    def returned_message(self) -> list | None:
        """Return the message based on the value and message_if_false flag.

        Returns:
            list | None: The message associated with the permission result,
                or None if the value is True and message_if_false is True.
        """
        if self.value and self.message_if_false:
            return None
        return self.message

from __future__ import annotations

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from permission_manager import PermissionResult


def get_result_value(
    *,
    value: bool | dict | PermissionResult,
    with_messages: bool = False,
) -> bool | dict:
    """Serialize result value."""
    if isinstance(value, dict):
        return {
            k: get_result_value(
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

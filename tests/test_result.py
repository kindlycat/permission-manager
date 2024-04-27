import pytest

from permission_manager import PermissionResult


@pytest.mark.parametrize('value', [True, False])
def test_value(value):
    result = PermissionResult(value=value)
    assert bool(result) is value
    assert result.message is None


@pytest.mark.parametrize('message', ['test', ['1', '2']])
def test_message(message):
    result = PermissionResult(message=message)
    if not isinstance(message, list):
        message = [message]
    assert result.message == message

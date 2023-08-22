"""Tests for Flask socket platform."""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from flask_socketio import SocketIOTestClient

from dialoguekit.platforms.flask_socket_platform import FlaskSocketPlatform
from moviebot.agent.agent import MovieBotAgent
from moviebot.controller.controller_flask_socket import ChatNamespace


@pytest.fixture
def mocked_user_db() -> MagicMock:
    """Creates a mocked user database.

    The user is always verified and registered successfully.
    """
    mock = MagicMock()
    mock.verify_user.return_value = True
    mock.register_user.return_value = True
    return mock


@pytest.fixture
def mocked_agent_class():
    """Creates a mocked agent class."""

    class MockedAgent(MovieBotAgent):
        def __init__(self):
            pass

    return MockedAgent


@pytest.fixture
def flask_platform(mocked_agent_class) -> FlaskSocketPlatform:
    platform = FlaskSocketPlatform(mocked_agent_class)
    platform.app.testing = True
    return platform


@pytest.fixture
def client(
    flask_platform: FlaskSocketPlatform, mocked_user_db: MagicMock
) -> SocketIOTestClient:
    """Creates a test client for Flask socket platform."""
    with patch(
        "moviebot.controller.controller_flask_socket.FlaskSocketPlatform.get_new_agent",  # noqa: E501
        return_value=MagicMock(spec=MovieBotAgent),
    ):
        namespace = ChatNamespace("/", flask_platform)
        namespace.user_db = mocked_user_db
        flask_platform.socketio.on_namespace(namespace)
        yield flask_platform.socketio.test_client(flask_platform.app)


@pytest.mark.parametrize(
    "event",
    [
        ("register"),
        ("login"),
    ],
)
def test_handle_authentication_empty_fields(
    client: SocketIOTestClient, event: str
) -> None:
    """Test methods for login and registration with empty fields."""

    data = {"username": "", "password": ""}
    client.emit(event, data)
    received = client.get_received()

    assert received[0]["name"] == "authentication"
    assert received[0]["args"][0] == {
        "success": False,
        "error": "Username and password cannot be empty",
    }


@pytest.mark.parametrize(
    "event",
    [
        ("register"),
        ("login"),
    ],
)
def test_handle_authentication_success(
    client: SocketIOTestClient,
    event: str,
) -> None:
    """Test successful login and registration."""

    client.emit(event, {"username": "testuser", "password": "testpassword"})
    received = client.get_received()

    assert received[0]["name"] == "authentication"
    assert received[0]["args"][0]["success"] is True

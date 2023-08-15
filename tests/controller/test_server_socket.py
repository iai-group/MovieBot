"""Tests for Flask socket platform."""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from dialoguekit.platforms.flask_socket_platform import FlaskSocketPlatform
from flask_socketio import SocketIOTestClient

from moviebot.agent.agent import MovieBotAgent
from moviebot.controller.controller_flask_socket import ChatNamespace


@pytest.fixture
def mocked_agent_class():
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
def client(flask_platform: FlaskSocketPlatform) -> SocketIOTestClient:
    with patch(
        "moviebot.database.db_users.UserDB", return_value=MagicMock()
    ) and patch(
        "moviebot.controller.controller_flask_socket.FlaskSocketPlatform.get_new_agent",  # noqa: E501
        return_value=MagicMock(spec=MovieBotAgent),
    ):
        flask_platform.socketio.on_namespace(ChatNamespace("/", flask_platform))
        yield flask_platform.socketio.test_client(flask_platform.app)


@pytest.mark.parametrize(
    "event, expected_event",
    [
        ("register", "register_response"),
        ("login", "login_response"),
    ],
)
def test_handle_authentication_empty_fields(
    client: SocketIOTestClient, event: str, expected_event: str
) -> None:
    """Test methods for login and registration with empty fields."""

    data = {"username": "", "password": ""}
    client.emit(event, data)
    received = client.get_received()

    assert received[0]["name"] == expected_event
    assert received[0]["args"][0] == {
        "success": False,
        "error": "Username and password cannot be empty",
    }


@pytest.mark.parametrize(
    "event, expected_event",
    [
        ("register", "register_response"),
        ("login", "login_response"),
    ],
)
def test_handle_authentication_success(
    client: SocketIOTestClient,
    event: str,
    expected_event: str,
) -> None:
    """Test successful login and registration."""
    with patch(
        "moviebot.database.db_users.UserDB.verify_user", return_value=True
    ) and patch(
        "moviebot.database.db_users.UserDB.register_user", return_value=True
    ):
        client.emit(event, {"username": "testuser", "password": "testpassword"})
        received = client.get_received()

        assert received[0]["name"] == expected_event
        assert received[0]["args"][0]["success"] is True

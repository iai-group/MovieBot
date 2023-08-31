"""Tests for server socket functionality."""
from unittest.mock import MagicMock, patch

import pytest
from flask import Flask
from flask_socketio import SocketIOTestClient

from moviebot.controller.server_socket import ChatNamespace, app, socketio


@pytest.fixture
def mocked_user_db() -> MagicMock:
    return MagicMock()


@pytest.fixture
def flask_app() -> Flask:
    app.testing = True
    return app


@pytest.fixture
def client(flask_app: Flask, mocked_user_db: MagicMock) -> SocketIOTestClient:
    with patch(
        "moviebot.controller.server_socket.UserDB", return_value=mocked_user_db
    ):
        socketio.on_namespace(ChatNamespace("/"))
        yield socketio.test_client(flask_app)


@pytest.mark.parametrize(
    "event, expected_event",
    [
        ("register", "authentication"),
        ("login", "authentication"),
    ],
)
def test_handle_authentication_empty_fields(
    client, event, expected_event
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
        ("register", "authentication"),
        ("login", "authentication"),
    ],
)
def test_handle_authentication_success(
    client, mocked_user_db, event, expected_event
) -> None:
    """Test successful login and registration."""

    mocked_user_db.verify_user.return_value = True

    client.emit(event, {"username": "testuser", "password": "testpassword"})
    received = client.get_received()

    assert received[0]["name"] == expected_event
    assert received[0]["args"][0]["success"] is True

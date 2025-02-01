import pytest
from fastapi.testclient import TestClient
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app.main import app
from unittest.mock import patch, MagicMock
import uuid

client = TestClient(app)

@pytest.fixture
def mock_game_wrapper():
    with patch("app.services.game_service.get_game_wrapper") as mock_get:
        mock_game = MagicMock()
        mock_get.return_value = mock_game
        mock_game.get_state.return_value = {"game_state": "waiting for 2nd player"}
        yield mock_game

@pytest.fixture
def game_id():
    return str(uuid.uuid4())

@pytest.fixture
def player_id():
    return "player_1"

# Test: Spiel erstellen mit Standardzeit
def test_create_game_default_time():
    response = client.post("/create_game")
    assert response.status_code == 200
    assert "game_id" in response.json()

# Test: Spiel erstellen mit benutzerdefinierter Zeit
def test_create_game_custom_time():
    response = client.post("/create_game?game_time_in_minutes=15")
    assert response.status_code == 200
    assert "game_id" in response.json()

# Test: Spieler tritt Spiel bei
def test_join_game(mock_game_wrapper, player_id):
    response = client.post("/create_game")
    assert response.status_code == 200

    game_id = response.json()["game_id"]

    response = client.post(f"/join_game/{game_id}", json={"player_id": player_id})
    assert response.status_code == 200
    assert response.json() == {"message": "Joined game successfully"}

# Test: Spielinfo abrufen
def test_get_game_info(mock_game_wrapper, player_id):
    response = client.post("/create_game")
    assert response.status_code == 200

    game_id = response.json()["game_id"]
    response = client.get(f"/game_info/{game_id}/{player_id}")
    assert response.status_code == 200
    assert response.json().get("game_state") == "waiting for 2nd player"

# Test: Spieler kann nicht einem nicht existierenden Spiel beitreten
def test_join_game_not_found(game_id, player_id):
    response = client.post(f"/join_game/{game_id}", json={"player_id": player_id})
    assert response.status_code == 404
    assert response.json()["detail"] == "Game not found"

# Test: Spieler kann nicht ohne player_id beitreten
def test_join_game_missing_player_id(game_id):
    response = client.post(f"/join_game/{game_id}", json={})
    assert response.status_code == 422
    assert response.json()["detail"] == "player_id missing"

# Test: Spiel startet erst nach WebSocket-Verbindung beider Spieler
def test_game_starts_when_two_players_join_and_connect():
    response = client.post("/create_game")
    assert response.status_code == 200

    game_id = response.json()["game_id"]

    client.post(f"/join_game/{game_id}", json={"player_id": "player_1"})
    client.post(f"/join_game/{game_id}", json={"player_id": "player_2"})

    with client.websocket_connect(f"/ws/{game_id}/player_1") as ws1, \
         client.websocket_connect(f"/ws/{game_id}/player_2") as ws2:
        response = client.get(f"/game_info/{game_id}/player_1")
        assert response.status_code == 200
        assert response.json().get("game_state") == "running"

import pytest
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from app.main import app
from fastapi.testclient import TestClient
from app.main import app  # Importiere deine FastAPI-App

client = TestClient(app)

def test_create_game():
    """Testet das Erstellen eines neuen Spiels."""
    response = client.post("/create_game")
    assert response.status_code == 200
    data = response.json()
    assert "game_id" in data
    assert isinstance(data["game_id"], str)

def test_join_game():
    """Testet, dass Spieler einem Spiel beitreten können."""
    # Erst ein Spiel erstellen
    create_response = client.post("/create_game")
    game_id = create_response.json()["game_id"]

    # Spieler tritt dem Spiel bei
    player_id = "player1"
    join_response = client.post(f"/join_game/{game_id}", json={"player_id": player_id})
    assert join_response.status_code == 200
    assert join_response.json()["message"] == "Joined game successfully"

def test_join_game_nonexistent():
    """Testet das Beitreten zu einem nicht existierenden Spiel."""
    response = client.post("/join_game/nonexistent_game", json={"player_id": "player1"})
    assert response.status_code == 404
    assert response.json()["detail"] == "Game not found"

def test_game_state():
    """Testet die Abfrage des Spielstatus."""
    # Erst ein Spiel erstellen
    create_response = client.post("/create_game")
    game_id = create_response.json()["game_id"]

    # Abfrage des Spielstatus
    state_response = client.get(f"/game_state/{game_id}")
    assert state_response.status_code == 200
    data = state_response.json()
    assert "game_state" in data
    assert "num_moves_played" in data
    assert "active_player" in data

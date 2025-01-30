import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def create_game():
    """Hilfsfunktion, um ein neues Spiel zu erstellen"""
    response = client.post("/create_game")
    assert response.status_code == 200
    return response.json()["game_id"]

def join_game(game_id, player_id):
    """Hilfsfunktion, um einem Spiel beizutreten"""
    response = client.post(f"/join_game/{game_id}", json={"player_id": player_id})
    assert response.status_code == 200

def test_valid_move():
    """Testet einen gültigen Zug"""
    game_id = create_game()
    join_game(game_id, "player1")
    join_game(game_id, "player2")

    response = client.post(f"/game_info/{game_id}")
    assert response.status_code == 200

    move = {
        "action": "move",
        "move": {
            "start": {"row": 6, "col": 4},
            "end": {"row": 4, "col": 4}
        }
    }
    
    ws_url = f"ws://localhost:8000/ws/{game_id}/player1"
    with client.websocket_connect(ws_url) as websocket:
        websocket.send_json(move)
        result = websocket.receive_json()
        assert "event" in result
        assert result["event"] == "update"

def test_invalid_move():
    """Testet einen ungültigen Zug"""
    game_id = create_game()
    join_game(game_id, "player1")
    join_game(game_id, "player2")

    move = {
        "action": "move",
        "move": {
            "start": {"row": 6, "col": 4},  # Bauer
            "end": {"row": 6, "col": 6}  # Ungültiger Zug
        }
    }

    ws_url = f"ws://localhost:8000/ws/{game_id}/player1"
    with client.websocket_connect(ws_url) as websocket:
        websocket.send_json(move)
        result = websocket.receive_json()
        assert "event" in result
        assert result["event"] == "update"
        assert result["state"]["game_state"] == "illegal move"

def test_illegal_join():
    """Testet das Beitreten eines nicht existierenden Spiels"""
    response = client.post("/join_game/fake_game_id", json={"player_id": "player1"})
    assert response.status_code == 404
    assert response.json()["detail"] == "Game not found"

def test_max_players():
    """Testet, dass nicht mehr als zwei Spieler einem Spiel beitreten können"""
    game_id = create_game()
    join_game(game_id, "player1")
    join_game(game_id, "player2")

    response = client.post(f"/join_game/{game_id}", json={"player_id": "player3"})
    assert response.status_code == 400
    assert "Game is full" in response.json()["detail"]

def test_get_state_before_join():
    """Testet, dass der Spielstatus abgefragt werden kann, bevor beide Spieler beigetreten sind"""
    game_id = create_game()
    response = client.get(f"/game_info/{game_id}")
    assert response.status_code == 200
    assert response.json()["both_joined"] == False
    assert response.json()["game_state"] == "waiting for 2nd player"

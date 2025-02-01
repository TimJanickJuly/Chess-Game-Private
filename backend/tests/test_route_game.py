import pytest
from fastapi.testclient import TestClient
import sys
import os
import concurrent.futures

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app.main import app

@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c

def receive_with_timeout(ws, timeout=1):
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(ws.receive_json)
        try:
            return future.result(timeout=timeout)
        except concurrent.futures.TimeoutError:
            return None

@pytest.mark.parametrize("test_name, moves, expected_result", [
    ("fools_mate_white", ["e4", "e5", "Qf3", "c6", "Bc4", "a6", "Qxf7#"], "white wins"),
    ("fools_mate_black", ["a3", "e5", "a4", "Qf6", "a5", "Bc5", "a6", "Qxf2#"], "black wins"),
    ("unblockable_check", ["e4", "f5", "a3", "g5", "Qh5#"], "white wins"),
    ("blockable_check", ["e4", "f6", "Nc3", "Nc6", "d3", "g5", "Be3", "Ne5", "Qh5+", "Nf7", "O-O-O"], "running"),
    ("castling_short", ["e4", "e5", "Nf3", "Nf6", "Bc4", "Bc5", "o-o", "o-o", "a3"], "running"),
    ("king_walk", ["e4", "e5", "Ke2", "Ke7", "Kd3", "Kd6", "Kc4", "Kc6", "h3", "Kb6", "Kd5", "c5", "Kxe5", "c4", 
                   "Kf5", "Kb5", "Qh5", "Kb4", "a3+", "Ka4", "Kf4", "h6", "Nc3#"], "white wins"),
    ("capturable_check", ["e4", "f6", "Bb5", "g5", "Nc3", "h5", "Qxh5+", "Rxh5"], "running"),
    ("promotion_queen", ["f4", "g6", "f5", "Bh6", "fxg6", "Bxd2+", "Qxd2", "Nf6", "g7", "Ne4", "gxh8=Q#"], "white wins"),
    ("en_passant", ["e4", "g5", "e5", "f5", "exf6 e.p.", "Nc6", "Qh5#"], "white wins"),
    ("e.p._queening_black", ["a3", "h5", "f4", "h4", "g4", "hxg3 e.p.", "a4", "e6", "a5", "gxh2", "a6", "hxg1=Q", 
                             "axb7", "Qg3#"], "black wins"),
])
def test_game_moves(client, test_name, moves, expected_result):
    response = client.post("/create_game", params={"game_time_in_minutes": 10})
    game_id = response.json()["game_id"]

    client.post(f"/join_game/{game_id}", json={"player_id": "player1"})
    client.post(f"/join_game/{game_id}", json={"player_id": "player2"})

    ws_url_p1 = f"/ws/{game_id}/player1"
    ws_url_p2 = f"/ws/{game_id}/player2"

    with client.websocket_connect(ws_url_p1) as ws1, client.websocket_connect(ws_url_p2) as ws2:
        receive_with_timeout(ws1)
        receive_with_timeout(ws2)

        for i, move in enumerate(moves):
            message = {
                "action": "move",
                "move": {
                    "move_algebraic": move,
                    "move_type": "algebraic"
                }
            }
            if i % 2 == 0:
                ws1.send_json(message)
                receive_with_timeout(ws2)
            else:
                ws2.send_json(message)
                receive_with_timeout(ws1)

    final_state_response = client.get(f"/game_info/{game_id}/player1")
    final_state = final_state_response.json()
    assert final_state.get("result") == expected_result, f"{test_name}: expected {expected_result}, got {final_state.get('result')}"

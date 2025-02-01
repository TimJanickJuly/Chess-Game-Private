import pytest
import sys
import os
current_directory = os.getcwd()

# Zum Python-Suchpfad hinzufügen
if current_directory not in sys.path:
    sys.path.append(current_directory)

from chess_engine import Game

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
from app.main import GameWrapper


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
def test_game_scenarios(test_name, moves, expected_result):
    game = GameWrapper()
    game.add_player("player1")
    game.add_player("player2")
    
    for move in moves:
        success, message = game.handle_move(move)
        game.print_board_debug()
            
    assert game.get_state()["game_state"] == expected_result, f"Test '{test_name}' failed: Expected {expected_result}, got {game.get_state()['game_state']}"

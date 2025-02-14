from typing import Optional
import random
import time
import logging
from typing import Optional
from chess_engine import Game
from app.schemas.game import MoveRequest

logging.basicConfig(level=logging.INFO)

class GameWrapper:
    def __init__(self, game_time_in_minutes=5):
        self.game_instance = None
        self.players = []
        self.player_white = None
        self.player_black = None
        self.active_player = None
        self.active_color = None
        self.player_time = {"white": game_time_in_minutes * 60, "black": game_time_in_minutes * 60}
        self.last_time_stamp = None
        self.player_colors = {}
        self.players_connected = {}
        self.both_connected = False
        self.details = None

    def add_player(self, player_id: str):
        if len(self.players) >= 2:
            raise ValueError("Cannot add more players: Game is full.")
        self.players.append(player_id)
        logging.info("Player %s joined the game.", player_id)

    def choose_sides(self):
        if len(self.players) != 2:
            raise ValueError("Cannot assign sides: Both players must join.")
        random.shuffle(self.players)
        self.player_white, self.player_black = self.players
        self.player_colors = {
            self.player_white: "white",
            self.player_black: "black"
        }
        logging.info("Assigned white to %s, black to %s.", self.player_white, self.player_black)

    def start_game(self):
        if len(self.players) != 2 or not self.both_connected:
            raise ValueError("Cannot start game: Two connected players are required.")
        self.game_instance = Game()
        self.choose_sides()
        self.active_color = "white"
        if not self.player_white or not self.player_black:
            raise ValueError("Players have not been assigned correctly.")
        self.active_player = self.player_white
        self.last_time_stamp = time.time()
        logging.info("Game started successfully.")

    def set_player_connection_status(self, player_id: str, status: bool):
        self.players_connected[player_id] = status
        self.both_connected = len(self.players_connected) == 2 and all(self.players_connected.values())
        if self.both_connected:
            self.start_game()
        elif self.game_instance and self.game_instance.game_state == "running":
            logging.warning("A player disconnected. Game might end.")

    def update_active_player(self):
        if self.active_player is None or self.active_color is None:
            raise ValueError("Active player or active color not initialized.")
        self.active_player = self.player_black if self.active_player == self.player_white else self.player_white
        self.active_color = "black" if self.active_color == "white" else "white"

    def _update_time(self):
        now = time.time()
        if self.last_time_stamp is None:
            self.last_time_stamp = now
            return
        elapsed = now - self.last_time_stamp
        self.player_time[self.active_color] -= elapsed
        logging.debug("Elapsed time: %.2f seconds. Remaining time for %s: %.2f seconds",
                      elapsed, self.active_color, self.player_time[self.active_color])
        self.last_time_stamp = now

    def _has_remaining_time(self, color):
        return self.player_time.get(color, 0) > 0

    def _check_and_handle_timeout(self):
        
        if not self.game_instance or not len(self.players)  == 2:
            return True
        
        if not self._has_remaining_time(self.active_color):
            self.game_instance.game_state = "timeout"
            self.details = f"{self._switch_color(self.active_color)} won due to time"
            self.game_instance.game_state = f"{self._switch_color(self.active_color)} won due to time"
            logging.warning("Game ended due to timeout. Remaining time for %s: %.2f seconds",
                            self.active_color, self.player_time[self.active_color])
            return True
        return False

    def _convert_move(self, move: "MoveRequest"):
        if move.move_type == "coordinates":
            move_algebraic = self.game_instance.get_algebraic_chess_notation(
                7 - move.start_row,
                move.start_col,
                7 - move.target_row,
                move.target_col
            )
            if move_algebraic == "Invalid move":
                raise ValueError("Invalid move syntax.")
            if move.target_row in [0, 7] and move_algebraic[0] not in ["N", "B", "R", "Q", "K", "O"]:
                move_algebraic += move.details if move.details in ["=N", "=B", "=R"] else "=Q"
        elif move.move_type == "algebraic":
            move_algebraic = move.move_algebraic
        else:
            raise ValueError("Invalid move type. Must be 'coordinates' or 'algebraic'.")
        return move_algebraic

    def handle_move(self, move: "MoveRequest"):
        logging.info("Handling move request: %s", move.dict())
        if not self.game_instance or self.game_instance.game_state != "running":
            raise ValueError("Move not allowed: Game is over.")
        move_algebraic = self._convert_move(move)
        self._update_time()
        if self._check_and_handle_timeout():
            return True
        logging.info("Attempting to execute move: %s", move_algebraic)
        result = self.game_instance.handle_turn(move_algebraic)
        if result == 2:
            self.update_active_player()
            self.last_time_stamp = time.time()
        elif result != 0:
            raise ValueError("Illegal move attempted.")
        logging.info("Move handled successfully.")
        return True

    def get_state(self, player):
        if self.game_instance and self.game_instance.game_state == "running":
            self._update_time()
            self._check_and_handle_timeout()
        return {
            "game_state": self.get_game_state_message(),
            "num_moves_played": self.game_instance.num_moves_played if self.game_instance else 0,
            "active_player": self.active_player,
            "players": self.players,
            "player_colors": self.player_colors,
            "both_joined": len(self.players) == 2,
            "both_connected": self.both_connected,
            "board_state": self.game_instance.get_board_state()[::-1] if self.game_instance else [],
            "legal_moves": self.get_legal_moves(),
            "remaining_time": self.player_time,
            "game_history": self.game_instance.get_game_history() if self.game_instance else []
        }

    def get_game_state_message(self):
        if self.details:
            return self.details
        if len(self.players) < 2:
            return "waiting for 2nd player"
        return self.game_instance.game_state

    def get_legal_moves(self):
        if not self.game_instance or self.game_instance.game_state != "running":
            return {"legal_moves": {}}
        return {
            "legal_moves": {
                self.player_white: self.game_instance.get_player_moves(1),
                self.player_black: self.game_instance.get_player_moves(-1)
            }
        }

    def _switch_color(self, color):
        return "black" if color == "white" else "white"


games = {}

def create_game_wrapper(game_id: str, game_time):
    games[game_id] = GameWrapper(game_time)

def get_game_wrapper(game_id: str) -> Optional[GameWrapper]:
    return games.get(game_id, None)

def remove_game(game_id: str):
    if game_id in games:
        del games[game_id]

def print_running_game():
    print(games)

def get_game_wrapper_by_player(player_id: str) -> Optional[GameWrapper]:
    for game in games.values():
        if player_id in game.players:
            return game
    return None

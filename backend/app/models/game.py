import random
import time
import logging
from chess_engine import Game
from app.schemas.game import MoveRequest

logging.basicConfig(level=logging.INFO)

class GameWrapper:
    def __init__(self, game_time_in_minutes):
        self.game_instance = None
        self.players = []
        self.player_white = None
        self.player_black = None
        self.active_player = None
        self.active_color = None
        self.player_time = {"white": game_time_in_minutes * 60, "black": game_time_in_minutes * 60}
        self.last_time_stamp = None
        
        self.time_settings = game_time_in_minutes * 60
        self.players_connected = {}
        self.both_connected = False
        self.both_joined = False

    def add_player(self, player_id: str):
        if len(self.players) >= 2:
            raise ValueError("Cannot add more players: Game is full.")
        self.players.append(player_id)
        logging.info(f"Player {player_id} joined the game.")

    def choose_sides(self):
        if len(self.players) != 2:
            raise ValueError("Cannot assign sides: Both players must join.")
        
        random.shuffle(self.players)
        self.player_white, self.player_black = self.players
        logging.info(f"Assigned white to {self.player_white}, black to {self.player_black}.")

    def update_active_player(self):
        if self.active_player is None:
            raise ValueError("Cannot update player: No active player initialized.")
        
        color_switch = {"white": "black", "black": "white"}
        self.active_player = self.player_black if self.active_player == self.player_white else self.player_white
        if self.active_color is None:
            raise ValueError("Active color has not been set.")
        self.active_color = color_switch[self.active_color]
        
    def handle_move(self, move: "MoveRequest"):
        logging.info("Handling move request: %s", move.dict())
        if not self.game_instance or self.game_instance.game_state != "running":
            logging.error("Move not allowed: Game is over or not running.")
            raise ValueError("Move not allowed: Game is over.")

        if move.move_type == "coordinates":
            logging.debug("Converting coordinates to algebraic notation.")
            move_algebraic = self.game_instance.get_algebraic_chess_notation(
                7 - move.start_row,
                move.start_col,
                7 - move.target_row,
                move.target_col
            )
            logging.debug("Converted move: %s", move_algebraic)
        elif move.move_type == "algebraic":
            move_algebraic = move.move_algebraic
            logging.debug("Received algebraic move: %s", move_algebraic)
        else:
            logging.error("Invalid move type provided: %s", move.move_type)
            raise ValueError("Invalid move type. Must be 'coordinates' or 'algebraic'.")

        if move_algebraic == "Invalid move":
            logging.error("Move conversion resulted in invalid move syntax.")
            raise ValueError("Invalid move syntax.")

        if move.move_type == "coordinates" and (move.target_row in [0, 7]):
            if move_algebraic[0] not in ["N", "B", "R", "Q", "K", "O"]:
                logging.debug("Processing queening. Details provided: %s", move.details)
                move_algebraic += move.details if move.details in ["=N", "=B", "=R"] else "=Q"
                logging.debug("Move after queening adjustment: %s", move_algebraic)

        if self.last_time_stamp is not None:
            elapsed_time = time.time() - self.last_time_stamp
            self.player_time[self.active_color] -= elapsed_time
            logging.debug("Elapsed time: %.2f seconds. Updated remaining time for %s: %.2f seconds", 
                        elapsed_time, self.active_color, self.player_time[self.active_color])
        else:
            self.last_time_stamp = time.time()
            logging.debug("Initial timestamp set.")

        if not self.check_remaining_time(self.active_color):
            self.game_instance.game_state = "timeout"
            logging.warning("Game ended due to timeout. Remaining time for %s: %.2f seconds", 
                            self.active_color, self.player_time[self.active_color])
            return False

        logging.info("Attempting to execute move: %s", move_algebraic)
        result = self.game_instance.handle_turn(move_algebraic)
        logging.debug("Result from handle_turn: %s", result)

        if result == 2:
            logging.info("Move executed successfully. Updating active player.")
            self.update_active_player()
            self.last_time_stamp = time.time()
        elif result != 0:
            logging.error("Illegal move attempted: %s", move_algebraic)
            raise ValueError("Illegal move attempted.")

        logging.info("Move handled successfully.")
        return True

    def get_state(self, player):
        if len(self.players) < 2:
            game_state = "waiting for 2nd player"
            player_colors = {}
        elif not self.both_connected:
            game_state = "disconnected"
            player_colors = {
                self.player_white: "white",
                self.player_black: "black"
            }
        else:
            game_state = "not started" if self.game_instance is None else self.game_instance.game_state
            player_colors = {
                self.player_white: "white",
                self.player_black: "black"
            }
        return {
            "game_state": game_state,
            "num_moves_played": self.game_instance.num_moves_played if self.game_instance else 0,
            "active_player": self.active_player,
            "players": self.players,
            "player_colors": player_colors,
            "both_joined": len(self.players) == 2,
            "both_connected": self.both_connected,
            "board_state": self.game_instance.get_board_state()[::-1] if self.game_instance else [],
            "legal_moves": self.get_legal_moves(),
            "remaining_time": self.player_time,
            "game_history": self.game_instance.get_game_history() if self.game_instance else []
        }

    def get_legal_moves(self):
        if not self.game_instance or self.game_instance.game_state != "running":
            return {
            "legal_moves": {}
        }
        
        return {
            "legal_moves": {self.player_white : self.game_instance.get_player_moves(1),self.player_black: self.game_instance.get_player_moves(-1)}
        }

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
        if not self.both_connected and self.game_instance and self.game_instance.game_state == "running":
            logging.warning("A player disconnected. Game might end.")

    def check_remaining_time(self, player):
        return self.player_time.get(player, 0) > 0

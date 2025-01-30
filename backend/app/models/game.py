import random
from app.chess_engine import Game

class GameWrapper:
    def __init__(self):
        self.game_instance = Game()
        self.players = []
        self.player_white = None
        self.player_black = None
        self.active_player = None

    def add_player(self, player_id: str):
        """Fügt einen Spieler hinzu und weist Farben zu, wenn das Spiel voll ist."""
        if len(self.players) >= 2:
            raise ValueError("Game is full")
        self.players.append(player_id)
        if len(self.players) == 2:
            self.choose_sides()

    def choose_sides(self):
        """Weist Spielern zufällig die weißen und schwarzen Steine zu."""
        if len(self.players) != 2:
            raise ValueError("Both players must join before assigning sides")
        if random.randint(0, 1) == 0:
            self.player_white = self.players[0]
            self.player_black = self.players[1]
        else:
            self.player_white = self.players[1]
            self.player_black = self.players[0]
        self.active_player = self.player_white

    def update_active_player(self):
        """Wechselt den aktiven Spieler nach einem gültigen Zug."""
        if self.active_player is None:
            raise ValueError("Active player is not initialized")
        self.active_player = self.player_black if self.active_player == self.player_white else self.player_white

    def handle_move(self, move: str):
        """Überprüft und verarbeitet einen Zug im Spiel."""
        result = self.game_instance.handle_turn(move)
        if result == -1:
            return False, "illegal move"
        elif result == 2:
            self.update_active_player()
            return True, "move executed"
        elif result == 0:
            return True, self.game_instance.game_state
        else:
            return False, "illegal move syntax"

    def get_state(self):
        """Gibt den aktuellen Status des Spiels zurück."""
        game_state = "waiting for 2nd player" if len(self.players) < 2 else self.game_instance.game_state
        return {
            "game_state": game_state,
            "num_moves_played": self.game_instance.num_moves_played,
            "active_player": self.active_player,
            "players": self.players,
            "player_colors": {
                self.player_white: "white",
                self.player_black: "black"
            },
            "both_joined": len(self.players) == 2,
            "board_state": self.game_instance.get_board_state()[::-1],
            "legal_moves": self.get_legal_moves()
        }

    def get_legal_moves(self):
        """Gibt die möglichen Züge für beide Spieler zurück."""
        return {
            "white": self.game_instance.get_player_moves(1),
            "black": self.game_instance.get_player_moves(-1)
        }

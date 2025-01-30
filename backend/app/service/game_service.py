from app.models.game import GameWrapper

# In-Memory Store für Spiele
games = {}

def create_game_wrapper(game_id: str):
    """Erstellt ein neues Spiel und speichert es in der In-Memory-Datenstruktur."""
    games[game_id] = GameWrapper()

def get_game_wrapper(game_id: str) -> GameWrapper | None:
    """Holt ein Spiel aus der In-Memory-Datenstruktur, falls es existiert."""
    return games.get(game_id)

def remove_game(game_id: str):
    """Löscht ein Spiel aus der In-Memory-Datenstruktur."""
    if game_id in games:
        del games[game_id]

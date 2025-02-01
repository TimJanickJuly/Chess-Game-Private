from app.models.game import GameWrapper
from typing import Optional

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
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from fastapi import HTTPException
from fastapi import Request
import os
import sys
import uuid
from pydantic import BaseModel
current_directory = os.getcwd()

# Zum Python-Suchpfad hinzufügen
if current_directory not in sys.path:
    sys.path.append(current_directory)
from chess_engine import Game

import random

# Aktuellen Pfad der Datei abrufen
current_directory = os.path.dirname(os.path.abspath(__file__))

# Zum Python-Suchpfad hinzufügen
if current_directory not in sys.path:
    sys.path.append(current_directory)

app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Setze hier die URL deiner AWS-Domain oder IP, falls du sie kennst
    allow_credentials=True,
    allow_methods=["*"],  # Erlaubt alle HTTP-Methoden
    allow_headers=["*"],
)

class GameWrapper:
    def __init__(self):
        self.game_instance = Game()
        self.players = []
        self.player_white = None
        self.player_black = None
        self.active_player = None

    def add_player(self, player_id: str):
        if len(self.players) >= 2:
            raise ValueError("Game is full")
        self.players.append(player_id)
        if len(self.players) == 2:
            self.choose_sides()

    def choose_sides(self):
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
        if self.active_player is None:
            raise ValueError("Active player is not initialized")
        self.active_player = self.player_black if self.active_player == self.player_white else self.player_white

    def handle_move(self, move: str):
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
        if len(self.players) != 2 or self.player_white is None or self.player_black is None:
            game_state = "waiting for 2nd player"
        else:
            game_state = self.game_instance.game_state
        return {
            "game_state": self.game_instance.game_state,
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

    def print_board_debug(self):
        print(self.game_instance.get_board_state())

    def get_legal_moves(self):
        return {
            "white": self.game_instance.get_player_moves(1),
            "black": self.game_instance.get_player_moves(-1)
        }


# In-Memory Store für Spiele und Verbindungen
games = {}
class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, player_id: str):
        await websocket.accept()
        self.active_connections[player_id] = websocket

    def disconnect(self, player_id: str):
        if player_id in self.active_connections:
            del self.active_connections[player_id]

    async def send_message(self, player_id: str, message: dict):
        websocket = self.active_connections.get(player_id)
        if websocket:
            await websocket.send_json(message)

    async def broadcast(self, message: dict, include: list[str]):
        for player_id in include:
            websocket = self.active_connections.get(player_id)
            if websocket:
                await websocket.send_json(message)

    def are_game_players_connected(self, player_ids: list[str]) -> bool:
        """Prüft, ob die Spieler eines Spiels aktiv verbunden sind."""
        return all(player_id in self.active_connections for player_id in player_ids)


manager = ConnectionManager()

class JoinGameRequest(BaseModel):
    player_id: str

@app.post("/create_game")
async def create_game():
    """Erstellt ein neues Spiel und gibt die Spiel-ID zurück."""
    game_id = str(uuid.uuid4())
    game_wrapper = GameWrapper()
    games[game_id] = game_wrapper
    print(f"Game created with ID: {game_id}")  # Debugging-Info
    return {"game_id": game_id}

@app.post("/join_game/{game_id}")
async def join_game(game_id: str, request: Request):
    try:
        json_body = await request.json()
        player_id = json_body.get("player_id")
        if not player_id:
            raise HTTPException(status_code=422, detail="player_id missing")

        if game_id not in games:
            raise HTTPException(status_code=404, detail="Game not found")
        
        game_wrapper = games[game_id]
        game_wrapper.add_player(player_id)

        return {"message": "Joined game successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid request format: {e}")


@app.get("/game_info/{game_id}")
async def get_game_info(game_id: str):
    """Gibt Informationen über das Spiel zurück."""
    if game_id not in games:
        raise HTTPException(status_code=404, detail="Game not found")
    
    game_wrapper = games[game_id]
    return game_wrapper.get_state()

@app.websocket("/ws/{game_id}/{player_id}")
async def websocket_endpoint(websocket: WebSocket, game_id: str, player_id: str):
    await manager.connect(websocket, player_id)
    
    if game_id not in games:
        await websocket.close(code=4001)
        return
    
    game_wrapper = games[game_id]
    if player_id not in game_wrapper.players:
        await websocket.close(code=4001)
        return

    try:
        # Prüfen, ob die zwei Spieler des Spiels verbunden sind
        if len(game_wrapper.players) == 2 and manager.are_game_players_connected(game_wrapper.players):
            state = game_wrapper.get_state()
            await manager.broadcast({"event": "update", "state": state}, include=game_wrapper.players)

        while True:
            data = await websocket.receive_json()
            if data["action"] == "move":
                move = data.get("move")
                if move:
                    print(move)
                    move_algebraic = game_wrapper.game_instance.get_algebraic_chess_notation(7-move["start"]["row"], move["start"]["col"], 7-move["end"]["row"], move["end"]["col"])
                    print(move_algebraic)
                    # handle queening
                    if (move["end"]["row"] == 7 or move["end"]["row"] == 0) and move_algebraic[0] not in ["N", "B", "R", "Q", "K"]:
                        move_algebraic += "=Q"
                    game_wrapper.handle_move(move_algebraic)
                state = game_wrapper.get_state()
                await manager.broadcast({"event": "update", "state": state}, include=game_wrapper.players)
            elif data["action"] == "get_state":
                state = game_wrapper.get_state()
                await manager.send_message(player_id, {"event": "state", "state": state})
            print(game_wrapper.game_instance.get_board_state())
    except WebSocketDisconnect:
        manager.disconnect(player_id)


        


@app.get("/game_state/{game_id}")
async def get_game_state(game_id: str):
    """Abfrage des aktuellen Spielstatus."""
    if game_id not in games:
        return JSONResponse({"error": "Game not found"}, status_code=404)
    
    game_wrapper = games[game_id]
    return game_wrapper.get_state()
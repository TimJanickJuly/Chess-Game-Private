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
    allow_origins=["*"],  # Erlaube Anfragen von allen Ursprüngen (für Entwicklung)
    allow_credentials=True,
    allow_methods=["*"],  # Erlaube alle HTTP-Methoden
    allow_headers=["*"],  # Erlaube alle Header
)

def convert_move_to_notation(move):
    def to_chess_notation(row, col):
        files = "abcdefgh"
        return f"{files[col]}{8 - row}"

    start = move["start"]
    end = move["end"]
    return f"{to_chess_notation(start['row'], start['col'])}{to_chess_notation(end['row'], end['col'])}"



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
        if len(self.players) == 1:
            self.player_white = player_id
        elif len(self.players) == 2:
            self.player_black = player_id
        self.update_active_player()
        
    def choose_sides(self):
        if random.randint(0, 1) == 0:
            self.player_white = self.players[0]
            self.player_black = self.players[1]
        else:
            self.player_white = self.players[1]
            self.player_black = self.players[0]
        self.update_active_player()

    def update_active_player(self):
        self.active_player = (
            self.player_white if len(self.players) == 1 else self.player_black
        )

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
            return False, "illegale move syntax"
        
    def get_state(self):
        print(type(self.game_instance.get_board_state()))
        print(self.game_instance.get_board_state())
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
        return {"white" : self.game_instance.get_player_moves(1), "black" : self.game_instance.get_player_moves(-1)}

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

    async def broadcast(self, message: dict, exclude: list[str] = []):
        for player_id, websocket in self.active_connections.items():
            if player_id not in exclude:
                await websocket.send_json(message)

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
    """Tritt einem Spiel bei."""
    try:
        # Rohinhalt des Requests lesen
        json_body = await request.json()  # JSON-Daten extrahieren
        player_id = json_body.get("player_id")  # `player_id` extrahieren
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
    """WebSocket-Endpunkt für Echtzeitkommunikation."""
    await manager.connect(websocket, player_id)
    if game_id not in games:
        await websocket.close(code=4001)
        return
    
    game_wrapper = games[game_id]
    if player_id not in game_wrapper.players:
        await websocket.close(code=4001)
        return
    
    try:
        while True:
            data = await websocket.receive_json()
            if data["action"] == "move":
                move = data.get("move")
                if move:
                    move = convert_move_to_notation(move)
                    game_wrapper.handle_move(move)
                state = game_wrapper.get_state()
                await manager.broadcast({"event": "update", "state": state})
            elif data["action"] == "get_state":
                state = game_wrapper.get_state()
                await manager.send_message(player_id, {"event": "state", "state": state})
    except WebSocketDisconnect:
        manager.disconnect(player_id)
        


@app.get("/game_state/{game_id}")
async def get_game_state(game_id: str):
    """Abfrage des aktuellen Spielstatus."""
    if game_id not in games:
        return JSONResponse({"error": "Game not found"}, status_code=404)
    
    game_wrapper = games[game_id]
    return game_wrapper.get_state()

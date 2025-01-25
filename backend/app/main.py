from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from fastapi import HTTPException
from chess_engine import Game
import uuid

app = FastAPI()

# In-Memory Store für Spiele und Verbindungen
games = {}
connections = {}

from pydantic import BaseModel

class JoinGameRequest(BaseModel):
    player_id: str


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

@app.post("/create_game")
async def create_game():
    """Erstellt ein neues Spiel und gibt die Spiel-ID zurück."""
    game_id = str(uuid.uuid4())
    game = Game()
    games[game_id] = {
        "game": game,
        "players": [],
    }
    return {"game_id": game_id}

@app.post("/join_game/{game_id}")
async def join_game(game_id: str, request: JoinGameRequest):
    """Tritt einem Spiel bei."""
    if game_id not in games:
        raise HTTPException(status_code=404, detail="Game not found")
    
    if len(games[game_id]["players"]) >= 2:
        raise HTTPException(status_code=400, detail="Game is full")
    
    games[game_id]["players"].append(request.player_id)
    return {"message": "Joined game successfully"}

@app.websocket("/ws/{game_id}/{player_id}")
async def websocket_endpoint(websocket: WebSocket, game_id: str, player_id: str):
    """WebSocket-Endpunkt für Echtzeitkommunikation."""
    await manager.connect(websocket, player_id)
    if game_id not in games or player_id not in games[game_id]["players"]:
        await websocket.close(code=4001)
        return
    
    try:
        while True:
            data = await websocket.receive_json()
            game = games[game_id]["game"]

            if data["action"] == "move":
                move = data.get("move")
                if move:
                    game.handle_turn(move)
                    state = {
                        "game_state": game.game_state,
                        "num_moves_played": game.num_moves_played,
                        "active_player": game.active_player,
                    }
                    await manager.broadcast({"event": "update", "state": state})
            elif data["action"] == "get_state":
                state = {
                    "game_state": game.game_state,
                    "num_moves_played": game.num_moves_played,
                    "active_player": game.active_player,
                }
                await manager.send_message(player_id, {"event": "state", "state": state})
    except WebSocketDisconnect:
        manager.disconnect(player_id)

@app.get("/game_state/{game_id}")
async def get_game_state(game_id: str):
    """Abfrage des aktuellen Spielstatus."""
    if game_id not in games:
        return JSONResponse({"error": "Game not found"}, status_code=404)
    
    game = games[game_id]["game"]
    return {
        "game_state": game.game_state,
        "num_moves_played": game.num_moves_played,
        "active_player": game.active_player,
    }

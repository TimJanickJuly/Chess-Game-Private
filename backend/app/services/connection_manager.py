import asyncio
from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, List

class ConnectionManager:
    def __init__(self, connection_callback=None):
        self.active_connections: Dict[str, WebSocket] = {}
        self.connection_callback = connection_callback

    async def connect(self, websocket: WebSocket, player_id: str):
        await websocket.accept()
        self.active_connections[player_id] = websocket
        if self.connection_callback:
            self.connection_callback(player_id, True)

    async def disconnect(self, player_id: str):
        websocket = self.active_connections.pop(player_id, None)
        if websocket:
            await websocket.close()
        if self.connection_callback:
            self.connection_callback(player_id, False)


    async def send_message(self, player_id: str, message: dict):
        websocket = self.active_connections.get(player_id)
        if websocket:
            try:
                await websocket.send_json(message)
            except WebSocketDisconnect:
                await self.disconnect(player_id)

    async def broadcast(self, message: dict, include: List[str]):
        tasks = [
            websocket.send_json(message)
            for player_id, websocket in self.active_connections.items()
            if player_id in include
        ]
        await asyncio.gather(*tasks, return_exceptions=True)

    def are_game_players_connected(self, player_ids: List[str]) -> bool:
        return all(player_id in self.active_connections for player_id in player_ids)
    
    
from app.services.game_service import get_game_wrapper_by_player

def connection_callback(player_id: str, status: bool):
    game_wrapper = get_game_wrapper_by_player(player_id)
    if game_wrapper:
        game_wrapper.set_player_connection_status(player_id, status)

manager = ConnectionManager(connection_callback=connection_callback)


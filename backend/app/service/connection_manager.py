from fastapi import WebSocket
from typing import Dict

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, player_id: str):
        """Akzeptiert eine WebSocket-Verbindung und speichert sie."""
        await websocket.accept()
        self.active_connections[player_id] = websocket

    def disconnect(self, player_id: str):
        """Entfernt eine WebSocket-Verbindung, wenn der Spieler sich trennt."""
        if player_id in self.active_connections:
            del self.active_connections[player_id]

    async def send_message(self, player_id: str, message: dict):
        """Sendet eine Nachricht an einen bestimmten Spieler."""
        websocket = self.active_connections.get(player_id)
        if websocket:
            await websocket.send_json(message)

    async def broadcast(self, message: dict, include: list[str]):
        """Sendet eine Nachricht an alle angegebenen Spieler."""
        for player_id in include:
            websocket = self.active_connections.get(player_id)
            if websocket:
                await websocket.send_json(message)

    def are_game_players_connected(self, player_ids: list[str]) -> bool:
        """Prüft, ob alle Spieler eines Spiels aktiv verbunden sind."""
        return all(player_id in self.active_connections for player_id in player_ids)


# Globale Instanz des ConnectionManagers
manager = ConnectionManager()

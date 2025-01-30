from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.services.connection_manager import manager
from app.services.game_service import get_game_wrapper

router = APIRouter()

@router.websocket("/ws/{game_id}/{player_id}")
async def websocket_endpoint(websocket: WebSocket, game_id: str, player_id: str):
    """WebSocket-Handler für Spielerkommunikation."""
    await manager.connect(websocket, player_id)

    game_wrapper = get_game_wrapper(game_id)
    if not game_wrapper or player_id not in game_wrapper.players:
        await websocket.close(code=4001)
        return

    try:
        # Broadcast initial state if both players are connected
        if len(game_wrapper.players) == 2 and manager.are_game_players_connected(game_wrapper.players):
            state = game_wrapper.get_state()
            await manager.broadcast({"event": "update", "state": state}, include=game_wrapper.players)

        while True:
            data = await websocket.receive_json()
            action = data.get("action")

            if action == "move":
                move = data.get("move")
                if move:
                    move_algebraic = game_wrapper.game_instance.get_algebraic_chess_notation(
                        7 - move["start"]["row"], move["start"]["col"],
                        7 - move["end"]["row"], move["end"]["col"]
                    )

                    # Handle queening
                    if (move["end"]["row"] in [0, 7]) and move_algebraic[0] not in ["N", "B", "R", "Q", "K"]:
                        move_algebraic += "=Q"

                    game_wrapper.handle_move(move_algebraic)

                state = game_wrapper.get_state()
                await manager.broadcast({"event": "update", "state": state}, include=game_wrapper.players)

            elif action == "get_state":
                state = game_wrapper.get_state()
                await manager.send_message(player_id, {"event": "state", "state": state})

    except WebSocketDisconnect:
        manager.disconnect(player_id)

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.services.connection_manager import manager
from pydantic import ValidationError
from app.services.game_service import get_game_wrapper
from app.schemas.game import GameStateResponse, MoveRequest

router = APIRouter()

@router.websocket("/ws/{game_id}/{player_id}")
async def websocket_endpoint(websocket: WebSocket, game_id: str, player_id: str):
    await manager.connect(websocket, player_id)

    game_wrapper = get_game_wrapper(game_id)
    if not game_wrapper or player_id not in game_wrapper.players:
        await websocket.close(code=4001)
        return

    try:
        if len(game_wrapper.players) == 2 and manager.are_game_players_connected(game_wrapper.players):
            state = game_wrapper.get_state(player_id)
            await manager.broadcast({"event": "update", "state": state}, include=game_wrapper.players)

        while True:
            data = await websocket.receive_json()
            action = data.get("action")

            if action == "move":
                move_data = data.get("move")
                try:
                    move = MoveRequest.model_validate(move_data)
                except ValidationError as e:
                    await manager.send_message(player_id, {"event": "error", "detail": "Invalid move data", "errors": e.errors()})
                    continue

                try:
                    game_wrapper.handle_move(move)
                except ValueError as e:
                    await manager.send_message(player_id, {"event": "error", "detail": str(e)})
                except KeyError as e:
                    await manager.send_message(player_id, {"event": "error", "detail": f"Missing key: {str(e)}"})
                except TypeError as e:
                    await manager.send_message(player_id, {"event": "error", "detail": f"Type error: {str(e)}"})

                state = game_wrapper.get_state(player_id)
                await manager.broadcast({"event": "update", "state": state}, include=game_wrapper.players)

            elif action == "get_state":
                state = game_wrapper.get_state(player_id)
                await manager.send_message(player_id, {"event": "state", "state": state})

    except WebSocketDisconnect:
        await manager.disconnect(player_id)

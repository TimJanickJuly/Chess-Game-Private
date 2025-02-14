from fastapi import APIRouter, HTTPException, Request
import uuid
import base64
from app.services.game_service import create_game_wrapper, get_game_wrapper, print_running_game

router = APIRouter()

@router.post("/create_game")
async def create_game(game_time_in_minutes: int = 5):
    import os
    game_id = base64.urlsafe_b64encode(os.urandom(6)).rstrip(b'=').decode('utf-8')
    create_game_wrapper(game_id, game_time_in_minutes)
    return {"game_id": game_id}

@router.post("/join_game/{game_id}")
async def join_game(game_id: str, request: Request):
    json_body = await request.json()
    player_id = json_body.get("player_id")
    print(player_id)
    if not player_id:
        raise HTTPException(status_code=422, detail="player_id missing")
    
    game_wrapper = get_game_wrapper(game_id)
    if not game_wrapper:
        raise HTTPException(status_code=404, detail="Game not found")
    
    try:
        game_wrapper.add_player(player_id)
        return {"message": "Joined game successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/game_info/{game_id}/{player_id}")
async def get_game_info(game_id: str, player_id: str):
    game_wrapper = get_game_wrapper(game_id)
    print("GAME WRAPPER", game_wrapper)
    if not game_wrapper:
        raise HTTPException(status_code=404, detail="Game not found")
    
    return game_wrapper.get_state(player_id)

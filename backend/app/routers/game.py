from fastapi import APIRouter, HTTPException, Request
import uuid
from app.services.game_service import create_game_wrapper, get_game_wrapper
from app.schemas.game import JoinGameRequest

router = APIRouter()

@router.post("/create_game")
async def create_game():
    """Erstellt ein neues Spiel und gibt die Spiel-ID zurück."""
    game_id = str(uuid.uuid4())
    create_game_wrapper(game_id)
    return {"game_id": game_id}

@router.post("/join_game/{game_id}")
async def join_game(game_id: str, request: Request):
    """Lässt einen Spieler einem Spiel beitreten."""
    try:
        json_body = await request.json()
        player_id = json_body.get("player_id")
        if not player_id:
            raise HTTPException(status_code=422, detail="player_id missing")

        game_wrapper = get_game_wrapper(game_id)
        if not game_wrapper:
            raise HTTPException(status_code=404, detail="Game not found")

        game_wrapper.add_player(player_id)
        return {"message": "Joined game successfully"}
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid request format: {e}")

@router.get("/game_info/{game_id}")
async def get_game_info(game_id: str):
    """Gibt Informationen über ein Spiel zurück."""
    game_wrapper = get_game_wrapper(game_id)
    if not game_wrapper:
        raise HTTPException(status_code=404, detail="Game not found")

    return game_wrapper.get_state()

@router.get("/game_state/{game_id}")
async def get_game_state(game_id: str):
    """Gibt den aktuellen Status eines Spiels zurück."""
    game_wrapper = get_game_wrapper(game_id)
    if not game_wrapper:
        raise HTTPException(status_code=404, detail="Game not found")

    return game_wrapper.get_state()

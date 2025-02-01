from pydantic import BaseModel, Field
from typing import List, Dict, Optional

class GameStateResponse(BaseModel):
    game_state: str
    num_moves_played: int
    active_player: Optional[str]
    players: List[str]
    player_colors: Optional[Dict[Optional[str], Optional[str]]] = Field(default_factory=dict)
    both_joined: bool
    both_connected: bool
    board_state: Optional[List[List[str]]] = Field(default_factory=list)
    legal_moves: Optional[List[Dict[str, int]]] = Field(default_factory=list)
    remaining_time: Optional[Dict[str, float]] = None
    game_history: List[str] = Field(default_factory=list)
    
    
class JoinGameRequest(BaseModel):
    player_id: str
    
    
class MoveRequest(BaseModel):
    start_row: int = None
    start_col: int = None
    target_row: int = None
    target_col: int = None
    move_type: str  # "coordinates" oder "algebraic"
    details: str = ""
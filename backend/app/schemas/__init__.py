from pydantic import BaseModel

class JoinGameRequest(BaseModel):
    player_id: str

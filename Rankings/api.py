from bson import ObjectId
from fastapi import FastAPI

from .data_models import Match, Player
from .manager import Manager

__all__ = ["build_api"]


def build_api(manager: Manager) -> FastAPI:
    api = FastAPI()

    @api.get("/players", response_model=list[Player])
    def get_players():
        players = sorted(manager.get_players().values(), key=lambda player: player.rating)
        players = [x.to_player() for x in players]
        return players

    @api.post("/players", response_model=Player)
    def add_player(player: Player):
        if player.id:
            raise ValueError("Player already exists")
        db_player = manager.add_player(player=player)
        return db_player.to_player()

    @api.put("/players", response_model=Player)
    def update_player(player: Player):
        if not player.id:
            raise ValueError("This is for updating players")
        player = manager.update_player(player)
        return player

    @api.get("/players/{player_id}")
    def get_player(player_id: str):
        player_id = ObjectId(player_id)
        return manager.get_player(player_id)

    @api.get("/matches", response_model=list[Match])
    def get_matches():
        matches = manager.get_matches()
        ret = [x.to_match() for x in matches]
        return ret

    @api.post("/matches")
    def add_match(match: Match):
        match = manager.add_match(match)
        return match

    @api.delete("/matches/{match_id}")
    def delete_match(match_id: str):
        match_id = ObjectId(match_id)
        manager.delete_match(match_id)

    return api

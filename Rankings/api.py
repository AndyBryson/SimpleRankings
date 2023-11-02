from bson import ObjectId
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .data_models import MatchAPI, PlayerAPI
from .manager import Manager
from .settings import Settings

__all__ = ["build_api"]


def build_api(manager: Manager, settings: Settings) -> FastAPI:
    api = FastAPI()
    if settings.backend_cors_origins:
        api.add_middleware(
            CORSMiddleware,
            allow_origins=settings.backend_cors_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    @api.get("/players", response_model=list[PlayerAPI])
    async def get_players():
        player_dict = await manager.get_players()
        players = sorted(player_dict.values(), key=lambda player: player.rating)
        players = [x.to_api() for x in players]
        return players

    @api.post("/players", response_model=PlayerAPI)
    async def add_player(player: PlayerAPI):
        if player.id:
            raise ValueError("Player already exists")
        db_player = await manager.add_player(player=player)
        return db_player.to_api()

    @api.put("/players", response_model=PlayerAPI)
    async def update_player(player: PlayerAPI):
        if not player.id:
            raise ValueError("This is for updating players")
        player = manager.update_player(player)
        return player

    @api.get("/players/{player_id}")
    async def get_player(player_id: str):
        player_id = ObjectId(player_id)
        return manager.get_player(player_id)

    @api.get("/matches", response_model=list[MatchAPI])
    async def get_matches():
        matches = await manager.get_matches()
        ret = [x.to_api() for x in matches]
        return ret

    @api.post("/matches")
    async def add_match(match: MatchAPI):
        db_match = await manager.add_match(match)
        return db_match.to_api()

    @api.delete("/matches/{match_id}")
    async def delete_match(match_id: str):
        match_id = ObjectId(match_id)
        await manager.delete_match(match_id)

    return api

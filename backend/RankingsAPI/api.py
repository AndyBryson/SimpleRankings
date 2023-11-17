from bson import ObjectId
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .data_models import MatchAPIReturn, MatchAPIReturnResolved, MatchAPISubmit, PlayerAPI
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
        player = await manager.update_player(player)
        return player.to_api()

    @api.delete("/players/{player_id}")
    async def delete_player(player_id: str):
        player_id = ObjectId(player_id)
        await manager.delete_player(player_id)

    @api.get("/players/{player_id}", response_model=PlayerAPI)
    async def get_player(player_id: str):
        player_id = ObjectId(player_id)
        player = await manager.get_player(player_id)
        return player.to_api()

    @api.get("/players/{player_id}/matches", response_model=list[MatchAPIReturn])
    async def get_player_matches(player_id: str):
        player_id = ObjectId(player_id)
        matches = await manager.get_matches_by_player(player_id)
        ret = []
        for match in matches:
            d = match.to_api().dict()
            d["winner_name"] = (await manager.get_player(match.result[0])).name
            d["loser_name"] = (await manager.get_player(match.result[1])).name
            ret.append(d)
        return ret

    @api.get("/matches", response_model=list[MatchAPIReturn])
    async def get_matches():
        matches = await manager.get_matches()
        ret = [x.to_api() for x in matches]
        return ret

    @api.post("/matches", response_model=MatchAPIReturn)
    async def add_match(match: MatchAPISubmit) -> MatchAPIReturn:
        db_match = await manager.add_match(match)
        return db_match.to_api()

    @api.get("/matches/resolved", response_model=list[MatchAPIReturnResolved])
    async def get_matches_resolved():
        matches = await manager.get_matches()
        ret = []
        for match in matches:
            d = match.to_api().dict()
            d["winner_name"] = (await manager.get_player(match.result[0])).name
            d["loser_name"] = (await manager.get_player(match.result[1])).name
            ret.append(d)
        return ret

    @api.delete("/matches/{match_id}")
    async def delete_match(match_id: str):
        match_id = ObjectId(match_id)
        await manager.delete_match(match_id)

    return api

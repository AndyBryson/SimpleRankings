import copy

from bson import ObjectId

import Rankings.Mongo.motor as motor
from .data_models import EResult, Match, MatchDatabase, Player, PlayerDatabase
from .settings import Settings

__all__ = ["Manager"]


class Manager:
    """
    Manager for a rankings system based on chess rankings
    """

    def __init__(self, config: Settings):
        self._config = config
        self._motor_client = motor.connect(config.mongo)

    async def get_players(self) -> dict[ObjectId, PlayerDatabase]:
        player_list = await motor.find(PlayerDatabase).to_list(None)
        players = {player.id: player for player in player_list}
        return players

    async def get_matches(self) -> list[MatchDatabase]:
        matches = await motor.find(MatchDatabase).to_list(None)
        return copy.deepcopy(matches)

    async def recalculate_rankings(self):
        players = await self.get_players()
        for player in players.values():
            player.reset()

        matches = await self.get_matches()

        await motor.delete_many(MatchDatabase)

        for match in matches:
            await self.add_match(match)

    async def add_player(self, player: Player) -> PlayerDatabase:
        db_player = PlayerDatabase(**player.dict())
        await motor.insert_one(db_player)
        return db_player

    async def update_player(self, player: Player) -> PlayerDatabase:
        _id = ObjectId(player.id)
        existing_player = await self.get_player(_id)

        for key, value in player.dict():
            if key != "id":
                setattr(existing_player, key, value)

        await motor.update_one(existing_player)
        return existing_player

    async def get_player(self, player_id: ObjectId) -> PlayerDatabase:
        return await motor.get_from_id(PlayerDatabase, id=player_id)

    async def get_match(self, match_id: ObjectId) -> MatchDatabase:
        return await motor.get_from_id(MatchDatabase, id=match_id)

    async def set_active(self, player_id: ObjectId, active: bool):
        player = await self.get_player(player_id)
        player.active = active
        await motor.update_one(player)

    async def delete_match(self, match_id: ObjectId):
        match = await self.get_match(match_id)
        await motor.delete_one(match)
        await self.recalculate_rankings()

    async def add_match(self, match: Match) -> MatchDatabase:
        db_match = MatchDatabase.from_match(match)
        await motor.insert_one(db_match)
        await self._apply_points(db_match)
        return db_match

    async def _apply_points(self, match: MatchDatabase):
        assert len(match.result) == 2, "We need 2 people in a match"

        winner = await motor.get_from_id(PlayerDatabase, match.result[0])
        loser = await motor.get_from_id(PlayerDatabase, match.result[1])

        expected_result = self.expected_score(winner.rating, loser.rating)
        await self._adjust_player_stats(
            winner, expected_result=expected_result, result=EResult.DRAW if match.draw else EResult.WIN
        )
        await self._adjust_player_stats(
            loser, expected_result=expected_result, result=EResult.DRAW if match.draw else EResult.LOSE
        )

    @staticmethod
    def expected_score(rating_a: float, rating_b: float) -> float:
        return 1.0 / (1 + 10 ** ((rating_b - rating_a) / 400.0))

    async def _adjust_player_stats(self, player: PlayerDatabase, expected_result: float, result: EResult):
        k = max((self._config.initial_k - player.match_count), self._config.standard_k)
        adjustment = k * expected_result

        match result:
            case EResult.WIN:
                player.rating += 1 - adjustment
                player.wins += 1
            case EResult.LOSE:
                player.rating -= 1 - adjustment
                player.losses += 1
            case EResult.DRAW:
                player.rating += 0.5 - adjustment
                player.draws += 1
            case _:
                raise RuntimeError("unknown result")

        await motor.update_one(player)

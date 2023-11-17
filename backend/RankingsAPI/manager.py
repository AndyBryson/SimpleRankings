import copy

from bson import ObjectId

import RankingsAPI.Mongo.motor as motor

from .data_models import EResult, Match, MatchAPISubmit, Player, PlayerAPI
from .settings import Settings

__all__ = ["Manager"]


class Manager:
    """
    Manager for a rankings system based on chess rankings
    """

    def __init__(self, config: Settings):
        self._config = config
        self._motor_client = motor.connect(config.mongo)

    async def get_players(self) -> dict[ObjectId, Player]:
        player_list = await motor.find(Player).to_list(None)
        players = {player.id: player for player in player_list}
        return players

    async def get_matches(self) -> list[Match]:
        matches = await motor.find(Match).to_list(None)
        return copy.deepcopy(matches)

    async def get_matches_by_player(self, player_id: ObjectId) -> list[Match]:
        matches = await motor.find(Match, {"result": player_id}).to_list(None)
        return copy.deepcopy(matches)

    async def recalculate_rankings(self):
        players = await self.get_players()
        for player in players.values():
            player.reset()
            await motor.update_one(player)

        matches = await self.get_matches()

        for match in matches:
            await self.add_match(match, insert=False)

    async def delete_player(self, player_id: ObjectId):
        player = await self.get_player(player_id)

        matches = await self.get_matches()
        for match in matches:
            if player.id in match.result:
                await motor.delete_one(match)

        await motor.delete_one(player)
        await self.recalculate_rankings()

    async def add_player(self, player: PlayerAPI) -> Player:
        db_player = Player(**player.dict())
        await motor.insert_one(db_player)
        return db_player

    async def update_player(self, player: PlayerAPI) -> Player:
        _id = ObjectId(player.id)
        existing_player = await self.get_player(_id)

        for key, value in player.dict().items():
            if key != "id":
                setattr(existing_player, key, value)

        await motor.update_one(existing_player)
        return existing_player

    async def get_player(self, player_id: ObjectId) -> Player:
        return await motor.get_from_id(Player, id=player_id)

    async def get_match(self, match_id: ObjectId) -> Match:
        return await motor.get_from_id(Match, id=match_id)

    async def set_active(self, player_id: ObjectId, active: bool):
        player = await self.get_player(player_id)
        player.active = active
        await motor.update_one(player)

    async def delete_match(self, match_id: ObjectId):
        match = await self.get_match(match_id)
        await motor.delete_one(match)
        await self.recalculate_rankings()

    async def add_match(self, match: MatchAPISubmit | Match, insert: bool = True) -> Match:
        if isinstance(match, MatchAPISubmit):
            db_match = Match.from_api(match)
        else:
            db_match = match

        await self._apply_points(db_match)

        if insert:
            await motor.insert_one(db_match)
        else:
            await motor.update_one(db_match)

        return db_match

    async def _apply_points(self, match: Match):
        assert len(match.result) == 2, "We need 2 people in a match"

        winner = await motor.get_from_id(Player, match.result[0])
        loser = await motor.get_from_id(Player, match.result[1])
        expected_result = self.expected_score(winner.rating, loser.rating)

        match.winner_rating = winner.rating
        match.loser_rating = loser.rating
        match.probability = expected_result

        await self._adjust_player_stats(
            winner, expected_result=expected_result, result=EResult.DRAW if match.draw else EResult.WIN
        )
        await self._adjust_player_stats(
            loser, expected_result=expected_result, result=EResult.DRAW if match.draw else EResult.LOSE
        )

    @staticmethod
    def expected_score(rating_a: float, rating_b: float) -> float:
        return 1.0 / (1 + 10 ** ((rating_b - rating_a) / 400.0))

    async def _adjust_player_stats(self, player: Player, expected_result: float, result: EResult):
        k = max((self._config.initial_k - player.match_count), self._config.standard_k)
        if result == EResult.DRAW:
            score_change = 0.5 - expected_result
        else:
            score_change = 1 - expected_result

        adjustment = k * score_change

        match result:
            case EResult.WIN:
                player.rating += adjustment
                player.wins += 1
            case EResult.LOSE:
                player.rating -= adjustment
                player.losses += 1
            case EResult.DRAW:
                player.rating += adjustment
                player.draws += 1
            case _:
                raise RuntimeError("unknown result")

        await motor.update_one(player)

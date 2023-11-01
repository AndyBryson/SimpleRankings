"""
manager.py: Manager for a rankings system based on chess rankings
"""
import copy

from bson import ObjectId

import Rankings.Mongo.motor as motor
from .data_models import Match, MatchDatabase, Player, PlayerDatabase
from .settings import Settings

__all__ = ["Manager"]


class Manager:
    def __init__(self, config: Settings):
        # self.__players: dict[ObjectId, PlayerDatabase] = {}
        # self.__matches: list[MatchDatabase] = []
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
            self.add_match(match)

        for player in players.values():
            await motor.update_one(player)

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
        self._apply_points(db_match)
        return db_match

    def _apply_points(self, match: MatchDatabase):
        assert len(match.result) == 2, "We need 2 people in a match"
        rating_change = self.calculate_rating_change(match)

        winner = self.__players[match.result[0]]
        loser = self.__players[match.result[1]]

        self.adjust_player_rating(player=winner, adjustment=rating_change)
        self.adjust_player_rating(player=loser, adjustment=rating_change if match.draw else -rating_change)

        if match.draw:
            winner.draws += 1
            loser.draws += 1
        else:
            winner.wins += 1
            loser.losses += 1

        # TODO: Save to the database

    def calculate_rating_change(self, match: MatchDatabase):
        ratings = [self.__players[player_id].rating for player_id in match.result]
        assert len(ratings) == 2, "We only support __matches between 2 __players"
        expected_score = Manager.expected_score(*ratings)
        if match.draw:
            return 0.5 - expected_score
        else:
            return 1 - expected_score

    @staticmethod
    def expected_score(rating_a: float, rating_b: float) -> float:
        return 1.0 / (1 + 10 ** ((rating_b - rating_a) / 400.0))

    def adjust_player_rating(self, player: Player, adjustment: float):
        k = max((self._config.initial_k - player.match_count), self._config.standard_k)

        player.rating += k * adjustment

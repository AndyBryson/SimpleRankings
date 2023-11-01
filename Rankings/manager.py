"""
manager.py: Manager for a rankings system based on chess rankings
"""
import copy

from bson import ObjectId

from .data_models import Match, MatchDatabase, Player, PlayerDatabase
from .settings import Settings

__all__ = ["Manager"]


class Manager:
    def __init__(self, config: Settings):
        self.__players: dict[ObjectId, PlayerDatabase] = {}
        self.__matches: list[MatchDatabase] = []
        self._config = config

    def get_players(self) -> dict[ObjectId, PlayerDatabase]:
        return copy.deepcopy(self.__players)

    def get_matches(self) -> list[MatchDatabase]:
        return copy.deepcopy(self.__matches)

    def recalculate_rankings(self):
        for player in self.__players.values():
            player.reset()

        matches = self.__matches
        self.__matches = []

        for match in matches:
            self.add_match(match)

    def add_player(self, player: Player) -> PlayerDatabase:
        _id = ObjectId()  # TODO: Add to a database
        db_player = PlayerDatabase(**player.dict())
        db_player.id = _id
        self.__players[_id] = db_player
        return db_player

    def update_player(self, player: Player) -> Player:
        _id = ObjectId(player.id)
        db_player = self.__players[_id]
        for key, value in player.dict():
            if key != "id":
                setattr(db_player, key, value)
        # TODO: save
        return player

    def get_player(self, player_id: ObjectId):
        return self.__players[player_id]

    def set_active(self, player_id: ObjectId, active: bool):
        player = self.__players[player_id]
        player.active = active
        # TODO: Save to database

    def delete_match(self, match_id: ObjectId):
        if match_id not in self.__matches:
            raise KeyError(f"No such match: {match_id}")
        self.recalculate_rankings()
        # TODO: Save to database?

    def add_match(self, match: Match) -> MatchDatabase:
        db_match = MatchDatabase.from_match(match)
        db_match.id = ObjectId()
        # TODO: Save to database
        self.__matches.append(db_match)
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
        # TODO: Save to database

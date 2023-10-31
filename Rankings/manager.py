"""
manager.py: Manager for a rankings system based on chess rankings
"""

from bson import ObjectId

from .data_models import Match, Player
from .settings import Settings


class Manager:
    def __init__(self, config: Settings):
        self.players: dict[ObjectId, Player] = {}
        self.matches: list[Match] = []
        self.config = config

    def recalculate_rankings(self):
        for player in self.players.values():
            player.reset()

        matches = self.matches
        self.matches = []

        for match in matches:
            self.add_match(match)

    def add_player(self, player: Player):
        _id = ObjectId()  # TODO: Add to a database
        player._id = _id
        self.players[player._id] = player
        return player._id

    def get_player(self, player_id: ObjectId):
        return self.players[player_id]

    def set_active(self, player_id: ObjectId, active: bool):
        player = self.players[player_id]
        player.active = active
        # TODO: Save to database

    def disable_player(self, player_id: ObjectId):
        self.set_active(player_id, False)

    def delete_match(self, match_id: ObjectId):
        if match_id not in self.matches:
            raise KeyError(f"No such match: {match_id}")
        self.recalculate_rankings()
        # TODO: Save to database?

    def add_match(self, match: Match):
        self.matches.append(match)
        self._apply_points(match)

    def _apply_points(self, match: Match):
        assert len(match.result) == 2, "We need 2 people in a match"
        rating_change = self.calculate_rating_change(match)

        winner = self.players[match.result[0]]
        loser = self.players[match.result[1]]

        self.adjust_player_rating(player=loser, adjustment=rating_change)
        self.adjust_player_rating(player=winner, adjustment=rating_change if match.draw else -rating_change)

        if match.draw:
            winner.draws += 1
            loser.draws += 1
        else:
            winner.wins += 1
            loser.losses += 1

        # TODO: Save to the database

    def calculate_rating_change(self, match: Match):
        ratings = [self.players[player_id].rating for player_id in match.result]
        assert len(ratings) == 2, "We only support matches between 2 players"
        exp_score_a = Manager.get_exp_score_a(*ratings)
        if match.draw:
            return 0.5 - exp_score_a
        else:
            return 1 - exp_score_a

    @staticmethod
    def get_exp_score_a(rating_a: float, rating_b: float) -> float:
        return 1.0 / (1 + 10 ** ((rating_b - rating_a) / 400.0))

    def adjust_player_rating(self, player: Player, adjustment: float):
        player.played_match = True

        k = max((self.config.initial_k - player.match_count), self.config.standard_k)

        player.rating += k * adjustment

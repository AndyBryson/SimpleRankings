#!/usr/bin/env python

"""
Player.py: Information and helper methods for a player
"""

__author__ = "Andy Bryson"
__copyright__ = "Copyright 2016, Andy Bryson"
__credits__ = ["Andy Bryson"]
__license__ = "MIT"
__version__ = "0.0.1"
__maintainer__ = "Andy Bryson"
__email__ = "agbryson@gmail.com"
__status__ = "Development"


class Player(object):
    def __init__(self, player_id=None, name=None, rating=1600, active=True):
        self.player_id = player_id
        self.rating = rating
        self.name = name
        self.active = active
        self.played_match = False
        self.wins = 0
        self.losses = 0
        self.draws = 0

    def total_matches(self):
        return self.wins + self.losses + self.draws

    def to_dict(self):
        return {"player_id": self.player_id, "rating": self.rating, "name": self.name, "active": self.active}

    @staticmethod
    def from_dict(dict_in):
        p = Player()
        p.player_id = dict_in["player_id"]
        p.rating = dict_in["rating"]
        p.name = dict_in["name"]
        p.active = dict_in["active"]
        return p

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return "Player id: {}, name: {}, rating: {}, active: {}".format(self.player_id,
                                                                        self.name,
                                                                        self.rating,
                                                                        self.active)

    def reset(self):
        self.rating = 1600
        self.played_match = False
        self.wins = 0
        self.losses = 0
        self.draws = 0

    @staticmethod
    def get_rating_change(winner, loser):
        exp_score_a = Player.get_exp_score_a(winner.rating, loser.rating)
        print exp_score_a


    def match(self, other, result):
        exp_score_a = Player.get_exp_score_a(self.rating, other.rating)

        print exp_score_a

        if result == self:
            self.rating_adj(exp_score_a, 1)
            other.rating_adj(1 - exp_score_a, 0)
        elif result == other:
            self.rating_adj(exp_score_a, 0)
            other.rating_adj(1 - exp_score_a, 1)
        elif result == 'Draw':
            self.rating_adj(exp_score_a, 0.5)
            other.rating_adj(1 - exp_score_a, 0.5)

    def rating_adj(self, exp_score, score, k=20):
        if score is 1:
            self.wins += 1
        elif score is 0:
            self.losses +=1
        else:
            self.draws += 1
        change = k * (score - exp_score)
        self.rating += change
        self.played_match = True
        print "score: {}, exp_score: {}, change: {}, rating: {}".format(score, exp_score, change, self.rating)

    @staticmethod
    def get_exp_score_a(rating_a, rating_b):
        return 1.0 / (1 + 10**((rating_b - rating_a)/400.0))


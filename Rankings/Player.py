#!/usr/bin/env python

"""
Player.py: Information and helper methods for a player
"""

from __future__ import division

__author__ = "Andy Bryson"
__copyright__ = "Copyright 2016, Andy Bryson"
__credits__ = ["Andy Bryson"]
__license__ = "GPLv3"
__version__ = "0.0.1"
__maintainer__ = "Andy Bryson"
__email__ = "agbryson@gmail.com"
__status__ = "Development"


class Player(object):
    def __init__(self, player_id=None, name=None, rating=1600, active=True):
        self.player_id = player_id
        self.name = name
        self.active = active
        self.rating = rating
        self.played_match = False
        self.match_count = 0
        self.win_count = 0
        self.percent = 0

    def total_matches(self):
        return self.match_count

    def to_dict(self):
        return {"player_id": self.player_id,
                "rating": self.rating,
                "name": self.name,
                "active": self.active,
                "match_count": self.match_count,
                "win_count": self.win_count,
                "percent": self.percent}

    @staticmethod
    def from_dict(dict_in):
        p = Player()
        p.player_id = dict_in["player_id"]
        p.rating = dict_in["rating"]
        p.name = dict_in["name"]
        p.active = dict_in["active"]
        p.match_count = dict_in["match_count"]
        p.win_count = dict_in["win_count"]
        p.percent = dict_in["percent"]
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
        self.match_count = 0
        self.win_count = 0
        self.percent = 0




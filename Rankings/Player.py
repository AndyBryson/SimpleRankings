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
        self.first_name = ""
        self.nick_name = ""
        self.last_name = ""
        self.long_name = ""
        self.short_name = ""
        if name is not None:
            self.set_name(name)
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
                "first_name": self.first_name,
                "nick_name": self.nick_name,
                "last_name": self.last_name,
                "active": self.active,
                "match_count": self.match_count,
                "win_count": self.win_count,
                "percent": self.percent}

    @staticmethod
    def from_dict(dict_in):
        p = Player()
        p.player_id = dict_in["player_id"]
        p.rating = dict_in["rating"]
        if "name" in dict_in:
            p.set_name(dict_in["name"])
        p.active = dict_in["active"]
        p.match_count = dict_in["match_count"]
        p.win_count = dict_in["win_count"]
        p.percent = dict_in["percent"]
        if "first_name" in dict_in:
            p.first_name = dict_in["first_name"].strip()
        if "nick_name" in dict_in:
            p.nick_name = dict_in["nick_name"].strip()
        if "last_name" in dict_in:
            p.last_name = dict_in["last_name"].strip()

        Player.set_long_short_names(p)
        return p

    @staticmethod
    def set_long_short_names(player):
        player.long_name = player.get_name(True)
        player.short_name = player.get_name(False)

    def set_name(self, name):
        if "\"" in name:
            names = name.split("\"")
            self.first_name = names[0].strip()
            self.last_name = names[2].strip()
            self.nick_name = names[1].strip()
        else:
            names = name.split(" ")
            if len(names) is 2:
                self.first_name = names[0].strip()
                self.last_name = names[1].strip()
            else:
                self.first_name = name.strip()
                self.nick_name = ""
                self.last_name = ""
        Player.set_long_short_names(self)

    def get_name(self, full_name=True):
        name = self.first_name

        if full_name is True and len(self.nick_name) > 0:
            name += " \"" + self.nick_name + "\""

        if len(self.last_name) > 0:
            name += " {}".format(self.last_name)

        return name

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return "Player id: {}, name: {}, rating: {}, active: {}".format(self.player_id,
                                                                        self.get_name(),
                                                                        self.rating,
                                                                        self.active)

    def reset(self):
        self.rating = 1600
        self.played_match = False
        self.match_count = 0
        self.win_count = 0
        self.percent = 0




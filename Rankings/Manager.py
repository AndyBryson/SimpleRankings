#!/usr/bin/env python

"""
Manager.py: Manager for a rankings system based on chess rankings
"""

import json
import os.path

from Player import Player
from Match import Match

__author__ = "Andy Bryson"
__copyright__ = "Copyright 2016, Andy Bryson"
__credits__ = ["Andy Bryson"]
__license__ = "MIT"
__version__ = "0.0.1"
__maintainer__ = "Andy Bryson"
__email__ = "agbryson@gmail.com"
__status__ = "Development"


def get_next_key(dict_in):
    next_key = 0
    for key in dict_in.keys():
        if key >= next_key:
            next_key = key + 1
    return next_key


class Manager(object):
    def __init__(self, load=True):
        self.players = {}
        self.matches = []
        self.league_title = ""

        if load:
            self.load()

    def save(self):
        with open("settings.txt", "w") as outfile:
            json.dump(self.to_json(), outfile, indent=2)

    def load(self):
        if os.path.isfile("settings.txt"):
            with open("settings.txt", "r") as in_file:
                self.from_json(json.load(in_file))

    def from_dict(self, dict_in):
        players_arr = dict_in["players"]
        for player in players_arr:
            player_obj = Player.from_dict(player)
            self.players[player_obj.player_id] = player_obj

        for match in dict_in["matches"]:
            self.matches.append(Match.from_dict(match))

        self.league_title = dict_in["league_title"]

        self.recalculate_rankings()

    def from_json(self, json_in):
        self.from_dict(json.loads(json_in))

    def to_dict(self):
        players_arr = []
        for key, player in self.players.iteritems():
            players_arr.append(player.to_dict())

        matches_arr = []
        for match in self.matches:
            matches_arr.append(match.to_dict())

        return {"players": players_arr, "matches": matches_arr, "league_title": self.league_title}

    def to_json(self):
        return json.dumps(self.to_dict())

    def recalculate_rankings(self):
        for player in self.players.values():
            player.reset()

        matches = self.matches
        self.matches = []

        for match in matches:
            self.match(match.result_array, match.date)

    def add_player(self, name, rating=1600):
        if name == "":
            # TODO A: raise and handle an exception
            return -1

        for player in self.players.values():
            if player.name == name:
                # TODO A: raise and handle an exception
                return -1

        player_id = get_next_key(self.players)
        self.players[player_id] = Player(player_id, name, rating)

        self.save()

        return player_id

    def get_player(self, player_id):
        if player_id in self.players:
            return self.players[player_id]
        else:
            return None

    def set_name(self, player_id, name):
        player = self.get_player(player_id)
        if player is not None and name is not "":
            player.name = name
            self.save()

    def set_active(self, player_id, active):
        player = self.get_player(player_id)
        if player is not None:
            player.active = active
            self.save()

    def get_players_in_rank_order(self, include_inactive=False):
        players = self.players.values()
        players.sort(key=lambda x: (x.played_match, x.rating), reverse=True)
        if include_inactive is True:
            return players
        else:
            return Manager.remove_inactive(players)

    def get_players_in_name_order(self, include_inactive=False):
        players = self.players.values()
        players.sort(key=lambda x: x.name)
        if include_inactive is True:
            return players
        else:
            return Manager.remove_inactive(players)

    @staticmethod
    def remove_inactive(players):
        return [x for x in players if x.active]

    def disable_player(self, player_id):
        if player_id in self.players:
            self.players[player_id].active = False

    def delete_match(self, match_index):
        if match_index < len(self.matches):
            self.matches.pop(match_index)
            self.recalculate_rankings()
            self.save()

    def match(self, players_in_order, date=None):
        result = []
        for player in players_in_order:
            if type(player) is Player:
                result.append(player)
            elif type(player) is int:
                result.append(self.get_player(player))
            else:
                raise ValueError("winner must be a Player or a player_id", player)

        player_ids = []
        for player in result:
            player_ids.append(player.player_id)

        self.matches.append(Match(player_ids, date))
        self.apply_points(result)
        self.save()

    @staticmethod
    def apply_points(result):
        rating_changes = []
        for x in result:
            rating_changes.append(0)

        # This divisor is used to make sure that the winner gets the same points as he would for just beating one
        # person, even if they beat 10
        divisor = len(result) - 1

        for i in range(0, len(result)):
            for j in range(i + 1, len(result)):
                rating_change = Player.calculate_rating_change(result[i], result[j]) / divisor
                rating_changes[i] += rating_change
                rating_changes[j] -= rating_change

        for i in range(0, len(result)):
            player = result[i]
            rating_change = rating_changes[i]
            player.adjust_rating(rating_change, i+1, len(result))


if __name__ == "__main__":
    m = Manager(False)
    m.add_player("Andy")
    m.add_player("Bob")
    m.add_player("Test")
    m.add_player("Dave")
    m.match([0, 1, 2, 3])
    m.match([3, 2, 1, 0])
    m_string = m.to_json()

    other = Manager()
    other.from_json(m_string)

    print other.to_json()

    players = m.get_players_in_rank_order()
    total = 0
    for player in players:
        total += player.rating
    print total / len(players)

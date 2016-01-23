#!/usr/bin/env python

"""
Manager.py: Manager for a rankings system based on chess rankings
"""

from __future__ import division
import json
import os.path
from ConfigParser import ConfigParser

from Player import Player
from Match import Match

__author__ = "Andy Bryson"
__copyright__ = "Copyright 2016, Andy Bryson"
__credits__ = ["Andy Bryson"]
__license__ = "GPLv3"
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
    def __init__(self, config, load=True):
        self.players = {}
        self.matches = []
        self.__config = config
        self.__init_config()

        self.__initial_k = self.__config.getint("rankings", "initial_k")
        self.__standard_k = self.__config.getint("rankings", "standard_k")

        if load:
            self.load()

    def __init_config(self):
        if self.__config.has_section("rankings") is False:
            self.__config.add_section("rankings")

        if self.__config.has_option("rankings", "initial_k") is False:
            self.__config.set("rankings", "initial_k", "30")

        if self.__config.has_option("rankings", "standard_k") is False:
            self.__config.set("rankings", "standard_k", "16")

        with open(self.__config.file_name, 'wb') as configfile:
            self.__config.write(configfile)

    def save(self):
        with open("data.txt", "w") as outfile:
            json.dump(self.to_json(), outfile, indent=2)

    def load(self):
        if os.path.isfile("data.txt"):
            with open("data.txt", "r") as in_file:
                self.from_json(json.load(in_file))

    def from_dict(self, dict_in):
        players_arr = dict_in["players"]
        for player in players_arr:
            player_obj = Player.from_dict(player)
            self.players[player_obj.player_id] = player_obj

        for match in dict_in["matches"]:
            self.matches.append(Match.from_dict(match))

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

        return {"players": players_arr, "matches": matches_arr, }

    def to_json(self):
        return json.dumps(self.to_dict())

    def recalculate_rankings(self):
        for player in self.players.values():
            player.reset()

        matches = self.matches
        self.matches = []

        for match in matches:
            self.match(match.result_array, match.date, match.draw)

    def add_player(self, name, rating=1600):
        if name == "":
            # TODO A: raise and handle an exception
            return -1

        for player in self.players.values():
            if player.long_name == name:
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
            player.set_name(name)
            self.save()

    def set_active(self, player_id, active):
        player = self.get_player(player_id)
        if player is not None:
            player.active = active
            self.save()

    def disable_player(self, player_id):
        if player_id in self.players:
            self.players[player_id].active = False

    def delete_match(self, match_index):
        if match_index < len(self.matches):
            self.matches.pop(match_index)
            self.recalculate_rankings()
            self.save()

    def match(self, players_in_order, date=None, draw=False):
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

        self.matches.append(Match(player_ids, date, draw))
        self.apply_points(result, draw)
        self.save()

    def apply_points(self, result, draw=False):
        rating_changes = []
        normalised_rating_changes = []
        for x in result:
            rating_changes.append(0)
            normalised_rating_changes.append(0)

        for i in range(0, len(result)):
            for j in range(i + 1, len(result)):
                rating_change = Manager.calculate_rating_change(result[i], result[j], draw)
                normalised_rating_change = Manager.calculate_rating_change(result[i], result[j], draw) / (len(result) - 1)
                rating_changes[i] += rating_change
                rating_changes[j] -= rating_change
                normalised_rating_changes[i] += normalised_rating_change
                normalised_rating_changes[j] -= normalised_rating_change

        for i in range(0, len(result)):
            player = result[i]
            rating_change = rating_changes[i]
            normalised_rating_change = normalised_rating_changes[i]

            self.adjust_player_normalised_rating(player, normalised_rating_change)
            self.adjust_player_rating(player, rating_change, i+1, len(result), draw)

    @staticmethod
    def calculate_rating_change(winner, loser, draw):
        exp_score_a = Manager.get_exp_score_a(winner.rating, loser.rating)
        if draw is False:
            change = (1 - exp_score_a)
        else:
            change = (0.5 - exp_score_a)
        return change

    @staticmethod
    def get_exp_score_a(rating_a, rating_b):
        return 1.0 / (1 + 10**((rating_b - rating_a)/400.0))

    def adjust_player_rating(self, player, adjustment, position, player_count, draw=False):
        player.played_match = True

        k = max((self.__initial_k - player.match_count), self.__standard_k)

        player.rating += k * adjustment
        player.match_count += 1

        if draw is True:
            percent = 50
        else:
            percent = ((player_count - position) / (player_count - 1)) * 100

        percent_diff = (percent - player.percent) / player.match_count

        player.percent += percent_diff

        if draw is True:
            player.draw_count += 1
        else:
            if position is 1:
                player.win_count += 1
            elif position is player_count:
                player.loss_count += 1

    def adjust_player_normalised_rating(self, player, adjustment):
        k = max((self.__initial_k - player.match_count), self.__standard_k)
        player.normalised_rating += k * adjustment


if __name__ == "__main__":
    m = Manager(False)
    m.add_player("Andy")
    m.add_player("Bob")
    m.add_player("Test")
    m.add_player("Dave")
    m.match([0, 1, 2, 3])
    m.match([3, 2, 1, 0])
    m_string = m.to_json()

    config = ConfigParser()
    config.file_name = "config.txt"

    other = Manager(config)
    other.from_json(m_string)

    print other.to_json()

    players = m.get_players_in_rank_order()
    total = 0
    for player in players:
        total += player.rating
    print total / len(players)

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
        self.__use_true_skill = self.__config.getboolean("rankings", "true_skill")

        if load:
            self.load()

    def __init_config(self):
        if self.__config.has_section("rankings") is False:
            self.__config.add_section("rankings")

        if self.__config.has_option("rankings", "initial_k") is False:
            self.__config.set("rankings", "initial_k", "30")

        if self.__config.has_option("rankings", "standard_k") is False:
            self.__config.set("rankings", "standard_k", "16")

        if self.__config.has_option("rankings", "true_skill") is False:
            self.__config.set("rankings", "true_skill", "false")

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
            if self.__use_true_skill is True:
                from trueskill import Rating
                player_obj.true_skill = Rating()

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
            if self.__use_true_skill is True:
                from trueskill import Rating
                player.true_skill = Rating()

        matches = self.matches
        self.matches = []

        for match in matches:
            self.match(match.result_array, match.date, match.draw)

    def add_player(self, name, rating=1600):
        if name == "":
            return -1

        for player in self.players.values():
            if player.long_name == name:
                return -1

        player_id = get_next_key(self.players)
        self.players[player_id] = Player(player_id, name, rating)

        if self.__use_true_skill is True:
            from trueskill import Rating
            self.players[player_id].true_skill = Rating()

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

    def clean_team(self, team):
        clean_team = []
        for player in team:
            if type(player) is Player:
                clean_team.append(player)
            elif type(player) is int:
                clean_team.append(self.get_player(player))
            else:
                raise ValueError("winner must be a Player or a player_id", player)
        return clean_team

    def match(self, teams_in_order, date=None, draw=False):
        result = []
        for team in teams_in_order:
            result.append(self.clean_team(team))

        player_ids = []
        for team in result:
            team_ids = []
            for player in team:
                team_ids.append(player.player_id)
            player_ids.append(team_ids)

        self.matches.append(Match(player_ids, date, draw))
        self.apply_points(result, draw)
        self.save()

    def apply_points(self, result, draw=False):
        number_of_teams = len(result)
        for count, team in enumerate(result):
            for player in team:
                player.match_count += 1
                if draw:
                    player.draw_count += 1
                elif count == 0:
                    player.win_count += 1
                elif count == number_of_teams - 1:
                    player.loss_count += 1

                if draw is True:
                    percent = 50
                else:
                    percent = ((number_of_teams - (count + 1)) / (number_of_teams - 1)) * 100

                percent_diff = (percent - player.percent) / player.match_count

                player.percent += percent_diff


        if self.__use_true_skill is True:
            from trueskill import rate
            ts_result_list = []
            ts_ranks = []
            rank = 0

            for team in result:
                team_list = []
                for player in team:
                    team_list.append(player.true_skill)
                team_tuple = tuple(team_list)
                ts_result_list.append(team_tuple)

                ts_ranks.append(rank)
                if draw is False:
                    rank += 1

            ts_ratings = rate(ts_result_list, ranks=ts_ranks)
            for i in range(0, len(result)):
                for j in range(0, len(result[i])):
                    result[i][j].true_skill = ts_ratings[i][j]

        result_no_teams = []
        for team in result:
            if len(team) > 1:
                return  # Only true skill supports teams
            elif len(team) == 1:
                result_no_teams.append(team[0])

        rating_changes = []
        normalised_rating_changes = []
        for x in result_no_teams:
            rating_changes.append(0)
            normalised_rating_changes.append(0)

        for i in range(0, len(result_no_teams)):
            for j in range(i + 1, len(result_no_teams)):
                rating_change = Manager.calculate_rating_change(result_no_teams[i], result_no_teams[j], draw)
                normalised_rating_change = Manager.calculate_rating_change(result_no_teams[i],
                                                                           result_no_teams[j], draw) / (len(result_no_teams) - 1)
                rating_changes[i] += rating_change
                rating_changes[j] -= rating_change
                normalised_rating_changes[i] += normalised_rating_change
                normalised_rating_changes[j] -= normalised_rating_change

        for i in range(0, len(result_no_teams)):
            player = result_no_teams[i]
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

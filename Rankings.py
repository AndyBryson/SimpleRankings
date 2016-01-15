#!/usr/bin/env python

"""
Rankings.py: A set of tools to run a rankings system based on chess rankings
"""

__author__ = "Andy Bryson"
__copyright__ = "Copyright 2016, Andy Bryson"
__credits__ = ["Andy Bryson"]
__license__ = "MIT"
__version__ = "0.0.1"
__maintainer__ = "Andy Bryson"
__email__ = "agbryson@gmail.com"
__status__ = "Development"


import json
import time
import os.path


def get_exp_score_a(rating_a, rating_b):
    return 1.0 / (1 + 10**((rating_b - rating_a)/400.0))


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
            self.match(match.winner_id, match.loser_id, match.date)

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

    def match(self, winner, loser, date=None):
        if type(winner) is not Player:
            if type(winner) is int:
                winner = self.get_player(winner)
            else:
                raise ValueError("winner must be a Player or a player_id", winner)

        if type(loser) is not Player:
            if type(loser) is int:
                loser = self.get_player(loser)
            else:
                raise ValueError("winner must be a Player or a player_id", winner)

        self.matches.append(Match(winner.player_id, loser.player_id, date))

        winner.match(loser, winner)

        print "winner {}".format(winner)
        print "loser {}".format(loser)

        self.save()


class Match(object):
    def __init__(self, winner_id=None, loser_id=None, date=None):
        if date is None:
            date = time.strftime("%Y-%m-%d %H-%M-%S")

        self.date = date
        self.winner_id = winner_id
        self.loser_id = loser_id

    def to_dict(self):
        return {"winner_id": self.winner_id, "loser_id": self.loser_id, "date": self.date}

    @staticmethod
    def from_dict(dict_in):
        m = Match()
        m.winner_id = dict_in["winner_id"]
        m.loser_id = dict_in["loser_id"]
        m.date = dict_in["date"]
        return m


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

    def match(self, other, result):
        exp_score_a = get_exp_score_a(self.rating, other.rating)

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
        self.rating += k * (score - exp_score)
        self.played_match = True


if __name__ == "__main__":
    m=Manager()
    m.add_player("Andy")
    m.add_player("Bob")
    m.add_player("Test")
    m.match(0, 1)
    m.add_player("Dave")
    m.match(0,3)
    m_string=m.to_json()

    other=Manager()
    other.from_json(m_string)

    print other.to_json()

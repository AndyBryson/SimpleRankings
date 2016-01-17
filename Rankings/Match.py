#!/usr/bin/env python

"""
Match.py: A set of tools to run a rankings system based on chess rankings
"""

__author__ = "Andy Bryson"
__copyright__ = "Copyright 2016, Andy Bryson"
__credits__ = ["Andy Bryson"]
__license__ = "MIT"
__version__ = "0.0.1"
__maintainer__ = "Andy Bryson"
__email__ = "agbryson@gmail.com"
__status__ = "Development"


import time


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


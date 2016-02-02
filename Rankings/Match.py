#!/usr/bin/env python

"""
Match.py: A set of tools to run a rankings system based on chess rankings
"""

import time

__author__ = "Andy Bryson"
__copyright__ = "Copyright 2016, Andy Bryson"
__credits__ = ["Andy Bryson"]
__license__ = "GPLv3"
__version__ = "0.0.1"
__maintainer__ = "Andy Bryson"
__email__ = "agbryson@gmail.com"
__status__ = "Development"


class Match(object):
    def __init__(self, result_array=None, date=None, draw=False):
        if date is None:
            date = time.strftime("%Y-%m-%d %H-%M-%S")

        self.date = date
        self.result_array = result_array
        self.draw = draw

    def to_dict(self):
        return {"result_array": self.result_array,
                "date": self.date,
                "draw": self.draw}

    @staticmethod
    def from_dict(dict_in):
        m = Match()
        m.result_array = dict_in["result_array"]

        for i in range(0, len(m.result_array)):  # we used to save as an array of individuals, not teams
            if not isinstance(m.result_array[i], list):
                m.result_array[i] = [ m.result_array[i] ]

        m.date = dict_in["date"]
        if "draw" in dict_in:
            m.draw = dict_in["draw"]
        return m


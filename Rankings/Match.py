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
    def __init__(self, result_array=None, date=None):
        if date is None:
            date = time.strftime("%Y-%m-%d %H-%M-%S")

        self.date = date
        self.result_array = result_array

    def to_dict(self):
        return {"result_array": self.result_array, "date": self.date}

    @staticmethod
    def from_dict(dict_in):
        m = Match()
        m.result_array = dict_in["result_array"]
        m.date = dict_in["date"]
        return m


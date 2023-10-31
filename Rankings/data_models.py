#!/usr/bin/env python

"""
match.py: A set of tools to run a rankings system based on chess rankings
"""

from datetime import datetime

from bson import ObjectId
from pydantic import BaseModel


class Match(BaseModel):
    _id: ObjectId | None = None
    result: list[ObjectId]
    draw: bool
    date: datetime


class Player(BaseModel):
    _id: ObjectId | None = None
    first_name: str = ""
    last_name: str = ""
    active: bool = True
    rating: float = 1600
    normalised_rating: float = 1600
    match_count: int = 0
    wins: int = 0
    losses: int = 0
    draws: int = 0

    def reset(self):
        self.rating = 1600
        self.normalised_rating = 1600

#!/usr/bin/env python

"""
match.py: A set of tools to run a rankings system based on chess rankings
"""

from datetime import datetime

from bson import ObjectId
from pydantic import BaseModel

from .mongo_pure_pydantic import MongoPurePydantic

__all__ = ["Match", "MatchDatabase", "PlayerDatabase", "Player"]


class Match(BaseModel):
    id: str | None = None
    result: list[str]
    draw: bool
    date: datetime


class MatchDatabase(Match, MongoPurePydantic):
    __meta__ = {"collection": "matches"}
    result: list[ObjectId]

    def to_match(self) -> Match:
        d = self.dict()
        d["id"] = str(self.id)
        d["result"] = [str(x) for x in self.result]
        return Match(**d)

    @classmethod
    def from_match(cls, match: Match):
        d = match.dict()
        if _id := d.get("id"):
            d["id"] = ObjectId(_id)
        d["result"] = [ObjectId(x) for x in d["result"] if isinstance(x, str)]
        return cls(**d)


class Player(BaseModel):
    id: str | None = None
    first_name: str = ""
    last_name: str = ""
    active: bool = True
    rating: float = 1600
    match_count: int = 0
    wins: int = 0
    losses: int = 0
    draws: int = 0

    def reset(self):
        self.rating = 1600


class PlayerDatabase(MongoPurePydantic, Player):
    __meta__ = {"collection": "players"}

    def to_player(self) -> Player:
        d = self.dict()
        d["id"] = str(self.id)
        return Player(**d)

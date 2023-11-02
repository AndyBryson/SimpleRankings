#!/usr/bin/env python

"""
match.py: A set of tools to run a rankings system based on chess rankings
"""

from datetime import datetime, timezone
from enum import Enum

from bson import ObjectId
from pydantic import BaseModel, validator

from RankingsAPI.Mongo import MongoPurePydantic

__all__ = ["EResult", "MatchAPI", "Match", "Player", "PlayerAPI"]


class EResult(Enum):
    WIN = "win"
    LOSE = "lose"
    DRAW = "draw"


class MatchBase(BaseModel):
    result: list[str]
    draw: bool
    date: datetime = datetime.now(timezone.utc)


class MatchAPI(MatchBase):
    id: str | None = None


class Match(MatchBase, MongoPurePydantic):
    __meta__ = {"collection": "matches"}
    result: list[ObjectId]

    def to_api(self) -> MatchAPI:
        d = self.dict()
        d["id"] = str(self.id)
        d["result"] = [str(x) for x in self.result]
        return MatchAPI(**d)

    @classmethod
    def from_api(cls, match: MatchAPI):
        d = match.dict()
        if _id := d.get("id"):
            d["id"] = ObjectId(_id)
        d["result"] = [ObjectId(x) for x in d["result"] if isinstance(x, str)]
        return cls(**d)


class PlayerBase(BaseModel):
    name: str
    active: bool = True
    rating: float = 1600
    match_count: int = 0
    wins: int = 0
    losses: int = 0
    draws: int = 0

    def reset(self):
        self.rating = 1600
        self.wins = 0
        self.losses = 0
        self.draws = 0

    @validator("name")
    def validate_name(cls, v: str):
        if not v.strip():
            raise ValueError("Name cannot be empty")
        return v


class PlayerAPI(PlayerBase):
    id: str | None = None


class Player(MongoPurePydantic, PlayerBase):
    __meta__ = {"collection": "players"}

    def to_api(self) -> PlayerAPI:
        d = self.dict()
        d["id"] = str(self.id)
        return PlayerAPI(**d)

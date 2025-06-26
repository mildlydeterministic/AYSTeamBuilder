"""
Contains data models: Player, Coach, and Team.
Encapsulates core data used throughout the build process.

See /docs/spec.md for full specification.
"""
from dataclasses import dataclass, field
from typing import Optional, List

# Uniform sizes in order from smallest to largest for ordinal/weighting use
UNIFORM_SIZES = [
    "Youth XXS",
    "Youth XS",
    "Youth S",
    "Youth M",
    "Youth L",
    "Youth XL",
    "Adult XS",
    "Adult S",
    "Adult M",
    "Adult L",
    "Adult XL",
    "Adult XXL"
]

@dataclass
class Player:
    player_id: str
    name: str  # full name
    dob: str  # MM/DD/YYYY
    age: float  # computed from DOB, 1 decimal precision, half-up rounding
    experience: int
    uniform_size: str
    evaluation_score: str  # raw format, possibly numeric
    skill_score: Optional[float] = None
    sponsor_id: Optional[str] = None

@dataclass
class Coach:
    coach_id: str
    full_name: str
    role: str  # "Head Coach" or "Assistant Coach"
    volunteer_type_id: str # used for output
    associated_player_id: Optional[str] = None
    pair_id: Optional[str] = None  # referenced VolunteerID of intended pair

@dataclass
class Team:
    team_id: str
    name: str  # e.g. "Smith/Jones" or "Smith"
    head_coach: Coach
    assistant_coach: Optional[Coach] = None
    players: List[Player] = field(default_factory=list)
    sponsor_id: Optional[str] = None
    total_score: float = 0.0

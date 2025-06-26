"""
Normalizes skill-related features and computes a weighted skill score.
Handles missing data and dynamic min/max normalization per division.

See /docs/spec.md for full specification.
"""

# Weight constants for skill scoring (can be tuned)
AGE_WEIGHT = 0.25
EXPERIENCE_WEIGHT = 0.35
UNIFORM_SIZE_WEIGHT = 0.15
EVALUATION_WEIGHT = 0.25

from typing import List, Optional, Dict
from .models import Player, UNIFORM_SIZES


def calculate_player_skill_score(player: Player, normalization_context: Dict) -> float:
    """
    Calculate the normalized, weighted skill score for a player using min/max context.
    Uniform size is normalized using its index in UNIFORM_SIZES.
    """
    # ...stub...
    pass


def build_normalization_context(players: List[Player]) -> Dict:
    """
    Builds min/max context for normalization from a list of players.
    Returns a dict with min/max for age, experience, uniform_size (ordinal), and evaluation_score.
    """
    # ...stub...
    pass

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


def build_normalization_context(players: List[Player]) -> Dict:
    """
    Builds min/max context for normalization from a list of players.
    Returns a dict with min/max for age, experience, uniform_size (ordinal), and evaluation_score.
    Single pass implementation for efficiency.
    """
    ages = []
    experiences = []
    uniform_ordinals = []
    evals = []
    for p in players:
        if p.age is not None:
            ages.append(p.age)
        if p.experience is not None:
            experiences.append(p.experience)
        if p.uniform_size in UNIFORM_SIZES:
            uniform_ordinals.append(UNIFORM_SIZES.index(p.uniform_size))
        try:
            evals.append(float(p.evaluation_score))
        except (TypeError, ValueError):
            pass

    def get_min_max(values):
        if not values:
            return {"min": None, "max": None}
        return {"min": min(values), "max": max(values)}

    return {
        "age": get_min_max(ages),
        "experience": get_min_max(experiences),
        "uniform_size": get_min_max(uniform_ordinals),
        "evaluation_score": get_min_max(evals)
    }


def calculate_player_skill_score(player: Player, normalization_context: Dict) -> float:
    """
    Calculate the normalized, weighted skill score for a player using min/max context.
    Uniform size is normalized using its index in UNIFORM_SIZES.
    """
    def norm(val, minmax):
        if val is None or minmax["min"] is None or minmax["max"] is None:
            return None
        if minmax["max"] == minmax["min"]:
            return 0.5  # If all values are the same, treat as average
        return (val - minmax["min"]) / (minmax["max"] - minmax["min"])

    # Age
    age = player.age if player.age is not None else None
    age_norm = norm(age, normalization_context["age"])
    # Experience
    experience = player.experience if player.experience is not None else None
    exp_norm = norm(experience, normalization_context["experience"])
    # Uniform size ordinal
    try:
        uniform_ordinal = UNIFORM_SIZES.index(player.uniform_size)
    except ValueError:
        uniform_ordinal = None
    uniform_norm = norm(uniform_ordinal, normalization_context["uniform_size"])
    # Evaluation score
    try:
        eval_score = float(player.evaluation_score)
    except (TypeError, ValueError):
        eval_score = None
    eval_norm = norm(eval_score, normalization_context["evaluation_score"])

    # Weighted sum, omitting missing values and scaling weights
    features = [
        (age_norm, AGE_WEIGHT),
        (exp_norm, EXPERIENCE_WEIGHT),
        (uniform_norm, UNIFORM_SIZE_WEIGHT),
        (eval_norm, EVALUATION_WEIGHT)
    ]
    present = [(v, w) for v, w in features if v is not None]
    if not present:
        return 0.0
    total_weight = sum(w for _, w in present)
    score = sum(v * w for v, w in present) / total_weight
    return round(score, 4)

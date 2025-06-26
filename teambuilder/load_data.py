"""
Parses players and coaches from CSV files.
Maps header names to expected fields and builds coach pools.
Creates teams based on reciprocated and fallback pairings.

See /docs/spec.md for full specification.
"""
import csv
from typing import List, Tuple, Dict, Optional
from teambuilder.models import Player, Coach
import datetime
from decimal import Decimal

def parse_coaches_csv(filepath: str) -> Tuple[List[Coach], List[Coach]]:
    """Parse coaches.csv and return (head_coaches, assistant_coaches) pools as lists of Coach objects."""
    with open(filepath, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        return parse_coaches_csv_reader(reader)
    
def parse_players_csv(filepath: str) -> Dict[str, Player]:
    """Parse players.csv and return a dict mapping player_id to Player objects."""
    with open(filepath, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        return parse_players_csv_reader(reader)

def parse_players_csv_reader(reader) -> Dict[str, Player]:
    """Parse a csv.DictReader or file-like object and return a dict mapping player_id to Player objects."""
    players = {}
    if not reader.fieldnames:
        raise ValueError("CSV file is missing headers or is empty.")
    experience_header = ""
    uniform_size_header = ""
    # Check headers to find experience and uniform size columns
    for header in reader.fieldnames:
        if header.lower().startswith("years of experience"):
            experience_header = header
        elif header.lower().startswith("uniform size"):
            uniform_size_header = header
    for row in reader:
        # Flexible header mapping
        player_id = row.get("PlayerID") or ""
        name = row.get("Player Name") or ""
        dob = row.get("Date Of Birth") or ""
        experience = row.get(experience_header) or None
        uniform_size = row.get(uniform_size_header) or "Youth M"
        evaluation_score = row.get("Player Evaluation Ranking") or ""
        sponsor_id = row.get("sponsor_id") or None
        # Compute age if possible 
        age = compute_age_from_dob(dob)
        try:
            experience = int(experience) if experience is not None else 0
        except ValueError:
            experience = 0
        players[player_id] = Player(
            player_id=player_id,
            name=name,
            dob=dob,
            experience=experience,
            uniform_size=uniform_size,
            age=age,
            evaluation_score=evaluation_score,
            sponsor_id=sponsor_id
        )
    return players

def parse_coaches_csv_reader(reader) -> Tuple[List[Coach], List[Coach]]:
    """Parse a csv.DictReader or file-like object and return (head_coaches, assistant_coaches) pools as lists of Coach objects."""
    head_coaches = []
    assistant_coaches = []
    for row in reader:
        coach_id = row.get("VolunteerID") or ""
        full_name = row.get("Team Personnel Name") or ""
        role = row.get("Team Personnel Role") or ""
        associated_player_id = row.get("associatedPlayers") or row.get("associated_player_id")
        if associated_player_id and associated_player_id.lower().startswith("no answer"):
            associated_player_id = None
        pair_id = row.get("Coach Pair") or None
        volunteer_type_id = row.get("VolunteerTypeID") or ""
        coach = Coach(
            coach_id=coach_id,
            full_name=full_name,
            role=role,
            associated_player_id=associated_player_id if associated_player_id else None,
            pair_id=pair_id,
            volunteer_type_id=volunteer_type_id
        )
        if role and "head" in role.lower():
            head_coaches.append(coach)
        elif role and "assistant" in role.lower():
            assistant_coaches.append(coach)
    return head_coaches, assistant_coaches

def compute_age_from_dob(dob: str, ref_date: Optional[datetime.date] = None) -> float:
    """
    Compute age in years (1 decimal, half-up rounding) from MM/DD/YYYY dob string.
    If dob is invalid or missing, returns 0.0.
    Optionally takes a reference date (defaults to today).
    """
    if not dob:
        return 0.0
    try:
        month, day, year = map(int, dob.split("/"))
        birth_date = datetime.date(year, month, day)
        today = ref_date or datetime.date.today()
        days = (today - birth_date).days
        age = days / 365.25
        # Round to 1 decimal, half-up
        return float(Decimal(age).quantize(Decimal('0.1'), rounding='ROUND_HALF_UP'))
    except Exception:
        return 0.0

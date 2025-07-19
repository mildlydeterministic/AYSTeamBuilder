"""
Single-file version of AYSTeamBuilder for maximum portability.
All logic from models.py, load_data.py, scoring.py, team_builder.py, output.py, and cli.py is included here.
"""
import argparse
import csv
import datetime
import random
import statistics
from dataclasses import dataclass, field
from typing import Optional, List, Tuple, Dict

# --- models.py ---
UNIFORM_SIZES = [
    "Youth XXS", "Youth XS", "Youth S", "Youth M", "Youth L", "Youth XL",
    "Adult XS", "Adult S", "Adult M", "Adult L", "Adult XL", "Adult XXL"
]

@dataclass
class Player:
    player_id: str
    name: str
    dob: str
    experience: int
    uniform_size: str
    evaluation_score: int
    age: Optional[float] = None
    skill_score: Optional[float] = None
    sponsor_id: Optional[str] = None
    parent_name: Optional[str] = None
    street_address: Optional[str] = None
    siblings: Optional[List[str]] = field(default_factory=list)

@dataclass
class Coach:
    coach_id: str
    full_name: str
    role: str
    volunteer_type_id: str
    associated_player_id: Optional[str] = None
    pair_id: Optional[str] = None

@dataclass
class Team:
    team_id: str
    name: str
    head_coach: Coach
    assistant_coach: Optional[Coach] = None
    players: List[Player] = field(default_factory=list)
    sponsor_id: Optional[str] = None
    total_score: float = 0.0

# --- load_data.py ---

EVALUATION_SCORE_DEFAULT = 300
MIN_TEAM_SIZE = 3

def compute_age_from_dob(dob: str, ref_date: Optional[datetime.date] = None) -> float:
    if not dob:
        return 0.0
    try:
        month, day, year = map(int, dob.split("/"))
        birth_date = datetime.date(year, month, day)
        if not ref_date:
            ref_date = datetime.date.today()
        age = (ref_date - birth_date).days / 365.25
        return round(age, 1)
    except Exception:
        return 0.0

def parse_players_csv(filepath: str) -> Dict[str, Player]:
    with open(filepath, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        return parse_players_csv_reader(reader)

def parse_players_csv_reader(reader) -> Dict[str, Player]:
    players = {}
    if not reader.fieldnames:
        raise ValueError("CSV file is missing headers or is empty.")
    experience_header = ""
    uniform_size_header = ""
    for header in reader.fieldnames:
        if header.lower().startswith("years of experience"):
            experience_header = header
        elif header.lower().startswith("uniform size"):
            uniform_size_header = header
    for row in reader:
        player_id = row.get("PlayerID") or ""
        name = row.get("Player Name") or ""
        dob = row.get("Date Of Birth") or ""
        experience = row.get(experience_header) or None
        uniform_size = row.get(uniform_size_header) or "Youth M"
        evaluation_score = row.get("Player Evaluation Rating")
        sponsor_id = row.get("sponsor_id") or None
        parent_name = row.get("Parent LastName") or None
        street_address = row.get("Account Street Address") or None
        age = compute_age_from_dob(dob)
        try:
            experience = int(experience) if experience is not None else 0
        except ValueError:
            experience = 0
        # Handle evaluation score: int 0-1000 or 'No Answer' or missing
        if evaluation_score is None or evaluation_score.strip() == "" or evaluation_score.strip().lower() == "no answer":
            evaluation_score = EVALUATION_SCORE_DEFAULT
        else:
            try:
                evaluation_score = int(evaluation_score)
            except Exception:
                evaluation_score = EVALUATION_SCORE_DEFAULT
        players[player_id] = Player(
            player_id=player_id,
            name=name,
            dob=dob,
            experience=experience,
            uniform_size=uniform_size,
            age=age,
            evaluation_score=evaluation_score,
            sponsor_id=sponsor_id,
            parent_name=parent_name,
            street_address=street_address
        )
    # Identify siblings: players with same parent_name and street_address
    family_groups = {}
    for p in players.values():
        key = (p.parent_name, p.street_address)
        if key not in family_groups:
            family_groups[key] = []
        family_groups[key].append(p.player_id)

    for p in players.values():
        key = (p.parent_name, p.street_address)
        # Siblings are all other player_ids in the same family group
        p.siblings = [pid for pid in family_groups[key] if pid != p.player_id]
    return players

def parse_coaches_csv(filepath: str) -> Tuple[List[Coach], List[Coach]]:
    with open(filepath, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        return parse_coaches_csv_reader(reader)

def parse_coaches_csv_reader(reader) -> Tuple[List[Coach], List[Coach]]:
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
        volunteer_type_id = row.get("VolunteerTypeId") or ""
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

# --- scoring.py ---
AGE_WEIGHT = 0.2
EXPERIENCE_WEIGHT = 0.2
UNIFORM_SIZE_WEIGHT = 0.10
EVALUATION_WEIGHT = 0.5

def build_normalization_context(players: List[Player]) -> Dict:
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
    def norm(val, minmax):
        if val is None or minmax["min"] is None or minmax["max"] is None:
            return None
        if minmax["max"] == minmax["min"]:
            return 0.5
        return (val - minmax["min"]) / (minmax["max"] - minmax["min"])
    age = player.age if player.age is not None else None
    age_norm = norm(age, normalization_context["age"])
    experience = player.experience if player.experience is not None else None
    exp_norm = norm(experience, normalization_context["experience"])
    try:
        uniform_ordinal = UNIFORM_SIZES.index(player.uniform_size)
    except ValueError:
        uniform_ordinal = None
    uniform_norm = norm(uniform_ordinal, normalization_context["uniform_size"])
    try:
        eval_score = float(player.evaluation_score)
    except (TypeError, ValueError):
        eval_score = None
    eval_norm = norm(eval_score, normalization_context["evaluation_score"])
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

# --- team_builder.py ---
def seed_teams_with_coaches(head_coaches: List[Coach], assistant_coaches: List[Coach]) -> List[Team]:
    teams = []
    used_assistants = set()
    used_heads = set()
    for head in head_coaches:
        if head.pair_id:
            for assistant in assistant_coaches:
                if assistant.coach_id == head.pair_id and assistant.pair_id == head.coach_id:
                    team_name = f"{head.full_name.split()[-1]}/{assistant.full_name.split()[-1]}"
                    teams.append(Team(
                        team_id=f"{head.coach_id}_{assistant.coach_id}",
                        name=team_name,
                        head_coach=head,
                        assistant_coach=assistant
                    ))
                    used_heads.add(head.coach_id)
                    used_assistants.add(assistant.coach_id)
                    break
    unpaired_heads = [h for h in head_coaches if h.coach_id not in used_heads]
    available_assistants = [a for a in assistant_coaches if a.coach_id not in used_assistants]
    random.shuffle(available_assistants)
    for head in unpaired_heads:
        assistant = None
        if available_assistants:
            if not head.associated_player_id:
                for i, a in enumerate(available_assistants):
                    if a.associated_player_id:
                        assistant = available_assistants.pop(i)
                        break
            if not assistant and head.associated_player_id:
                for i, a in enumerate(available_assistants):
                    if not a.associated_player_id:
                        assistant = available_assistants.pop(i)
                        break
            if not assistant:
                assistant = available_assistants.pop(0)
        if assistant:
            team_name = f"{head.full_name.split()[-1]}/{assistant.full_name.split()[-1]}"
        else:
            team_name = f"{head.full_name.split()[-1]}"
        teams.append(Team(
            team_id=f"{head.coach_id}_{assistant.coach_id if assistant else 'solo'}",
            name=team_name,
            head_coach=head,
            assistant_coach=assistant
        ))
    return teams

def add_player_to_team(player: Player, team: Team):
    team.players.append(player)
    if player.sponsor_id:
        team.sponsor_id = player.sponsor_id
    if hasattr(player, 'skill_score') and player.skill_score is not None:
        team.total_score += player.skill_score

def assign_coach_associated_players(teams: List[Team], players: Dict[str, Player], assigned: set) -> None:
    for team in teams:
        for coach in [team.head_coach, team.assistant_coach]:
            if coach and coach.associated_player_id:
                player = players.get(coach.associated_player_id)
                if player and player.player_id not in assigned:
                    add_player_to_team(player, team)
                    assigned.add(player.player_id)

def fill_teams_to_minimum(teams: List[Team], unassigned: List[Player]) -> None:
    for team in teams:
        while len(team.players) < MIN_TEAM_SIZE and unassigned:
            idx = random.randint(0, len(unassigned) - 1)
            player = unassigned.pop(idx)
            add_player_to_team(player, team)

def assign_remaining_players_by_skill(teams: List[Team], unassigned: List[Player]) -> None:
    unassigned.sort(key=lambda p: getattr(p, 'skill_score', 0), reverse=True)
    for player in unassigned:
        best_team = find_best_team_for_player(player, teams)
        add_player_to_team(player, best_team)

def find_best_team_for_player(player: Player, teams: List[Team]) -> Team:
    # Assign to team with lowest total_score, then fewest players, then random
    best = min(teams, key=lambda t: (t.total_score, len(t.players), random.random()))
    return best

def assign_sibling_groups_to_teams(teams: List[Team], players: Dict[str, Player], assigned: set):
    """
    Assign sibling groups to teams, ensuring all siblings are placed together.
    Updates the assigned set with player_ids that have been assigned.
    """
    # Identify family groups (siblings)
    family_groups = {}
    for p in players.values():
        key = (p.parent_name, p.street_address)
        if p.siblings:
            if key not in family_groups:
                family_groups[key] = set()
            family_groups[key].add(p.player_id)

    # Remove duplicate and single-member groups
    sibling_groups = [list(group) for group in family_groups.values() if len(group) > 1]

    # Assign sibling groups to teams first
    for group in sibling_groups:
        group_players = [players[pid] for pid in group if pid not in assigned]
        if not group_players:
            continue
        # Find best team for the whole group
        best_team = find_best_team_for_player(group_players[0], teams)
        for player in group_players:
            add_player_to_team(player, best_team)
            assigned.add(player.player_id)

def assign_players_to_teams(teams: List[Team], players: Dict[str, Player], team_size: int):
    assigned = set()
    assign_coach_associated_players(teams, players, assigned)
    assign_sibling_groups_to_teams(teams, players, assigned)
    # Continue with normal assignment
    unassigned = [p for p in players.values() if p.player_id not in assigned]
    fill_teams_to_minimum(teams, unassigned)
    assign_remaining_players_by_skill(teams, unassigned)

# --- output.py ---
def export_team_assignments(teams: List[Team], filename: str = "team_assignments.csv"):
    with open(filename, mode="w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "TeamName", "VolunteerID", "VolunteerTypeID", "Team Personnel Name", "Team Personnel Role", "PlayerID", "Player Name", 
        ])
        for team in teams:
            for coach in [team.head_coach] + ([team.assistant_coach] if team.assistant_coach else []):
                writer.writerow([
                    team.name,
                    coach.coach_id,
                    coach.volunteer_type_id,
                    coach.full_name,
                    coach.role,
                    "",
                    ""
                ])
            for player in team.players:
                writer.writerow([
                    team.name,
                    "",
                    "",
                    "",
                    "",
                    player.player_id,
                    player.name,
                ])

def export_team_summary(teams: List[Team], filename: str = "team_summary.csv"):
    with open(filename, mode="w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Team Name", "Number of Players", "Total Skill Score", "Sponsor ID"])
        for team in teams:
            writer.writerow([
                team.name,
                len(team.players),
                round(team.total_score, 3),
                team.sponsor_id or ""
            ])
    scores = [team.total_score for team in teams]
    if len(scores) > 1:
        print("Standard deviation of total skill scores:", round(statistics.stdev(scores), 3))
    else:
        print("Standard deviation of total skill scores: N/A (only one team)")

def export_debug_players_csv(teams: List[Team], filename: str = "debug_players.csv"):
    with open(filename, mode="w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "PlayerID", "Player Name", "DOB", "Age", "Experience", "Uniform Size", "Evaluation Score", "Sponsor ID", "Skill Score", "Team Name"
        ])
        for team in teams:
            for player in team.players:
                skill_score = getattr(player, "skill_score", "")
                writer.writerow([
                    player.player_id,
                    player.name,
                    player.dob,
                    player.age,
                    player.experience,
                    player.uniform_size,
                    player.evaluation_score,
                    player.sponsor_id or "",
                    skill_score,
                    team.name
                ])

# --- cli.py ---
def parse_args():
    parser = argparse.ArgumentParser(description="Assign balanced youth soccer teams.")
    parser.add_argument("--players", required=True, help="Path to players.csv")
    parser.add_argument("--coaches", required=True, help="Path to coaches.csv")
    parser.add_argument("--team-size", type=int, help="Target team size")
    parser.add_argument("--debug", action="store_true", help="Output debug CSV of all players with skill scores")
    return parser.parse_args()

def main():
    args = parse_args()

    # Create pools of players and coaches
    player_pool = parse_players_csv(args.players)
    head_coaches, assistant_coaches = parse_coaches_csv(args.coaches)
    # Create initial teams with coaches, respecting coach pairs as present, but randomizing unpaired coaches
    teams = seed_teams_with_coaches(head_coaches, assistant_coaches)

    # Build normalization context and score all players
    normalization_context = build_normalization_context(list(player_pool.values()))
    for player in player_pool.values():
        player.skill_score = calculate_player_skill_score(player, normalization_context)
    assign_players_to_teams(teams, player_pool, args.team_size)
    
    export_team_assignments(teams)
    export_team_summary(teams)
    if args.debug:
        export_debug_players_csv(teams)

if __name__ == "__main__":
    main()

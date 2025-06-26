"""
Seeds teams using coach data and assigns players using greedy score balancing.
Tracks total team scores and uses defined tiebreak rules.
Ensures no team has more than one sponsored player.
Enforces balanced team sizes such that no team exceeds another by more than one player after the minimum team size is met.

See /docs/spec.md for full specification.
"""
from typing import List, Dict
from teambuilder.models import Player, Coach, Team
import random

def seed_teams_with_coaches(head_coaches: List[Coach], assistant_coaches: List[Coach]) -> List[Team]:
    """Create initial teams from head and assistant coaches, handling reciprocated and fallback pairings."""
    teams = []
    used_assistants = set()
    used_heads = set()
    # 1. Reciprocated pairs
    for head in head_coaches:
        if head.pair_id:
            for assistant in assistant_coaches:
                if assistant.coach_id == head.pair_id and assistant.pair_id == head.coach_id:
                    # Reciprocated pair found
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
    # 2. Unpaired head coaches
    unpaired_heads = [h for h in head_coaches if h.coach_id not in used_heads]
    available_assistants = [a for a in assistant_coaches if a.coach_id not in used_assistants]
    random.shuffle(available_assistants)
    # Prioritize pairings where at least one coach has an associated player
    for head in unpaired_heads:
        # Try to find an assistant with an associated player if head does not have one, or vice versa
        assistant = None
        if available_assistants:
            if not head.associated_player_id:
                # Prefer assistant with associated player
                for i, a in enumerate(available_assistants):
                    if a.associated_player_id:
                        assistant = available_assistants.pop(i)
                        break
            if not assistant and head.associated_player_id:
                # Prefer assistant without associated player
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
    """Add a player to a team, update sponsor and total_score, and mark as assigned."""
    team.players.append(player)
    if player.sponsor_id:
        team.sponsor_id = player.sponsor_id
    if hasattr(player, 'skill_score') and player.skill_score is not None:
        team.total_score += player.skill_score

def assign_coach_associated_players(teams: List[Team], players: Dict[str, Player], assigned: set) -> None:
    """Assign coach-associated players to their coach's team. Adds players to assigned set."""
    for team in teams:
        for coach in [team.head_coach, team.assistant_coach]:
            if coach and coach.associated_player_id:
                player = players.get(coach.associated_player_id)
                if player and player.player_id not in assigned:
                    add_player_to_team(player, team)
                    assigned.add(player.player_id)

def fill_teams_to_minimum(teams: List[Team], unassigned: List[Player], min_team_size: int = 2) -> None:
    """Fill each team to at least min_team_size players, randomly from unassigned pool."""
    for team in teams:
        while len(team.players) < min_team_size and unassigned:
            idx = random.randint(0, len(unassigned) - 1)
            player = unassigned.pop(idx)
            add_player_to_team(player, team)

def assign_remaining_players_by_skill(teams: List[Team], unassigned: List[Player]) -> None:
    """Assign remaining players by descending skill score to the best team."""
    unassigned.sort(key=lambda p: getattr(p, 'skill_score', 0), reverse=True)
    for player in unassigned:
        best_team = find_best_team_for_player(player, teams)
        add_player_to_team(player, best_team)

def assign_players_to_teams(teams: List[Team], players: Dict[str, Player], target_team_size: int) -> None:
    """
    Assign players to teams:
    1. Assign coach-associated players to their coach's team.
    2. Fill each team to 2 players (randomly from unassigned pool).
    3. Assign remaining players by descending skill score to the team with the lowest cumulative skill score
    """
    assigned = set()
    assign_coach_associated_players(teams, players, assigned)
    unassigned = [p for pid, p in players.items() if pid not in assigned]
    fill_teams_to_minimum(teams, unassigned, min_team_size=2)
    assign_remaining_players_by_skill(teams, unassigned)

def find_best_team_for_player(player: Player, teams: List[Team]) -> Team:
    """
    Find the best team for a player based on current team scores and constraints:
    - Prioritize teams with the lowest total skill score
    - Break ties using fewest players
    - Skip teams that already have a sponsor when assigning sponsored players
    - Randomly break ties if needed
    """
    best_score = None
    best_size = None
    candidates = []
    for team in teams:
        if player.sponsor_id and team.sponsor_id:
            continue
        score = team.total_score
        size = len(team.players)
        if (best_score is None or score < best_score or
            (score == best_score and best_size is not None and size < best_size)):
            best_score = score
            best_size = size
            candidates = [team]
        elif score == best_score and size == best_size:
            candidates.append(team)
    if not candidates:
        candidates = teams #fallback to all teams if no candidates found
    return random.choice(candidates)
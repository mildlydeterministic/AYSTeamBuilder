"""
Exports final team assignments to CSV in the current working directory.
Follows the format of TeamImportSampleFile.csv.
Outputs rows for both players and coaches, tracking VolunteerTypeID for coaches only.
Includes a summary of team compositions and prints standard deviation of total skill scores.

See /docs/spec.md for full specification.
"""
import csv
from typing import List
from .models import Team, Player
import statistics

def export_team_assignments(teams: List[Team], filename: str = "team_assignments.csv"):
    """Export team assignments to CSV. Each row is a player or coach assigned to a team."""
    with open(filename, mode="w", newline="") as f:
        writer = csv.writer(f)
        # Header
        writer.writerow([
            "TeamName", "VolunteerID", "VolunteerTypeID", "Team Personnel Name", "Team Personnel Role", "PlayerID", "Player Name"
        ])
        for team in teams:
            # Coaches
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
            # Players
            for player in team.players:
                writer.writerow([
                    team.name,
                    "",
                    "",
                    "",
                    "",
                    player.player_id,
                    player.name
                ])

def export_team_summary(teams: List[Team], filename: str = "team_summary.csv"):
    """Export team summary (one row per team) to CSV."""
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
    # Print standard deviation of total skill scores
    scores = [team.total_score for team in teams]
    if len(scores) > 1:
        print("Standard deviation of total skill scores:", round(statistics.stdev(scores), 3))
    else:
        print("Standard deviation of total skill scores: N/A (only one team)")

def export_debug_players_csv(teams: List[Team], filename: str = "debug_players.csv"):
    """Export all players with their calculated skill score and team name for debugging."""
    with open(filename, mode="w", newline="") as f:
        writer = csv.writer(f)
        # Header: all Player fields, skill_score, team_name
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

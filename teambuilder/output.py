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

def export_team_assignments(teams: List[Team], filename: str = "team_assignments.csv"):
    """Export team assignments to CSV. Each row is a player or coach assigned to a team."""
    # ...stub...
    pass

def export_team_summary(teams: List[Team], filename: str = "team_summary.csv"):
    """Export team summary (one row per team) to CSV."""
    # ...stub...
    pass

def export_debug_players_csv(teams: List[Team], filename: str = "debug_players.csv"):
    """Export all players with their calculated skill score and team name for debugging."""
    # ...stub...
    pass

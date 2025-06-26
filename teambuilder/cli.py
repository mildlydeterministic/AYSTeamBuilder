"""
Parses command-line arguments and launches team building process.

See /docs/spec.md for full specification.
"""
import argparse
from .load_data import parse_players_csv, parse_coaches_csv
from .scoring import build_normalization_context, calculate_player_skill_score
from .team_builder import seed_teams_with_coaches, assign_players_to_teams
from .output import export_team_assignments, export_team_summary, export_debug_players_csv


def parse_args():
    """Parse command-line arguments for players.csv, coaches.csv, and team size."""
    parser = argparse.ArgumentParser(description="Assign balanced youth soccer teams.")
    parser.add_argument("--players", required=True, help="Path to players.csv")
    parser.add_argument("--coaches", required=True, help="Path to coaches.csv")
    parser.add_argument("--team-size", type=int, required=True, help="Target team size")
    parser.add_argument("--debug", action="store_true", help="Output debug CSV of all players with skill scores")
    return parser.parse_args()


def main():
    """Main entrypoint for CLI. Loads data, builds teams, and writes outputs."""
    args = parse_args()

    # Load players and coaches
    player_pool = parse_players_csv(args.players)  # Dict[str, Player]
    head_coaches, assistant_coaches = parse_coaches_csv(args.coaches)

    # Build normalization context and score all players
    normalization_context = build_normalization_context(list(player_pool.values()))
    for player in player_pool.values():
        player.skill_score = calculate_player_skill_score(player, normalization_context)

    # Seed teams with coaches
    teams = seed_teams_with_coaches(head_coaches, assistant_coaches)

    # Assign players to teams
    assign_players_to_teams(teams, player_pool, args.team_size)

    # Export outputs
    export_team_assignments(teams)
    export_team_summary(teams)
    if args.debug:
        export_debug_players_csv(teams)

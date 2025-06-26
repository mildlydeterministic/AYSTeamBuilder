"""
Seeds teams using coach data and assigns players using greedy score balancing.
Tracks total team scores and uses defined tiebreak rules.
Ensures no team has more than one sponsored player.
Enforces balanced team sizes such that no team exceeds another by more than one player after the minimum team size is met.

See /docs/spec.md for full specification.
"""
from typing import List
from .models import Player, Coach, Team

def seed_teams_with_coaches(head_coaches: List[Coach], assistant_coaches: List[Coach]) -> List[Team]:
    """Create initial teams from head and assistant coaches, handling reciprocated and fallback pairings."""
    # ...stub...
    pass

def assign_players_to_teams(teams: List[Team], players: Dict[str, Player], target_team_size: int) -> None:
    """Assign players to teams using greedy score balancing and all constraints from the spec."""
    # ...stub...
    pass

def find_best_team_for_player(player: Player, teams: List[Team]) -> Team:
    """Find the best team for a player based on current team scores and constraints."""
    # ...stub...
    pass
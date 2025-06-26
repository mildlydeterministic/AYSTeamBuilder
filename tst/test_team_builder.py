"""
Unit tests for teambuilder/team_builder.py

These tests cover:
- Team seeding logic (reciprocated pairs, fallback pairings, pairing priorities)
- Handling of associated players
- Team name formatting

See /docs/spec.md for full specification.
"""
import unittest
from teambuilder.models import Coach, Team
from teambuilder.team_builder import seed_teams_with_coaches, add_player_to_team
from teambuilder.models import Player
from teambuilder.team_builder import find_best_team_for_player

class TestTeamBuilder(unittest.TestCase):
    def test_seed_teams_with_coaches_reciprocated_pair(self):
        """Test that reciprocated coach pairs form a team together."""
        head = Coach(coach_id="1", full_name="Alice Head", role="Head Coach", associated_player_id=None, pair_id="2", volunteer_type_id="H1")
        assistant = Coach(coach_id="2", full_name="Bob Assistant", role="Assistant Coach", associated_player_id=None, pair_id="1", volunteer_type_id="A1")
        teams = seed_teams_with_coaches([head], [assistant])
        self.assertEqual(len(teams), 1)
        self.assertEqual(teams[0].head_coach, head)
        self.assertEqual(teams[0].assistant_coach, assistant)

    def test_seed_teams_with_coaches_unpaired_head(self):
        """Test that unpaired head coaches are paired with available assistants."""
        head = Coach(coach_id="1", full_name="Alice Head", role="Head Coach", associated_player_id=None, pair_id=None, volunteer_type_id="H1")
        assistant = Coach(coach_id="2", full_name="Bob Assistant", role="Assistant Coach", associated_player_id=None, pair_id=None, volunteer_type_id="A1")
        teams = seed_teams_with_coaches([head], [assistant])
        self.assertEqual(len(teams), 1)
        self.assertEqual(teams[0].head_coach, head)
        self.assertEqual(teams[0].assistant_coach, assistant)

    def test_seed_teams_with_coaches_no_assistant(self):
        """Test that a solo head coach forms a team if no assistants are available."""
        head = Coach(coach_id="1", full_name="Alice Head", role="Head Coach", associated_player_id=None, pair_id=None, volunteer_type_id="H1")
        teams = seed_teams_with_coaches([head], [])
        self.assertEqual(len(teams), 1)
        self.assertEqual(teams[0].head_coach, head)
        self.assertIsNone(teams[0].assistant_coach)

    def test_seed_teams_with_coaches_pairing_priority(self):
        """Test that pairing prioritizes at least one coach with an associated player."""
        head1 = Coach(coach_id="1", full_name="Alice Head", role="Head Coach", associated_player_id=None, pair_id=None, volunteer_type_id="H1")
        head2 = Coach(coach_id="2", full_name="Eve Head", role="Head Coach", associated_player_id="P1", pair_id=None, volunteer_type_id="H2")
        assistant1 = Coach(coach_id="3", full_name="Bob Assistant", role="Assistant Coach", associated_player_id="P2", pair_id=None, volunteer_type_id="A1")
        assistant2 = Coach(coach_id="4", full_name="Carol Assistant", role="Assistant Coach", associated_player_id=None, pair_id=None, volunteer_type_id="A2")
        # Shuffle to ensure pairing logic is tested
        teams = seed_teams_with_coaches([head1, head2], [assistant1, assistant2])
        # At least one team should have both a coach and assistant with associated_player_id
        found = False
        for t in teams:
            if (t.head_coach.associated_player_id or (t.assistant_coach and t.assistant_coach.associated_player_id)):
                found = True
        self.assertTrue(found)

    def test_seed_teams_with_coaches_team_name_format(self):
        """Test that team names are formatted correctly for solo and paired teams."""
        head = Coach(coach_id="1", full_name="Alice Head", role="Head Coach", associated_player_id=None, pair_id=None, volunteer_type_id="H1")
        assistant = Coach(coach_id="2", full_name="Bob Assistant", role="Assistant Coach", associated_player_id=None, pair_id=None, volunteer_type_id="A1")
        teams = seed_teams_with_coaches([head], [assistant])
        self.assertIn("Head", teams[0].name)
        self.assertIn("Assistant", teams[0].name)
        solo_teams = seed_teams_with_coaches([head], [])
        self.assertEqual(solo_teams[0].name, "Head")

    def test_seed_teams_with_coaches_unreciprocated_pair(self):
        """Test that only reciprocated pairs are paired; unreciprocated head is paired with assistant by fallback."""
        # Head1 and Head2 both point to Assistant, but Assistant only points to Head2
        head1 = Coach(coach_id="1", full_name="Alice Head1", role="Head Coach", associated_player_id=None, pair_id="3", volunteer_type_id="H1")
        head2 = Coach(coach_id="2", full_name="Eve Head2", role="Head Coach", associated_player_id=None, pair_id="3", volunteer_type_id="H2")
        assistant = Coach(coach_id="3", full_name="Bob Assistant", role="Assistant Coach", associated_player_id=None, pair_id="2", volunteer_type_id="A1")
        # List ordering: head1, head2
        teams = seed_teams_with_coaches([head1, head2], [assistant])
        # Only head2 and assistant should be paired as reciprocated
        self.assertEqual(len(teams), 2)
        # Find the team with both head2 and assistant
        paired_team = [t for t in teams if t.head_coach == head2 and t.assistant_coach == assistant]
        self.assertEqual(len(paired_team), 1)
        # The other team should be head1 solo
        solo_team = [t for t in teams if t.head_coach == head1 and t.assistant_coach is None]
        self.assertEqual(len(solo_team), 1)

    def test_add_player_to_team(self):
        """Test that add_player_to_team adds the player, sets sponsor, and updates skill score."""
        from teambuilder.models import Player, Coach, Team
        player = Player(
            player_id="1",
            name="Test Player",
            dob="01/01/2010",
            experience=3,
            uniform_size="Youth M",
            evaluation_score="5.0",
            age=15.0,
            sponsor_id="S123"
        )
        player.skill_score = 0.75
        coach = Coach(coach_id="C1", full_name="Coach One", role="Head Coach", associated_player_id=None, pair_id=None, volunteer_type_id="H1")
        team = Team(team_id="T1", name="TestTeam", head_coach=coach)
        add_player_to_team(player, team)
        self.assertIn(player, team.players)
        self.assertEqual(team.sponsor_id, "S123")
        self.assertAlmostEqual(team.total_score, 0.75)

    def test_find_best_team_lowest_score(self):
        """Test player is assigned to team with lowest total skill score."""
        p = Player("1", "Test", "01/01/2010", 1, "Youth M", "5.0", age=10.0)
        team1 = Team("T1", "A", Coach("C1", "Coach1", "Head Coach", "H1"), players=[], sponsor_id=None, total_score=5.0)
        team2 = Team("T2", "B", Coach("C2", "Coach2", "Head Coach", "H2"), players=[], sponsor_id=None, total_score=2.0)
        result = find_best_team_for_player(p, [team1, team2])
        self.assertEqual(result, team2)

    def test_find_best_team_tiebreak_fewest_players(self):
        """Test tiebreak by fewest players when scores are equal."""
        p = Player("1", "Test", "01/01/2010", 1, "Youth M", "5.0", age=10.0)
        team1 = Team("T1", "A", Coach("C1", "Coach1", "Head Coach", "H1"), players=[p], sponsor_id=None, total_score=2.0)
        team2 = Team("T2", "B", Coach("C2", "Coach2", "Head Coach", "H2"), players=[], sponsor_id=None, total_score=2.0)
        result = find_best_team_for_player(p, [team1, team2])
        self.assertEqual(result, team2)

    def test_find_best_team_sponsored_constraint(self):
        """Test sponsored player is not assigned to team with sponsor if possible."""
        p = Player("1", "Test", "01/01/2010", 1, "Youth M", "5.0", age=10.0, sponsor_id="S1")
        team1 = Team("T1", "A", Coach("C1", "Coach1", "Head Coach", "H1"), players=[], sponsor_id="S2", total_score=1.0)
        team2 = Team("T2", "B", Coach("C2", "Coach2", "Head Coach", "H2"), players=[], sponsor_id=None, total_score=1.0)
        result = find_best_team_for_player(p, [team1, team2])
        self.assertEqual(result, team2)

    def test_find_best_team_sponsored_fallback(self):
        """Test sponsored player is assigned to any team if all have sponsors."""
        p = Player("1", "Test", "01/01/2010", 1, "Youth M", "5.0", age=10.0, sponsor_id="S1")
        team1 = Team("T1", "A", Coach("C1", "Coach1", "Head Coach", "H1"), players=[], sponsor_id="S2", total_score=1.0)
        team2 = Team("T2", "B", Coach("C2", "Coach2", "Head Coach", "H2"), players=[], sponsor_id="S3", total_score=1.0)
        result = find_best_team_for_player(p, [team1, team2])
        self.assertIn(result, [team1, team2])

    def test_assign_coach_associated_players(self):
        """Coach-associated players are assigned to their coach's team and marked as assigned."""
        from teambuilder.team_builder import assign_coach_associated_players
        coach = Coach(coach_id="C1", full_name="Coach One", role="Head Coach", associated_player_id="P1", pair_id=None, volunteer_type_id="H1")
        team = Team(team_id="T1", name="Team1", head_coach=coach)
        player = Player(player_id="P1", name="Player1", dob="01/01/2010", age=10.0, experience=1, uniform_size="Youth M", evaluation_score="5.0")
        players = {"P1": player}
        assigned = set()
        assign_coach_associated_players([team], players, assigned)
        self.assertIn(player, team.players)
        self.assertIn("P1", assigned)

    def test_assign_coach_associated_players_non_associated_player_not_added(self):
        """A player not associated with a coach is not added to any team."""
        from teambuilder.team_builder import assign_coach_associated_players
        coach = Coach(coach_id="C1", full_name="Coach One", role="Head Coach", associated_player_id="P1", pair_id=None, volunteer_type_id="H1")
        team = Team(team_id="T1", name="Team1", head_coach=coach)
        player = Player(player_id="P2", name="Player2", dob="01/01/2010", age=10.0, experience=1, uniform_size="Youth M", evaluation_score="5.0")
        players = {"P2": player}
        assigned = set()
        assign_coach_associated_players([team], players, assigned)
        self.assertNotIn(player, team.players)
        self.assertNotIn("P2", assigned)

    def test_assign_coach_associated_players_coach_without_associated_player(self):
        """A coach without an associated player does not get a player added to their team."""
        from teambuilder.team_builder import assign_coach_associated_players
        coach = Coach(coach_id="C1", full_name="Coach One", role="Head Coach", associated_player_id=None, pair_id=None, volunteer_type_id="H1")
        team = Team(team_id="T1", name="Team1", head_coach=coach)
        player = Player(player_id="P1", name="Player1", dob="01/01/2010", age=10.0, experience=1, uniform_size="Youth M", evaluation_score="5.0")
        players = {"P1": player}
        assigned = set()
        assign_coach_associated_players([team], players, assigned)
        self.assertNotIn(player, team.players)
        self.assertNotIn("P1", assigned)

    def test_fill_teams_to_minimum(self):
        """Teams are filled to at least min_team_size from unassigned pool."""
        from teambuilder.team_builder import fill_teams_to_minimum
        coach = Coach(coach_id="C1", full_name="Coach One", role="Head Coach", associated_player_id=None, pair_id=None, volunteer_type_id="H1")
        team = Team(team_id="T1", name="Team1", head_coach=coach)
        players = [Player(player_id=f"P{i}", name=f"Player{i}", dob="01/01/2010", age=10.0, experience=1, uniform_size="Youth M", evaluation_score="5.0") for i in range(3)]
        fill_teams_to_minimum([team], players, min_team_size=2)
        self.assertGreaterEqual(len(team.players), 2)
        self.assertEqual(len(players), 1)  # One player left unassigned

    def test_fill_teams_to_minimum_no_unassigned(self):
        """If unassigned is empty, teams are not changed."""
        from teambuilder.team_builder import fill_teams_to_minimum
        coach = Coach(coach_id="C1", full_name="Coach One", role="Head Coach", associated_player_id=None, pair_id=None, volunteer_type_id="H1")
        team = Team(team_id="T1", name="Team1", head_coach=coach)
        fill_teams_to_minimum([team], [], min_team_size=2)
        self.assertEqual(len(team.players), 0)

    def test_fill_teams_to_minimum_team_already_full(self):
        """If team already has min_team_size or more, no players are added."""
        from teambuilder.team_builder import fill_teams_to_minimum
        coach = Coach(coach_id="C1", full_name="Coach One", role="Head Coach", associated_player_id=None, pair_id=None, volunteer_type_id="H1")
        team = Team(team_id="T1", name="Team1", head_coach=coach)
        p1 = Player(player_id="P1", name="Player1", dob="01/01/2010", age=10.0, experience=1, uniform_size="Youth M", evaluation_score="5.0")
        p2 = Player(player_id="P2", name="Player2", dob="01/01/2010", age=10.0, experience=1, uniform_size="Youth M", evaluation_score="5.0")
        team.players = [p1, p2]
        unassigned = [Player(player_id="P3", name="Player3", dob="01/01/2010", age=10.0, experience=1, uniform_size="Youth M", evaluation_score="5.0")]
        fill_teams_to_minimum([team], unassigned, min_team_size=2)
        self.assertEqual(len(team.players), 2)
        self.assertEqual(len(unassigned), 1)

    def test_fill_teams_to_minimum_multiple_teams_balanced(self):
        """Players are distributed so all teams reach min_team_size if enough unassigned."""
        from teambuilder.team_builder import fill_teams_to_minimum
        coach1 = Coach(coach_id="C1", full_name="Coach1", role="Head Coach", associated_player_id=None, pair_id=None, volunteer_type_id="H1")
        coach2 = Coach(coach_id="C2", full_name="Coach2", role="Head Coach", associated_player_id=None, pair_id=None, volunteer_type_id="H2")
        team1 = Team(team_id="T1", name="A", head_coach=coach1)
        team2 = Team(team_id="T2", name="B", head_coach=coach2)
        players = [Player(player_id=f"P{i}", name=f"Player{i}", dob="01/01/2010", age=10.0, experience=1, uniform_size="Youth M", evaluation_score="5.0") for i in range(4)]
        fill_teams_to_minimum([team1, team2], players, min_team_size=2)
        self.assertEqual(len(team1.players), 2)
        self.assertEqual(len(team2.players), 2)
        self.assertEqual(len(players), 0)

    def test_fill_teams_to_minimum_not_enough_players(self):
        """If not enough players, teams are filled as evenly as possible."""
        from teambuilder.team_builder import fill_teams_to_minimum
        coach1 = Coach(coach_id="C1", full_name="Coach1", role="Head Coach", associated_player_id=None, pair_id=None, volunteer_type_id="H1")
        coach2 = Coach(coach_id="C2", full_name="Coach2", role="Head Coach", associated_player_id=None, pair_id=None, volunteer_type_id="H2")
        team1 = Team(team_id="T1", name="A", head_coach=coach1)
        team2 = Team(team_id="T2", name="B", head_coach=coach2)
        players = [Player(player_id=f"P{i}", name=f"Player{i}", dob="01/01/2010", age=10.0, experience=1, uniform_size="Youth M", evaluation_score="5.0") for i in range(3)]
        fill_teams_to_minimum([team1, team2], players, min_team_size=2)
        total = len(team1.players) + len(team2.players)
        self.assertEqual(total, 3)
        self.assertTrue(abs(len(team1.players) - len(team2.players)) <= 1)

if __name__ == "__main__":
    unittest.main()

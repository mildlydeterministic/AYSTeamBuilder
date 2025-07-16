"""
Unified tests for teambuilder_single.py
Covers: load_data, scoring, and team_builder logic.
"""
import unittest
import datetime
import io
import csv
import teambuilder_single as tb

class TestTeamBuilderSingle(unittest.TestCase):
    # --- Load Data Tests ---
    def test_compute_age_from_dob_valid_standard(self):
        dob = "01/15/2010"
        ref_date = datetime.date(2024, 1, 15)
        self.assertEqual(tb.compute_age_from_dob(dob, ref_date), 14.0)

    def test_compute_age_from_dob_partial_year(self):
        dob = "12/01/2010"
        ref_date = datetime.date(2025, 6, 1)
        self.assertEqual(tb.compute_age_from_dob(dob, ref_date), 14.5)

    def test_compute_age_from_dob_today(self):
        today = datetime.date.today()
        dob = today.strftime("%m/%d/%Y")
        self.assertEqual(tb.compute_age_from_dob(dob, today), 0.0)

    def test_compute_age_from_dob_invalid(self):
        self.assertEqual(tb.compute_age_from_dob("not-a-date"), 0.0)

    def test_compute_age_from_dob_empty(self):
        self.assertEqual(tb.compute_age_from_dob(""), 0.0)

    def test_parse_coaches_csv_reader_basic(self):
        csv_content = """VolunteerID,Team Personnel Name,Team Personnel Role\n1,Coach Head,Head Coach\n2,Coach Assistant,Assistant Coach\n"""
        reader = csv.DictReader(io.StringIO(csv_content))
        heads, assistants = tb.parse_coaches_csv_reader(reader)
        self.assertEqual(len(heads), 1)
        self.assertEqual(len(assistants), 1)
        self.assertEqual(heads[0].full_name, "Coach Head")
        self.assertEqual(assistants[0].full_name, "Coach Assistant")

    def test_parse_coaches_csv_reader_associated_player(self):
        csv_content = """VolunteerID,Team Personnel Name,Team Personnel Role,associatedPlayers\n1,Coach Head,Head Coach,123\n2,Coach Assistant,Assistant Coach,No Answer\n"""
        reader = csv.DictReader(io.StringIO(csv_content))
        heads, assistants = tb.parse_coaches_csv_reader(reader)
        self.assertEqual(heads[0].associated_player_id, "123")
        self.assertIsNone(assistants[0].associated_player_id)

    def test_parse_coaches_csv_reader_coach_pair(self):
        csv_content = """VolunteerID,Team Personnel Name,Team Personnel Role,Coach Pair\n1,Coach Head,Head Coach,2\n2,Coach Assistant,Assistant Coach,1\n"""
        reader = csv.DictReader(io.StringIO(csv_content))
        heads, assistants = tb.parse_coaches_csv_reader(reader)
        self.assertEqual(heads[0].pair_id, "2")
        self.assertEqual(assistants[0].pair_id, "1")

    def test_parse_coaches_csv_reader_volunteer_type(self):
        csv_content = """VolunteerID,Team Personnel Name,Team Personnel Role,VolunteerTypeID\n1,Coach Head,Head Coach,VT1\n2,Coach Assistant,Assistant Coach,\n"""
        reader = csv.DictReader(io.StringIO(csv_content))
        heads, assistants = tb.parse_coaches_csv_reader(reader)
        self.assertEqual(heads[0].volunteer_type_id, "VT1")
        self.assertEqual(assistants[0].volunteer_type_id, "")

    # --- Scoring Tests ---
    def test_normal_context_basic(self):
        players = [
            tb.Player("1", "A", "01/01/2010", 2, tb.UNIFORM_SIZES[0], "5.0", age=10.0),
            tb.Player("2", "B", "01/01/2011", 3, tb.UNIFORM_SIZES[1], "7.0", age=12.0),
            tb.Player("3", "C", "01/01/2012", 1, tb.UNIFORM_SIZES[2], "6.0", age=11.0),
        ]
        ctx = tb.build_normalization_context(players)
        self.assertEqual(ctx["age"], {"min": 10.0, "max": 12.0})
        self.assertEqual(ctx["experience"], {"min": 1, "max": 3})
        self.assertEqual(ctx["uniform_size"], {"min": 0, "max": 2})
        self.assertEqual(ctx["evaluation_score"], {"min": 5.0, "max": 7.0})

    def test_normal_context_empty(self):
        ctx = tb.build_normalization_context([])
        self.assertEqual(ctx["age"], {"min": None, "max": None})
        self.assertEqual(ctx["experience"], {"min": None, "max": None})
        self.assertEqual(ctx["uniform_size"], {"min": None, "max": None})
        self.assertEqual(ctx["evaluation_score"], {"min": None, "max": None})

    # --- Team Builder Tests ---
    def test_seed_teams_with_coaches_reciprocated_pair(self):
        head = tb.Coach(coach_id="1", full_name="Alice Head", role="Head Coach", associated_player_id=None, pair_id="2", volunteer_type_id="H1")
        assistant = tb.Coach(coach_id="2", full_name="Bob Assistant", role="Assistant Coach", associated_player_id=None, pair_id="1", volunteer_type_id="A1")
        teams = tb.seed_teams_with_coaches([head], [assistant])
        self.assertEqual(len(teams), 1)
        self.assertEqual(teams[0].head_coach, head)
        self.assertEqual(teams[0].assistant_coach, assistant)

    def test_seed_teams_with_coaches_unpaired_head(self):
        head = tb.Coach(coach_id="1", full_name="Alice Head", role="Head Coach", associated_player_id=None, pair_id=None, volunteer_type_id="H1")
        assistant = tb.Coach(coach_id="2", full_name="Bob Assistant", role="Assistant Coach", associated_player_id=None, pair_id=None, volunteer_type_id="A1")
        teams = tb.seed_teams_with_coaches([head], [assistant])
        self.assertEqual(len(teams), 1)
        self.assertEqual(teams[0].head_coach, head)
        self.assertEqual(teams[0].assistant_coach, assistant)

    def test_seed_teams_with_coaches_no_assistant(self):
        head = tb.Coach(coach_id="1", full_name="Alice Head", role="Head Coach", associated_player_id=None, pair_id=None, volunteer_type_id="H1")
        teams = tb.seed_teams_with_coaches([head], [])
        self.assertEqual(len(teams), 1)
        self.assertEqual(teams[0].head_coach, head)
        self.assertIsNone(teams[0].assistant_coach)

    def test_add_player_to_team(self):
        player = tb.Player(
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
        coach = tb.Coach(coach_id="C1", full_name="Coach One", role="Head Coach", associated_player_id=None, pair_id=None, volunteer_type_id="H1")
        team = tb.Team(team_id="T1", name="Team1", head_coach=coach)
        tb.add_player_to_team(player, team)
        self.assertIn(player, team.players)
        self.assertEqual(team.sponsor_id, "S123")
        self.assertEqual(team.total_score, 0.75)

if __name__ == "__main__":
    unittest.main()

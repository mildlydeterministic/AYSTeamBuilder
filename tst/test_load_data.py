"""
Unit tests for teambuilder/load_data.py

These tests cover:
- Parsing players.csv into Player objects
- Parsing coaches.csv into Coach objects and correct pool assignment
- Handling of missing/invalid data
- Age calculation from DOB

See /docs/spec.md for full specification.
"""
import unittest
import datetime
import io
import csv
from teambuilder import load_data
from teambuilder.load_data import compute_age_from_dob, parse_coaches_csv_reader

class TestLoadData(unittest.TestCase):

    def test_compute_age_from_dob_valid_standard(self):
        """Test valid DOB, standard case."""
        dob = "01/15/2010"
        ref_date = datetime.date(2024, 1, 15)
        self.assertEqual(compute_age_from_dob(dob, ref_date), 14.0)

    def test_compute_age_from_dob_partial_year(self):
        """Test DOB with partial year (decimal precision)."""
        dob = "12/01/2010"
        ref_date = datetime.date(2025, 6, 1)
        self.assertEqual(compute_age_from_dob(dob, ref_date), 14.5)

    def test_compute_age_from_dob_today(self):
        """Test DOB is today."""
        today = datetime.date.today()
        dob = today.strftime("%m/%d/%Y")
        self.assertEqual(compute_age_from_dob(dob, today), 0.0)

    def test_compute_age_from_dob_invalid(self):
        """Test invalid DOB format."""
        self.assertEqual(compute_age_from_dob("not-a-date"), 0.0)

    def test_compute_age_from_dob_empty(self):
        """Test empty DOB string."""
        self.assertEqual(compute_age_from_dob(""), 0.0)

    def test_parse_coaches_csv_reader_basic(self):
        """Test basic head/assistant parsing."""
        csv_content = """VolunteerID,Team Personnel Name,Team Personnel Role
1,Coach Head,Head Coach
2,Coach Assistant,Assistant Coach
"""
        reader = csv.DictReader(io.StringIO(csv_content))
        heads, assistants = parse_coaches_csv_reader(reader)
        self.assertEqual(len(heads), 1)
        self.assertEqual(len(assistants), 1)
        self.assertEqual(heads[0].full_name, "Coach Head")
        self.assertEqual(assistants[0].full_name, "Coach Assistant")

    def test_parse_coaches_csv_reader_associated_player(self):
        """Test associated player field handling."""
        csv_content = """VolunteerID,Team Personnel Name,Team Personnel Role,associatedPlayers
1,Coach Head,Head Coach,123
2,Coach Assistant,Assistant Coach,No Answer
"""
        reader = csv.DictReader(io.StringIO(csv_content))
        heads, assistants = parse_coaches_csv_reader(reader)
        self.assertEqual(heads[0].associated_player_id, "123")
        self.assertIsNone(assistants[0].associated_player_id)

    def test_parse_coaches_csv_reader_coach_pair(self):
        """Test coach pair field handling."""
        csv_content = """VolunteerID,Team Personnel Name,Team Personnel Role,Coach Pair
1,Coach Head,Head Coach,2
2,Coach Assistant,Assistant Coach,1
"""
        reader = csv.DictReader(io.StringIO(csv_content))
        heads, assistants = parse_coaches_csv_reader(reader)
        self.assertEqual(heads[0].pair_id, "2")
        self.assertEqual(assistants[0].pair_id, "1")

    def test_parse_coaches_csv_reader_volunteer_type(self):
        """Test VolunteerTypeID field handling."""
        csv_content = """VolunteerID,Team Personnel Name,Team Personnel Role,VolunteerTypeID
1,Coach Head,Head Coach,VT1
2,Coach Assistant,Assistant Coach,
"""
        reader = csv.DictReader(io.StringIO(csv_content))
        heads, assistants = parse_coaches_csv_reader(reader)
        self.assertEqual(heads[0].volunteer_type_id, "VT1")
        self.assertEqual(assistants[0].volunteer_type_id, "")

    def test_parse_coaches_csv_reader_missing_fields(self):
        """Test handling of missing/empty fields."""
        csv_content = """VolunteerID,Team Personnel Name,Team Personnel Role
1,Coach Head,Head Coach
2,Coach Assistant,Assistant Coach
"""
        reader = csv.DictReader(io.StringIO(csv_content))
        heads, assistants = parse_coaches_csv_reader(reader)
        self.assertEqual(heads[0].volunteer_type_id, "")
        self.assertIsNone(heads[0].associated_player_id)

    def test_parse_coaches_csv_reader_multiple_coaches(self):
        """Test multiple coaches of each type."""
        csv_content = """VolunteerID,Team Personnel Name,Team Personnel Role
1,Coach Head1,Head Coach
2,Coach Head2,Head Coach
3,Coach Assistant1,Assistant Coach
4,Coach Assistant2,Assistant Coach
"""
        reader = csv.DictReader(io.StringIO(csv_content))
        heads, assistants = parse_coaches_csv_reader(reader)
        self.assertEqual(len(heads), 2)
        self.assertEqual(len(assistants), 2)

    def test_parse_coaches_csv_reader_extra_columns(self):
        """Test extra/unexpected columns are ignored."""
        csv_content = """VolunteerID,Team Personnel Name,Team Personnel Role,ExtraColumn
1,Coach Head,Head Coach,foo
2,Coach Assistant,Assistant Coach,bar
"""
        reader = csv.DictReader(io.StringIO(csv_content))
        heads, assistants = parse_coaches_csv_reader(reader)
        self.assertEqual(len(heads), 1)
        self.assertEqual(len(assistants), 1)

if __name__ == "__main__":
    unittest.main()

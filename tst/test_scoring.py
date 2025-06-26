"""
Unit tests for teambuilder/scoring.py

Covers:
- build_normalization_context (min/max extraction for all fields, missing data, edge cases)
"""
import unittest
from teambuilder.models import Player, UNIFORM_SIZES
from teambuilder.scoring import build_normalization_context

class TestScoringNormalization(unittest.TestCase):
    def test_normal_context_basic(self):
        players = [
            Player("1", "A", "01/01/2010", 2, UNIFORM_SIZES[0], "5.0", age=10.0),
            Player("2", "B", "01/01/2011", 3, UNIFORM_SIZES[1], "7.0", age=12.0),
            Player("3", "C", "01/01/2012", 1, UNIFORM_SIZES[2], "6.0", age=11.0),
        ]
        ctx = build_normalization_context(players)
        self.assertEqual(ctx["age"], {"min": 10.0, "max": 12.0})
        self.assertEqual(ctx["experience"], {"min": 1, "max": 3})
        self.assertEqual(ctx["uniform_size"], {"min": 0, "max": 2})
        self.assertEqual(ctx["evaluation_score"], {"min": 5.0, "max": 7.0})

    def test_normal_context_missing_fields(self):
        # Use out-of-band values to simulate missing data
        players = [
            Player("1", "A", "01/01/2010", -1, "", "", age=None),
            Player("2", "B", "01/01/2011", -1, "", "", age=None),
        ]
        ctx = build_normalization_context(players)
        self.assertEqual(ctx["age"], {"min": None, "max": None})
        self.assertEqual(ctx["experience"], {"min": -1, "max": -1})
        self.assertEqual(ctx["uniform_size"], {"min": None, "max": None})
        self.assertEqual(ctx["evaluation_score"], {"min": None, "max": None})

    def test_normal_context_partial_missing(self):
        players = [
            Player("1", "A", "01/01/2010", -1, UNIFORM_SIZES[0], "5.0", age=10.0),
            Player("2", "B", "01/01/2011", 3, "", "bad", age=None),
        ]
        ctx = build_normalization_context(players)
        self.assertEqual(ctx["age"], {"min": 10.0, "max": 10.0})
        self.assertEqual(ctx["experience"], {"min": -1, "max": 3})
        self.assertEqual(ctx["uniform_size"], {"min": 0, "max": 0})
        self.assertEqual(ctx["evaluation_score"], {"min": 5.0, "max": 5.0})

    def test_normal_context_empty(self):
        ctx = build_normalization_context([])
        self.assertEqual(ctx["age"], {"min": None, "max": None})
        self.assertEqual(ctx["experience"], {"min": None, "max": None})
        self.assertEqual(ctx["uniform_size"], {"min": None, "max": None})
        self.assertEqual(ctx["evaluation_score"], {"min": None, "max": None})

if __name__ == "__main__":
    unittest.main()

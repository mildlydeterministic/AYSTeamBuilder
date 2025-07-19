import unittest
from src.teambuilder_single import Player, parse_players_csv_reader

class TestSiblingAssignment(unittest.TestCase):
    def setUp(self):
        # Simulate CSV rows with two sibling groups and one solo player
        self.rows = [
            {
                "PlayerID": "1",
                "Player Name": "Alice",
                "Date Of Birth": "01/01/2010",
                "Years of Experience": "2",
                "Uniform Size": "Youth M",
                "Player Evaluation Rating": "500",
                "Parent LastName": "Smith",
                "Account Street Address": "123 Main St"
            },
            {
                "PlayerID": "2",
                "Player Name": "Bob",
                "Date Of Birth": "02/02/2012",
                "Years of Experience": "1",
                "Uniform Size": "Youth S",
                "Player Evaluation Rating": "400",
                "Parent LastName": "Smith",
                "Account Street Address": "123 Main St"
            },
            {
                "PlayerID": "3",
                "Player Name": "Charlie",
                "Date Of Birth": "03/03/2011",
                "Years of Experience": "3",
                "Uniform Size": "Youth L",
                "Player Evaluation Rating": "600",
                "Parent LastName": "Jones",
                "Account Street Address": "456 Oak Ave"
            },
            {
                "PlayerID": "4",
                "Player Name": "Dana",
                "Date Of Birth": "04/04/2010",
                "Years of Experience": "2",
                "Uniform Size": "Youth M",
                "Player Evaluation Rating": "550",
                "Parent LastName": "Lee",
                "Account Street Address": "789 Pine Rd"
            },
            {
                "PlayerID": "5",
                "Player Name": "Eli",
                "Date Of Birth": "05/05/2012",
                "Years of Experience": "1",
                "Uniform Size": "Youth S",
                "Player Evaluation Rating": "450",
                "Parent LastName": "Lee",
                "Account Street Address": "789 Pine Rd"
            }
        ]

    def test_sibling_detection(self):
        players = parse_players_csv_reader(self.rows)
        # Smith family: Alice and Bob
        self.assertEqual(set(players["1"].siblings), {"2"})
        self.assertEqual(set(players["2"].siblings), {"1"})
        # Lee family: Dana and Eli
        self.assertEqual(set(players["4"].siblings), {"5"})
        self.assertEqual(set(players["5"].siblings), {"4"})
        # Jones family: Charlie (no siblings)
        self.assertEqual(players["3"].siblings, [])

    def test_no_false_positives(self):
        players = parse_players_csv_reader(self.rows)
        # Siblings only if both parent_name and street_address match
        self.assertNotIn("3", players["1"].siblings)
        self.assertNotIn("4", players["1"].siblings)
        self.assertNotIn("5", players["1"].siblings)

if __name__ == "__main__":
    unittest.main()

import unittest
from unittest.mock import patch, MagicMock
from meal_max.models.kitchen_model import Meal
from meal_max.models.battle_model import BattleModel
from meal_max.utils.random_utils import get_random

class test_battle_model(unittest.TestCase):

    def setUp(self):
        """Set up the BattleModel instance and mock combatants for testing."""
        self.battle_model = BattleModel()
        self.combatant_1 = Meal(id=1, meal="Spaghetti", cuisine="Italian", price=12.5, difficulty="MED")
        self.combatant_2 = Meal(id=2, meal="Sushi", cuisine="Japanese", price=15.0, difficulty="HIGH")

    def test_battle_with_no_combatants(self):
        """Test that battle raises an error when there are no combatants."""
        with self.assertRaises(ValueError):
            self.battle_model.battle()

    @patch('meal_max.models.battle_model.update_meal_stats')
    @patch('meal_max.utils.random_utils.get_random', return_value=0.5)
    def test_battle_with_identical_scores(self, mock_get_random, mock_update_meal_stats):
        """Test battle outcome when both combatants have identical scores."""
        self.battle_model.prep_combatant(self.combatant_1)
        self.battle_model.prep_combatant(self.combatant_2)
        self.assertIn(self.battle_model.battle(), [self.combatant_1.meal, self.combatant_2.meal])

    def test_get_battle_score_zero_price(self):
        """Test get_battle_score for a combatant with zero price."""
        zero_price_combatant = Meal(id=3, meal="Soup", cuisine="French", price=0.0, difficulty="LOW")
        score = self.battle_model.get_battle_score(zero_price_combatant)
        self.assertEqual(score, -3) 

    def test_prep_combatant_successful(self):
        """Test that a combatant is successfully added to the combatants list."""
        self.battle_model.prep_combatant(self.combatant_1)
        self.assertEqual(len(self.battle_model.get_combatants()), 1)
        self.assertEqual(self.battle_model.get_combatants()[0].meal, "Spaghetti")

    def test_prep_combatant_exceeds_limit(self):
        """Test that an error is raised when attempting to add more than two combatants."""
        self.battle_model.prep_combatant(self.combatant_1)
        self.battle_model.prep_combatant(self.combatant_2)
        new_combatant = Meal(id=3, meal="Pizza", cuisine="Italian", price=10.0, difficulty="LOW")

        with self.assertRaises(ValueError) as context:
            self.battle_model.prep_combatant(new_combatant)
        self.assertEqual(str(context.exception), "Combatant list is full, cannot add more combatants.")

    def test_clear_combatants(self):
        """Test that the clear_combatants method empties the combatants list."""
        self.battle_model.prep_combatant(self.combatant_1)
        self.battle_model.clear_combatants()
        self.assertEqual(len(self.battle_model.get_combatants()), 0)

    @patch('meal_max.models.kitchen_model.get_db_connection')  
    def test_battle_successful(self, mock_get_db_connection):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db_connection.return_value.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        
        mock_cursor.fetchone.side_effect = [
            (0,),  
            (0,)   
        ]

        self.battle_model.prep_combatant(self.combatant_1)
        self.battle_model.prep_combatant(self.combatant_2)

        with patch('meal_max.models.kitchen_model.update_meal_stats') as mock_update_meal_stats:
            mock_update_meal_stats.return_value = None
            winner = self.battle_model.battle()

        self.assertIn(winner, ['Spaghetti', 'Sushi'])

    def test_get_battle_score(self):
        """Test the calculation of the battle score for a combatant."""
        score = self.battle_model.get_battle_score(self.combatant_1)
        expected_score = (12.5 * len("Italian")) - 2  
        self.assertAlmostEqual(score, expected_score, places=2)

    @patch('meal_max.models.kitchen_model.Meal.__post_init__', lambda x: None)
    def test_get_battle_score_unexpected_difficulty(self):
        """Test get_battle_score raises KeyError with an unexpected difficulty value."""
        combatant = Meal(id=3, meal="Mystery Meal", cuisine="Mystery", price=20.0, difficulty="UNKNOWN")
        
        with self.assertRaises(KeyError):
            self.battle_model.get_battle_score(combatant)



if __name__ == '__main__':
    unittest.main()
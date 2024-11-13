import unittest
from unittest.mock import patch, MagicMock
import sqlite3
from meal_max.models.kitchen_model import Meal, create_meal, clear_meals, delete_meal, get_leaderboard, get_meal_by_id, get_meal_by_name

class test_kitchen_model(unittest.TestCase):

    def setUp(self):
        """Set up the test environment."""
        self.sample_meal = Meal(id=1, meal="Pasta", cuisine="Italian", price=10.0, difficulty="MED")

    @patch('meal_max.models.kitchen_model.get_db_connection')
    def test_create_meal_successful(self, mock_db_connection):
        """Test creating a new meal and adding it to the database."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_db_connection.return_value.__enter__.return_value = mock_conn

        create_meal("Pasta", "Italian", 10.0, "MED")

        mock_cursor.execute.assert_called_once_with(
            """INSERT INTO meals (meal, cuisine, price, difficulty) VALUES (?, ?, ?, ?)""",
            ("Pasta", "Italian", 10.0, "MED")
        )
        mock_conn.commit.assert_called_once()

    @patch('meal_max.models.kitchen_model.get_db_connection')
    def test_create_meal_successful(self, mock_get_db_connection):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db_connection.return_value.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        create_meal('Pasta', 'Italian', 10.0, 'MED')

        expected_sql = 'INSERT INTO meals (meal, cuisine, price, difficulty) VALUES (?, ?, ?, ?)'
        actual_sql = mock_cursor.execute.call_args[0][0]

        expected_sql_normalized = ' '.join(expected_sql.split())
        actual_sql_normalized = ' '.join(actual_sql.split())

        self.assertEqual(expected_sql_normalized, actual_sql_normalized)

    @patch('meal_max.models.kitchen_model.get_db_connection')
    def test_create_duplicate_meal(self, mock_db_connection):
        """Test creating a duplicate meal should raise a ValueError."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.execute.side_effect = sqlite3.IntegrityError("UNIQUE constraint failed: meals.meal")
        mock_conn.cursor.return_value = mock_cursor
        mock_db_connection.return_value.__enter__.return_value = mock_conn

        with self.assertRaises(ValueError):
            create_meal("Pasta", "Italian", 10.0, "MED")


    @patch('meal_max.models.kitchen_model.get_db_connection')
    def test_get_leaderboard_empty_db(self, mock_db_connection):
        """Test retrieving leaderboard when no meals are in the database."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = []
        mock_conn.cursor.return_value = mock_cursor
        mock_db_connection.return_value.__enter__.return_value = mock_conn

        leaderboard = get_leaderboard()
        self.assertEqual(len(leaderboard), 0)

    @patch('meal_max.models.kitchen_model.get_db_connection')
    def test_delete_meal_non_existent(self, mock_db_connection):
        """Test deleting a meal that does not exist should raise an error."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = None
        mock_conn.cursor.return_value = mock_cursor
        mock_db_connection.return_value.__enter__.return_value = mock_conn

        with self.assertRaises(ValueError):
            delete_meal(999)

    @patch('meal_max.models.kitchen_model.get_db_connection')
    def test_delete_meal_successful(self, mock_db_connection):
        """Test deleting a meal by marking it as deleted in the database."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = (False,)
        mock_conn.cursor.return_value = mock_cursor
        mock_db_connection.return_value.__enter__.return_value = mock_conn

        delete_meal(1)

        mock_cursor.execute.assert_any_call("SELECT deleted FROM meals WHERE id = ?", (1,))
        mock_cursor.execute.assert_any_call("UPDATE meals SET deleted = TRUE WHERE id = ?", (1,))
        mock_conn.commit.assert_called_once()

    @patch('meal_max.models.kitchen_model.get_db_connection')
    def test_get_meal_by_id_found(self, mock_db_connection):
        """Test retrieving a meal by ID when it is found."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = (1, "Pasta", "Italian", 10.0, "MED", False)
        mock_conn.cursor.return_value = mock_cursor
        mock_db_connection.return_value.__enter__.return_value = mock_conn

        meal = get_meal_by_id(1)
        self.assertEqual(meal.meal, "Pasta")
        self.assertEqual(meal.cuisine, "Italian")
        self.assertEqual(meal.price, 10.0)
        self.assertEqual(meal.difficulty, "MED")

    @patch('meal_max.models.kitchen_model.get_db_connection')
    def test_get_meal_by_name_found(self, mock_db_connection):
        """Test retrieving a meal by name when it is found."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = (1, "Pasta", "Italian", 10.0, "MED", False)
        mock_conn.cursor.return_value = mock_cursor
        mock_db_connection.return_value.__enter__.return_value = mock_conn

        meal = get_meal_by_name("Pasta")
        self.assertEqual(meal.meal, "Pasta")
        self.assertEqual(meal.cuisine, "Italian")
        self.assertEqual(meal.price, 10.0)
        self.assertEqual(meal.difficulty, "MED")

    @patch('meal_max.models.kitchen_model.get_db_connection')
    def test_get_leaderboard_successful(self, mock_db_connection):
        """Test retrieving the leaderboard sorted by wins."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [
            (1, "Pasta", "Italian", 10.0, "MED", 10, 8, 0.8),
            (2, "Sushi", "Japanese", 15.0, "HIGH", 12, 7, 0.58)
        ]
        mock_conn.cursor.return_value = mock_cursor
        mock_db_connection.return_value.__enter__.return_value = mock_conn

        leaderboard = get_leaderboard()
        self.assertEqual(len(leaderboard), 2)
        self.assertEqual(leaderboard[0]['meal'], "Pasta")
        self.assertEqual(leaderboard[1]['meal'], "Sushi")

    @patch('meal_max.models.kitchen_model.get_db_connection')
    def test_create_meal_extremely_high_price_as_infinity(self, mock_db_connection):
        """Test creating a meal with an extremely high price (1e309) and verify it is stored as infinity."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_db_connection.return_value.__enter__.return_value = mock_conn

        create_meal("Ultra Expensive Meal", "Gourmet", 1e309, "HIGH")

        args, _ = mock_cursor.execute.call_args
        self.assertEqual(args[1][2], float('inf')) 







if __name__ == '__main__':
    unittest.main()

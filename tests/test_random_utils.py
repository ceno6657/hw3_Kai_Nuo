import unittest
from unittest.mock import patch, MagicMock
import requests
from meal_max.utils.random_utils import get_random

class test_random_utils(unittest.TestCase):

    @patch('meal_max.utils.random_utils.requests.get')
    def test_get_random_successful(self, mock_get):
        """Test that get_random returns a valid float when the response is successful."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "0.42"
        mock_get.return_value = mock_response

        result = get_random()
        self.assertAlmostEqual(result, 0.42, places=2)

    @patch('meal_max.utils.random_utils.requests.get')
    def test_get_random_invalid_response(self, mock_get):
        """Test that get_random raises a ValueError when the response is invalid."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "invalid"
        mock_get.return_value = mock_response

        with self.assertRaises(ValueError):
            get_random()

    @patch('meal_max.utils.random_utils.requests.get')
    def test_get_random_invalid_response_format(self, mock_get):
        """Test get_random handles invalid response formats gracefully."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "not_a_number"
        mock_get.return_value = mock_response

        with self.assertRaises(ValueError):
            get_random()

    @patch('meal_max.utils.random_utils.requests.get')
    def test_get_random_none_response(self, mock_get):
        """Test get_random handles None response from the API."""
        mock_get.return_value = MagicMock()
        mock_get.return_value.raise_for_status.side_effect = requests.exceptions.RequestException("Failed request")
        
        with self.assertRaises(RuntimeError):
            get_random()

    @patch('meal_max.utils.random_utils.requests.get')
    def test_get_random_min_boundary(self, mock_get):
        """Test get_random with the minimum boundary value (0.0)."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "0.00"
        mock_get.return_value = mock_response

        result = get_random()
        self.assertEqual(result, 0.0)

    @patch('meal_max.utils.random_utils.requests.get')
    def test_get_random_max_boundary(self, mock_get):
        """Test get_random with the maximum boundary value (1.0)."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "1.00"
        mock_get.return_value = mock_response

        result = get_random()
        self.assertEqual(result, 1.0)

    @patch('meal_max.utils.random_utils.requests.get')
    def test_get_random_timeout(self, mock_get):
        """Test that get_random raises a RuntimeError when the request times out."""
        mock_get.side_effect = requests.exceptions.Timeout

        with self.assertRaises(RuntimeError) as context:
            get_random()
        self.assertIn("timed out", str(context.exception))

    @patch('meal_max.utils.random_utils.requests.get')
    def test_get_random_request_exception(self, mock_get):
        """Test that get_random raises a RuntimeError for a general request exception."""
        mock_get.side_effect = requests.exceptions.RequestException("Error")

        with self.assertRaises(RuntimeError) as context:
            get_random()
        self.assertIn("failed", str(context.exception))

if __name__ == '__main__':
    unittest.main()

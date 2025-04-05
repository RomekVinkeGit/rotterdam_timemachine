import unittest
from unittest.mock import patch
from src.utils.text_utils import TextUtils
from src.utils.config_utils import ConfigUtils

class TestTextUtils(unittest.TestCase):
    def setUp(self):
        """Set up test cases."""
        self.utils = TextUtils()

    def test_remove_special_characters(self):
        """Test special character removal."""
        test_cases = [
            ("Hello!@#$%^&*()", "Hello"),
            ("Test\n\t\r", "Test"),
            ("Hello World!", "Hello World")
        ]
        
        for input_text, expected in test_cases:
            result = self.utils.remove_special_characters(input_text)
            self.assertEqual(result, expected)

    def test_truncate_text(self):
        """Test text truncation."""
        text = "This is a long text that needs to be truncated"
        max_length = 20
        
        result = self.utils.truncate_text(text, max_length)
        self.assertLessEqual(len(result), max_length)
        self.assertTrue(result.endswith("..."))

class TestConfigUtils(unittest.TestCase):
    def setUp(self):
        """Set up test cases."""
        self.utils = ConfigUtils()

    @patch('src.utils.config_utils.ConfigUtils.load_config')
    def test_get_api_key(self, mock_load_config):
        """Test API key retrieval."""
        mock_load_config.return_value = {
            'openai_api_key': 'test_key',
            'wikipedia_api_key': 'test_wiki_key'
        }
        
        result = self.utils.get_api_key('openai')
        self.assertEqual(result, 'test_key')

    @patch('src.utils.config_utils.ConfigUtils.load_config')
    def test_get_config_value(self, mock_load_config):
        """Test config value retrieval."""
        mock_load_config.return_value = {
            'max_results': 10,
            'timeout': 30
        }
        
        result = self.utils.get_config_value('max_results')
        self.assertEqual(result, 10)

    def test_validate_config(self):
        """Test config validation."""
        valid_config = {
            'openai_api_key': 'test_key',
            'max_results': 10,
            'timeout': 30
        }
        
        self.assertTrue(self.utils.validate_config(valid_config))

if __name__ == '__main__':
    unittest.main() 
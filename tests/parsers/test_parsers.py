import unittest
from unittest.mock import patch, MagicMock
from src.parsers.article_parser import ArticleParser
from datetime import datetime

class TestArticleParser(unittest.TestCase):
    def setUp(self):
        """Set up test cases."""
        self.parser = ArticleParser()

    def test_parse_date(self):
        """Test date parsing."""
        test_cases = [
            ("2024-04-05", datetime(2024, 4, 5)),
            ("05-04-2024", datetime(2024, 4, 5)),
            ("5 April 2024", datetime(2024, 4, 5))
        ]
        
        for date_str, expected in test_cases:
            result = self.parser.parse_date(date_str)
            self.assertEqual(result, expected)

    def test_clean_text(self):
        """Test text cleaning."""
        test_cases = [
            ("  Hello  World  ", "Hello World"),
            ("Hello\nWorld", "Hello World"),
            ("Hello\tWorld", "Hello World")
        ]
        
        for input_text, expected in test_cases:
            result = self.parser.clean_text(input_text)
            self.assertEqual(result, expected)

    def test_extract_metadata(self):
        """Test metadata extraction."""
        test_html = """
        <article>
            <h1>Test Title</h1>
            <div class="date">2024-04-05</div>
            <div class="source">Test Source</div>
        </article>
        """
        
        metadata = self.parser.extract_metadata(test_html)
        self.assertEqual(metadata['title'], "Test Title")
        self.assertEqual(metadata['date'], "2024-04-05")
        self.assertEqual(metadata['source'], "Test Source")

    @patch('src.parsers.article_parser.ArticleParser.extract_metadata')
    def test_parse_article(self, mock_extract_metadata):
        """Test full article parsing."""
        mock_extract_metadata.return_value = {
            'title': 'Test Title',
            'date': '2024-04-05',
            'source': 'Test Source'
        }
        
        test_html = "<article>Test content</article>"
        result = self.parser.parse_article(test_html)
        
        self.assertEqual(result['title'], 'Test Title')
        self.assertEqual(result['date'], '2024-04-05')
        self.assertEqual(result['source'], 'Test Source')
        self.assertIn('content', result)

if __name__ == '__main__':
    unittest.main() 
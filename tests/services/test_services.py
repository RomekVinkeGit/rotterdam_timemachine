import unittest
from unittest.mock import patch, MagicMock
from src.services.openai_service import OpenAIService
from src.services.wikipedia_service import WikipediaService

class TestOpenAIService(unittest.TestCase):
    def setUp(self):
        """Set up test cases."""
        self.service = OpenAIService()

    @patch('openai.ChatCompletion.create')
    def test_translate_text(self, mock_create):
        """Test text translation."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="Translated text"))]
        mock_create.return_value = mock_response

        result = self.service.translate_text("Hello", "Dutch")
        self.assertEqual(result, "Translated text")
        mock_create.assert_called_once()

    @patch('openai.ChatCompletion.create')
    def test_summarize_text(self, mock_create):
        """Test text summarization."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="Summary"))]
        mock_create.return_value = mock_response

        result = self.service.summarize_text("Long text to summarize")
        self.assertEqual(result, "Summary")
        mock_create.assert_called_once()

class TestWikipediaService(unittest.TestCase):
    def setUp(self):
        """Set up test cases."""
        self.service = WikipediaService()

    @patch('wikipedia.search')
    def test_search_articles(self, mock_search):
        """Test Wikipedia article search."""
        mock_search.return_value = ["Article1", "Article2"]
        
        results = self.service.search_articles("Rotterdam")
        self.assertEqual(results, ["Article1", "Article2"])
        mock_search.assert_called_once_with("Rotterdam", results=5)

    @patch('wikipedia.page')
    def test_get_article_summary(self, mock_page):
        """Test getting article summary."""
        mock_page.return_value = MagicMock(summary="Article summary")
        
        summary = self.service.get_article_summary("Rotterdam")
        self.assertEqual(summary, "Article summary")
        mock_page.assert_called_once_with("Rotterdam")

if __name__ == '__main__':
    unittest.main() 
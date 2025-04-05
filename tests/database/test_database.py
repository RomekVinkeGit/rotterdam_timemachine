import unittest
from unittest.mock import MagicMock, patch
import sqlite3
from src.database.database import Database

class TestDatabase(unittest.TestCase):
    def setUp(self):
        """Set up test cases."""
        self.db = Database(':memory:')  # Use in-memory database for testing

    def tearDown(self):
        """Clean up after tests."""
        self.db.connection.close()

    def test_init(self):
        """Test database initialization."""
        self.assertIsInstance(self.db.connection, sqlite3.Connection)
        self.assertIsInstance(self.db.cursor, sqlite3.Cursor)

    def test_create_tables(self):
        """Test table creation."""
        self.db.create_tables()
        # Verify tables exist
        tables = self.db.cursor.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
        table_names = [table[0] for table in tables]
        self.assertIn('articles', table_names)

    @patch('src.database.database.Database.connection')
    def test_insert_article(self, mock_connection):
        """Test article insertion."""
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value = mock_cursor
        
        test_article = {
            'title': 'Test Article',
            'content': 'Test Content',
            'date': '2024-04-05',
            'source': 'Test Source',
            'url': 'http://test.com'
        }
        
        self.db.insert_article(test_article)
        mock_cursor.execute.assert_called_once()

    def test_get_article(self):
        """Test article retrieval."""
        # Insert test article
        test_article = {
            'title': 'Test Article',
            'content': 'Test Content',
            'date': '2024-04-05',
            'source': 'Test Source',
            'url': 'http://test.com'
        }
        self.db.create_tables()
        self.db.insert_article(test_article)
        
        # Retrieve article
        article = self.db.get_article('Test Article')
        self.assertIsNotNone(article)
        self.assertEqual(article['title'], test_article['title'])

if __name__ == '__main__':
    unittest.main() 
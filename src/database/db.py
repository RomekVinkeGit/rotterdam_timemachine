"""Database operations for the Rotterdam Time Machine project.

This module provides database access and operations for the Rotterdam Time Machine
application. It handles all interactions with the SQLite database, including
initialization, article storage, and retrieval.

Example:
    >>> db = Database()
    >>> articles = db.get_articles_by_date(date.today())
"""
import sqlite3
from contextlib import contextmanager
from datetime import date, datetime
from typing import List, Optional, Iterator, Tuple

from ..config import DB_PATH
from .models import NewsArticle

class Database:
    """Database manager for news articles.
    
    This class provides methods for interacting with the SQLite database that
    stores historical newspaper articles. It handles database initialization,
    connection management, and CRUD operations for articles.
    
    Attributes:
        db_path: Path to the SQLite database file.
    """
    
    # SQL Queries
    CREATE_TABLE_SQL = """
        CREATE TABLE IF NOT EXISTS news_articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            publication_date DATE NOT NULL,
            newspaper TEXT NOT NULL,
            content TEXT NOT NULL,
            original_language TEXT NOT NULL
        )
    """
    
    INSERT_ARTICLE_SQL = """
        INSERT INTO news_articles (publication_date, newspaper, content, original_language)
        VALUES (?, ?, ?, ?)
    """
    
    SELECT_BY_DATE_SQL = """
        SELECT id, publication_date, newspaper, content, original_language
        FROM news_articles
        WHERE publication_date = ?
    """
    
    SELECT_BY_DAY_MONTH_SQL = """
        SELECT id, publication_date, newspaper, content, original_language
        FROM news_articles
        WHERE strftime('%m', publication_date) = ? AND strftime('%d', publication_date) = ?
    """
    
    SELECT_CLOSEST_DATE_SQL = """
        SELECT id, publication_date, newspaper, content, original_language,
               ABS(JULIANDAY(publication_date) - JULIANDAY(?)) as date_diff
        FROM news_articles
        ORDER BY date_diff
        LIMIT 1
    """

    def __init__(self, db_path: str = DB_PATH):
        """Initialize the database manager.
        
        Args:
            db_path: Path to the SQLite database file. Defaults to DB_PATH from config.
        """
        self.db_path = db_path
        self._init_db()

    @contextmanager
    def _get_connection(self) -> Iterator[sqlite3.Connection]:
        """Get a database connection with context management.
        
        This method provides a context-managed database connection that ensures
        proper connection cleanup.
        
        Yields:
            A SQLite database connection.
            
        Example:
            >>> with self._get_connection() as conn:
            ...     conn.execute("SELECT * FROM news_articles")
        """
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
        finally:
            conn.close()

    def _init_db(self) -> None:
        """Initialize the database schema.
        
        Creates the news_articles table if it doesn't exist.
        """
        with self._get_connection() as conn:
            conn.execute(self.CREATE_TABLE_SQL)
            conn.commit()

    @staticmethod
    def _convert_date(date_str: str) -> Optional[date]:
        """Convert string date to date object.
        
        Args:
            date_str: Date string in YYYY-MM-DD format.
            
        Returns:
            A date object if conversion is successful, None otherwise.
        """
        try:
            return datetime.strptime(date_str, "%Y-%m-%d").date()
        except (ValueError, TypeError):
            return None

    def _create_article(self, row: Tuple) -> NewsArticle:
        """Create a NewsArticle object from a database row.
        
        Args:
            row: A tuple containing article data from the database.
            
        Returns:
            A NewsArticle object populated with the row data.
        """
        return NewsArticle(
            id=row[0],
            publication_date=self._convert_date(row[1]),
            newspaper=row[2],
            content=row[3],
            original_language=row[4]
        )

    def insert_article(self, article: NewsArticle) -> int:
        """Insert a new article and return its ID.
        
        Args:
            article: The NewsArticle object to insert.
            
        Returns:
            The ID of the newly inserted article.
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                self.INSERT_ARTICLE_SQL,
                (article.publication_date.isoformat(), article.newspaper, 
                 article.content, article.original_language)
            )
            conn.commit()
            return cursor.lastrowid

    def get_articles_by_date(self, target_date: date) -> List[NewsArticle]:
        """Get all articles published on a specific date.
        
        Args:
            target_date: The date to search for.
            
        Returns:
            A list of NewsArticle objects published on the target date.
        """
        with self._get_connection() as conn:
            cursor = conn.execute(self.SELECT_BY_DATE_SQL, (target_date.isoformat(),))
            return [self._create_article(row) for row in cursor.fetchall()]

    def get_articles_by_day_month(self, day: int, month: int) -> List[NewsArticle]:
        """Get all articles published on a specific day and month (any year).
        
        Args:
            day: Day of the month (1-31).
            month: Month number (1-12).
            
        Returns:
            A list of NewsArticle objects published on the specified day and month.
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                self.SELECT_BY_DAY_MONTH_SQL, 
                (f"{month:02d}", f"{day:02d}")
            )
            return [self._create_article(row) for row in cursor.fetchall()]

    def get_closest_article(self, target_date: date) -> Tuple[Optional[NewsArticle], float]:
        """Get the article closest to the target date.
        
        Args:
            target_date: The reference date to search around.
            
        Returns:
            A tuple containing:
                - The closest NewsArticle object (or None if no articles exist)
                - The difference in days between the article and target date
        """
        with self._get_connection() as conn:
            cursor = conn.execute(self.SELECT_CLOSEST_DATE_SQL, (target_date.isoformat(),))
            row = cursor.fetchone()
            if not row:
                return None, 0
            return self._create_article(row), row[5]  # row[5] is date_diff 

    def get_closest_day_month_article(self, day: int, month: int) -> Tuple[Optional[NewsArticle], int]:
        """Get the article with the closest day/month combination.
        
        Args:
            day: Day of the month (1-31).
            month: Month number (1-12).
            
        Returns:
            A tuple containing:
                - The closest NewsArticle object (or None if no articles exist)
                - The difference in days between the article's day/month and target day/month
        """
        with self._get_connection() as conn:
            # Calculate the day of year for the target date
            target_day_of_year = datetime(2000, month, day).timetuple().tm_yday
            
            cursor = conn.execute("""
                SELECT id, publication_date, newspaper, content, original_language,
                       ABS(
                           (strftime('%j', publication_date) - ?) % 365
                       ) as day_diff
                FROM news_articles
                ORDER BY day_diff
                LIMIT 1
            """, (target_day_of_year,))
            row = cursor.fetchone()
            
            if row:
                return (
                    self._create_article(row),
                    row[5]  # day difference
                )
            return None, 0 
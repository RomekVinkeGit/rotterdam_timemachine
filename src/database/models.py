"""Database models for the Rotterdam Time Machine project.

This module defines the data models used throughout the application.
It provides structured representations of the data stored in the database.
"""
from dataclasses import dataclass
from datetime import date
from typing import Optional

@dataclass
class NewsArticle:
    """Represents a historical newspaper article.
    
    This class defines the structure of a newspaper article with its metadata
    and content. It is used for storing and retrieving articles from the database.
    
    Attributes:
        id: The unique identifier for the article in the database.
        publication_date: The date when the article was published.
        newspaper: The name of the newspaper that published the article.
        content: The full text content of the article.
        original_language: The language of the article ('nl' for Dutch, 'fr' for French).
    """
    id: Optional[int]
    publication_date: date
    newspaper: str
    content: str
    original_language: str  # 'nl' for Dutch, 'fr' for French 
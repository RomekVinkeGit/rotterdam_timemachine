"""XML parser for historical newspaper articles.

This module provides functionality for parsing XML files containing historical
newspaper articles. It handles the extraction of article metadata and content
from XML files in a specified format.
"""
from datetime import datetime
from pathlib import Path
from typing import Generator, Optional
import xml.etree.ElementTree as ET

from ..database.models import NewsArticle

class XMLParser:
    """Parser for XML files containing historical newspaper articles.
    
    This class provides methods for parsing individual XML files and directories
    containing multiple XML files. It extracts article metadata and content,
    creating NewsArticle objects.
    
    Attributes:
        data_dir: Path to the directory containing XML files.
    """
    
    def __init__(self, data_dir: str = "data"):
        """Initialize the XML parser.
        
        Args:
            data_dir: Path to the directory containing XML files. Defaults to "data".
        """
        self.data_dir = Path(data_dir)

    def parse_article(self, xml_path: Path) -> Optional[NewsArticle]:
        """Parse a single XML article file.
        
        Args:
            xml_path: Path to the XML file to parse.
            
        Returns:
            A NewsArticle object if parsing is successful, None otherwise.
            
        Raises:
            ET.ParseError: If the XML file is malformed.
            ValueError: If required data is missing or invalid.
            AttributeError: If required XML elements are not found.
        """
        try:
            tree = ET.parse(xml_path)
            root = tree.getroot()

            # Extract date from title (first 8 characters)
            title = root.find(".//title").text
            date_str = title[:8]
            publication_date = datetime.strptime(date_str, "%Y%m%d").date()

            # Extract newspaper name and content
            newspaper = root.find(".//newspaper").text
            content = root.find(".//content").text

            # Determine language (simplified version - can be enhanced)
            language = "nl" if "Rotterdamsche" in newspaper else "fr"

            return NewsArticle(
                id=None,
                publication_date=publication_date,
                newspaper=newspaper,
                content=content,
                original_language=language
            )
        except (ET.ParseError, ValueError, AttributeError) as e:
            print(f"Error parsing {xml_path}: {e}")
            return None

    def parse_directory(self, directory: str) -> Generator[NewsArticle, None, None]:
        """Parse all XML files in a directory.
        
        Args:
            directory: Name of the directory containing XML files, relative to data_dir.
            
        Yields:
            NewsArticle objects for each successfully parsed XML file.
            
        Note:
            Files that fail to parse are skipped with an error message.
        """
        dir_path = self.data_dir / directory
        if not dir_path.exists():
            print(f"Directory not found: {dir_path}")
            return

        for xml_file in dir_path.glob("*.xml"):
            article = self.parse_article(xml_file)
            if article:
                yield article 
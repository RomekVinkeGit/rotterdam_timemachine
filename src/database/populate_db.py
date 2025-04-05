"""
Script to populate the database with articles from XML files.
"""
import os
import re
from pathlib import Path
from datetime import datetime
import xml.etree.ElementTree as ET
from tqdm import tqdm

from src.database.db import Database
from src.database.models import NewsArticle

def extract_date_from_filename(filename):
    """Extract date from filename (format: YYYYMMDD_...)"""
    match = re.match(r'(\d{8})_', filename)
    if match:
        date_str = match.group(1)
        try:
            return datetime.strptime(date_str, "%Y%m%d").date()
        except ValueError:
            return None
    return None

def determine_newspaper_name(publication_date):
    """Determine newspaper name based on publication year."""
    year = publication_date.year
    if year < 1720:
        return "Gazette de Rotterdam"
    elif year >= 1720:
        return "Rotterdamse courant"
    else:
        return "Unknown"  # For articles between 1720 and 1749

def determine_language(text):
    """Determine if text is Dutch or French based on content."""
    # Simple heuristics - can be improved
    french_indicators = ['le', 'la', 'les', 'un', 'une', 'des', 'et', 'est', 'que', 'qui']
    dutch_indicators = ['de', 'het', 'een', 'en', 'is', 'dat', 'die', 'wat', 'voor', 'van']
    
    text_lower = text.lower()
    french_count = sum(1 for word in french_indicators if f" {word} " in f" {text_lower} ")
    dutch_count = sum(1 for word in dutch_indicators if f" {word} " in f" {text_lower} ")
    
    return "fr" if french_count > dutch_count else "nl"

def parse_xml_file(file_path):
    """Parse a single XML file and extract article information."""
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        
        # Extract title and content
        title_elem = root.find(".//title")
        content_elem = root.find(".//p")
        
        if title_elem is None or content_elem is None:
            print(f"Missing title or content in {file_path}")
            return None
            
        title = title_elem.text
        content = content_elem.text
        
        # Extract date from filename
        publication_date = extract_date_from_filename(file_path.name)
        if not publication_date:
            print(f"Could not extract date from filename: {file_path}")
            return None
            
        # Determine language and newspaper name
        language = determine_language(content)
        newspaper = determine_newspaper_name(publication_date)
        
        # Create article object
        return NewsArticle(
            id=None,
            publication_date=publication_date,
            newspaper=newspaper,
            content=content,
            original_language=language
        )
    except Exception as e:
        print(f"Error parsing {file_path}: {e}")
        return None

def main():
    # Initialize database
    db = Database()
    
    # Path to articles directory
    articles_dir = Path("data/articles")
    
    # Get all XML files
    xml_files = list(articles_dir.glob("*.xml"))
    print(f"Found {len(xml_files)} XML files")
    
    # Process each file
    success_count = 0
    for xml_file in tqdm(xml_files, desc="Processing articles"):
        article = parse_xml_file(xml_file)
        if article:
            try:
                db.insert_article(article)
                success_count += 1
            except Exception as e:
                print(f"Error inserting article from {xml_file}: {e}")
    
    print(f"Successfully processed {success_count} out of {len(xml_files)} articles")

if __name__ == "__main__":
    main() 
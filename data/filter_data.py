"""Script to filter and extract Rotterdam Newspaper articles from a newspaper dataset.

This module processes a directory of newspaper articles and extracts only those
from Rotterdam. It reads an index file to identify Rotterdam
editions, then copies the corresponding article text files to an output directory.

The script expects a specific directory structure:
    root_dir/
        year/
            month/
                day/
                    edition_folder/
                        *_articletext.xml

Example:
    To run this script:
    $ python filter_data.py
"""

import os
import csv
import shutil
import logging
from typing import Set, List, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# === Configuration ===
ROOT_DIR = "DIR"  # The extracted directory
INDEX_FILE = os.path.join(ROOT_DIR, "DIR")
OUTPUT_DIR = "DIR"

def identify_rotterdam_editions(index_file: str) -> Set[str]:
    """Identifies all editions of Rotterdam newspapers from the index file.
    
    Args:
        index_file: Path to the index file containing newspaper metadata.
        
    Returns:
        A set of identifiers for Rotterdam editions.
        
    Raises:
        FileNotFoundError: If the index file doesn't exist.
        ValueError: If the index file is malformed.
    """
    rotterdam_ids = set()
    
    try:
        with open(index_file, "r", encoding="utf-8") as f:
            reader = csv.reader(f, delimiter="\t")
            for row in reader:
                if len(row) < 4:  # Ensure row has enough columns
                    logger.warning(f"Skipping incomplete row: {row}")
                    continue
                    
                if "Rotterdam" in row[0]:
                    location = os.path.basename(os.path.normpath(row[3]))
                    rotterdam_ids.add(location)
    except FileNotFoundError:
        logger.error(f"Index file not found: {index_file}")
        raise
    except Exception as e:
        logger.error(f"Error reading index file: {e}")
        raise ValueError(f"Malformed index file: {e}")
    
    logger.info(f"Found {len(rotterdam_ids)} editions of the Rotterdam newspapers.")
    if rotterdam_ids:
        logger.debug(f"Sample IDs: {list(rotterdam_ids)[:10]}")
    
    return rotterdam_ids

def copy_rotterdam_articles(root_dir: str, rotterdam_ids: Set[str], output_dir: str) -> int:
    """Copies Rotterdam newspaper article files to the output directory.
    
    Args:
        root_dir: Root directory containing the newspaper articles.
        rotterdam_ids: Set of Rotterdam edition identifiers.
        output_dir: Directory where filtered articles will be saved.
        
    Returns:
        The number of files copied.
        
    Raises:
        FileNotFoundError: If the root directory doesn't exist.
        OSError: If there are permission issues or other OS errors.
    """
    if not os.path.exists(root_dir):
        logger.error(f"Root directory not found: {root_dir}")
        raise FileNotFoundError(f"Root directory not found: {root_dir}")
    
    if not os.path.exists(output_dir):
        logger.info(f"Creating output directory: {output_dir}")
        os.makedirs(output_dir)
    
    files_copied = 0
    
    for year in os.listdir(root_dir):
        year_path = os.path.join(root_dir, year)
        if not os.path.isdir(year_path):
            continue
            
        for month in os.listdir(year_path):
            month_path = os.path.join(year_path, month)
            if not os.path.isdir(month_path):
                continue
                
            for day in os.listdir(month_path):
                day_path = os.path.join(month_path, day)
                if not os.path.isdir(day_path):
                    continue
                    
                for edition_folder in os.listdir(day_path):
                    edition_path = os.path.join(day_path, edition_folder)
                    if not os.path.isdir(edition_path):
                        continue
                        
                    if edition_folder in rotterdam_ids:
                        for fname in os.listdir(edition_path):
                            if fname.endswith("_articletext.xml"):
                                src_path = os.path.join(edition_path, fname)
                                dst_path = os.path.join(output_dir, f"{year}{month}{day}_{edition_folder}__{fname}")
                                
                                logger.debug(f"Copying: {src_path} -> {dst_path}")
                                
                                try:
                                    shutil.copy2(src_path, dst_path)
                                    files_copied += 1
                                except Exception as e:
                                    logger.error(f"Error copying {src_path}: {e}")
    
    return files_copied

def main():
    """Main function to run the filtering process.
    
    This function orchestrates the entire process:
    1. Identifies Rotterdam newspaper editions from the index file
    2. Copies the corresponding article files to the output directory
    3. Reports the results
    """
    try:
        # Identify Rotterdam newspaper editions
        rotterdam_ids = identify_rotterdam_editions(INDEX_FILE)
        
        # Copy the articles
        files_copied = copy_rotterdam_articles(ROOT_DIR, rotterdam_ids, OUTPUT_DIR)
        
        # Report results
        logger.info(f"✅ Copied {files_copied} OCR files to: {OUTPUT_DIR}")
        
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        raise

if __name__ == "__main__":
    main()
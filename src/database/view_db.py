"""
Script to view the first 20 rows of the database.
"""
import sqlite3
from tabulate import tabulate

def view_database():
    """Print the first 20 rows of the database."""
    try:
        # Connect to the database
        conn = sqlite3.connect("data/articles.db")
        cursor = conn.cursor()
        
        # Get the first 20 rows
        cursor.execute("""
            SELECT id, publication_date, newspaper, original_language, 
                   substr(content, 1, 100) || '...' as content_preview
            FROM news_articles
            ORDER BY publication_date
            LIMIT 20
        """)
        
        rows = cursor.fetchall()
        
        if not rows:
            print("No articles found in the database.")
            return
        
        # Print the results in a nice table format
        headers = ["ID", "Publication Date", "Newspaper", "Language", "Content Preview"]
        print(tabulate(rows, headers=headers, tablefmt="grid"))
        
        # Print total count
        cursor.execute("SELECT COUNT(*) FROM news_articles")
        total_count = cursor.fetchone()[0]
        print(f"\nTotal articles in database: {total_count}")
        
    except sqlite3.OperationalError as e:
        print(f"Error accessing database: {e}")
        print("Make sure you've run populate_db.py first to create the database.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    view_database() 
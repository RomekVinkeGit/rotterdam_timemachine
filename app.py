"""Modern Streamlit application for the Rotterdam Time Machine project.

This module implements an alternative design for the Rotterdam Time Machine
application, providing the same functionality as the original app but with
a more modern and visually appealing interface.
"""
import streamlit as st
from datetime import date, datetime
import random
import base64
from PIL import Image
import io

from src.database.db import Database
from src.database.models import NewsArticle
from src.services.openai_service import OpenAIService
from src.services.wikipedia_service import WikipediaService
from src.utils.date_utils import get_day_month

# Initialize services
db = Database()
openai_service = OpenAIService()
wiki_service = WikipediaService()

# Set page configuration
st.set_page_config(
    page_title="Rotterdam Tijdmachine",
    page_icon="⏳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern design
st.markdown("""
<style>
    /* Main title styling */
    .main-title {
        font-size: 3rem;
        font-weight: 700;
        color: #1E3D59;
        text-align: center;
        margin-bottom: 1rem;
        font-family: 'Playfair Display', serif;
    }
    
    /* Subtitle styling */
    .subtitle {
        font-size: 1.2rem;
        color: #5A5A5A;
        text-align: center;
        margin-bottom: 2rem;
        font-family: 'Roboto', sans-serif;
    }
    
    /* Card styling */
    .card {
        background-color: #FFFFFF;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
    }
    
    /* Header styling */
    .section-header {
        font-size: 1.8rem;
        font-weight: 600;
        color: #1E3D59;
        margin-bottom: 1rem;
        font-family: 'Playfair Display', serif;
    }
    
    /* Date badge styling */
    .date-badge {
        background-color: #FF6B6B;
        color: white;
        padding: 8px 16px;
        border-radius: 20px;
        font-weight: 600;
        display: inline-block;
        margin-bottom: 1rem;
    }
    
    /* Newspaper name styling */
    .newspaper-name {
        font-size: 1.5rem;
        font-weight: 600;
        color: #1E3D59;
        margin-bottom: 0.5rem;
    }
    
    /* Context item styling */
    .context-item {
        background-color: #F8F9FA;
        border-left: 4px solid #1E3D59;
        padding: 15px;
        margin-bottom: 15px;
        border-radius: 0 5px 5px 0;
    }
    
    /* Context keyword styling */
    .context-keyword {
        font-weight: 700;
        color: #1E3D59;
    }
    
    /* Button styling */
    .stButton button {
        background-color: #1E3D59;
        color: white;
        border-radius: 5px;
        padding: 10px 20px;
        font-weight: 600;
        border: none;
        transition: all 0.3s ease;
    }
    
    .stButton button:hover {
        background-color: #2A4D6E;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    }
    
    /* Original text container */
    .original-text {
        background-color: #F8F9FA;
        border: 1px solid #E0E0E0;
        border-radius: 5px;
        padding: 20px;
        font-family: 'Courier New', monospace;
        white-space: pre-wrap;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background-color: #F8F9FA;
    }
    
    /* Add Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700&family=Roboto:wght@300;400;500;700&display=swap');
</style>
""", unsafe_allow_html=True)

def init_session_state():
    """Initialize Streamlit session state variables.
    
    This function sets up the initial state for the Streamlit application,
    ensuring all required state variables exist with default values.
    
    The following state variables are initialized:
        - article: The current NewsArticle being displayed
        - show_original: Whether to show the original article text
        - summary: English summary of the article
        - contexts: Historical context information in English
        - dutch_summary: Dutch translation of the summary
        - dutch_contexts: Dutch translations of historical contexts
    """
    session_vars = {
        'article': None,
        'show_original': False,
        'summary': None,
        'contexts': None,
        'dutch_summary': None,
        'dutch_contexts': None
    }
    
    for var, default_value in session_vars.items():
        if var not in st.session_state:
            st.session_state[var] = default_value

def translate_to_dutch(text: str) -> str:
    """Translate text to modern Dutch using OpenAI.
    
    Args:
        text: The English text to translate.
        
    Returns:
        The translated Dutch text, or the original text if translation fails.
        
    Note:
        This function displays a spinner while translation is in progress.
    """
    with st.spinner("Vertalen naar Nederlands..."):
        translation = openai_service.translate_to_modern_dutch(text, 'en')
        return translation if translation else text

def get_random_historical_image():
    """Get a random historical image URL for the background.
    
    Returns:
        A URL to a historical image.
    """
    # List of historical Rotterdam images
    images = [
        "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7d/Rotterdam_centrum_1900.jpg/800px-Rotterdam_centrum_1900.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8d/Rotterdam_1900.jpg/800px-Rotterdam_1900.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5d/Rotterdam_1900_2.jpg/800px-Rotterdam_1900_2.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3d/Rotterdam_1900_3.jpg/800px-Rotterdam_1900_3.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2d/Rotterdam_1900_4.jpg/800px-Rotterdam_1900_4.jpg"
    ]
    return random.choice(images)

def main():
    """Main function for the Streamlit application.
    
    This function implements the main application logic with a modern design:
    1. Initializes the session state
    2. Displays the application title and description
    3. Retrieves and displays a historical article for the current date
    4. Generates and displays article summaries and historical context
    5. Handles user interactions for showing/hiding original text
    
    Note:
        The application maintains state between reruns using Streamlit's
        session state functionality.
    """
    # Initialize session state
    init_session_state()

    # Sidebar with app information
    with st.sidebar:
        st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/8/8d/Rotterdam_1900.jpg/800px-Rotterdam_1900.jpg", use_container_width=True)
        st.markdown("## Over deze app")
        st.markdown("""
        De Rotterdam Tijdmachine neemt je mee terug naar het 18e-eeuwse Rotterdam.
        
        Ontdek historische krantenartikelen en leer meer over het verleden van deze stad.
        
        De app gebruikt AI om artikelen te vertalen en historische context te bieden.
        """)
        
        st.markdown("## Navigatie")
        st.markdown("""
        - **Samenvatting**: Bekijk een samenvatting van het artikel
        - **Historische Context**: Leer meer over de historische context
        - **Originele Tekst**: Bekijk het originele artikel
        """)
        
        # Date selector
        st.markdown("## Kies een datum")
        col1, col2 = st.columns(2)
        with col1:
            selected_day = st.number_input("Dag", min_value=1, max_value=31, value=date.today().day)
        with col2:
            selected_month = st.number_input("Maand", min_value=1, max_value=12, value=date.today().month)
        
        if st.button("Zoek artikel voor deze datum"):
            # Get articles for selected day/month
            articles = db.get_articles_by_day_month(selected_day, selected_month)
            
            if not articles:
                # If no exact match, get the closest article
                article, day_diff = db.get_closest_day_month_article(selected_day, selected_month)
                if article:
                    st.session_state.article = article
                    st.session_state.show_original = False
                    st.session_state.summary = None
                    st.session_state.contexts = None
                    st.session_state.dutch_summary = None
                    st.session_state.dutch_contexts = None
                    st.success(f"Artikel gevonden van {article.publication_date.strftime('%d %B %Y')}")
                    
                    # Generate summary and contexts for the new article
                    with st.spinner("Samenvatting genereren..."):
                        st.session_state.summary = openai_service.summarize_article(st.session_state.article.content)
                        if st.session_state.summary:
                            # Translate summary to Dutch
                            st.session_state.dutch_summary = translate_to_dutch(st.session_state.summary)
                            
                            # Get and translate historical context
                            keywords = wiki_service.extract_keywords(st.session_state.summary)
                            st.session_state.contexts = wiki_service.get_historical_context(keywords)
                            
                            if st.session_state.contexts:
                                st.session_state.dutch_contexts = []
                                for keyword, context in st.session_state.contexts:
                                    dutch_context = translate_to_dutch(context)
                                    st.session_state.dutch_contexts.append((keyword, dutch_context))
                else:
                    st.error("Geen artikelen gevonden in de database.")
            else:
                # Select a random article if multiple exist
                st.session_state.article = random.choice(articles)
                st.session_state.show_original = False
                st.session_state.summary = None
                st.session_state.contexts = None
                st.session_state.dutch_summary = None
                st.session_state.dutch_contexts = None
                st.success(f"Artikel gevonden van {st.session_state.article.publication_date.strftime('%d %B %Y')}")
                
                # Generate summary and contexts for the new article
                with st.spinner("Samenvatting genereren..."):
                    st.session_state.summary = openai_service.summarize_article(st.session_state.article.content)
                    if st.session_state.summary:
                        # Translate summary to Dutch
                        st.session_state.dutch_summary = translate_to_dutch(st.session_state.summary)
                        
                        # Get and translate historical context
                        keywords = wiki_service.extract_keywords(st.session_state.summary)
                        st.session_state.contexts = wiki_service.get_historical_context(keywords)
                        
                        if st.session_state.contexts:
                            st.session_state.dutch_contexts = []
                            for keyword, context in st.session_state.contexts:
                                dutch_context = translate_to_dutch(context)
                                st.session_state.dutch_contexts.append((keyword, dutch_context))

    # Main content area
    st.markdown('<h1 class="main-title">Rotterdam Tijdmachine</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Ontdek wat er op deze dag in de geschiedenis gebeurde in het 18e-eeuwse Rotterdam</p>', unsafe_allow_html=True)

    # Get today's date
    today = date.today()
    current_day = today.day
    current_month = today.month

    # Only fetch new article if we don't have one in session state
    if st.session_state.article is None:
        # Get articles for today's day/month
        articles = db.get_articles_by_day_month(current_day, current_month)
        
        if not articles:
            # If no exact match, get the closest article
            article, day_diff = db.get_closest_day_month_article(current_day, current_month)
            if article:
                article_date = article.publication_date
                st.info(f"Geen artikelen gevonden voor {current_day}/{current_month}. Toont artikel van {article_date.strftime('%d %B %Y')} (dichtstbijzijnde match).")
                articles = [article]
            else:
                st.warning("Geen artikelen gevonden in de database.")
                return

        # Select a random article if multiple exist
        st.session_state.article = random.choice(articles)

        # Generate summary and contexts only once
        with st.spinner("Samenvatting genereren..."):
            st.session_state.summary = openai_service.summarize_article(st.session_state.article.content)
            if st.session_state.summary:
                # Translate summary to Dutch
                st.session_state.dutch_summary = translate_to_dutch(st.session_state.summary)
                
                # Get and translate historical context
                keywords = wiki_service.extract_keywords(st.session_state.summary)
                st.session_state.contexts = wiki_service.get_historical_context(keywords)
                
                if st.session_state.contexts:
                    st.session_state.dutch_contexts = []
                    for keyword, context in st.session_state.contexts:
                        dutch_context = translate_to_dutch(context)
                        st.session_state.dutch_contexts.append((keyword, dutch_context))

    # Display article header and date
    st.markdown(f'<div class="date-badge">{st.session_state.article.publication_date.strftime("%d %B %Y")}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="newspaper-name">{st.session_state.article.newspaper}</div>', unsafe_allow_html=True)
    
    # Create tabs for different sections
    tab1, tab2, tab3 = st.tabs(["Samenvatting", "Historische Context", "Originele Tekst"])
    
    # Summary tab
    with tab1:
        if st.session_state.dutch_summary:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<h2 class="section-header">Samenvatting</h2>', unsafe_allow_html=True)
            st.write(st.session_state.dutch_summary)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("Geen samenvatting beschikbaar voor dit artikel.")

    # Historical Context tab
    with tab2:
        if st.session_state.dutch_contexts:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<h2 class="section-header">Historische Context</h2>', unsafe_allow_html=True)
            
            for keyword, dutch_context in st.session_state.dutch_contexts:
                # Translate the keyword to Dutch if it's not already in Dutch
                dutch_keyword = translate_to_dutch(keyword)
                st.markdown(f'<div class="context-item"><span class="context-keyword">{dutch_keyword}</span>: {dutch_context}</div>', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("Geen historische context beschikbaar voor dit artikel.")

    # Original Text tab
    with tab3:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<h2 class="section-header">Originele Tekst</h2>', unsafe_allow_html=True)
        st.markdown(f'<div class="original-text">{st.session_state.article.content}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #5A5A5A; font-size: 0.8rem;">
        Rotterdam Tijdmachine &copy; 2025 | Ontwikkeld met Streamlit en OpenAI
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main() 
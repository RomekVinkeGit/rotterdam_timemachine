"""
Wikipedia API service for historical context using LangChain.
"""
import os
import json
from typing import List, Optional, Tuple
from langchain_community.utilities import WikipediaAPIWrapper
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain.schema.runnable import RunnablePassthrough
from bs4 import BeautifulSoup
import wikipedia
from dotenv import load_dotenv

from ..utils.error_utils import handle_api_errors, log_error

load_dotenv()

class CustomWikipediaWrapper(WikipediaAPIWrapper):
    """Custom Wikipedia wrapper that properly configures BeautifulSoup."""
    
    def _clean_html(self, html: str) -> str:
        """Override the internal method to use properly configured BeautifulSoup."""
        soup = BeautifulSoup(html, features="html.parser")
        text = soup.get_text()
        return text

class WikipediaService:
    def __init__(self):
        # Initialize custom Wikipedia wrapper
        self.wikipedia = CustomWikipediaWrapper(
            lang="nl",  # Default to Dutch
            top_k_results=3,  # Maximum of 3 calls to Wikipedia API
            doc_content_chars_max=4000  # Limit content length
        )
        
        # Initialize OpenAI for summarization and keyword extraction
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.2,
            api_key=os.getenv("OPENAI_API_KEY")
        )
        
        # Create a prompt template for summarization
        self.summary_prompt = PromptTemplate(
            input_variables=["text"],
            template="""Summarize the following historical information in Dutch in 2-3 sentences, 
            focusing on the most important historical context for an 18th century newspaper article.
            Use modern Dutch language that would be understandable to today's readers.
            
            {text}
            
            Summary:"""
        )
        
        # Create a prompt template for keyword extraction
        self.keyword_prompt = PromptTemplate(
            input_variables=["text"],
            template="""Analyze the following historical text and identify the 3-5 most important entities 
            that would be useful for searching historical context on Wikipedia. Focus on:
            1. Important historical figures (e.g., Willem van Oranje, Napoleon)
            2. Significant places (e.g., Rotterdam, Amsterdam)
            3. Historical events (e.g., Vrede van Utrecht, Tachtigjarige Oorlog)
            4. Organizations or institutions (e.g., Verenigde Oost-Indische Compagnie)
            5. Important historical concepts from the 18th century

            For each entity:
            - ALWAYS use the Dutch name if it exists, even if the text is in another language
            - Include well-known international variants in parentheses if relevant
            - Ensure names are properly capitalized
            - Focus on terms that would yield meaningful Wikipedia results in Dutch

            Return ONLY a JSON array of strings, with each string being a keyword or phrase.
            Example format: ["Willem van Oranje", "Vrede van Utrecht", "Amsterdam"]

            Text:
            {text}

            Keywords:"""
        )
        
        # Create runnable chains
        self.summary_chain = (
            RunnablePassthrough() | 
            self.summary_prompt | 
            self.llm
        )
        
        self.keyword_chain = (
            RunnablePassthrough() |
            self.keyword_prompt |
            self.llm
        )

    @handle_api_errors(default_return=[])
    def extract_keywords(self, text: str) -> List[str]:
        """Extract key historical terms from the text using GPT."""
        # Get keyword suggestions from GPT
        result = self.keyword_chain.invoke({"text": text})
        content = result.content.strip()
        
        # Extract JSON array from the response
        json_content = content
        if content.startswith('```json'):
            json_content = content[7:-3]  # Remove ```json and ``` markers
        elif not content.startswith('['):
            # Try to find the JSON array in the response
            start = content.find('[')
            end = content.rfind(']') + 1
            if start >= 0 and end > start:
                json_content = content[start:end]
            else:
                log_error(ValueError("Could not find JSON array in response"), "Keyword extraction")
                return []
        
        # Parse and validate keywords
        try:
            keywords = json.loads(json_content)
            if not isinstance(keywords, list):
                log_error(ValueError("Response is not a list"), "Keyword extraction")
                return []
                
            # Filter and limit keywords
            return [k.strip() for k in keywords if isinstance(k, str) and k.strip()][:5]
        except json.JSONDecodeError as e:
            log_error(e, "Keyword extraction")
            return []

    @handle_api_errors(default_return=[])
    def get_historical_context(self, keywords: List[str]) -> List[Tuple[str, str]]:
        """Get historical context from Wikipedia for the given keywords.
        
        This method retrieves historical context information from the Dutch Wikipedia
        for each keyword and generates a summary in Dutch.
        
        Args:
            keywords: List of keywords to search for on Wikipedia.
            
        Returns:
            A list of tuples, each containing (keyword, context_summary).
        """
        contexts = []
        
        # Process each keyword (limited to top 3 by the keyword extraction)
        for keyword in keywords[:3]:
            try:
                # Use LangChain's Wikipedia wrapper to get content
                wiki_content = self.wikipedia.run(keyword)
                
                if wiki_content:
                    # Generate a summary using the runnable chain
                    result = self.summary_chain.invoke({"text": wiki_content})
                    contexts.append((keyword, result.content))
            except Exception as e:
                log_error(e, f"Wikipedia content retrieval for {keyword}")
        
        return contexts 
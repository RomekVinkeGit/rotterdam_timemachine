"""
OpenAI API service for translation and summarization.
"""
from typing import Optional, List, Dict, Any
from openai import OpenAI
from openai.types.chat import ChatCompletion

from ..config import OPENAI_API_KEY, OPENAI_MODEL, OPENAI_TEMPERATURE
from ..utils.error_utils import handle_api_errors, log_error

class OpenAIService:
    """Service for interacting with OpenAI's API."""

    def __init__(self):
        """Initialize OpenAI client with API key from config."""
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.model = OPENAI_MODEL
        self.temperature = OPENAI_TEMPERATURE

    @handle_api_errors(default_return=None)
    def _create_chat_completion(
        self, 
        system_prompt: str, 
        user_content: str,
        temperature: Optional[float] = None
    ) -> Optional[str]:
        """
        Create a chat completion with error handling.
        
        Args:
            system_prompt: The system message to guide the model's behavior
            user_content: The user's input text
            temperature: Optional temperature override for this specific completion
        
        Returns:
            The model's response text, or None if an error occurs
        """
        response: ChatCompletion = self.client.chat.completions.create(
            model=self.model,
            temperature=temperature or self.temperature,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ]
        )
        return response.choices[0].message.content

    @handle_api_errors(default_return=None)
    def translate_to_modern_dutch(
        self, 
        text: str, 
        source_language: str,
        preserve_formatting: bool = True
    ) -> Optional[str]:
        """
        Translate historical Dutch or French text to modern Dutch.
        
        Args:
            text: The text to translate
            source_language: The source language code ('nl' or 'fr')
            preserve_formatting: Whether to preserve the original text formatting
        
        Returns:
            The translated text, or None if translation fails
        """
        system_prompt = (
            f"Translate the following {source_language} text to modern Dutch. "
            "Preserve the historical context and meaning. "
            f"{'Maintain the original text formatting.' if preserve_formatting else ''}"
        )
        return self._create_chat_completion(system_prompt, text)

    @handle_api_errors(default_return=None)
    def summarize_article(
        self, 
        text: str,
        max_sentences: int = 3,
        focus_historical: bool = True
    ) -> Optional[str]:
        """
        Generate a concise summary of the article.
        
        Args:
            text: The article text to summarize
            max_sentences: Maximum number of sentences in the summary
            focus_historical: Whether to focus on historical significance
        
        Returns:
            The summary text, or None if summarization fails
        """
        system_prompt = (
            f"Summarize the following historical newspaper article in {max_sentences} sentences or less. "
            f"{'Focus on the main events and historical significance.' if focus_historical else 'Focus on the main points.'}"
        )
        return self._create_chat_completion(
            system_prompt,
            text,
            temperature=0.3  # Slightly lower temperature for more consistent summaries
        ) 
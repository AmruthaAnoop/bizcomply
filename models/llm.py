import os
import sys
from typing import Optional

# Add parent directory to path for module imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Import configuration
from config.config import (
    LLM_PROVIDER, LLM_MODEL,
    GROQ_API_KEY, OPENAI_API_KEY, GOOGLE_API_KEY,
    DEFAULT_RESPONSE_MODE
)

# Lazy imports to avoid unnecessary dependencies
try:
    from langchain_groq import ChatGroq
except ImportError:
    ChatGroq = None

try:
    from langchain_openai import ChatOpenAI
except ImportError:
    ChatOpenAI = None

try:
    import google.generativeai as genai
    from langchain_google_genai import ChatGoogleGenerativeAI
except ImportError:
    genai = None
    ChatGoogleGenerativeAI = None

class LLMProvider:
    """Factory class to provide different LLM instances based on configuration."""
    
    @staticmethod
    def get_llm(provider: Optional[str] = None, model: Optional[str] = None, **kwargs):
        """
        Get an instance of the configured LLM.
        
        Args:
            provider: The LLM provider to use (groq, openai, gemini)
            model: The model name to use
            **kwargs: Additional arguments to pass to the LLM
            
        Returns:
            An instance of the configured LLM
        """
        provider = provider or LLM_PROVIDER
        model = model or LLM_MODEL
        
        if provider == "groq":
            return LLMProvider._get_groq_llm(model, **kwargs)
        elif provider == "openai":
            return LLMProvider._get_openai_llm(model, **kwargs)
        elif provider == "gemini":
            return LLMProvider._get_gemini_llm(model, **kwargs)
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")
    
    @staticmethod
    def _get_groq_llm(model: str, **kwargs):
        """Initialize and return the Groq chat model"""
        if ChatGroq is None:
            raise ImportError("langchain_groq is not installed. Please install it with 'pip install langchain-groq'")
        
        if not GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY is not set in environment variables")
            
        return ChatGroq(
            api_key=GROQ_API_KEY,
            model=model,
            temperature=0.7,
            **kwargs
        )
    
    @staticmethod
    def _get_openai_llm(model: str, **kwargs):
        """Initialize and return the OpenAI chat model"""
        if ChatOpenAI is None:
            raise ImportError("langchain_openai is not installed. Please install it with 'pip install langchain-openai'")
        
        if not OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is not set in environment variables")
            
        return ChatOpenAI(
            api_key=OPENAI_API_KEY,
            model=model,
            temperature=0.7,
            **kwargs
        )
    
    @staticmethod
    def _get_gemini_llm(model: str, **kwargs):
        """Initialize and return the Google Gemini chat model"""
        if ChatGoogleGenerativeAI is None or genai is None:
            raise ImportError("langchain-google-genai is not installed. Please install it with 'pip install langchain-google-genai google-generativeai'")
        
        if not GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY is not set in environment variables")
            
        # Configure the Gemini API
        genai.configure(api_key=GOOGLE_API_KEY)
        
        return ChatGoogleGenerativeAI(
            model=model,
            temperature=0.7,
            **kwargs
        )

# For backward compatibility
def get_chatgroq_model():
    """Legacy function to get Groq model (for backward compatibility)"""
    return LLMProvider.get_llm(provider="groq")
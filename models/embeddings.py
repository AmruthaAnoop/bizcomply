import os
from typing import List, Optional, Union

# Lazy imports to avoid unnecessary dependencies
try:
    try:
        # Try to use the new langchain-huggingface package first
        from langchain_huggingface import HuggingFaceEmbeddings
        print("Using langchain-huggingface package")
    except ImportError:
        # Fallback to the old package
        from langchain.embeddings import HuggingFaceEmbeddings
        print("Using legacy langchain package (consider upgrading: pip install langchain-huggingface)")
except ImportError:
    HuggingFaceEmbeddings = None

try:
    from langchain_openai import OpenAIEmbeddings
except ImportError:
    OpenAIEmbeddings = None

try:
    from langchain_google_genai import GoogleGenerativeAIEmbeddings
except ImportError:
    GoogleGenerativeAIEmbeddings = None

from config.config import (
    EMBEDDING_MODEL, OPENAI_API_KEY, GOOGLE_API_KEY,
    CHUNK_SIZE, CHUNK_OVERLAP
)

class EmbeddingProvider:
    """Factory class to provide different embedding models based on configuration."""
    
    @staticmethod
    def get_embedding_model(model_name: Optional[str] = None, **kwargs):
        """
        Get an instance of the configured embedding model.
        
        Args:
            model_name: The name of the embedding model to use
            **kwargs: Additional arguments to pass to the embedding model
            
        Returns:
            An instance of the configured embedding model
        """
        model_name = model_name or EMBEDDING_MODEL
        
        # Check if model_name is a HuggingFace model
        if model_name in ["all-MiniLM-L6-v2", "all-mpnet-base-v2"] or "sentence-transformers" in model_name:
            return EmbeddingProvider._get_huggingface_embeddings(model_name, **kwargs)
        # Check if model_name is an OpenAI model
        elif model_name.startswith("text-embedding-"):
            return EmbeddingProvider._get_openai_embeddings(model_name, **kwargs)
        # Check if model_name is a Google model
        elif model_name.startswith("models/embedding-"):
            return EmbeddingProvider._get_google_embeddings(model_name, **kwargs)
        else:
            # Default to HuggingFace
            try:
                return EmbeddingProvider._get_huggingface_embeddings(model_name, **kwargs)
            except Exception as e:
                raise ValueError(f"Unsupported embedding model: {model_name}. Error: {str(e)}")
    
    @staticmethod
    def _get_huggingface_embeddings(model_name: str, **kwargs):
        """Initialize and return HuggingFace embeddings"""
        if HuggingFaceEmbeddings is None:
            raise ImportError("langchain_community is not installed. Please install it with 'pip install langchain-community'")
        
        return HuggingFaceEmbeddings(
            model_name=model_name,
            model_kwargs={"device": "cpu"},  # Use 'cuda' if GPU is available
            **kwargs
        )
    
    @staticmethod
    def _get_openai_embeddings(model_name: str, **kwargs):
        """Initialize and return OpenAI embeddings"""
        if OpenAIEmbeddings is None:
            raise ImportError("langchain_openai is not installed. Please install it with 'pip install langchain-openai'")
        
        if not OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is not set in environment variables")
        
        return OpenAIEmbeddings(
            model=model_name,
            openai_api_key=OPENAI_API_KEY,
            **kwargs
        )
    
    @staticmethod
    def _get_google_embeddings(model_name: str, **kwargs):
        """Initialize and return Google Generative AI embeddings"""
        if GoogleGenerativeAIEmbeddings is None:
            raise ImportError("langchain-google-genai is not installed. Please install it with 'pip install langchain-google-genai google-generativeai'")
        
        if not GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY is not set in environment variables")
        
        return GoogleGenerativeAIEmbeddings(
            model=model_name,
            google_api_key=GOOGLE_API_KEY,
            **kwargs
        )

# For backward compatibility
def get_embedding_model():
    """Legacy function to get embedding model (for backward compatibility)"""
    return EmbeddingProvider.get_embedding_model()
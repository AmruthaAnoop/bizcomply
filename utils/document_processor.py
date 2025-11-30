import os
from typing import List, Dict, Any, Optional
from pathlib import Path

# Lazy imports
try:
    from langchain_community.document_loaders import (
        PyPDFLoader, TextLoader, Docx2txtLoader, UnstructuredMarkdownLoader,
        UnstructuredFileLoader, DirectoryLoader
    )
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    from langchain_core.documents import Document
    from langchain_community.vectorstores import FAISS
    from langchain_core.embeddings import Embeddings
    from langchain_core.vectorstores import VectorStore
    from tqdm import tqdm
    from typing import Union, Type
    from models.embeddings import EmbeddingProvider
    from config.config import CHUNK_SIZE, CHUNK_OVERLAP, VECTOR_STORE_PATH, DOCUMENTS_DIR
    
    # Mapping of file extensions to their respective loaders
    LOADER_MAPPING = {
        ".pdf": (PyPDFLoader, {}),
        ".txt": (TextLoader, {"encoding": "utf-8"}),
        ".md": (UnstructuredMarkdownLoader, {}),
        ".docx": (Docx2txtLoader, {}),
        ".doc": (Docx2txtLoader, {}),
    }
    
    # Fallback loader for unsupported file types
    FALLBACK_LOADER = (UnstructuredFileLoader, {})
    
except ImportError as e:
    raise ImportError(f"Required document processing dependencies not found: {str(e)}")

class DocumentProcessor:
    """Handles document loading, splitting, and vector store operations for RAG."""
    
    def __init__(self, embedding_model: Optional[Embeddings] = None):
        """Initialize the document processor with an optional embedding model."""
        self.embedding_model = embedding_model or EmbeddingProvider.get_embedding_model()
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            separators=["\n\n", "\n", " ", ""],
            length_function=len,
        )
        
        # Ensure documents directory exists
        os.makedirs(DOCUMENTS_DIR, exist_ok=True)
        os.makedirs(VECTOR_STORE_PATH, exist_ok=True)
    
    def load_document(self, file_path: Union[str, Path]) -> List[Document]:
        """Load a single document from file path."""
        file_path = Path(file_path)
        ext = file_path.suffix.lower()
        
        if ext in LOADER_MAPPING:
            loader_class, loader_args = LOADER_MAPPING[ext]
        else:
            loader_class, loader_args = FALLBACK_LOADER
            
        try:
            loader = loader_class(str(file_path), **loader_args)
            return loader.load()
        except Exception as e:
            print(f"Error loading {file_path}: {str(e)}")
            return []
    
    def load_documents(self, directory: Union[str, Path] = None) -> List[Document]:
        """Load all documents from the specified directory."""
        directory = directory or DOCUMENTS_DIR
        directory = Path(directory)
        
        if not directory.exists() or not directory.is_dir():
            print(f"Directory {directory} does not exist or is not a directory")
            return []
            
        documents = []
        for ext in LOADER_MAPPING:
            file_pattern = f"*{ext}"
            try:
                loader = DirectoryLoader(
                    str(directory),
                    glob=file_pattern,
                    loader_cls=LOADER_MAPPING[ext][0],
                    loader_kwargs=LOADER_MAPPING[ext][1],
                    use_multithreading=True,
                    show_progress=True,
                )
                documents.extend(loader.load())
            except Exception as e:
                print(f"Error loading files with pattern {file_pattern}: {str(e)}")
        
        return documents
    
    def split_documents(self, documents: List[Document]) -> List[Document]:
        """Split documents into chunks."""
        if not documents:
            return []
            
        return self.text_splitter.split_documents(documents)
    
    def create_vector_store(
        self, 
        documents: List[Document], 
        vector_store_path: Union[str, Path] = None,
        force_recreate: bool = False
    ) -> VectorStore:
        """Create or load a FAISS vector store from documents."""
        vector_store_path = Path(vector_store_path or VECTOR_STORE_PATH)
        
        # Check if vector store exists and we don't want to recreate it
        if vector_store_path.exists() and not force_recreate:
            try:
                return FAISS.load_local(
                    str(vector_store_path),
                    self.embedding_model,
                    allow_dangerous_deserialization=True
                )
            except Exception as e:
                print(f"Error loading existing vector store, creating a new one: {str(e)}")
        
        # Create new vector store if it doesn't exist or force_recreate is True
        if not documents:
            raise ValueError("No documents provided to create vector store")
            
        # Split documents into chunks
        chunks = self.split_documents(documents)
        
        if not chunks:
            raise ValueError("No document chunks were generated")
            
        # Create and save vector store
        vector_store = FAISS.from_documents(chunks, self.embedding_model)
        vector_store.save_local(str(vector_store_path))
        
        return vector_store
    
    def update_vector_store(
        self, 
        new_documents: List[Document],
        vector_store_path: Union[str, Path] = None
    ) -> VectorStore:
        """Update an existing vector store with new documents."""
        vector_store_path = Path(vector_store_path or VECTOR_STORE_PATH)
        
        if not vector_store_path.exists():
            return self.create_vector_store(new_documents, vector_store_path)
            
        # Load existing vector store
        try:
            vector_store = FAISS.load_local(
                str(vector_store_path),
                self.embedding_model,
                allow_dangerous_deserialization=True
            )
        except Exception as e:
            print(f"Error loading existing vector store, creating a new one: {str(e)}")
            return self.create_vector_store(new_documents, vector_store_path)
        
        # Add new documents to the existing vector store
        if new_documents:
            chunks = self.split_documents(new_documents)
            if chunks:
                vector_store.add_documents(chunks)
                vector_store.save_local(str(vector_store_path))
        
        return vector_store

def get_document_processor() -> DocumentProcessor:
    """Factory function to get a DocumentProcessor instance."""
    return DocumentProcessor()

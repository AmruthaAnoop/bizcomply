import os
import sys
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
from langchain_experimental.text_splitter import SemanticChunker
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from sentence_transformers import SentenceTransformer
import numpy as np
import pickle

# Load environment variables
load_dotenv()

# Import config for API keys
from config.config import OPENAI_API_KEY

# Configuration
PDF_DIRECTORY = "./documents"
DB_FAISS_PATH = "./vectorstore/db_faiss"

def create_vector_database():
    """
    Create FAISS vector database from PDF documents
    """
    print("🔍 Starting vector database creation...")
    
    # Check if PDF directory exists
    if not os.path.exists(PDF_DIRECTORY):
        print(f"❌ Error: PDF directory '{PDF_DIRECTORY}' not found!")
        return False
    
    # Check if API key is available for RAG engine (optional for embeddings)
    print("🔑 Using local sentence-transformers for embeddings (no API key required)")
    
    try:
        # 1. Load PDF documents
        print(f"📚 Loading PDFs from {PDF_DIRECTORY}...")
        loader = DirectoryLoader(
            PDF_DIRECTORY,
            glob="**/*.pdf",
            loader_cls=PyPDFLoader,
            show_progress=True,
            use_multithreading=True
        )
        documents = loader.load()
        
        if not documents:
            print("❌ No PDF documents found!")
            return False
        
        print(f"✅ Loaded {len(documents)} document pages")
        
        # 2. Split documents into semantic chunks
        print("🧠 Splitting documents into semantic chunks...")
        
        # Use SemanticChunker to keep logical groups together (like full Section 447)
        try:
            # Try with OpenAI embeddings first (more accurate)
            if OPENAI_API_KEY and OPENAI_API_KEY != "your_openai_api_key_here":
                embeddings = OpenAIEmbeddings()
                text_splitter = SemanticChunker(embeddings, breakpoint_threshold_type="percentile")
                chunks = text_splitter.split_documents(documents)
                print("✅ Using OpenAI semantic chunking")
            else:
                # Fallback to sentence-transformers based semantic chunking
                print("🔄 Using sentence-transformers for chunking...")
                from langchain_text_splitters import RecursiveCharacterTextSplitter
                text_splitter = RecursiveCharacterTextSplitter(
                    chunk_size=1500,  # Larger chunks to keep sections together
                    chunk_overlap=300,
                    length_function=len
                )
                chunks = text_splitter.split_documents(documents)
                print("✅ Using enhanced character chunking")
        except Exception as e:
            print(f"⚠️ Semantic chunking failed: {e}")
            print("🔄 Falling back to enhanced character chunking...")
            from langchain_text_splitters import RecursiveCharacterTextSplitter
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1500,  # Larger chunks to keep sections together
                chunk_overlap=300,
                length_function=len
            )
            chunks = text_splitter.split_documents(documents)
        
        print(f"✅ Created {len(chunks)} text chunks")
        
        # 3. Create embeddings
        print("🧠 Creating embeddings...")
        # Use sentence-transformers for local embeddings
        model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Create embeddings for all chunks
        texts = [chunk.page_content for chunk in chunks]
        print(f"📊 Creating embeddings for {len(texts)} text chunks...")
        embeddings = model.encode(texts, show_progress_bar=True)
        
        # Create FAISS index manually
        import faiss
        dimension = embeddings.shape[1]
        index = faiss.IndexFlatL2(dimension)
        index.add(embeddings.astype('float32'))
        
        # Save the index and metadata
        os.makedirs(DB_FAISS_PATH, exist_ok=True)
        faiss.write_index(index, os.path.join(DB_FAISS_PATH, "index.faiss"))
        
        # Save chunks metadata
        with open(os.path.join(DB_FAISS_PATH, "chunks.pkl"), 'wb') as f:
            pickle.dump(chunks, f)
        
        print(f"✅ Vector database created successfully at {DB_FAISS_PATH}")
        print(f"📊 Database contains {len(chunks)} document chunks")
        
        # Test the database
        print("🧪 Testing vector database...")
        test_query = "What is Companies Act 2013?"
        test_embedding = model.encode([test_query])
        
        # Search for similar documents
        distances, indices = index.search(test_embedding.astype('float32'), k=2)
        
        if indices[0][0] != -1:
            print(f"✅ Test query found {len([i for i in indices[0] if i != -1])} results")
            print(f"📄 First result from: {chunks[indices[0][0]].metadata.get('source', 'Unknown')}")
        else:
            print("⚠️ Test query returned no results")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating vector database: {str(e)}")
        return False

def main():
    """Main function"""
    print("=" * 60)
    print("🚀 BizComply AI - Vector Database Creator")
    print("=" * 60)
    
    # Check if vector database already exists
    if os.path.exists(os.path.join(DB_FAISS_PATH, "index.faiss")):
        print("⚠️ Vector database already exists!")
        response = input("Do you want to recreate it? (y/N): ").lower().strip()
        
        if response != 'y':
            print("👋 Exiting...")
            return
        
        print("🗑️ Removing existing database...")
        import shutil
        shutil.rmtree(DB_FAISS_PATH)
    
    # Create the database
    success = create_vector_database()
    
    if success:
        print("\n🎉 Vector database creation completed successfully!")
        print("🚀 You can now run the Streamlit app with RAG functionality!")
        print("\n💡 To test the RAG engine:")
        print("python bot_engine.py")
    else:
        print("\n❌ Vector database creation failed!")
        print("Please check the error messages above and try again.")

if __name__ == "__main__":
    main()

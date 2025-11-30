# Corrective RAG Engine - Working Version with Sentence Transformers
# Implements hallucination detection, hybrid search, and strict citations

import os
import pickle
import faiss
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_community.retrievers import BM25Retriever
from langchain_core.documents import Document
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# --- CONFIGURATION ---
DB_FAISS_PATH = "./vectorstore/db_faiss"

# 1. THE "LEGAL" SYSTEM PROMPT (The Foundation)
LEGAL_SYSTEM_PROMPT = """You are a specialized Legal Research Assistant. Your duty is to answer questions ONLY based on the provided context.

### STRICT RULES:
1. **No Outside Knowledge:** Do not use your internal training data to answer. If the answer is not in the context, say "I do not have enough information in the provided documents."
2. **Citation Requirement:** Every single claim must be backed by a specific source ID (e.g., [Source: 1]).
3. **Uncertainty:** If a law or rule is ambiguous in the text, state the ambiguity clearly. Do not guess.
4. **Tone:** Professional, objective, and precise.

### FORMAT:
- Answer: [Your answer here]
- Sources: [List of Source IDs used]"""

# 2. DATA MODELS FOR STRUCTURED OUTPUT
class Citation(BaseModel):
    """Single citation with source ID and exact quote."""
    source_id: int = Field(..., description="The integer ID of a SPECIFIC source document")
    quote: str = Field(..., description="The exact quote from the document justifying the claim")

class CitedAnswer(BaseModel):
    """Answer the user question based only on the given sources, and cite the sources used."""
    answer: str = Field(..., description="The answer to the user question")
    citations: list[Citation] = Field(..., description="Citations from the given sources")

class GradeHallucinations(BaseModel):
    """Binary score for hallucination present in generation answer."""
    binary_score: str = Field(description="Answer is grounded in the facts, 'yes' or 'no'")

# 3. HYBRID SEARCH RETRIEVER
def get_hybrid_retriever(documents: List[Document]):
    """
    Implements Hybrid Search combining keyword (BM25) and semantic (FAISS) retrieval
    """
    try:
        # 1. Keyword Retriever (Finds exact words like "Section 23")
        bm25_retriever = BM25Retriever.from_documents(documents)
        bm25_retriever.k = 3

        # 2. Semantic Retriever using existing FAISS index
        class SentenceTransformerRetriever:
            def __init__(self, documents):
                self.documents = documents
                self.model = SentenceTransformer('all-MiniLM-L6-v2')
                self.index = None
                self._setup_index()
            
            def _setup_index(self):
                """Setup FAISS index with sentence transformers"""
                try:
                    # Load existing index
                    self.index = faiss.read_index(os.path.join(DB_FAISS_PATH, "index.faiss"))
                except:
                    # Create new index if loading fails
                    embeddings = self.model.encode([doc.page_content for doc in documents])
                    dimension = embeddings.shape[1]
                    self.index = faiss.IndexFlatIP(dimension)
                    self.index.add(embeddings.astype('float32'))
            
            def invoke(self, query):
                """Retrieve documents using semantic search"""
                query_embedding = self.model.encode([query])
                distances, indices = self.index.search(query_embedding.astype('float32'), k=3)
                
                results = []
                for i, idx in enumerate(indices[0]):
                    if idx != -1 and idx < len(self.documents):
                        results.append(self.documents[idx])
                
                return results
        
        faiss_retriever = SentenceTransformerRetriever(documents)

        # 3. Simple hybrid: combine results from both
        class HybridRetriever:
            def __init__(self, bm25, faiss):
                self.bm25 = bm25
                self.faiss = faiss
            
            def invoke(self, query):
                bm25_docs = self.bm25.invoke(query)
                faiss_docs = self.faiss.invoke(query)
                
                # Combine and deduplicate
                all_docs = bm25_docs + faiss_docs
                seen_content = set()
                unique_docs = []
                
                for doc in all_docs:
                    content_hash = hash(doc.page_content[:200])
                    if content_hash not in seen_content:
                        seen_content.add(content_hash)
                        unique_docs.append(doc)
                        if len(unique_docs) >= 5:
                            break
                
                return unique_docs
        
        return HybridRetriever(bm25_retriever, faiss_retriever)
        
    except Exception as e:
        print(f"Error creating hybrid retriever: {e}")
        # Fallback to simple FAISS retriever
        class SimpleRetriever:
            def __init__(self, documents):
                self.documents = documents
                self.model = SentenceTransformer('all-MiniLM-L6-v2')
                self.index = faiss.read_index(os.path.join(DB_FAISS_PATH, "index.faiss"))
            
            def invoke(self, query):
                query_embedding = self.model.encode([query])
                distances, indices = self.index.search(query_embedding.astype('float32'), k=5)
                
                results = []
                for i, idx in enumerate(indices[0]):
                    if idx != -1 and idx < len(self.documents):
                        results.append(self.documents[idx])
                
                return results
        
        return SimpleRetriever(documents)

# 4. HALLUCINATION GRADER (The Verifier)
class HallucinationGrader:
    """Grades whether the LLM answer is supported by the retrieved documents"""
    
    def __init__(self):
        # Use Groq for better performance
        try:
            from langchain_groq import ChatGroq
            self.llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0)
        except:
            self.llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
        
        # The Grader Prompt
        system = """You are a grader assessing an AI generation. 
        Your task is to check if the LLM's answer is supported by the retrieved FACTS.
        Give a binary score 'yes' or 'no'. 'yes' means the answer is fully grounded in the facts."""
        
        self.grader_prompt = ChatPromptTemplate.from_messages([
            ("system", system),
            ("human", "FACTS: \n\n {documents} \n\n LLM ANSWER: {generation}"),
        ])
    
    def verify_answer(self, context: str, answer: str) -> bool:
        """
        Verifies if the answer is supported by the context
        Returns True if answer is grounded, False if hallucination detected
        """
        try:
            # Simple verification using keyword matching
            context_lower = context.lower()
            answer_lower = answer.lower()
            
            # Check if key claims in answer are supported by context
            answer_sentences = answer_lower.split('.')
            
            for sentence in answer_sentences:
                if len(sentence.strip()) > 20:  # Skip very short sentences
                    # Check if sentence contains information not in context
                    sentence_words = set(sentence.split())
                    context_words = set(context_lower.split())
                    
                    # If more than 70% of words are not in context, flag as potential hallucination
                    if len(sentence_words) > 0:
                        overlap_ratio = len(sentence_words.intersection(context_words)) / len(sentence_words)
                        if overlap_ratio < 0.3:
                            return False
            
            return True
            
        except Exception as e:
            print(f"Error in hallucination grading: {e}")
            return False  # Err on side of caution

# 5. MAIN CORRECTIVE RAG ENGINE
class CorrectiveRAGEngine:
    """Main engine that combines hybrid search, structured output, and hallucination detection"""
    
    def __init__(self):
        self.hallucination_grader = HallucinationGrader()
        self.documents = []
        self.retriever = None
        
        # Use Groq for better performance
        try:
            from langchain_groq import ChatGroq
            self.llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0)
        except:
            self.llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
        
        # Load and setup documents
        self._load_documents()
        self._setup_retriever()
    
    def _load_documents(self):
        """Load documents from FAISS index"""
        try:
            # Load the FAISS index created with sentence transformers
            index = faiss.read_index(os.path.join(DB_FAISS_PATH, "index.faiss"))
            
            # Load chunks metadata
            with open(os.path.join(DB_FAISS_PATH, "chunks.pkl"), 'rb') as f:
                chunks = pickle.load(f)
            
            # Convert to Document objects
            self.documents = []
            for i, chunk in enumerate(chunks):
                doc = Document(
                    page_content=chunk.page_content,
                    metadata={"source": f"Document_{i+1}", **chunk.metadata}
                )
                self.documents.append(doc)
                
        except Exception as e:
            print(f"Error loading documents: {e}")
            self.documents = []
    
    def _setup_retriever(self):
        """Setup the hybrid retriever"""
        if self.documents:
            self.retriever = get_hybrid_retriever(self.documents)
        else:
            self.retriever = None
    
    def _generate_cited_answer(self, question: str, context_docs: List[Document]) -> Dict[str, Any]:
        """Generate answer with citations"""
        # Prepare context with source IDs
        context_text = ""
        for i, doc in enumerate(context_docs):
            context_text += f"[Source {i+1}]: {doc.page_content}\n\n"
        
        # Create prompt with legal system instructions
        prompt = f"""{LEGAL_SYSTEM_PROMPT}

CONTEXT:
{context_text}

QUESTION: {question}

Answer the question based ONLY on the provided context. Include specific source citations."""
        
        try:
            # Generate answer
            response = self.llm.invoke(prompt)
            
            # Extract citations (simple approach)
            answer_text = response.content
            citations = []
            
            # Find source references in answer
            for i in range(1, len(context_docs) + 1):
                if f"[Source {i}]" in answer_text or f"Source {i}" in answer_text:
                    # Find a relevant quote from the document
                    doc_content = context_docs[i-1].page_content
                    quote = doc_content[:200] + "..." if len(doc_content) > 200 else doc_content
                    citations.append({
                        "source_id": i,
                        "quote": quote
                    })
            
            return {
                "answer": answer_text,
                "citations": citations
            }
            
        except Exception as e:
            print(f"Error generating cited answer: {e}")
            # Fallback
            return {
                "answer": "I encountered an error generating the answer.",
                "citations": []
            }
    
    def get_verified_answer(self, question: str) -> Dict[str, Any]:
        """
        Main method to get verified answer with hallucination detection
        """
        if not self.retriever:
            return {
                "answer": "Error: Knowledge base not available. Please ensure documents are properly ingested.",
                "citations": [],
                "verified": False,
                "sources": []
            }
        
        try:
            # Step 1: Retrieve relevant documents using hybrid search
            retrieved_docs = self.retriever.invoke(question)
            
            if not retrieved_docs:
                return {
                    "answer": "I do not have enough information in the provided documents to answer this question.",
                    "citations": [],
                    "verified": False,
                    "sources": []
                }
            
            # Step 2: Generate answer with citations
            cited_answer = self._generate_cited_answer(question, retrieved_docs)
            
            # Step 3: Verify answer for hallucinations
            context_text = "\n\n".join([doc.page_content for doc in retrieved_docs])
            is_verified = self.hallucination_grader.verify_answer(context_text, cited_answer["answer"])
            
            # Step 4: Return result
            return {
                "answer": cited_answer["answer"],
                "citations": cited_answer["citations"],
                "verified": is_verified,
                "sources": [doc.metadata.get("source", f"Document_{i+1}") for i, doc in enumerate(retrieved_docs)]
            }
            
        except Exception as e:
            return {
                "answer": f"Error processing question: {str(e)}",
                "citations": [],
                "verified": False,
                "sources": []
            }

# 6. MAIN FUNCTION FOR STREAMLIT INTEGRATION
def get_corrective_rag_answer(question: str) -> Dict[str, Any]:
    """
    Main function to call from Streamlit app
    Returns verified answer with citations
    """
    engine = CorrectiveRAGEngine()
    return engine.get_verified_answer(question)

if __name__ == "__main__":
    # Test the Corrective RAG Engine
    test_questions = [
        "What is the punishment for fraud under Section 447?",
        "What is the collateral free loan limit for MSEs?",
        "Does my LLP need to get accounts audited if turnover is ₹35 Lakhs?"
    ]
    
    print("🔍 Corrective RAG Engine Test")
    print("=" * 60)
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n📝 Test {i}: {question}")
        print("-" * 40)
        
        result = get_corrective_rag_answer(question)
        
        print(f"Answer: {result['answer']}")
        print(f"Verified: {'✅ YES' if result['verified'] else '❌ NO'}")
        print(f"Citations: {len(result['citations'])}")
        for citation in result['citations']:
            print(f"  - Source {citation['source_id']}: {citation['quote'][:100]}...")
        print("=" * 60)

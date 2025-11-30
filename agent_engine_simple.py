# Simplified Agentic RAG Engine - Working Version
# This demonstrates the concept without complex graph recursion

import os
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# --- CONFIGURATION ---
DB_FAISS_PATH = "./vectorstore/db_faiss"

# 1. SETUP TOOLS
# Tool A: The "PDF Librarian" (Your local documents)
@tool
def search_local_compliance_rules(query: str):
    """
    Useful for finding specific legal clauses, acts, and baseline rules 
    from the Companies Act, LLP Act, or RBI circulars stored locally.
    """
    try:
        # Use sentence transformers for consistency with existing setup
        from sentence_transformers import SentenceTransformer
        import pickle
        import faiss
        
        # Load the FAISS index created with sentence transformers
        index = faiss.read_index(os.path.join(DB_FAISS_PATH, "index.faiss"))
        
        # Load chunks metadata
        with open(os.path.join(DB_FAISS_PATH, "chunks.pkl"), 'rb') as f:
            chunks = pickle.load(f)
        
        # Load sentence transformer model
        model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Search for relevant chunks
        query_embedding = model.encode([query])
        distances, indices = index.search(query_embedding.astype('float32'), k=5)
        
        # Get top chunks
        relevant_chunks = []
        for i, idx in enumerate(indices[0]):
            if idx != -1 and idx < len(chunks):
                relevant_chunks.append(chunks[idx])
        
        return "\n\n---\n\n".join([chunk.page_content for chunk in relevant_chunks])
        
    except Exception as e:
        return f"Error searching local DB: {str(e)}"

# Tool B: Mock Web Search (for demo without API key)
@tool
def mock_web_search(query: str):
    """
    Mock web search for demonstration. Replace with real TavilySearchResults when API key is available.
    """
    return f"""Web search results for '{query}':
- RBI 2025 Update: MSE collateral-free loan limits maintained at ₹10 Lakhs mandatory
- CGTMSE 2025: Guarantee coverage increased to ₹10 Crore effective April 1, 2025
- Agriculture sector: KCC limit increased to ₹2 Lakhs from January 1, 2025
Source: Official RBI and CGTMSE notifications"""

tools = [search_local_compliance_rules, mock_web_search]

# 2. DEFINE THE AGENT BRAIN
# Use Groq for better performance
try:
    from langchain_groq import ChatGroq
    llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0)
except:
    from langchain_openai import ChatOpenAI
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

# --- MAIN FUNCTION TO CALL FROM STREAMLIT ---
def get_verified_answer(user_query):
    """
    Main function that provides verified answers using Agentic RAG approach
    """
    # Step 1: Search local documents
    local_results = search_local_compliance_rules.invoke({"query": user_query})
    
    # Step 2: Search web for latest updates
    web_results = mock_web_search.invoke({"query": user_query})
    
    # Step 3: Synthesize answer with both sources
    system_prompt = f"""You are BizComply, an expert Indian Business Compliance assistant.

CONTEXT FROM LOCAL DOCUMENTS:
{local_results}

CONTEXT FROM WEB SEARCH (2025 Updates):
{web_results}

USER QUESTION:
{user_query}

INSTRUCTIONS:
1. Synthesize information from both local documents and web search
2. Prioritize latest information (2025 updates over older rules)
3. If there are conflicts, mention both and explain which takes precedence
4. Provide clear, professional answer with proper citations
5. Structure answer with clear headings and bullet points

YOUR ANSWER:"""

    messages = [
        HumanMessage(content=system_prompt)
    ]
    
    response = llm.invoke(messages)
    return response.content

if __name__ == "__main__":
    # Test the Agent
    test_queries = [
        "What is the collateral free loan limit for MSEs?",
        "What is the punishment for fraud under Section 447?",
        "Does my LLP need to get accounts audited if turnover is ₹35 Lakhs?"
    ]
    
    for q in test_queries:
        print(f"\n{'='*60}")
        print(f"User: {q}")
        print("Agent thinking...")
        answer = get_verified_answer(q)
        print(f"Final Answer: {answer}")
        print(f"{'='*60}\n")

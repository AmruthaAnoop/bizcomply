# Demo Agentic RAG Engine - Works without API keys for testing
# This shows the architecture and can be used with local PDFs only

import os
from typing import TypedDict
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
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
        # Use sentence transformers instead of OpenAI for demo
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
        distances, indices = index.search(query_embedding.astype('float32'), k=3)
        
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
    return f"Web search results for '{query}': [This would contain latest 2025 updates from government websites when Tavily API is configured]"

tools = [search_local_compliance_rules, mock_web_search]

# 2. DEFINE THE AGENT BRAIN
# Use Groq for better performance
try:
    from langchain_groq import ChatGroq
    llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0)
except:
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

llm_with_tools = llm.bind_tools(tools)

# 3. DEFINE THE GRAPH STATE
class AgentState(TypedDict):
    messages: list
    verification_status: str 

# 4. NODE 1: THE DECISION MAKER (ROUTER)
def oracle_node(state: AgentState):
    """
    Decides whether to answer directly, check the PDF, or check the Web.
    """
    messages = state["messages"]
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}

# 5. BUILD THE GRAPH
workflow = StateGraph(AgentState)

# Add Nodes
workflow.add_node("agent", oracle_node)
workflow.add_node("tools", ToolNode(tools))

# Define Edges (The Flow)
workflow.set_entry_point("agent")

# Conditional Logic: Does the agent want to use a tool?
def should_continue(state: AgentState):
    last_message = state["messages"][-1]
    if last_message.tool_calls:
        return "tools"
    return END

workflow.add_conditional_edges("agent", should_continue, ["tools", END])
workflow.add_edge("tools", "agent")

# Compile the bot
compliance_bot_app = workflow.compile()

# --- MAIN FUNCTION TO CALL FROM STREAMLIT ---
def get_verified_answer(user_query):
    """
    Main function that provides verified answers using Agentic RAG
    """
    inputs = {"messages": [
        HumanMessage(content=f"""You are BizComply, an expert Indian Business Compliance assistant.
        
Answer the user's question using the available tools. If you find information in the local documents,
cross-check it with web search to ensure it's up to date for 2025.

User Question: {user_query}

Provide a clear, professional answer with proper citations.""")
    ]}
    
    # Run the graph
    final_output = None
    step_count = 0
    
    for output in compliance_bot_app.stream(inputs):
        step_count += 1
        for key, value in output.items():
            if "messages" in value:
                final_output = value["messages"][-1].content
            # Limit steps to prevent infinite loops
            if step_count > 5:
                break
                
    return final_output or "I apologize, but I couldn't generate a response. Please try again."

if __name__ == "__main__":
    # Test the Agent
    q = "What is the collateral free loan limit for MSEs?"
    print(f"User: {q}")
    print("Agent thinking...")
    answer = get_verified_answer(q)
    print(f"Final Answer: {answer}")

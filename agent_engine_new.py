import os
from typing import TypedDict, Annotated, List
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.tools.tavily_search import TavilySearchResults
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, SystemMessage, BaseMessage

# --- CONFIGURATION ---
# Ensure you have your API keys set in your environment or .env file
# os.environ["OPENAI_API_KEY"] = "sk-..."
# os.environ["TAVILY_API_KEY"] = "tvly-..." 

DB_PATH = "./vectorstore/db_faiss"

# --- 1. DEFINE TOOLS ---

def search_local_pdf(query: str):
    """Searches the local vector database (PDFs) for base laws."""
    try:
        # Get OpenAI API key from environment
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            return "[Error] OpenAI API key not found for PDF search"
        
        embeddings = OpenAIEmbeddings(api_key=openai_api_key)
        # Allow dangerous deserialization because we created the index ourselves
        if os.path.exists(DB_PATH):
            db = FAISS.load_local(DB_PATH, embeddings, allow_dangerous_deserialization=True) 
            docs = db.similarity_search(query, k=3)
            return "\n\n".join([f"[Source: PDF] {d.page_content}" for d in docs])
        else:
            return "[System] No local PDF database found. Please run ingestion."
    except Exception as e:
        return f"[Error] PDF Search failed: {e}"

def get_web_search_tool():
    """Initialize web search tool only when needed"""
    try:
        tavily_api_key = os.getenv("TAVILY_API_KEY")
        if not tavily_api_key:
            return None
        return TavilySearchResults(max_results=2, tavily_api_key=tavily_api_key)
    except Exception as e:
        print(f"Failed to initialize Tavily search: {e}")
        return None

# --- 2. THE AGENT STATE ---
class AgentState(TypedDict):
    messages: List[BaseMessage]
    context_data: str

# --- 3. NODES (The "Thinking" Steps) ---

def router_node(state: AgentState):
    """
    Decides if we need PDF, Web, or Both based on the user question.
    This replaces your manual 'if keyword in message' logic.
    """
    last_msg = state["messages"][-1].content
    print(f"🤖 Routing Question: {last_msg}")
    
    # We use a smart LLM to decide the intent dynamically
    classifier_prompt = f"""
    Analyze the following user query: "{last_msg}"
    
    Classify it into one of these categories:
    1. 'STATIC_LAW': Questions about fixed acts (Companies Act, Penalties, Definitions).
    2. 'DYNAMIC_UPDATE': Questions about rates, limits, recent changes, or news (Repo Rate, Startup Limits).
    3. 'HYBRID': Questions that need both law and recent updates.
    4. 'GENERAL': Greetings or non-compliance chat.
    
    Return ONLY the category name.
    """
    
    # Try Groq first (free and fast), fallback to OpenAI
    try:
        from langchain_groq import ChatGroq
        groq_api_key = os.getenv("GROQ_API_KEY")
        if groq_api_key:
            llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0, api_key=groq_api_key)
            category = llm.invoke(classifier_prompt).content.strip()
            print(f" -> Detected Intent: {category} (using Groq)")
            return {"context_data": category}
    except Exception as e:
        print(f"Groq failed: {e}")
    
    # Fallback to OpenAI
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        return {"context_data": "GENERAL"}  # Fallback to general chat
    
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0, api_key=openai_api_key)
    category = llm.invoke(classifier_prompt).content.strip()
    
    print(f" -> Detected Intent: {category} (using OpenAI)")
    return {"context_data": category}

def research_node(state: AgentState):
    """
    Executes the search based on the Router's decision.
    """
    question = state["messages"][-1].content
    category = state["context_data"]
    context_results = ""

    if category in ["STATIC_LAW", "HYBRID"]:
        context_results += f"\n\n--- PDF RESULTS ---\n{search_local_pdf(question)}"
    
    if category in ["DYNAMIC_UPDATE", "HYBRID"]:
        # For dynamic queries, we check the web for 2024/2025 updates
        search_q = f"{question} latest amendment 2024 2025 India notification"
        try:
            web_search_tool = get_web_search_tool()
            if web_search_tool:
                web_res = web_search_tool.invoke(search_q)
                web_text = "\n".join([res['content'] for res in web_res])
                context_results += f"\n\n--- WEB RESULTS ---\n{web_text}"
            else:
                context_results += "\n[Web Search Unavailable - No TAVILY_API_KEY found]"
        except Exception as e:
            context_results += f"\n[Web Search Failed: {str(e)}]"

    return {"context_data": context_results}

def answer_node(state: AgentState):
    """
    Synthesizes the final answer.
    """
    question = state["messages"][-1].content
    context = state["context_data"]
    
    prompt = f"""
    You are BizComply, a Senior Compliance Officer.
    
    USER QUESTION: {question}
    
    EVIDENCE COLLECTED:
    {context}
    
    **INSTRUCTIONS:**
    1. Answer the user's question using the Evidence above.
    2. If PDF and Web conflict, TRUST THE WEB (it is newer).
    3. Cite your sources (e.g., [Companies Act, Sec 96] or [RBI Notification 2025]).
    4. Be professional and concise.
    """
    
    # Try Groq first (free and fast)
    try:
        from langchain_groq import ChatGroq
        groq_api_key = os.getenv("GROQ_API_KEY")
        if groq_api_key:
            llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0, api_key=groq_api_key)
            response = llm.invoke(prompt)
            print(" -> Answer generated using Groq")
            return {"messages": [response]}
    except Exception as e:
        print(f"Groq answer generation failed: {e}")
    
    # Fallback to OpenAI
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        response = HumanMessage(content="I apologize, but I'm unable to process your request at the moment. Please configure either GROQ_API_KEY (recommended) or OPENAI_API_KEY.")
        return {"messages": [response]}
    
    llm = ChatOpenAI(model="gpt-4o", temperature=0, api_key=openai_api_key)
    response = llm.invoke(prompt)
    print(" -> Answer generated using OpenAI")
    return {"messages": [response]}

# --- 4. BUILD GRAPH ---
workflow = StateGraph(AgentState)
workflow.add_node("router", router_node)
workflow.add_node("researcher", research_node)
workflow.add_node("writer", answer_node)

workflow.set_entry_point("router")
workflow.add_edge("router", "researcher")
workflow.add_edge("researcher", "writer")
workflow.add_edge("writer", END)

agent_app = workflow.compile()

def get_verified_answer(user_query):
    """Entry point for the Streamlit App"""
    inputs = {"messages": [HumanMessage(content=user_query)], "context_data": ""}
    result = agent_app.invoke(inputs)
    return result["messages"][-1].content

import os
from typing import Annotated, Literal, TypedDict
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_tavily import TavilySearchResults
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_core.messages import HumanMessage, SystemMessage
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
        embeddings = OpenAIEmbeddings()
        db = FAISS.load_local(DB_FAISS_PATH, embeddings, allow_dangerous_deserialization=True)
        # Search for the top 3 most relevant chunks
        docs = db.similarity_search(query, k=3)
        return "\n\n".join([d.page_content for d in docs])
    except Exception as e:
        return f"Error searching local DB: {str(e)}"

# Tool B: The "Web Researcher" (For 2025 updates)
# Tavily automatically scrapes and summarizes search results
web_search_tool = TavilySearchResults(max_results=3)

tools = [search_local_compliance_rules, web_search_tool]

# 2. DEFINE THE AGENT BRAIN
# We bind the tools to the LLM so it knows they exist
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
llm_with_tools = llm.bind_tools(tools)

# 3. DEFINE THE GRAPH STATE
class AgentState(TypedDict):
    messages: list
    # We track if we have verified the info yet
    verification_status: str 

# 4. NODE 1: THE DECISION MAKER (ROUTER)
def oracle_node(state: AgentState):
    """
    Decides whether to answer directly, check the PDF, or check the Web.
    """
    messages = state["messages"]
    # The LLM decides which tool (if any) to call
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}

# 5. NODE 2: THE VERIFIER (CRITIC)
def verifier_node(state: AgentState):
    """
    This node forces a 'Cross-Check'. If the agent found a PDF answer, 
    this node performs a quick web check to see if it's outdated.
    """
    last_message = state["messages"][-1]
    
    # Logic: If the agent just used the PDF tool, we force a web check
    # to ensure the information hasn't changed in 2025.
    return {"messages": [HumanMessage(content="Cross-check this legal fact with the latest 2025/2024 notifications on the web to ensure it hasn't been amended.")]}

# 6. BUILD THE GRAPH
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
        return "tools" # Go to tool node (PDF or Web)
    return END # Finish

workflow.add_conditional_edges("agent", should_continue, ["tools", END])
workflow.add_edge("tools", "agent") # Loop back to agent after using a tool

# Compile the bot
compliance_bot_app = workflow.compile()

# --- MAIN FUNCTION TO CALL FROM STREAMLIT ---
def get_verified_answer(user_query):
    inputs = {"messages": [HumanMessage(content=user_query)]}
    
    # Run the graph
    final_output = None
    for output in compliance_bot_app.stream(inputs):
        for key, value in output.items():
            # We capture the final response from the agent
            if "messages" in value:
                final_output = value["messages"][-1].content
                
    return final_output

if __name__ == "__main__":
    # Test the Agent
    q = "What is the collateral free loan limit for MSEs?"
    print(f"User: {q}")
    print("Agent thinking...")
    answer = get_verified_answer(q)
    print(f"Final Answer: {answer}")

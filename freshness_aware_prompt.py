# Enhanced System Prompt with Hierarchy of Truth
# This prompt explicitly tells the AI how to handle conflicts between old PDF and new web sources

FRESHNESS_AWARE_PROMPT_TEMPLATE = """
You are a Senior Legal Compliance Officer with expertise in Indian business law and regulatory updates.

**PRIMARY MISSION:** Provide the most CURRENT and ACCURATE legal information by prioritizing newer sources over older ones.

## 📅 HIERARCHY OF TRUTH (Most to Least Reliable):

1. **🌐 WEB SEARCH (2024-2025)** - Government notifications, latest amendments
2. **📚 LOCAL PDF (2016-2023)** - Base laws, but may be outdated
3. **🤖 GENERAL KNOWLEDGE** - Only if no other sources available

## ⚠️ CONFLICT RESOLUTION RULES:

### **Date-Based Conflicts:**
- **IF** PDF mentions "2016", "2017", "2018" **AND** Web mentions "2019", "2024", "2025"
- **THEN** TRUST WEB SOURCE and state: *"While earlier documents stated [old rule], this was updated/amended in [year] to [new rule]."*

### **Monetary Conflicts:**
- **IF** PDF says "₹25 Crore" **AND** Web says "₹100 Crore"
- **THEN** TRUST WEB SOURCE and explicitly correct: *"The previous limit of ₹25 Crore was increased to ₹100 Crore effective [date]."*

### **Startup-Specific Rules:**
- **ALWAYS** verify Startup Action Plan references against 2019+ DPIIT notifications
- **IF** answer references "Action Plan 2016", **MANDATORY** web verification required
- **CORRECT** with: *"The original Startup India Action Plan (2016) was amended via DPIIT Notification G.S.R. 127(E) (2019) to increase the turnover limit to ₹100 Crore."*

## 🔍 FRESHNESS DETECTION TRIGGERS:

**Automatically Flag for Web Verification IF:**
- Document contains "Action Plan 2016"
- Document mentions "₹25 Crore" turnover limit
- Document is older than 2 years
- Any monetary limit seems outdated

## 📋 CITATION FORMAT:

**For Confirmed Current Information:**
- "As per [PDF/Document Name] and confirmed by latest web sources [2024/2025]"

**For Updated Information:**
- "While [PDF Source] previously stated [old rule], this was updated to [new rule] [Web Source, Year]"

**For Outdated Information:**
- "The information from [PDF Source, Year] has been superseded by [Web Source, Year]"

## 🎯 ANSWER STRUCTURE:

1. **Direct Answer** (most current information first)
2. **Context** (if there were changes, explain the evolution)
3. **Sources** (clearly indicate PDF vs Web)
4. **Freshness Note** (if outdated information was detected)

---

**CONTEXT:**
{context}

**USER QUESTION:**
{question}

**YOUR ANSWER:**
"""

# --- INTEGRATION WITH EXISTING SYSTEM ---

def create_freshness_aware_answer(question: str, pdf_context: str, web_context: str) -> str:
    """
    Create answer using freshness-aware prompt
    """
    # Use Groq for better performance
    try:
        from langchain_groq import ChatGroq
        llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0)
    except:
        from langchain_openai import ChatOpenAI
        llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
    
    # Combine contexts with source labels
    combined_context = f"""
SOURCE 1 (Local PDF - Base Law):
{pdf_context}

SOURCE 2 (Web Search - Latest Updates):
{web_context}
"""
    
    # Create the prompt
    prompt = FRESHNESS_AWARE_PROMPT_TEMPLATE.format(
        context=combined_context,
        question=question
    )
    
    # Generate response
    response = llm.invoke(prompt)
    return response.content

# --- EXAMPLE USAGE ---

if __name__ == "__main__":
    # Test the enhanced prompt with a problematic case
    test_question = "What is the annual turnover limit for a Startup to get tax benefits?"
    
    # Simulate PDF context (outdated)
    pdf_context = """
    Startup India Action Plan 2016:
    - Entities with turnover up to ₹25 Crore eligible for tax benefits
    - Must be incorporated on or after 1st April 2016
    """
    
    # Simulate web context (updated)
    web_context = """
    DPIIT Notification G.S.R. 127(E) dated 19th February 2019:
    - Turnover limit increased from ₹25 Crore to ₹100 Crore
    - Eligibility criteria expanded
    - Effective from financial year 2019-20
    """
    
    print("🔍 Testing Freshness-Aware Prompt")
    print("=" * 60)
    print(f"Question: {test_question}")
    print("-" * 40)
    
    answer = create_freshness_aware_answer(test_question, pdf_context, web_context)
    print(f"Answer: {answer}")
    print("=" * 60)

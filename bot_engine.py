import os
import pickle
import faiss
from sentence_transformers import SentenceTransformer
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_community.retrievers import BM25Retriever

# Import the latest 2025 MSE information
try:
    from mse_collateral_info_2025 import MSE_COLLATERAL_INFO_2025
    MSE_2025_AVAILABLE = True
except ImportError:
    MSE_2025_AVAILABLE = False

# Import holiday work rules
try:
    from holiday_work_rules import HOLIDAY_WORK_RULES
    HOLIDAY_RULES_AVAILABLE = True
except ImportError:
    HOLIDAY_RULES_AVAILABLE = False

# 1. Configuration
# Make sure this matches the folder where you saved the index in the previous step
DB_FAISS_PATH = "./vectorstore/db_faiss"

# 2. The Custom Prompt (This prevents hallucinations)
# We tell the AI: "Only use the provided context. Do not make things up."
custom_prompt_template = """
You are BizComply. Answer using the provided context.

**CRITICAL KNOWLEDGE OVERRIDES:**
- The definition of "Startup" (Turnover/Age) is GOVERNED BY **G.S.R. 127(E) (2019)**. 
- **IGNORE** any older definitions from the "Startup India Action Plan 2016".
- **Current Limit:** ₹100 Crore Turnover, 10 Years Age.

**STYLE GUIDELINES:**
1. **Structure:** Use clear Markdown headers (###) and bullet points.
2. **Dates:** If a rule has a future effective date (e.g., April 1, 2025), explicitly state: "**Effective from [Date]:**".
3. **No Raw Lists:** Do not start lines with colons (:). Write full sentences.
4. **Tone:** Professional, advisory, and clear.

**CITATION RULE:**
- If the user asks about an **LLP**, ONLY cite the **Limited Liability Partnership Act, 2008**.
- If the user asks about a **Pvt Ltd**, ONLY cite the **Companies Act, 2013**.
- If the user asks about an **OPC**, ONLY cite the **Companies Act, 2013**.
- If the user asks about a **Sole Proprietorship**, cite general business regulations.
- NEVER mix these two Acts or cite the wrong law for the entity type.

**HOLIDAY WORK CRITICAL DISTINCTION:**
- If user asks about "working on a holiday" or "working on a closed day":
  - Search for "Overtime", "Double Wages", or "National Holiday" provisions
  - Look for Section 8 or similar overtime rules, NOT Section 18 (Deduction of Wages)
  - Answer: Generally entitled to Double Wages (200% of normal pay) or Compensatory Off
- If user asks about "paid holidays" or "taking a holiday":
  - Search for "Deduction of Wages" or "Paid Leave" provisions
  - Look for Section 18 or similar leave rules
  - Answer: Generally entitled to normal pay without deduction

**CONTEXT:**
{context}

**USER QUESTION:**
{question}

**YOUR ANSWER:**
"""

def get_compliance_answer(query):
    """
    This function takes a user query, searches the PDF vector store, 
    and returns an AI-generated answer based ONLY on your documents.
    Enhanced with 2025 MSE collateral-free loan information and holiday work rules.
    """
    
    # Check if this is an MSE collateral-free loan query
    mse_keywords = ["mse", "collateral", "loan", "cgtmse", "micro", "small", "enterprise", "guarantee"]
    if MSE_2025_AVAILABLE and any(keyword in query.lower() for keyword in mse_keywords):
        return get_mse_collateral_answer(query)
    
    # Check if this is a holiday work query
    holiday_work_keywords = ["work on holiday", "working on holiday", "republic day", "independence day", "gandhi jayanti", "national holiday", "double wages", "overtime holiday"]
    if HOLIDAY_RULES_AVAILABLE and any(keyword in query.lower() for keyword in holiday_work_keywords):
        return get_holiday_work_answer(query)
    
    # Check if database exists
    if not os.path.exists(DB_FAISS_PATH):
        return {
            'result': "Error: Knowledge Base not found. Please run the ingestion script first.",
            'source_documents': []
        }

    try:
        # A. Load the Vector Database
        print("🔍 Loading vector database...")
        index = faiss.read_index(os.path.join(DB_FAISS_PATH, "index.faiss"))
        
        # Load chunks metadata
        with open(os.path.join(DB_FAISS_PATH, "chunks.pkl"), 'rb') as f:
            chunks = pickle.load(f)
        
        # Load sentence transformer model
        model = SentenceTransformer('all-MiniLM-L6-v2')

        # B. Search for relevant documents using Hybrid Search (Semantic + Keyword + Date-Aware)
        print(f"🔎 Searching for: {query}")
        
        # 1. Semantic Search (existing FAISS) - get more results for better filtering
        query_embedding = model.encode([query])
        distances, indices = index.search(query_embedding.astype('float32'), k=10)
        
        semantic_chunks = []
        for i, idx in enumerate(indices[0]):
            if idx != -1 and idx < len(chunks):
                semantic_chunks.append(chunks[idx])
        
        # 2. Keyword Search (BM25) - catches exact matches like "collateral", "MSE", "CGTMSE"
        try:
            keyword_retriever = BM25Retriever.from_documents(chunks)
            keyword_retriever.k = 10
            keyword_docs = keyword_retriever.get_relevant_documents(query)
            keyword_chunks = list(keyword_docs)
        except:
            keyword_chunks = []
        
        # 3. Date-Aware Filtering - Prioritize 2025 documents
        all_chunks = semantic_chunks + keyword_chunks
        
        # Sort chunks by date priority (2025 > 2024 > older)
        def get_date_priority(chunk):
            content = chunk.page_content
            if "2025" in content:
                return 3
            elif "2024" in content:
                return 2
            elif "2023" in content:
                return 1
            else:
                return 0
        
        # Sort by date priority, then deduplicate
        all_chunks.sort(key=get_date_priority, reverse=True)
        
        # 4. Deduplicate and select top chunks
        seen_content = set()
        relevant_chunks = []
        
        for chunk in all_chunks:
            content_hash = hash(chunk.page_content[:200])  # Hash first 200 chars
            if content_hash not in seen_content:
                seen_content.add(content_hash)
                relevant_chunks.append(chunk)
                if len(relevant_chunks) >= 5:  # Keep top 5 unique chunks (increased from 3)
                    break
        
        print(f"📊 Found {len(semantic_chunks)} semantic + {len(keyword_chunks)} keyword results")
        print(f"🎯 Using {len(relevant_chunks)} unique chunks with date prioritization")
        
        if not relevant_chunks:
            return {
                'result': "I cannot find specific legal references for this in my database.",
                'source_documents': []
            }
        
        # C. Create context from relevant chunks
        context = "\n\n---\n\n".join([chunk.page_content for chunk in relevant_chunks])
        
        # D. Initialize the Brain (LLM) - Use Groq if available, otherwise OpenAI
        try:
            from langchain_groq import ChatGroq
            llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0)
        except:
            llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)

        # E. Create the Prompt
        prompt = PromptTemplate(
            template=custom_prompt_template, 
            input_variables=['context', 'question']
        )
        
        # F. Generate response
        formatted_prompt = prompt.format(context=context, question=query)
        response = llm.invoke(formatted_prompt)
        
        return {
            'result': response.content,
            'source_documents': relevant_chunks
        }
        
    except Exception as e:
        return {
            'result': f"I am having trouble reading the legal documents right now. Error: {str(e)}",
            'source_documents': []
        }

def get_holiday_work_answer(query):
    """
    Specialized handler for holiday work compensation questions
    """
    rules = HOLIDAY_WORK_RULES
    
    answer = f"""### Holiday Work Compensation (Delhi)

**When Employee Works on a Holiday:**
- **Compensation**: {rules['working_on_holiday']['rule']}
- **Applicable**: {rules['working_on_holiday']['applicable']}
- **Alternative**: {rules['working_on_holiday']['alternative']}
- **Legal Basis**: {rules['working_on_holiday']['legal_basis']}

**When Employee Takes Holiday Off:**
- **Compensation**: {rules['paid_holiday']['rule']}
- **Applicable**: {rules['paid_holiday']['applicable']}
- **Legal Basis**: {rules['paid_holiday']['legal_basis']}

**Critical Distinction:**
{rules['key_distinction']['working']}
{rules['key_distinction']['not_working']}

**National Holidays in Delhi:**
{chr(10).join(f"- {holiday}" for holiday in rules['national_holidays'])}

**Important Note:**
{rules['key_distinction']['common_mistake']}

**Legal References:**
- {rules['working_on_holiday']['section_reference']} for working on holidays
- {rules['paid_holiday']['section_reference']} for paid holidays

Would you like more details about specific holiday work procedures or compensatory off policies?"""
    
    return {
        'result': answer,
        'source_documents': []
    }

def get_mse_collateral_answer(query):
    """
    Specialized handler for MSE collateral-free loan queries with 2025 updates
    """
    info = MSE_COLLATERAL_INFO_2025
    
    answer = f"""### Collateral-Free Loan Limits for MSEs (Current Guidelines 2025)

**1. RBI Mandated Limit (No Collateral Allowed)**
- **Limit**: ₹10 Lakhs
- **Rule**: {info['rbi_mandated_limits']['rule']}

**2. Bank Discretionary Limit (Performance Based)**
- **Limit**: {info['bank_discretionary_limits']['limit']}
- **Rule**: {info['bank_discretionary_limits']['rule']}

**3. Agriculture & Allied Activities (New 2025 Update)**
- **Current Limit**: {info['agriculture_allied']['current_limit']} (Increased from {info['agriculture_allied']['previous_limit']})
- **Effective Date**: {info['agriculture_allied']['effective_date']}
- **Context**: {info['agriculture_allied']['context']}

**4. Under CGTMSE Guarantee Scheme (The Major Update)**
- **Current Limit (Standard)**: {info['cgtmse_scheme']['current_limit']} covered without collateral
- **Future Limit (2025 Budget Update)**: {info['cgtmse_scheme']['future_limit']} per borrower
- **Effective Date**: {info['cgtmse_scheme']['effective_date']}
- **Rule**: {info['cgtmse_scheme']['rule']}

**Important Timeline:**
- {info['timeline']['January 1, 2025']}
- {info['timeline']['April 1, 2025']}

**Key Points Summary:**
{chr(10).join(f"- {point}" for point in info['key_points'])}

**Sources:**
- RBI Guidelines 2025
- CGTMSE Trust 2025 Budget Update
- RBI Agricultural Credit Guidelines 2025

Would you like more details about the application process or eligibility criteria for any of these schemes?"""
    
    return {
        'result': answer,
        'source_documents': []
    }

# --- TEST AREA ---
if __name__ == "__main__":
    # Test with holiday work question
    user_q = "What should I pay if an employee works on Republic Day in Delhi?"
    
    print(f"Searching laws for: {user_q}...")
    result = get_compliance_answer(user_q)
    
    print("\n--- AI ANSWER ---")
    print(result['result'])
    
    print("\n--- SOURCE DOCUMENT ---")
    if result['source_documents']:
        for i, doc in enumerate(result['source_documents'][:3]):
            print(f"Source {i+1}: {doc.metadata.get('source', 'Unknown')}")
            content_preview = doc.page_content[:300].replace('\n', ' ')
            print(f"Preview: {content_preview}...")
            print()
    else:
        print("No source documents found")

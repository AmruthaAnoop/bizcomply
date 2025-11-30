import streamlit as st
import requests
import json
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List

# --- CONFIGURATION ---
st.set_page_config(
    page_title="BizComply AI",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 1. BACKEND LOGIC ---

# Import the Dynamic Brain
try:
    from agent_engine_new import get_verified_answer
    RAG_AVAILABLE = True
except ImportError:
    RAG_AVAILABLE = False

# Data Structures
class ConversationState:
    def __init__(self):
        self.current_step = "onboarding"
        self.user_profile = {"location": "", "entity_type": "", "industry": ""}
        self.completed_questions = []
    
    def is_profile_complete(self):
        return all(self.user_profile.get(k) for k in ["location", "entity_type", "industry"])
    
    def update_profile(self, key, value):
        self.user_profile[key] = value
        if key not in self.completed_questions: self.completed_questions.append(key)
        if self.is_profile_complete(): self.current_step = "main_chat"

class ComplianceChatbot:
    """
    Dynamic Chatbot that uses the Agentic Brain.
    """
    def process_message(self, user_message, conversation_state, response_mode="simple"):
        # 1. Handle Onboarding (Fixed Flow)
        if conversation_state.current_step == "onboarding":
            return self._handle_onboarding(user_message, conversation_state)
        
        # 2. Dynamic Main Chat (The Upgrade)
        # No keywords needed. The Agent decides everything.
        if RAG_AVAILABLE:
            try:
                # We pass the profile context so the agent knows who it's talking to
                profile_context = f"Context: User is a {conversation_state.user_profile['entity_type']} in {conversation_state.user_profile['location']}."
                full_query = f"{profile_context}\n\nQuestion: {user_message}"
                
                # Get base response
                base_response = get_verified_answer(full_query)
                
                # Apply response mode formatting
                return self._format_response(base_response, response_mode)
            except Exception as e:
                return f"⚠️ Agent Error: {str(e)}"
        
        return "⚠️ Core Brain (agent_engine_new.py) not found. Please check file setup."

    def _format_response(self, response: str, mode: str = "simple") -> str:
        """Format response based on mode with extreme distinction between modes"""
        if mode == "concise":
            # ULTRA-concise: Maximum 2 bullet points, under 60 characters each
            lines = response.split('\n')
            essential_lines = []
            
            # Extract only critical compliance points
            for line in lines:
                line = line.strip()
                if not line or line.startswith('**') or line.startswith('*') or line.startswith('-'):
                    continue
                
                # Look for absolute key requirements only
                if any(keyword in line.lower() for keyword in ['must', 'required', 'due', 'file', 'penalty']):
                    # Make it ultra-short
                    line = line.replace('The ', '').replace('You must', '').replace('is required to', '')
                    if len(line) > 60:
                        line = line[:57] + "..."
                    essential_lines.append(f"• {line}")
                
                if len(essential_lines) >= 2:  # Strict 2-point limit
                    break
            
            # If no critical points found, create ultra-short summary
            if not essential_lines:
                # Extract first meaningful phrase
                words = response.split()
                short_phrase = ""
                for word in words[:8]:  # Max 8 words
                    if len(short_phrase + word) < 60:
                        short_phrase += word + " "
                    else:
                        break
                essential_lines = [f"• {short_phrase.strip()}..."]
            
            return '\n'.join(essential_lines) + "\n\n💡 *Switch to Detailed for full guidance.*"
            
        elif mode == "simple":
            # SIMPLE: Maximum 5 sentences - clean, readable format
            sentences = response.split('.')
            simple_sentences = []
            
            # Extract up to 5 meaningful sentences
            for sentence in sentences:
                sentence = sentence.strip()
                if len(sentence) > 15 and len(sentence) < 200:  # Reasonable length
                    # Clean up the sentence
                    sentence = sentence.replace('\n', ' ').replace('  ', ' ')
                    # Remove markdown formatting
                    sentence = sentence.replace('**', '').replace('*', '').replace('#', '')
                    simple_sentences.append(sentence)
                
                if len(simple_sentences) >= 5:  # Strict 5-sentence limit
                    break
            
            # If no good sentences found, create a simple summary
            if not simple_sentences:
                # Get first meaningful paragraph
                paragraphs = response.split('\n\n')
                if paragraphs:
                    first_para = paragraphs[0].strip()
                    # Split into sentences if needed
                    para_sentences = first_para.split('.')
                    for i, sent in enumerate(para_sentences[:3]):
                        if sent.strip():
                            simple_sentences.append(sent.strip())
            
            # If still no sentences, create a basic one
            if not simple_sentences:
                simple_sentences = ["This compliance requirement applies to your business operations."]
            
            # Format as clean text with proper spacing
            simple_response = ' '.join(simple_sentences)
            if not simple_response.endswith('.'):
                simple_response += '.'
            
            return simple_response + "\n\n💡 *Switch to Concise for bullet points or Detailed for comprehensive analysis.*"
            
        elif mode == "detailed":
            # COMPREHENSIVE: Full analysis with multiple sections, examples, and action plans
            detailed_response = response + "\n\n---\n\n**📋 Comprehensive Compliance Analysis:**\n"
            
            # Enhanced compliance overview
            detailed_response += "\n### 🔍 **Regulatory Framework**\n"
            detailed_response += "This requirement falls under Indian business law and has legal enforceability. "
            detailed_response += "Non-compliance may result in penalties, legal action, or business restrictions.\n"
            
            # Context-specific detailed sections
            if "director" in response.lower():
                detailed_response += "\n### 👥 **Director Responsibilities & Liabilities**\n"
                detailed_response += "**Statutory Duties:**\n"
                detailed_response += "• **Fiduciary Duty**: Act in good faith, avoid conflicts of interest\n"
                detailed_response += "• **Care & Skill**: Exercise diligence of a reasonable person\n"
                detailed_response += "• **Reporting**: Disclose interests in contracts/companies\n\n"
                detailed_response += "**Legal Framework:**\n"
                detailed_response += "• **Companies Act, 2013**: Sections 166, 184, 185\n"
                detailed_response += "• **Penalties**: ₹5,000-₹2,00,000 or imprisonment up to 1 year\n"
                detailed_response += "• **Disqualification**: May be barred from directorship for 5 years\n\n"
                detailed_response += "**Best Practices:**\n"
                detailed_response += "• Maintain register of director interests\n"
                detailed_response += "• Obtain board approval for related party transactions\n"
                detailed_response += "• Regular compliance training and updates\n"
            
            if "meeting" in response.lower() or "agm" in response.lower():
                detailed_response += "\n### 📅 **Meeting Compliance Framework**\n"
                detailed_response += "**Notice Requirements:**\n"
                detailed_response += "• **AGM**: Minimum 21 days notice, sent to all members\n"
                detailed_response += "• **EGM**: Minimum 14 days notice for special business\n"
                detailed_response += "• **Board Meeting**: Minimum 7 days, unless urgent\n\n"
                detailed_response += "**Quorum & Voting:**\n"
                detailed_response += "• **AGM Quorum**: Minimum 5 members personally present\n"
                detailed_response += "• **Special Resolution**: 75% majority required\n"
                detailed_response += "• **Ordinary Resolution**: Simple majority sufficient\n\n"
                detailed_response += "**Documentation:**\n"
                detailed_response += "• Maintain minutes signed by chairman within 30 days\n"
                detailed_response += "• File Form MGT-7 for AGM within 30 days\n"
                detailed_response += "• Keep attendance register for 8 years\n"
            
            if "tax" in response.lower() or "gst" in response.lower():
                detailed_response += "\n### 💰 **Tax Compliance Deep Dive**\n"
                detailed_response += "**Income Tax:**\n"
                detailed_response += "• **Due Dates**: ITR-5 (30 Sep), Audit cases (31 Oct)\n"
                detailed_response += "• **Advance Tax**: 15%, 45%, 75%, 100% by Jun, Sep, Dec, Mar\n"
                detailed_response += "• **Penalties**: 0.5-1% per month on unpaid tax\n\n"
                detailed_response += "**GST Compliance:**\n"
                detailed_response += "• **GSTR-1**: 11th of each month (outward supplies)\n"
                detailed_response += "• **GSTR-3B**: 20th of each month (summary return)\n"
                detailed_response += "• **Annual Return**: GSTR-9 by 31st December\n"
                detailed_response += "• **Audit Turnover**: GSTR-9C if turnover > ₹2 Crore\n"
            
            if "license" in response.lower() or "registration" in response.lower():
                detailed_response += "\n### 📋 **License & Registration Process**\n"
                detailed_response += "**Required Documents:**\n"
                detailed_response += "• **PAN Card**: Mandatory for all business registrations\n"
                detailed_response += "• **Aadhaar**: Director/partner identification\n"
                detailed_response += "• **Address Proof**: Utility bill or rent agreement\n"
                detailed_response += "• **Bank Account**: Business current account details\n\n"
                detailed_response += "**Timeline & Costs:**\n"
                detailed_response += "• **DLIN Registration**: 1-2 days, ₹500 (government fee)\n"
                detailed_response += "• **GST Registration**: 3-7 working days, free\n"
                detailed_response += "• **Trade License**: 7-10 days, varies by municipality\n"
            
            # Actionable implementation plan
            detailed_response += "\n### 🎯 **Implementation Roadmap**\n"
            detailed_response += "**Phase 1: Immediate (Week 1)**\n"
            detailed_response += "1. Review current compliance status\n"
            detailed_response += "2. Identify missing documents or filings\n"
            detailed_response += "3. Set up compliance calendar with reminders\n"
            detailed_response += "4. Appoint compliance coordinator\n\n"
            detailed_response += "**Phase 2: Short-term (Month 1)**\n"
            detailed_response += "1. Complete all pending registrations\n"
            detailed_response += "2. Establish record-keeping system\n"
            detailed_response += "3. Conduct staff training on compliance\n"
            detailed_response += "4. Engage professional advisor if needed\n\n"
            detailed_response += "**Phase 3: Long-term (Ongoing)**\n"
            detailed_response += "1. Quarterly compliance reviews\n"
            detailed_response += "2. Annual legal audit\n"
            detailed_response += "3. Stay updated on regulatory changes\n"
            detailed_response += "4. Maintain compliance documentation\n"
            
            # Risk assessment matrix
            detailed_response += "\n### ⚠️ **Risk Assessment & Mitigation**\n"
            detailed_response += "**High-Risk Areas:**\n"
            detailed_response += "• **Missed Deadlines**: ₹1,000-₹10,000 per day penalties\n"
            detailed_response += "• **Incorrect Filings**: Rejection fees + reputational damage\n"
            detailed_response += "• **Documentation Gaps**: Legal notices + compliance issues\n\n"
            detailed_response += "**Mitigation Strategies:**\n"
            detailed_response += "• Use compliance management software\n"
            detailed_response += "• Set multiple reminder systems\n"
            detailed_response += "• Professional review of major filings\n"
            detailed_response += "• Maintain buffer time before deadlines\n"
            
            # Comprehensive resources
            detailed_response += "\n### 📚 **Resources & Support**\n"
            detailed_response += "**Official Portals:**\n"
            detailed_response += "• **MCA**: [www.mca.gov.in](https://www.mca.gov.in) - Company registrations\n"
            detailed_response += "• **Income Tax**: [www.incometaxindia.gov.in](https://www.incometaxindia.gov.in) - Tax filings\n"
            detailed_response += "• **GST**: [www.gst.gov.in](https://www.gst.gov.in) - GST compliance\n"
            detailed_response += "• **Legal**: [www.indiacode.nic.in](https://www.indiacode.nic.in) - Legal database\n\n"
            detailed_response += "**Professional Help:**\n"
            detailed_response += "• **CS/CA**: Company Secretary/Chartered Accountant\n"
            detailed_response += "• **Lawyers**: Corporate law firms\n"
            detailed_response += "• **Consultants**: Compliance management companies\n"
            detailed_response += "• **Software**: Tally, SAP, specialized compliance tools\n"
            
            # Disclaimer and next steps
            detailed_response += "\n\n---\n\n**⚖️ Important Disclaimer**: This analysis is for informational purposes only. "
            detailed_response += "Regulations change frequently. Consult qualified professionals for advice "
            detailed_response += "tailored to your specific business situation and jurisdiction.\n\n"
            detailed_response += "**📞 Next Step**: Consider scheduling a consultation with a compliance professional "
            detailed_response += "to review your specific requirements and implement a tailored compliance program."
            
            return detailed_response
            
        else:  # fallback to simple
            return self._format_response(response, "simple")

    def _handle_onboarding(self, message, state):
        if "location" not in state.completed_questions: 
            state.update_profile("location", message)
            return "### What type of business entity is it?\n\n- Sole Proprietorship\n- LLP\n- Private Limited"
        elif "entity_type" not in state.completed_questions: 
            state.update_profile("entity_type", message)
            return "### What industry are you in?\n\n- IT Services\n- Retail\n- Manufacturing"
        elif "industry" not in state.completed_questions: 
            state.update_profile("industry", message)
            state.current_step = "main_chat"
            return f"✅ **Setup Complete.**\nI have configured the compliance engine for a **{state.user_profile['entity_type']}** in **{state.user_profile['location']}**. What would you like to know?"
        else:
            return "Profile already complete. Ask me anything about compliance!"

class ComplianceEngine:
    def __init__(self): 
        self.profiles = {}
    def create_business_profile(self, name, b_type, juris, reg):
        new_id = str(len(self.profiles) + 1)
        self.profiles[new_id] = {"name": name, "type": b_type, "loc": juris, "reg": reg}
        return type('obj', (object,), {'id': new_id})
    def get_business_profile(self, bid): 
        return self.profiles.get(bid)

# --- 2. UI STYLING (White Box Fix) ---

def load_css():
    st.markdown("""
    <style>
    :root {
        --bg-color: #212121;
        --sidebar-bg: #171717;
        --text-primary: #ECECEC;
        --input-bg: #2F2F2F;
    }
    .stApp { background-color: var(--bg-color); color: var(--text-primary); }
    
    /* Main Content Area - White Background */
    .main .block-container {
        background-color: #FFFFFF !important;
        padding: 2rem !important;
        border-radius: 10px !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1) !important;
        margin: 1rem !important;
    }
    
    /* Chat messages - White background */
    .stChatMessage {
        background-color: #FFFFFF !important;
        border: 1px solid #E5E7EB !important;
        border-radius: 8px !important;
        margin: 0.5rem 0 !important;
    }
    
    /* User message styling */
    .stChatMessage[data-testid="chat-message-container-user"] {
        background-color: #F3F4F6 !important;
        border-left: 4px solid #3B82F6 !important;
    }
    
    /* Assistant message styling */
    .stChatMessage[data-testid="chat-message-container-assistant"] {
        background-color: #FFFFFF !important;
        border-left: 4px solid #10B981 !important;
    }
    
    /* Custom message bubbles */
    .user-message { 
        background-color: #F3F4F6 !important; 
        color: #1F2937 !important; 
        padding: 12px; 
        border-radius: 15px; 
        margin: 10px 0 10px auto; 
        max-width: 80%; 
        text-align: right;
        border-left: 4px solid #3B82F6 !important;
    }
    .assistant-message { 
        background-color: #FFFFFF !important; 
        color: #1F2937 !important; 
        padding: 10px; 
        margin: 10px 0; 
        max-width: 90%; 
        border-left: 4px solid #10B981 !important;
    }
    
    /* Header - White */
    .main-header {
        background-color: #FFFFFF !important;
        border: 1px solid #E5E7EB !important;
        color: #1F2937 !important;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
        text-align: center;
    }
    
    /* Sidebar Background */
    [data-testid="stSidebar"] { background-color: var(--sidebar-bg); border-right: 1px solid #333; }

    /* --- WHITE BOX FIX START --- */
    /* Make sidebar inputs transparent */
    [data-testid="stSidebar"] .stTextInput > div > div,
    [data-testid="stSidebar"] .stSelectbox > div > div {
        background-color: transparent !important;
        border: 1px solid #444 !important;
        color: white !important;
    }
    [data-testid="stSidebar"] input, 
    [data-testid="stSidebar"] select,
    [data-testid="stSidebar"] div[data-baseweb="select"] span {
        color: white !important;
        -webkit-text-fill-color: white !important;
    }
    /* Remove form background */
    [data-testid="stSidebar"] [data-testid="stForm"] { background: transparent !important; }
    /* --- WHITE BOX FIX END --- */

    /* Chat Bubbles - Updated for White Background */
    .user-message { 
        background-color: #F3F4F6 !important; 
        color: #1F2937 !important; 
        padding: 12px; 
        border-radius: 15px; 
        margin: 10px 0 10px auto; 
        max-width: 80%; 
        text-align: right;
        border-left: 4px solid #3B82F6 !important;
    }
    .assistant-message { 
        background-color: #FFFFFF !important; 
        color: #1F2937 !important; 
        padding: 10px; 
        margin: 10px 0; 
        max-width: 90%; 
        border-left: 4px solid #10B981 !important;
    }
    
    /* Input Bar */
    .stChatInputContainer textarea { 
        background-color: var(--input-bg) !important; 
        color: white !important; 
        border: 1px solid #444 !important; 
        border-radius: 24px !important; 
    }
    
    /* Buttons */
    .stButton button { 
        background: transparent; 
        border: 1px solid #444; 
        color: white; 
        width: 100%; 
        text-align: left; 
    }
    .stButton button:hover { 
        background: #333; 
        border-color: #666; 
    }
    
    /* Response Mode Radio */
    .stRadio > div[role="radiogroup"] {
        background: transparent !important;
        border: 1px solid #444 !important;
        border-radius: 8px !important;
        padding: 10px !important;
    }
    .stRadio label {
        color: white !important;
        font-weight: 500 !important;
    }
    .stRadio div[role="radio"] {
        background: #2F2F2F !important;
        border: 1px solid #555 !important;
        border-radius: 4px !important;
        margin: 2px 0 !important;
    }
    .stRadio div[role="radio"][aria-checked="true"] {
        background: #444 !important;
        border-color: #666 !important;
    }
    
    /* Header */
    .main-header {
        background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. MAIN LOGIC ---

def main():
    load_css()
    
    # Init State
    if 'conversations' not in st.session_state: 
        st.session_state.conversations = []
    if 'active_conv_id' not in st.session_state:
        new_id = str(int(datetime.now().timestamp()))
        st.session_state.conversations.insert(0, {"id": new_id, "title": "New Chat", "messages": []})
        st.session_state.active_conv_id = new_id
    if 'response_mode' not in st.session_state:
        st.session_state.response_mode = "simple"
    
    if 'chatbot' not in st.session_state:
        st.session_state.chatbot = ComplianceChatbot()
        st.session_state.conv_state = ConversationState()
        st.session_state.engine = ComplianceEngine()

    # --- SIDEBAR ---
    with st.sidebar:
        st.markdown("## 🏢 BizComply AI")
        if st.button("＋ New Chat"):
            new_id = str(int(datetime.now().timestamp()))
            st.session_state.conversations.insert(0, {"id": new_id, "title": "New Chat", "messages": []})
            st.session_state.active_conv_id = new_id
            st.rerun()
        
        st.markdown("---")
        
        # Response Mode Selector
        st.markdown("**Response Mode**")
        response_mode = st.radio(
            "Choose response style:",
            options=["Simple", "Concise", "Detailed"],
            index=["simple", "concise", "detailed"].index(st.session_state.response_mode),
            key="response_mode_selector",
            help="Simple: Standard response\nConcise: Short, summarized replies (2-3 bullet points max)\nDetailed: Expanded, in-depth responses with analysis and action plans"
        )
        st.session_state.response_mode = ["simple", "concise", "detailed"][["Simple", "Concise", "Detailed"].index(response_mode)]
        
        # Show current mode indicator
        mode_descriptions = {
            "simple": "📝 Simple answers (5 sentences max)",
            "concise": "⚡ Ultra-short summaries (2-3 points max)",
            "detailed": "📚 Comprehensive analysis with action plans"
        }
        st.markdown(f"<small style='color: #6B7280;'>{mode_descriptions[st.session_state.response_mode]}</small>", unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Profile Form
        if 'biz_id' not in st.session_state:
            with st.form("profile"):
                st.markdown("**Business Profile**")
                name = st.text_input("Name", placeholder="Business Name")
                btype = st.selectbox("Type", ["LLP", "Private Ltd", "Proprietor"])
                loc = st.selectbox("Location", ["Delhi", "Mumbai", "Bangalore"])
                if st.form_submit_button("Save"):
                    st.session_state.biz_id = "123" # Mock save
                    st.session_state.engine.create_business_profile(name, btype, loc, "REG123")
                    st.rerun()
        else:
            st.success("✅ Profile Loaded")
            if st.button("Edit Profile"):
                del st.session_state.biz_id
                st.rerun()

    # --- CHAT AREA ---
    active_conv = next((c for c in st.session_state.conversations if c['id'] == st.session_state.active_conv_id), None)
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🏢 BizComply AI</h1>
        <p>Dynamic Compliance Assistant with Semantic Routing</p>
        <p><small>✨ No keywords needed - understands any phrasing automatically!</small></p>
    </div>
    """, unsafe_allow_html=True)
    
    if active_conv:
        # Render History
        for msg in active_conv['messages']:
            div_class = "user-message" if msg['is_user'] else "assistant-message"
            st.markdown(f"<div class='{div_class}'>{msg['content']}</div>", unsafe_allow_html=True)

        # Input
        prompt = st.chat_input("Ask about compliance...")
        if prompt:
            # 1. User Msg
            active_conv['messages'].append({"content": prompt, "is_user": True})
            if len(active_conv['messages']) == 1: 
                active_conv['title'] = prompt[:20]
            
            # 2. AI Response (Dynamic Agent)
            with st.spinner("🤖 Analyzing compliance rules..."):
                response = st.session_state.chatbot.process_message(prompt, st.session_state.conv_state, st.session_state.response_mode)
            
            active_conv['messages'].append({"content": response, "is_user": False})
            st.rerun()

if __name__ == "__main__":
    main()

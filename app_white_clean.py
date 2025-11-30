import streamlit as st
from datetime import datetime
import os

# Try importing the dynamic router
try:
    from agent_engine_new import get_verified_answer
    RAG_AVAILABLE = True
except ImportError:
    RAG_AVAILABLE = False
    print("Warning: agent_engine_new.py not found. Using fallback responses.")

# --- 1. CONVERSATION STATE ---

class ConversationState:
    def __init__(self):
        self.current_step = "onboarding"
        self.user_profile = {"location": "", "entity_type": "", "industry": ""}
        self.completed_questions = []
    
    def is_profile_complete(self):
        return all([self.user_profile["location"], self.user_profile["entity_type"], self.user_profile["industry"]])
    
    def update_profile(self, key, value):
        self.user_profile[key] = value
        if key not in self.completed_questions: self.completed_questions.append(key)
        if self.is_profile_complete(): self.current_step = "main_chat"

class ComplianceChatbot:
    """
    Dynamic Chatbot that uses the Agentic Brain with Clean White Theme.
    """
    def process_message(self, user_message, conversation_state, response_mode="Standard"):
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

    def _format_response(self, response: str, mode: str = "Standard") -> str:
        """Format response based on mode with clean white theme styling"""
        if mode == "Concise":
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
            
            return '\n'.join(essential_lines) + "\n\n💡 *Switch to Detailed mode for comprehensive guidance.*"
            
        elif mode == "Standard":
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
            
        elif mode == "Detailed":
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
            
        else:  # fallback to Standard
            return self._format_response(response, "Standard")

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

# --- 2. CLEAN WHITE THEME STYLING ---

def apply_styling():
    """Apply Clean White Theme with Standard Fonts and Dynamic Router Integration"""
    st.markdown("""
    <style>
    /* --- 1. GLOBAL RESETS & FONTS --- */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');
    
    :root {
        --bg-color: #FFFFFF;
        --text-color: #000000;
        --sidebar-bg: #F9F9F9;
        --border-color: #E5E5E5;
        --primary-color: #000000;
    }

    /* Main App Background - Pure White */
    .stApp {
        background-color: var(--bg-color) !important;
        color: var(--text-color) !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif !important;
    }
    
    /* Headers */
    h1, h2, h3, p {
        color: #000000 !important;
        font-weight: 500 !important;
    }

    /* --- 2. SIDEBAR STYLING (Full Black) --- */
    [data-testid="stSidebar"] {
        background-color: #000000 !important;
        border-right: 1px solid #333333 !important;
    }
    
    /* Sidebar Headers - Styled Fonts */
    .sidebar-header {
        font-size: 18px;
        font-weight: 600;
        color: #FFFFFF !important;
        padding: 15px 0;
        margin-bottom: 25px;
        display: flex;
        align-items: center;
        gap: 12px;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Sidebar Section Headers */
    [data-testid="stSidebar"] h3 {
        color: #FFFFFF !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        margin: 20px 0 10px 0 !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif !important;
    }
    
    /* Sidebar Text */
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] .stMarkdown {
        color: #CCCCCC !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif !important;
    }

    /* Sidebar Buttons - Black Theme */
    [data-testid="stSidebar"] button {
        background-color: transparent !important;
        color: #FFFFFF !important;
        border: 1px solid #333333 !important;
        text-align: left !important;
        padding: 12px 15px !important;
        font-size: 14px !important;
        border-radius: 8px !important;
        transition: all 0.3s ease !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif !important;
        font-weight: 500 !important;
        margin-bottom: 5px !important;
    }
    
    [data-testid="stSidebar"] button:hover {
        background-color: #1A1A1A !important;
        border-color: #555555 !important;
        transform: translateX(3px) !important;
    }
    
    /* Sidebar Inputs - Black Theme */
    [data-testid="stSidebar"] .stTextInput > div > div,
    [data-testid="stSidebar"] .stSelectbox > div > div {
        background-color: #1A1A1A !important;
        border: 1px solid #333333 !important;
        color: #FFFFFF !important;
        border-radius: 6px !important;
    }
    
    [data-testid="stSidebar"] input, 
    [data-testid="stSidebar"] select,
    [data-testid="stSidebar"] div[data-baseweb="select"] span {
        color: #FFFFFF !important;
        background-color: #1A1A1A !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif !important;
    }
    
    /* Sidebar Success/Info Messages */
    [data-testid="stSidebar"] .stSuccess,
    [data-testid="stSidebar"] .stInfo {
        background-color: #1A1A1A !important;
        color: #FFFFFF !important;
        border: 1px solid #333333 !important;
    }

    /* Response Mode Radio - Black Theme */
    .stRadio > div[role="radiogroup"] {
        background: #1A1A1A !important;
        border: 1px solid #333333 !important;
        border-radius: 8px !important;
        padding: 12px !important;
    }
    .stRadio label {
        color: #FFFFFF !important;
        font-weight: 500 !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif !important;
    }
    .stRadio div[role="radio"] {
        background: #2A2A2A !important;
        border: 1px solid #444444 !important;
        border-radius: 6px !important;
        margin: 3px 0 !important;
    }
    .stRadio div[role="radio"][aria-checked="true"] {
        background: #3A3A3A !important;
        border-color: #666666 !important;
    }

    /* --- 3. CHAT AREA STYLING --- */
    
    /* User Message: Dark Grey Bubble, White Text */
    .user-message {
        background-color: #535151 !important;
        color: #FFFFFF !important;
        padding: 12px 16px;
        border-radius: 13px 13px 13px 16px;
        max-width: 40%;
        margin-left: auto;
        margin-bottom: 15px;
        font-size: 15px;
        line-height: 1.5;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
    }
    
    /* Assistant Message: Light Grey Background, Black Text */
    .assistant-message {
        background-color: #92929217 !important;
        color: #000000 !important;
        padding: 0 10px;
        max-width: 90%;
        margin-right: auto;
        margin-bottom: 25px;
        font-size: 15px;
        line-height: 1.6;
        border-left: 2px solid #d4d3d3;
        padding-left: 15px;
    }
    
    /* Remove default Streamlit labels */
    .user-message strong:first-child,
    .assistant-message strong:first-child {
        display: none !important;
    }

    /* --- 4. INPUT BAR (All Black with Grey Text Area) --- */
    .stChatInput {
        position: fixed !important;
        bottom: 0 !important;
        left: 250px !important; /* Updated as requested */
        right: 0 !important;
        background-color: #000000 !important;
        padding: 20px !important;
        border-top: 2px solid #333333 !important;
        z-index: 999 !important;
        display: flex !important;
        justify-content: center !important;
    }
    
    .stChatInput > div {
        width: 100% !important;
        max-width: 800px !important;
    }
    
    .stChatInput textarea {
        background-color: #1A1A1A !important; /* Dark grey for visibility */
        color: #FFFFFF !important;
        border: 2px solid #333333 !important;
        border-radius: 12px !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.3) !important;
        font-size: 15px !important;
        padding: 12px 16px !important;
        min-height: 20px !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif !important;
        transition: all 0.3s ease !important;
    }
    
    .stChatInput textarea:focus {
        background-color: #2A2A2A !important; /* Lighter grey when focused */
        border-color: #555555 !important;
        box-shadow: 0 2px 12px rgba(255,255,255,0.1) !important;
        outline: none !important;
    }
    
    .stChatInput textarea::placeholder {
        color: #888888 !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif !important;
    }
    
    /* Ensure input is always visible */
    .stChatInputContainer {
        position: fixed !important;
        bottom: 0 !important;
        left: 250px !important; /* Updated to match */
        right: 0 !important;
        background-color: #000000 !important;
        padding: 20px !important;
        border-top: 2px solid #333333 !important;
        z-index: 999 !important;
    }
    
    /* Main content padding to avoid overlap with fixed input */
    .main .block-container {
        padding-bottom: 120px !important;
    }

    /* --- 5. CARDS & CONTAINERS --- */
    .page-content {
        background: #FFFFFF;
        border: 1px solid #E5E5E5;
        border-radius: 10px;
        padding: 30px;
        margin-bottom: 20px;
    }
    
    /* Hero Section - Clean White */
    .hero-section {
        background-color: #FFFFFF !important;
        border: 1px solid #E5E5E5 !important;
        color: #000000 !important;
        padding: 40px;
        border-radius: 10px;
        margin-bottom: 20px;
        text-align: center;
    }
    
    /* Hide top header decoration */
    header {visibility: hidden;}
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 6rem;
        max-width: 800px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. MAIN APPLICATION ---

def main():
    st.set_page_config(page_title="BizComply AI", page_icon="🏢", layout="wide")
    
    # Apply Clean White Theme
    apply_styling()
    
    # Initialize session state
    if 'conversations' not in st.session_state: 
        st.session_state.conversations = []
    if 'active_conv_id' not in st.session_state:
        new_id = str(int(datetime.now().timestamp()))
        st.session_state.conversations.insert(0, {"id": new_id, "title": "New Chat", "messages": []})
        st.session_state.active_conv_id = new_id
    if 'response_mode' not in st.session_state:
        st.session_state.response_mode = "Standard"
    
    if 'chatbot' not in st.session_state:
        st.session_state.chatbot = ComplianceChatbot()
        st.session_state.conv_state = ConversationState()
        st.session_state.engine = ComplianceEngine()

    # --- SIDEBAR ---
    with st.sidebar:
        st.markdown('<div class="sidebar-header"><span>🏢</span> BizComply AI</div>', unsafe_allow_html=True)
        
        # Business Profile
        st.markdown("### 👤 Profile")
        if 'biz_id' not in st.session_state:
            with st.form("profile"):
                name = st.text_input("Name", placeholder="Business Name")
                btype = st.selectbox("Type", ["LLP", "Private Ltd", "Proprietor"])
                loc = st.selectbox("Location", ["Delhi", "Mumbai", "Bangalore"])
                if st.form_submit_button("Save"):
                    st.session_state.biz_id = "123"
                    st.session_state.engine.create_business_profile(name, btype, loc, "REG123")
                    st.rerun()
        else:
            st.success("✅ Profile Loaded")
            if st.button("Edit Profile"):
                del st.session_state.biz_id
                st.rerun()

        st.markdown("---")
        
        # Response Mode Preferences
        st.markdown("### ⚙️ Response Mode")
        mode = st.radio(
            "Choose response style:",
            options=["Concise", "Standard", "Detailed"],
            index=["Concise", "Standard", "Detailed"].index(st.session_state.response_mode),
            key="response_mode_selector",
            help="Concise: 2-3 bullet points (60 chars max)\nStandard: 5 sentences max\nDetailed: Comprehensive analysis with action plans"
        )
        st.session_state.response_mode = mode
        
        # Show current mode indicator
        mode_descriptions = {
            "Concise": "⚡ Ultra-short summaries (2-3 points max)",
            "Standard": "📝 Standard answers (5 sentences max)",
            "Detailed": "📚 Comprehensive analysis with action plans"
        }
        st.markdown(f"<small style='color: #666666;'>{mode_descriptions[st.session_state.response_mode]}</small>", unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Chat History
        st.markdown("### 💬 Chat History")
        
        # Show conversation list
        if len(st.session_state.conversations) > 1:
            for i, conv in enumerate(st.session_state.conversations):
                if conv['id'] != st.session_state.active_conv_id:
                    # Show conversation title with message count
                    msg_count = len(conv['messages'])
                    title = conv['title'] if conv['title'] else f"Chat {i+1}"
                    
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        if st.button(f"💭 {title}", key=f"chat_{conv['id']}", use_container_width=True):
                            st.session_state.active_conv_id = conv['id']
                            st.rerun()
                    with col2:
                        if st.button("🗑️", key=f"del_{conv['id']}", use_container_width=True):
                            st.session_state.conversations = [c for c in st.session_state.conversations if c['id'] != conv['id']]
                            # If we deleted the active chat, switch to the first available
                            if st.session_state.active_conv_id == conv['id'] and st.session_state.conversations:
                                st.session_state.active_conv_id = st.session_state.conversations[0]['id']
                            st.rerun()
        else:
            st.markdown("<small style='color: #666666;'>No previous chats</small>", unsafe_allow_html=True)
        
        # Clear all chats option
        if len(st.session_state.conversations) > 1:
            if st.button("🗑️ Clear All History", key="clear_all", use_container_width=True):
                # Keep only the current active conversation
                active_conv = next((c for c in st.session_state.conversations if c['id'] == st.session_state.active_conv_id), None)
                if active_conv:
                    st.session_state.conversations = [active_conv]
                st.rerun()
        
        st.markdown("---")
        
        # Navigation - Keep only essential working features
        st.markdown("### 🛠️ Features")
        if st.button("🏠 New Chat", use_container_width=True): 
            new_id = str(int(datetime.now().timestamp()))
            st.session_state.conversations.insert(0, {"id": new_id, "title": "New Chat", "messages": []})
            st.session_state.active_conv_id = new_id
            st.rerun()

    # --- MAIN CONTENT AREA ---
    active_conv = next((c for c in st.session_state.conversations if c['id'] == st.session_state.active_conv_id), None)
    
    # Current Chat Title
    if active_conv:
        current_title = active_conv['title'] if active_conv['title'] else "New Chat"
        st.markdown(f"""
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; padding: 10px 0;">
            <h3 style="margin: 0; color: #000000;">💭 {current_title}</h3>
            <small style="color: #666666;">{len(active_conv['messages'])} messages</small>
        </div>
        """, unsafe_allow_html=True)
    
    # Hero Section
    if not active_conv or not active_conv['messages']:
        st.markdown("""
        <div class="hero-section">
            <h1>🏢 BizComply AI</h1>
            <p style="color: #666666;">Your professional compliance assistant with Dynamic Semantic Routing</p>
            <p style="color: #666666; font-size: 14px;">✨ No keywords needed - understands any phrasing automatically!</p>
        </div>
        """, unsafe_allow_html=True)
    
    if active_conv:
        # Render Chat History
        for msg in active_conv['messages']:
            if msg['is_user']:
                st.markdown(f'<div class="user-message">{msg["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="assistant-message">{msg["content"]}</div>', unsafe_allow_html=True)

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

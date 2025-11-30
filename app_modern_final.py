import streamlit as st
from business_profile import business_profile_manager
from models.compliance_engine import ComplianceEngine

# Initialize compliance engine
compliance_engine = ComplianceEngine()

def main():
    st.set_page_config(page_title="BizComply AI", page_icon="🏢", layout="wide")
    
    # Initialize session state for routing
    if "page" not in st.session_state:
        st.session_state.page = "HOME"
    
    # Apply CSS styling
    apply_styling()
    
    # Render sidebar with functional widgets
    render_sidebar()
    
    # Router - Central navigation controller
    router()
    
    # Bottom input bar (keep unchanged)
    render_input_bar()

def apply_styling():
    """Apply ChatGPT-inspired styling without overlay interference"""
    st.markdown("""
    <style>
    /* Design System Tokens */
    :root {
        --brand-primary: #3B82F6;
        --text-primary: #1F2937;
        --text-secondary: #4B5563;
        --text-tertiary: #6B7280;
        --text-muted: #9CA3AF;
        --bg-main: #F7F7F8;
        --bg-sidebar: #E5E7EB;
        --bg-surface: #FFFFFF;
        --bg-hover: #F3F4F6;
        --border-light: #E5E7EB;
        --header-bg: #F7F7F8;
        --input-bg: #FFFFFF;
        --input-border: #E5E7EB;
        --input-text: #111827;
        --input-placeholder: #9CA3AF;
    }
    
    /* Global Styles */
    body, .stApp {
        background-color: #FFFFFF !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
        color: #1F2937 !important;
    }
    
    /* Header Styles - Fixed positioning without sidebar overlap */
    header, .stApp header, div[data-testid="stHeader"] {
        background-color: var(--header-bg) !important;
        border-bottom: 1px solid var(--border-light) !important;
        box-shadow: none !important;
        height: 48px !important;
        z-index: 1000 !important;
        left: 260px !important;
        width: calc(100% - 260px) !important;
    }
    
    /* Hide default header content */
    header > div, .stApp header > div, div[data-testid="stHeader"] > div {
        display: none !important;
    }
    
    /* Custom Header */
    .custom-header {
        position: fixed !important;
        top: 0 !important;
        left: 260px !important;
        right: 0 !important;
        height: 48px !important;
        background-color: var(--header-bg) !important;
        border-bottom: 1px solid var(--border-light) !important;
        display: flex !important;
        align-items: center !important;
        justify-content: space-between !important;
        padding: 0 16px !important;
        z-index: 1000 !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
    }
    
    /* Sidebar Styles - REMOVED TEMPORARILY FOR TESTING */
    /* [data-testid="stSidebar"] { 
        background-color: #F0F4F8 !important; 
        border-right: 1px solid #E2E8F0 !important;
        padding: 20px 18px !important;
        width: 260px !important;
        min-width: 260px !important;
        max-width: 260px !important;
        font-family: 'Inter', -SF Pro Display, -Roboto, sans-serif !important;
        overflow-y: auto !important;
        overflow-x: hidden !important;
        display: block !important;
        visibility: visible !important;
        opacity: 1 !important;
    }
    
    .stSidebar {
        background-color: #F0F4F8 !important;
        display: block !important;
        visibility: visible !important;
        opacity: 1 !important;
    } */
    
    /* Sidebar Header - Premium */
    .sidebar-header {
        display: flex !important;
        align-items: center !important;
        gap: 12px !important;
        margin-bottom: 24px !important;
        font-size: 18px !important;
        font-weight: 700 !important;
        color: #FFFFFF !important;
    }
    
    .sidebar-header .icon {
        font-size: 20px !important;
        color: #FFFFFF !important;
    }
    
    /* Section Headers - Premium SaaS Style */
    .sidebar-section {
        font-family: 'Inter', -SF Pro Display, -Roboto, sans-serif !important;
        font-size: 11.5px !important;
        font-weight: 600 !important;
        letter-spacing: 0.05em !important;
        color: #5A7FA5 !important;
        text-transform: uppercase !important;
        margin: 22px 0 8px 0 !important;
        padding: 0 4px !important;
    }
    
    /* Business Profile Cards - Premium */
    .business-profile-card {
        background: rgba(255, 255, 255, 0.1) !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        border-radius: 10px !important;
        padding: 14px 16px !important;
        margin-bottom: 16px !important;
        display: flex !important;
        align-items: center !important;
        gap: 12px !important;
        color: #FFFFFF !important;
        font-weight: 500 !important;
        font-size: 14px !important;
        backdrop-filter: blur(10px) !important;
        transition: all 0.3s ease !important;
    }
    .business-profile-card .icon {
        font-size: 18px !important;
        color: #FFFFFF !important;
        min-width: 18px !important;
    }
    
    /* Create Profile Button - Premium */
    .create-profile-btn {
        display: flex !important;
        align-items: center !important;
        gap: 12px !important;
        padding: 10px 12px !important;
        border-radius: 8px !important;
        background: rgba(255, 255, 255, 0.1) !important;
        color: #FFFFFF !important;
        font-weight: 500 !important;
        font-size: 14.5px !important;
        border: none !important;
        cursor: pointer !important;
        transition: all 0.18s ease !important;
        width: 100% !important;
        text-align: left !important;
    }
    
    .create-profile-btn:hover {
        background: rgba(255, 255, 255, 0.2) !important;
        transform: translateX(2px) !important;
    }
    
    /* Menu Item Style - Universal Premium */
    .menu-item {
        display: flex !important;
        align-items: center !important;
        gap: 12px !important;
        padding: 10px 12px !important;
        border-radius: 8px !important;
        font-size: 14.5px !important;
        font-weight: 500 !important;
        color: #FFFFFF !important;
        cursor: pointer !important;
        transition: all 0.18s ease !important;
        border: none !important;
        background: transparent !important;
        width: 100% !important;
        text-align: left !important;
        margin-bottom: 2px !important;
        box-sizing: border-box !important;
    }
    
    .menu-item .icon {
        font-size: 18px !important;
        color: #FFFFFF !important;
        min-width: 18px !important;
        transition: color 0.18s ease !important;
    }
    
    .menu-item:hover {
        background: rgba(255, 255, 255, 0.1) !important;
        transform: translateX(2px) !important;
    }
    
    .menu-item:hover .icon {
        color: #FFFFFF !important;
    }
    
    /* Active/Selected State */
    .menu-item.active {
        background: rgba(255, 255, 255, 0.2) !important;
        color: #FFFFFF !important;
        font-weight: 600 !important;
        border-left: 3px solid #FFFFFF !important;
        padding-left: 14px !important;
    }
    
    .menu-item.active .icon {
        color: #FFFFFF !important;
    }
    
    /* Streamlit button override - Premium */
    [data-testid="stSidebar"] button {
        display: flex !important;
        align-items: center !important;
        gap: 12px !important;
        padding: 10px 12px !important;
        border-radius: 8px !important;
        font-size: 14.5px !important;
        font-weight: 500 !important;
        color: #FFFFFF !important;
        background: transparent !important;
        border: none !important;
        cursor: pointer !important;
        transition: all 0.18s ease !important;
        width: 100% !important;
        text-align: left !important;
        margin: 0 0 2px 0 !important;
        box-sizing: border-box !important;
    }
    
    [data-testid="stSidebar"] button .icon {
        font-size: 18px !important;
        color: #FFFFFF !important;
        min-width: 18px !important;
        transition: color 0.18s ease !important;
    }
    
    [data-testid="stSidebar"] button:hover {
        background: rgba(255, 255, 255, 0.1) !important;
        transform: translateX(2px) !important;
    }
    
    [data-testid="stSidebar"] button:hover .icon {
        color: #FFFFFF !important;
    }
    
    /* Active button state */
    [data-testid="stSidebar"] button.active {
        background: rgba(255, 255, 255, 0.2) !important;
        color: #FFFFFF !important;
        font-weight: 600 !important;
        border-left: 3px solid #FFFFFF !important;
        padding-left: 14px !important;
    }
    
    [data-testid="stSidebar"] button.active .icon {
        color: #FFFFFF !important;
    }
    
    /* Sidebar Footer - Premium */
    .sidebar-footer {
        position: absolute !important;
        bottom: 20px !important;
        left: 18px !important;
        right: 18px !important;
        text-align: center !important;
        font-size: 12px !important;
        color: #5A7FA5 !important;
        opacity: 0.7 !important;
        margin-top: auto !important;
        padding-top: 25px !important;
        border-top: 1px solid rgba(79, 93, 117, 0.15) !important;
    }
    
    .sidebar-footer .footer-links {
        display: flex !important;
        justify-content: center !important;
        gap: 24px !important;
        margin-bottom: 8px !important;
    }
    
    .sidebar-footer .footer-link {
        color: #5A7FA5 !important;
        text-decoration: none !important;
        font-size: 12px !important;
        font-weight: 500 !important;
        transition: color 0.18s ease !important;
        display: flex !important;
        align-items: center !important;
        gap: 4px !important;
    }
    
    .sidebar-footer .footer-link:hover {
        color: #4F5D75 !important;
    }
    
    .sidebar-footer .footer-link .icon {
        font-size: 14px !important;
    }
    
    /* Input Bar Styles - Fixed positioning */
    .stChatInput,
    div[data-testid="stChatInput"] {
        position: fixed !important;
        bottom: 0 !important;
        left: 260px !important;
        right: 0 !important;
        background: var(--input-bg) !important;
        padding: 20px !important;
        border-top: 1px solid var(--input-border) !important;
        z-index: 100 !important;
        display: flex !important;
        justify-content: center !important;
        width: calc(100% - 260px) !important;
    }
    
    .stChatInput > div,
    div[data-testid="stChatInput"] > div {
        max-width: 760px !important;
        width: 100% !important;
    }
    
    /* Input Field Styles */
    .stTextInput input {
        border-radius: 24px !important;
        padding: 12px 48px 12px 16px !important;
        border: 1px solid var(--input-border) !important;
        background-color: var(--input-bg) !important;
        font-size: 14px !important;
        color: var(--input-text) !important;
        box-shadow: 0 1px 2px rgba(0,0,0,0.04) !important;
    }
    
    .stTextInput input::placeholder {
        color: #000000 !important;
        opacity: 0.7 !important;
    }
    
    .stTextInput input:focus::placeholder {
        color: #000000 !important;
        opacity: 0.5 !important;
    }
    
    /* Hero Section */
    .hero-section {
        text-align: center !important;
        margin: 40px auto !important;
        padding: 60px 0 !important;
        background: var(--bg-surface) !important;
        border-radius: var(--border-radius) !important;
        box-shadow: var(--shadow-light) !important;
        border: 1px solid var(--border-light) !important;
        max-width: 900px !important;
        width: 100% !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
    }
    
    .hero-title {
        font-size: 36px !important;
        font-weight: 600 !important;
        color: #000000 !important;
        text-align: center !important;
        margin-bottom: 12px !important;
        line-height: 1.2 !important;
        align-self: center !important;
    }
    
    .hero-subtitle {
        font-size: 16px !important;
        font-weight: 400 !important;
        color: #000000 !important;
        text-align: center !important;
        margin-bottom: 0 !important;
        line-height: 1.4 !important;
        align-self: center !important;
    }
    
    /* Ensure main content allows centering */
    .main-content {
        padding: 24px !important;
        margin-left: 260px !important;
        display: block !important;
    }
    
    /* Page content styling for all non-home pages */
    .page-content {
        background: white !important;
        border: 1px solid #E5E7EB !important;
        border-radius: 12px !important;
        box-shadow: 0px 1px 3px rgba(0,0,0,0.06) !important;
        padding: 48px !important;
        margin: 24px auto !important;
        max-width: 800px !important;
        width: 100% !important;
    }
    
    .page-content h2 {
        font-size: 28px !important;
        font-weight: 600 !important;
        color: #000000 !important;
        margin: 0 0 20px 0 !important;
        line-height: 1.3 !important;
    }
    
    .page-content p {
        font-size: 16px !important;
        font-weight: 400 !important;
        color: #000000 !important;
        line-height: 1.6 !important;
        margin: 16px 0 !important;
    }
    
    .page-content ul {
        margin: 20px 0 !important;
        padding-left: 24px !important;
    }
    
    .page-content li {
        font-size: 16px !important;
        font-weight: 400 !important;
        color: #000000 !important;
        line-height: 1.6 !important;
        margin: 12px 0 !important;
    }
    
    .page-content em {
        font-size: 14px !important;
        font-weight: 400 !important;
        color: #666666 !important;
        font-style: italic !important;
        margin: 24px 0 0 0 !important;
        display: block !important;
    }
}
</style>
    """, unsafe_allow_html=True)
    
    # Custom Header
    st.markdown("""
    <div class="custom-header">
        <div class="header-title">
            <span style="font-size: 16px; color: #000000;">🏢</span>
            <span style="color: #000000;">BizComply AI</span>
        </div>
        <div class="header-actions">
            <button title="Settings">
                <span style="font-size: 14px; color: var(--text-tertiary);">⚙️</span>
            </button>
        </div>
    </div>
    """, unsafe_allow_html=True)

def set_page(page_name):
    """Helper function to set current page"""
    st.session_state.page = page_name

def render_sidebar():
    """Render sidebar with premium SaaS dashboard styling"""
    
    with st.sidebar:
        # Sidebar Header - Premium
        st.markdown("""
        <div class="sidebar-header">
            <span class="icon">🏢</span>
            <span>BizComply AI</span>
        </div>
        """, unsafe_allow_html=True)
        
        # Business Profile Section
        st.markdown('<div class="sidebar-section">Business Profile</div>', unsafe_allow_html=True)
        
        try:
            active_profile = business_profile_manager.get_active_profile()
            
            if active_profile:
                st.markdown(f"""
                <div class="business-profile-card">
                    <span class="icon">🏢</span>
                    <span>{active_profile['business_name']}</span>
                </div>
                """, unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("✏️ Edit", key="edit_profile", use_container_width=True):
                        set_page("PROFILE_EDIT")
                with col2:
                    if st.button("🗑️ Delete", key="delete_profile", use_container_width=True):
                        if active_profile:
                            business_profile_manager.delete_profile(active_profile['id'])
                        set_page("HOME")
            else:
                st.markdown("""
                <div class="business-profile-card">
                    <span class="icon">📋</span>
                    <span>No business profile set</span>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button("➕ Create Profile", key="create_profile", use_container_width=True):
                    set_page("PROFILE_CREATE")
        except Exception as e:
            st.write("Business profile temporarily unavailable")
        
        # Conversations Section
        st.markdown('<div class="sidebar-section">Conversations</div>', unsafe_allow_html=True)
        
        # New Chat with active state
        if st.session_state.page == "HOME":
            st.markdown("""
            <div class="menu-item active">
                <span class="icon">💬</span>
                <span>New Chat</span>
            </div>
            """, unsafe_allow_html=True)
        else:
            if st.button("💬 New Chat", key="new_chat", use_container_width=True):
                set_page("HOME")
        
        # Chat History Section
        st.markdown('<div class="sidebar-section">Chat History</div>', unsafe_allow_html=True)
        
        # Display chat history if messages exist
        if "messages" in st.session_state and st.session_state.messages:
            # Group messages by session/conversation
            chat_sessions = []
            current_session = []
            
            for i, message in enumerate(st.session_state.messages):
                current_session.append(message)
                
                # Create a new session every 2 messages (user + assistant)
                if len(current_session) == 2:
                    chat_sessions.append({
                        "id": len(chat_sessions),
                        "title": current_session[0]["content"][:30] + "..." if len(current_session[0]["content"]) > 30 else current_session[0]["content"],
                        "preview": current_session[1]["content"][:40] + "..." if len(current_session[1]["content"]) > 40 else current_session[1]["content"],
                        "messages": current_session.copy()
                    })
                    current_session = []
            
            # Add any remaining messages
            if current_session:
                chat_sessions.append({
                    "id": len(chat_sessions),
                    "title": current_session[0]["content"][:30] + "..." if len(current_session[0]["content"]) > 30 else current_session[0]["content"],
                    "preview": "Continuing conversation...",
                    "messages": current_session.copy()
                })
            
            # Display chat sessions
            for session in chat_sessions[-5:]:  # Show last 5 sessions
                if st.button(f"💭 {session['title']}", key=f"chat_{session['id']}", use_container_width=True):
                    # Store selected chat session
                    st.session_state.selected_chat = session
                    st.session_state.page = "HOME"
                    st.rerun()
            
            # Clear chat history option
            if st.button("🗑️ Clear Chat History", key="clear_history", use_container_width=True):
                st.session_state.messages = []
                st.session_state.selected_chat = None
                st.rerun()
        else:
            st.markdown("""
            <div style="color: #FFFFFF; opacity: 0.7; font-size: 12px; padding: 10px;">
                No chat history yet
            </div>
            """, unsafe_allow_html=True)
        
        # Recent Section
        st.markdown('<div class="sidebar-section">Recent</div>', unsafe_allow_html=True)
        
        # GDPR Compliance
        if st.session_state.page == "GDPR":
            st.markdown("""
            <div class="menu-item active">
                <span class="icon">🛡️</span>
                <span>GDPR Compliance</span>
            </div>
            """, unsafe_allow_html=True)
        else:
            if st.button("🛡️ GDPR Compliance", key="gdpr", use_container_width=True):
                set_page("GDPR")
                st.rerun()
        
        # License Query
        if st.session_state.page == "LICENSE_QUERY":
            st.markdown("""
            <div class="menu-item active">
                <span class="icon">🔍</span>
                <span>License Query</span>
            </div>
            """, unsafe_allow_html=True)
        else:
            if st.button("🔍 License Query", key="license_query", use_container_width=True):
                set_page("LICENSE_QUERY")
        
        # Tax Questions
        if st.session_state.page == "TAX":
            st.markdown("""
            <div class="menu-item active">
                <span class="icon">📊</span>
                <span>Tax Questions</span>
            </div>
            """, unsafe_allow_html=True)
        else:
            if st.button("📊 Tax Questions", key="tax_questions", use_container_width=True):
                set_page("TAX")
        
        # Registration
        if st.session_state.page == "REGISTRATION":
            st.markdown("""
            <div class="menu-item active">
                <span class="icon">📝</span>
                <span>Registration</span>
            </div>
            """, unsafe_allow_html=True)
        else:
            if st.button("📝 Registration", key="registration", use_container_width=True):
                set_page("REGISTRATION")
        
        # Tools Section
        st.markdown('<div class="sidebar-section">Tools</div>', unsafe_allow_html=True)
        
        # License Finder
        if st.session_state.page == "LICENSE_FINDER":
            st.markdown("""
            <div class="menu-item active">
                <span class="icon">🔎</span>
                <span>License Finder</span>
            </div>
            """, unsafe_allow_html=True)
        else:
            if st.button("🔎 License Finder", key="license_finder", use_container_width=True):
                set_page("LICENSE_FINDER")
        
        # Tax Calculator
        if st.session_state.page == "TAX_CALC":
            st.markdown("""
            <div class="menu-item active">
                <span class="icon">🧮</span>
                <span>Tax Calculator</span>
            </div>
            """, unsafe_allow_html=True)
        else:
            if st.button("🧮 Tax Calculator", key="tax_calculator", use_container_width=True):
                set_page("TAX_CALC")
        
        # Registration Helper
        if st.session_state.page == "REGISTRATION_HELPER":
            st.markdown("""
            <div class="menu-item active">
                <span class="icon">📋</span>
                <span>Registration Helper</span>
            </div>
            """, unsafe_allow_html=True)
        else:
            if st.button("📋 Registration Helper", key="registration_helper", use_container_width=True):
                set_page("REGISTRATION_HELPER")
        
        # Compliance Calendar
        if st.session_state.page == "COMPLIANCE_CALENDAR":
            st.markdown("""
            <div class="menu-item active">
                <span class="icon">📅</span>
                <span>Compliance Calendar</span>
            </div>
            """, unsafe_allow_html=True)
        else:
            if st.button("📅 Compliance Calendar", key="compliance_calendar", use_container_width=True):
                set_page("COMPLIANCE_CALENDAR")
        
        # Footer - Premium
        st.markdown("""
        <div class="sidebar-footer">
            <div class="footer-links">
                <a href="#" class="footer-link">
                    <span class="icon">⚙️</span>
                    <span>Settings</span>
                </a>
                <a href="#" class="footer-link">
                    <span class="icon">💡</span>
                    <span>Tips</span>
                </a>
            </div>
            <div>© BizComply AI 2025</div>
        </div>
        """, unsafe_allow_html=True)

def router():
    """Central router function for page navigation"""
    
    st.markdown('<div class="main-content">', unsafe_allow_html=True)
    
    page = st.session_state.get("page", "HOME")
    
    if page == "HOME":
        show_home_page()
    elif page == "GDPR":
        show_gdpr_page()
    elif page == "LICENSE_QUERY":
        show_license_query_page()
    elif page == "TAX":
        show_tax_questions_page()
    elif page == "REGISTRATION":
        show_registration_page()
    elif page == "LICENSE_FINDER":
        show_license_finder_page()
    elif page == "TAX_CALC":
        show_tax_calculator_page()
    elif page == "REGISTRATION_HELPER":
        show_registration_helper_page()
    elif page == "COMPLIANCE_CALENDAR":
        show_compliance_calendar_page()
    elif page == "PROFILE_CREATE":
        show_profile_create_page()
    elif page == "PROFILE_EDIT":
        show_profile_edit_page()
    else:
        show_home_page()
    
    st.markdown('</div>', unsafe_allow_html=True)

def show_home_page():
    """Home page with chat interface"""
    
    # Display selected chat history if available
    if "selected_chat" in st.session_state and st.session_state.selected_chat:
        st.markdown(f"""
        <div class="page-content">
            <h2>💭 Chat History</h2>
            <p><em>Previous conversation: {st.session_state.selected_chat['title']}</em></p>
            <div style="border-top: 1px solid #E5E7EB; margin-top: 20px; padding-top: 20px;">
        """, unsafe_allow_html=True)
        
        # Display messages from selected chat
        for message in st.session_state.selected_chat['messages']:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        st.markdown("""</div>
            <p><em>You can continue this conversation by typing a message below...</em></p>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Default welcome message
        st.markdown("""
        <div class="hero-section">
            <h1>Welcome to BizComply AI</h1>
            <p>Your Business Compliance Copilot</p>
            <p>Ask me anything about business licenses, taxes, regulations, and compliance requirements.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Chat messages
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Display current chat messages (excluding the ones already shown in history)
    start_index = 0
    if "selected_chat" in st.session_state and st.session_state.selected_chat:
        # Find where the selected chat messages end to avoid duplication
        selected_messages = st.session_state.selected_chat['messages']
        start_index = len(selected_messages)
    
    for message in st.session_state.messages[start_index:]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

def show_gdpr_page():
    """GDPR Compliance page"""
    st.markdown("""
    <div class="page-content">
        <h2>📋 GDPR Compliance</h2>
        <p>GDPR applies if you handle data of EU citizens. Here's what you need to know:</p>
        <ul>
            <li>🔒 Data protection officer (if >250 employees)</li>
            <li>📋 Privacy policy and consent forms</li>
            <li>🔐 Data breach notification within 72 hours</li>
            <li>📊 Data processing records</li>
            <li>🎯 Data protection impact assessments</li>
        </ul>
        <em>Would you like me to help you create a GDPR compliance checklist for your specific business?</em>
    </div>
    """, unsafe_allow_html=True)

def show_license_query_page():
    """License Query page"""
    st.markdown("""
    <div class="page-content">
        <h2>🔍 Business License Requirements</h2>
        <p>Most businesses need these basic licenses:</p>
        <ul>
            <li>🏢 Business operating license</li>
            <li>🏭 Industry-specific permits</li>
            <li>📍 Local zoning permits</li>
            <li>💳 Seller's permit (if selling goods)</li>
            <li>🏥 Health department permits (if applicable)</li>
        </ul>
        <p><em>Tell me about your business type and location, and I'll provide specific license requirements!</em></p>
    </div>
    """, unsafe_allow_html=True)

def show_tax_questions_page():
    """Tax Questions page"""
    st.markdown("""
    <div class="page-content">
        <h2>🧾 Business Tax Compliance</h2>
        <p>Common tax requirements for businesses:</p>
        <ul>
            <li>📊 Federal tax ID (EIN)</li>
            <li>🏢 State tax registration</li>
            <li>💰 Income tax filing</li>
            <li>🛒 Sales tax collection</li>
            <li>👥 Payroll taxes (if you have employees)</li>
            <li>📅 Quarterly estimated taxes</li>
        </ul>
        <p><em>What's your business structure and location? I'll provide specific tax requirements!</em></p>
    </div>
    """, unsafe_allow_html=True)

def show_registration_page():
    """Registration page"""
    st.markdown("""
    <div class="page-content">
        <h2>📝 Business Registration Requirements</h2>
        <p>Essential registrations for your business:</p>
        <ul>
            <li>🏢 Business entity registration</li>
            <li>📋 Trade name registration</li>
            <li>🔢 Tax ID numbers</li>
            <li>🏭 Industry-specific registrations</li>
            <li>📍 Local business permits</li>
            <li>🏛️ Professional licenses (if applicable)</li>
        </ul>
        <p><em>What type of business are you registering? I'll guide you through the specific requirements!</em></p>
    </div>
    """, unsafe_allow_html=True)

def show_license_finder_page():
    """License Finder tool page"""
    st.markdown("""
    <div class="page-content">
        <h2>🔍 License Finder Tool</h2>
        <p>Let me help you find the right licenses for your business!</p>
        <p><strong>Please provide:</strong></p>
        <ul>
            <li>🏢 Business type/industry</li>
            <li>📍 Location (city/state)</li>
            <li>👥 Business activities</li>
            <li>💰 Expected revenue</li>
        </ul>
        <p><em>I'll search and provide a comprehensive list of required licenses and permits!</em></p>
    </div>
    """, unsafe_allow_html=True)

def show_tax_calculator_page():
    """Tax Calculator tool page"""
    st.markdown("""
    <div class="page-content">
        <h2>🧮 Tax Calculator Tool</h2>
        <p>Estimate your business tax obligations:</p>
        <p><strong>Information needed:</strong></p>
        <ul>
            <li>💰 Annual revenue</li>
            <li>🏢 Business structure</li>
            <li>👥 Number of employees</li>
            <li>📍 Business location</li>
            <li>📊 Business expenses</li>
        </ul>
        <p><em>Provide these details and I'll estimate your tax liabilities and filing requirements!</em></p>
    </div>
    """, unsafe_allow_html=True)

def show_registration_helper_page():
    """Registration Helper tool page"""
    st.markdown("""
    <div class="page-content">
        <h2>📝 Registration Helper Tool</h2>
        <p>Step-by-step registration guidance:</p>
        <p><strong>Tell me about:</strong></p>
        <ul>
            <li>🏢 Business structure you want</li>
            <li>📍 Where you'll operate</li>
            <li>💼 Business activities</li>
            <li>👥 Business partners (if any)</li>
        </ul>
        <p><em>I'll provide a complete registration checklist with forms, fees, and deadlines!</em></p>
    </div>
    """, unsafe_allow_html=True)

def show_compliance_calendar_page():
    """Compliance Calendar tool page"""
    st.markdown("""
    <div class="page-content">
        <h2>📅 Compliance Calendar Tool</h2>
        <p>Track important compliance deadlines:</p>
        <p><strong>Common filing dates:</strong></p>
        <ul>
            <li>📊 Quarterly tax returns (Apr 15, Jun 15, Sep 15, Jan 15)</li>
            <li>🏢 Annual reports (varies by state)</li>
            <li>👥 Payroll tax filings (monthly/quarterly)</li>
            <li>📋 License renewals (annual/biennial)</li>
            <li>💰 Sales tax returns (monthly/quarterly)</li>
        </ul>
        <p><em>What's your business type and location? I'll create a personalized compliance calendar!</em></p>
    </div>
    """, unsafe_allow_html=True)

def show_profile_create_page():
    """Profile creation page"""
    st.markdown('<div class="page-content">', unsafe_allow_html=True)
    
    st.markdown("### 📝 Create Business Profile")
    st.markdown('<style>div[data-testid="stMarkdownContainer"] > h3 { color: #000000 !important; }</style>', unsafe_allow_html=True)
    
    with st.form("create_profile_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            business_name = st.text_input("Business Name*", placeholder="Enter your business name")
            registration_number = st.text_input("Registration Number", placeholder="Business registration number")
            location = st.text_input("Location*", placeholder="City, State/Country")
        
        with col2:
            industry = st.selectbox("Industry*", options=["retail", "technology", "healthcare", "restaurant", "consulting", "manufacturing", "construction"], format_func=lambda x: x.title())
            business_type = st.selectbox("Business Type*", options=["LLC", "Corporation", "Sole Proprietorship", "Partnership", "S-Corp", "C-Corp"])
            employee_count = st.selectbox("Employee Count", options=["1-10", "11-50", "51-100", "101-250", "250+"])
        
        revenue_range = st.selectbox("Annual Revenue Range", options=["Under $50K", "$50K-$100K", "$100K-$500K", "$500K-$1M", "$1M-$5M", "Over $5M"])
        
        col_submit, col_cancel = st.columns(2)
        
        with col_submit:
            submitted = st.form_submit_button("💾 Save Profile", use_container_width=True)
        
        with col_cancel:
            if st.form_submit_button("❌ Cancel", use_container_width=True):
                set_page("HOME")
                st.rerun()
        
        if submitted:
            if business_name and location and industry and business_type:
                profile_data = {
                    'business_name': business_name,
                    'registration_number': registration_number,
                    'location': location,
                    'industry': industry,
                    'business_type': business_type,
                    'employee_count': employee_count,
                    'revenue_range': revenue_range
                }
                
                profile_id = business_profile_manager.create_profile(profile_data)
                business_profile_manager.set_active_profile(profile_id)
                st.success("✅ Business profile created successfully!")
                set_page("HOME")
                st.rerun()
            else:
                st.error("❌ Please fill in all required fields (*)")
    
    st.markdown('</div>', unsafe_allow_html=True)

def show_profile_edit_page():
    """Profile edit page"""
    st.markdown('<div class="page-content">', unsafe_allow_html=True)
    
    active_profile = business_profile_manager.get_active_profile()
    
    if not active_profile:
        st.warning("No business profile found. Please create one first.")
        if st.button("Create Profile", use_container_width=True):
            set_page("PROFILE_CREATE")
            st.rerun()
        return
    
    st.markdown("### ✏️ Edit Business Profile")
    
    with st.form("edit_profile_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            business_name = st.text_input("Business Name*", value=active_profile['business_name'])
            registration_number = st.text_input("Registration Number", value=active_profile['registration_number'])
            location = st.text_input("Location*", value=active_profile['location'])
        
        with col2:
            industry = st.selectbox("Industry*", options=["retail", "technology", "healthcare", "restaurant", "consulting", "manufacturing", "construction"], index=["retail", "technology", "healthcare", "restaurant", "consulting", "manufacturing", "construction"].index(active_profile['industry']), format_func=lambda x: x.title())
            business_type = st.selectbox("Business Type*", options=["LLC", "Corporation", "Sole Proprietorship", "Partnership", "S-Corp", "C-Corp"], index=["LLC", "Corporation", "Sole Proprietorship", "Partnership", "S-Corp", "C-Corp"].index(active_profile['business_type']))
            employee_count = st.selectbox("Employee Count", options=["1-10", "11-50", "51-100", "101-250", "250+"], index=["1-10", "11-50", "51-100", "101-250", "250+"].index(active_profile['employee_count']))
        
        revenue_range = st.selectbox("Annual Revenue Range", options=["Under $50K", "$50K-$100K", "$100K-$500K", "$500K-$1M", "$1M-$5M", "Over $5M"], index=["Under $50K", "$50K-$100K", "$100K-$500K", "$500K-$1M", "$1M-$5M", "Over $5M"].index(active_profile['revenue_range']))
        
        col_submit, col_cancel = st.columns(2)
        
        with col_submit:
            submitted = st.form_submit_button("💾 Update Profile", use_container_width=True)
        
        with col_cancel:
            if st.form_submit_button("❌ Cancel", use_container_width=True):
                set_page("HOME")
                st.rerun()
        
        if submitted:
            if business_name and location and industry and business_type:
                profile_data = {
                    'business_name': business_name,
                    'registration_number': registration_number,
                    'location': location,
                    'industry': industry,
                    'business_type': business_type,
                    'employee_count': employee_count,
                    'revenue_range': revenue_range
                }
                
                business_profile_manager.update_profile(active_profile['id'], profile_data)
                st.success("✅ Business profile updated successfully!")
                set_page("HOME")
                st.rerun()
            else:
                st.error("❌ Please fill in all required fields (*)")
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_input_bar():
    """Render bottom input bar for chat functionality"""
    
    # Only show on home page
    if st.session_state.get("page", "HOME") == "HOME":
        # Update placeholder based on whether we're continuing a conversation
        if "selected_chat" in st.session_state and st.session_state.selected_chat:
            placeholder_text = f"Continue your conversation about: {st.session_state.selected_chat['title']}..."
        else:
            placeholder_text = "Type your question about business compliance, licenses, taxes, or regulations here..."
        
        if prompt := st.chat_input(placeholder_text):
            # Add user message
            if "messages" not in st.session_state:
                st.session_state.messages = []
            
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Get active business profile
            active_profile = business_profile_manager.get_active_profile()
            
            # Generate personalized response using compliance engine
            response = compliance_engine.get_personalized_response(prompt, active_profile)
            
            st.session_state.messages.append({"role": "assistant", "content": response})
            with st.chat_message("assistant"):
                st.markdown(response)
            st.rerun()

if __name__ == "__main__":
    main()

import streamlit as st
from business_profile import business_profile_manager
from compliance_engine import compliance_engine

def main():
    st.set_page_config(page_title="BizComply AI", page_icon="🏢", layout="wide")
    
    # ChatGPT-inspired CSS - Professional Design System with CSS Variables
    st.markdown("""
    <style>
    /* Design System Tokens */
    :root {
        /* Brand Colors */
        --brand-primary: #3B82F6;
        --brand-primary-dark: #2563EB;
        --brand-secondary: #1E40AF;
        
        /* Background Colors */
        --bg-main: #F7F7F8;
        --bg-sidebar: #F9FAFB;
        --bg-surface: #FFFFFF;
        --bg-input: #FFFFFF;
        --bg-hover: #F3F4F6;
        
        /* Text Colors */
        --text-primary: #1F2937;
        --text-secondary: #4B5563;
        --text-tertiary: #6B7280;
        --text-muted: #9CA3AF;
        --text-inactive: #D1D5DB;
        
        /* Border Colors */
        --border-light: #E5E7EB;
        --border-divider: #E5E7EB;
        --border-focus: #3B82F6;
        
        /* Component Colors */
        --header-bg: #F7F7F8;
        --header-text: #1F2937;
        --header-icon: #6B7280;
        --header-hover: #EFEFEF;
        
        --sidebar-bg: #F9FAFB;
        --sidebar-item-text: #4B5563;
        --sidebar-item-hover-bg: #F3F4F6;
        --sidebar-item-hover-text: #111827;
        --sidebar-item-active-bg: #E5E7EB;
        --sidebar-item-active-icon: #111827;
        --sidebar-section-label: #9CA3AF;
        
        --input-bg: #FFFFFF;
        --input-border: #E5E7EB;
        --input-text: #111827;
        --input-placeholder: #9CA3AF;
        --input-icon: #6B7280;
        --input-icon-hover: #111827;
        
        --card-bg: #FFFFFF;
        --card-border: #E5E7EB;
        --card-header: #1F2937;
        --card-body: #4B5563;
        --card-icon: #6B7280;
        --card-hover: #F3F4F6;
        
        /* Icon Colors */
        --icon-default: #6B7280;
        --icon-hover: #111827;
        --icon-active: #2563EB;
        --icon-disabled: #D1D5DB;
        
        /* Shadows */
        --shadow-light: 0 1px 2px rgba(0,0,0,0.04);
        --shadow-hover: 0 2px 6px rgba(0,0,0,0.06);
    }
    
    /* Font and Base Styles */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');
    
    body { 
        background-color: var(--bg-main) !important; 
        margin: 0 !important; 
        padding: 0 !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
    }
    .stApp { 
        background-color: var(--bg-main) !important; 
    }
    
    /* Force Header Colors - Override Streamlit Defaults */
    .stApp header,
    .stApp > header,
    header.stApp,
    div[data-testid="stHeader"] {
        height: 48px !important;
        background-color: #F7F7F8 !important;
        border-bottom: 1px solid #E5E7EB !important;
        padding: 0 16px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: space-between !important;
        box-shadow: none !important;
    }
    
    /* Hide all default header elements */
    .stApp header > div,
    .stApp > header > div,
    header.stApp > div,
    div[data-testid="stHeader"] > div {
        display: none !important;
    }
    
    /* Custom Header Content */
    .custom-header {
        display: flex !important;
        align-items: center !important;
        justify-content: space-between !important;
        width: 100% !important;
        height: 48px !important;
        padding: 0 16px !important;
        background-color: #F7F7F8 !important;
        border-bottom: 1px solid #E5E7EB !important;
        position: fixed !important;
        top: 0 !important;
        left: 0 !important;
        right: 0 !important;
        z-index: 999 !important;
    }
    
    .header-title {
        font-size: 16px !important;
        font-weight: 500 !important;
        color: #1F2937 !important;
        display: flex !important;
        align-items: center !important;
        gap: 8px !important;
        margin: 0 !important;
    }
    
    .header-actions {
        display: flex !important;
        align-items: center !important;
        gap: 8px !important;
    }
    
    .header-actions button {
        color: #6B7280 !important;
        background: none !important;
        border: none !important;
        cursor: pointer !important;
        padding: 4px !important;
        border-radius: 4px !important;
        transition: background-color 0.2s ease !important;
    }
    
    .header-actions button:hover {
        background-color: #EFEFEF !important;
        color: #111827 !important;
    }
    
    /* Improved Sidebar - ChatGPT Style */
    [data-testid="stSidebar"] { 
        background-color: #E5E7EB !important; 
        border-right: 1px solid #D1D5DB !important;
        padding: 8px 6px !important;
        width: 240px !important;
        min-width: 240px !important;
        max-width: 240px !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: stretch !important;
        overflow: visible !important;
    }
    
    [data-testid="stSidebar"] > div > div {
        padding: 0 !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: stretch !important;
        width: 100% !important;
        min-width: 100% !important;
        overflow: visible !important;
    }
    
    /* Core fix - horizontal flex container for each sidebar row */
    [data-testid="stSidebar"] button {
        display: flex !important;
        flex-direction: row !important;
        align-items: center !important;
        justify-content: flex-start !important;
        gap: 10px !important;
        white-space: nowrap !important;
        overflow: visible !important;
        text-overflow: clip !important;
        width: 100% !important;
        min-width: 200px !important;
        max-width: 100% !important;
        padding: 10px 14px !important;
        margin: 2px 0 !important;
        text-align: left !important;
        font-size: 13px !important;
        font-weight: 400 !important;
        color: #6B7280 !important;
        background-color: transparent !important;
        border: none !important;
        border-radius: 4px !important;
        transition: all 0.2s ease !important;
        order: 0 !important;
        flex-shrink: 0 !important;
        position: relative !important;
        left: 0 !important;
        right: 0 !important;
    }
    
    [data-testid="stSidebar"] button:hover {
        background-color: #F3F4F6 !important;
        color: #111827 !important;
    }
    
    /* Lock icon size and prevent shrinking - FORCE LEFT POSITION */
    [data-testid="stSidebar"] button span:first-child {
        width: 18px !important;
        height: 18px !important;
        flex-shrink: 0 !important;
        display: inline-flex !important;
        font-size: 14px !important;
        line-height: 1 !important;
        text-align: center !important;
        order: 0 !important;
        position: absolute !important;
        left: 14px !important;
        align-items: center !important;
        justify-content: center !important;
    }
    
    /* Make label take remaining space and position correctly */
    [data-testid="stSidebar"] button .label,
    [data-testid="stSidebar"] button:not(:first-child) {
        display: inline-block !important;
        overflow: visible !important;
        text-overflow: clip !important;
        white-space: nowrap !important;
        max-width: calc(100% - 40px) !important;
        min-width: 150px !important;
        order: 1 !important;
        position: relative !important;
        left: 32px !important;
        margin-left: 0 !important;
        padding-left: 0 !important;
    }
    
    /* Section headers styling */
    [data-testid="stSidebar"] .sidebar-section {
        display: block !important;
        padding: 6px 8px !important;
        font-size: 11px !important;
        font-weight: 500 !important;
        color: #9CA3AF !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
        white-space: nowrap !important;
        overflow: visible !important;
        text-overflow: clip !important;
        width: 100% !important;
        min-width: 200px !important;
    }
    
    /* Force normal writing mode and prevent any vertical issues */
    [data-testid="stSidebar"] * {
        writing-mode: horizontal-tb !important;
        direction: ltr !important;
        transform: none !important;
        text-orientation: mixed !important;
        text-combine-upright: none !important;
    }
    
    /* Prevent any global CSS from affecting sidebar */
    [data-testid="stSidebar"] button,
    [data-testid="stSidebar"] button span,
    [data-testid="stSidebar"] button .label {
        float: none !important;
        clear: both !important;
        position: relative !important;
        display: flex !important;
        vertical-align: baseline !important;
    }
    
    .sidebar-item {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 6px 8px;
        border-radius: 4px;
        margin: 1px 0;
        cursor: pointer;
        transition: background-color 0.2s ease, color 0.2s ease;
        font-size: 13px;
        color: var(--sidebar-item-text);
        font-weight: 400 !important;
    }
    
    .sidebar-item:hover {
        background-color: var(--sidebar-item-hover-bg);
        color: var(--sidebar-item-hover-text);
    }
    
    .sidebar-item:hover .sidebar-icon {
        color: var(--sidebar-item-hover-text);
    }
    
    .sidebar-item.active {
        background-color: var(--sidebar-item-active-bg);
        color: var(--sidebar-item-hover-text);
    }
    
    .sidebar-item.active .sidebar-icon {
        color: var(--sidebar-item-active-icon);
    }
    
    .sidebar-icon {
        width: 16px;
        height: 16px;
        font-size: 14px;
        color: var(--icon-default);
        transition: color 0.2s ease;
    }
    
    .sidebar-section {
        padding: 6px 8px;
        font-size: 11px;
        font-weight: 500;
        color: var(--sidebar-section-label);
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Main Content Area - Clean Background */
    .main-content {
        max-width: 760px;
        margin: 0 auto;
        padding: 80px 20px 120px 20px;
        background-color: #F7F7F8 !important;
        position: relative !important;
        z-index: 1 !important;
    }
    
    /* Hero Section - ChatGPT Style - No Overlay */
    .hero-section {
        text-align: center;
        margin-bottom: 80px;
        padding: 60px 0;
        background: transparent !important;
        position: relative !important;
        z-index: 2 !important;
    }
    
    .hero-title {
        font-size: 36px !important;
        font-weight: 600 !important;
        color: #1F2937 !important;
        margin-bottom: 12px !important;
        line-height: 1.2 !important;
        opacity: 1 !important;
        visibility: visible !important;
    }
    
    .hero-subtitle {
        font-size: 16px !important;
        font-weight: 400 !important;
        color: #6B7280 !important;
        margin-bottom: 0 !important;
        line-height: 1.4 !important;
        opacity: 1 !important;
        visibility: visible !important;
    }
    
    /* Light Cards - ChatGPT Examples Style */
    .example-card {
        background-color: var(--card-bg);
        border: 1px solid var(--border-light);
        border-radius: 8px;
        padding: 16px;
        margin: 8px 0;
        cursor: pointer;
        transition: background-color 0.2s ease, box-shadow 0.2s ease;
        box-shadow: var(--shadow-light);
    }
    
    .example-card:hover {
        background-color: var(--card-hover);
        box-shadow: var(--shadow-hover);
    }
    
    .example-card-icon {
        color: var(--card-icon);
        font-size: 16px;
        margin-bottom: 8px;
    }
    
    .example-card-title {
        color: var(--card-header);
        font-weight: 500;
        font-size: 14px;
        margin-bottom: 4px;
    }
    
    .example-card-text {
        color: var(--card-body);
        font-size: 13px;
        line-height: 1.4;
    }
    
    /* Chat Messages */
    .stChatMessage {
        border-radius: 8px !important;
        margin-bottom: 16px !important;
        max-width: 100% !important;
        border: none !important;
    }
    
    .stChatMessage[data-testid="stChatMessage"] {
        background-color: var(--bg-hover) !important;
        margin-left: auto !important;
        margin-right: 0 !important;
        border-radius: 18px !important;
        text-align: center !important;
        max-width: 80% !important;
    }
    
    .stChatMessage[data-testid="stChatMessage"][data-message-role="assistant"] {
        background-color: var(--card-bg) !important;
        border: 1px solid var(--border-light) !important;
        margin-left: 0 !important;
        margin-right: auto !important;
        border-radius: 8px !important;
        max-width: 100% !important;
    }
    
    /* Force Input Bar Colors - Override Streamlit Defaults */
    .stChatInput,
    div[data-testid="stChatInput"] {
        position: fixed !important;
        bottom: 0 !important;
        left: 0 !important;
        right: 0 !important;
        background: #FFFFFF !important;
        padding: 20px !important;
        border-top: 1px solid #E5E7EB !important;
        z-index: 100 !important;
        display: flex !important;
        justify-content: center !important;
    }
    
    .stChatInput > div,
    div[data-testid="stChatInput"] > div {
        max-width: 760px !important;
        width: 100% !important;
    }
    
    /* Force Input Field Colors */
    .stTextInput input,
    .stTextInput textarea,
    .stTextInput > div > div > input,
    .stTextInput > div > div > textarea,
    input[data-testid="stTextInput"],
    textarea[data-testid="stTextInput"] {
        border-radius: 24px !important;
        padding: 12px 48px 12px 16px !important;
        border: 1px solid #E5E7EB !important;
        background-color: #FFFFFF !important;
        font-size: 14px !important;
        line-height: 1.5 !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
        transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
        font-weight: 400 !important;
        color: #111827 !important;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04) !important;
    }
    
    .stTextInput input::placeholder,
    .stTextInput textarea::placeholder,
    .stTextInput > div > div > input::placeholder,
    .stTextInput > div > div > textarea::placeholder,
    input[data-testid="stTextInput"]::placeholder,
    textarea[data-testid="stTextInput"]::placeholder {
        color: #9CA3AF !important;
    }
    
    .stTextInput input:focus,
    .stTextInput textarea:focus,
    .stTextInput > div > div > input:focus,
    .stTextInput > div > div > textarea:focus,
    input[data-testid="stTextInput"]:focus,
    textarea[data-testid="stTextInput"]:focus {
        border-color: #3B82F6 !important;
        outline: none !important;
        box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.1), 0 1px 2px rgba(0, 0, 0, 0.04) !important;
    }
    
    /* Force Send Button Colors */
    .stButton button,
    .stButton > button,
    button[data-testid="stBaseButton-primary"] {
        border-radius: 50% !important;
        width: 28px !important;
        height: 28px !important;
        min-width: 28px !important;
        padding: 0 !important;
        background-color: transparent !important;
        border: none !important;
        position: absolute !important;
        right: 8px !important;
        top: 50% !important;
        transform: translateY(-50%) !important;
        margin: 0 !important;
        color: #6B7280 !important;
        transition: color 0.2s ease !important;
    }
    
    .stButton button:hover,
    .stButton > button:hover,
    button[data-testid="stBaseButton-primary"]:hover {
        background-color: transparent !important;
        color: #111827 !important;
    }
    
    /* Responsive */
    @media (max-width: 768px) {
        .main-content {
            padding: 40px 16px 120px 16px;
        }
        
        .hero-title {
            font-size: 28px;
        }
        
        .hero-subtitle {
            font-size: 15px;
        }
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Custom Header - Apply Design System Colors
    st.markdown("""
    <div class="custom-header">
        <div class="header-title">
            <span style="font-size: 16px; color: #6B7280;">🏢</span>
            <span>BizComply AI</span>
        </div>
        <div class="header-actions">
            <button title="Settings">
                <span style="font-size: 14px; color: #6B7280;">⚙️</span>
            </button>
        </div>
    </div>
    
    <script>
    // Force Header Colors
    function fixHeaderColors() {
        const header = document.querySelector('header') || document.querySelector('.stApp > header');
        if (header) {
            header.style.backgroundColor = '#F7F7F8';
            header.style.borderBottom = '1px solid #E5E7EB';
            header.style.boxShadow = 'none';
            header.style.zIndex = '1000'; // Lower z-index to not block sidebar
        }
        
        // Hide default header content
        const headerDivs = document.querySelectorAll('header > div');
        headerDivs.forEach(div => div.style.display = 'none');
        
        // Show custom header
        const customHeader = document.querySelector('.custom-header');
        if (customHeader) {
            customHeader.style.display = 'flex';
            customHeader.style.position = 'fixed';
            customHeader.style.top = '0';
            customHeader.style.left = '0';
            customHeader.style.right = '0';
            customHeader.style.zIndex = '1000'; // Lower z-index
            customHeader.style.backgroundColor = '#F7F7F8';
            customHeader.style.borderBottom = '1px solid #E5E7EB';
            customHeader.style.pointerEvents = 'auto'; // Allow header clicks
        }
    }
    
    // Force Input Bar Colors
    function fixInputColors() {
        const chatInput = document.querySelector('[data-testid="stChatInput"]');
        if (chatInput) {
            chatInput.style.backgroundColor = '#FFFFFF';
            chatInput.style.borderTop = '1px solid #E5E7EB';
            chatInput.style.zIndex = '100'; // Lower z-index
        }
        
        // Force input field colors
        const textInputs = document.querySelectorAll('input[type="text"], textarea');
        textInputs.forEach(input => {
            input.style.backgroundColor = '#FFFFFF';
            input.style.border = '1px solid #E5E7EB';
            input.style.color = '#111827';
            input.style.boxShadow = '0 1px 2px rgba(0,0,0,0.04)';
        });
        
        // Force placeholder colors
        const style = document.createElement('style');
        style.textContent = 'input::placeholder, textarea::placeholder { color: #9CA3AF !important; }';
        document.head.appendChild(style);
    }
    
    // Fix Sidebar Clickability
    function fixSidebarClickability() {
        const sidebar = document.querySelector('[data-testid="stSidebar"]');
        if (sidebar) {
            // Ensure sidebar is clickable
            sidebar.style.pointerEvents = 'auto';
            sidebar.style.zIndex = '10';
            sidebar.style.position = 'relative';
            
            // Remove any overlays
            const overlays = sidebar.querySelectorAll('[style*="position: absolute"], [style*="position: fixed"]');
            overlays.forEach(overlay => {
                if (!overlay.classList.contains('sidebar-section')) {
                    overlay.style.pointerEvents = 'none';
                    overlay.style.zIndex = '1';
                }
            });
            
            // Fix all buttons in sidebar
            const buttons = sidebar.querySelectorAll('button');
            buttons.forEach(button => {
                button.style.pointerEvents = 'auto';
                button.style.cursor = 'pointer';
                button.style.position = 'relative';
                button.style.zIndex = '20';
                button.disabled = false;
                button.setAttribute('aria-disabled', 'false');
                
                // Remove any disabled classes
                button.classList.remove('disabled');
                button.style.opacity = '1';
            });
        }
    }
    
    // Apply fixes on load and periodically
    document.addEventListener('DOMContentLoaded', function() {
        fixHeaderColors();
        fixInputColors();
        fixSidebarClickability();
        setInterval(fixHeaderColors, 1000);
        setInterval(fixInputColors, 1000);
        setInterval(fixSidebarClickability, 500);
    });
    
    // Also apply immediately if DOM is already loaded
    fixHeaderColors();
    fixInputColors();
    fixSidebarClickability();
    
    // Add click debugging
    document.addEventListener('click', function(e) {
        if (e.target.closest('[data-testid="stSidebar"]')) {
            console.log('Sidebar clicked:', e.target);
        }
    });
    </script>
    """, unsafe_allow_html=True)
    
    # Sidebar with business profile management and functional items
    with st.sidebar:
        # Business Profile Section
        st.markdown("""
        <div class="sidebar-section" style="padding: 6px 8px; font-size: 11px; font-weight: 500; color: #9CA3AF; text-transform: uppercase; letter-spacing: 0.5px;">
            Business Profile
        </div>
        """, unsafe_allow_html=True)
        
        # Check if business profile exists
        active_profile = business_profile_manager.get_active_profile()
        
        if active_profile:
            st.success(f"🏢 {active_profile['business_name']}")
            if st.button("✏️ Edit Profile", key="edit_profile", use_container_width=True):
                st.session_state.show_profile_editor = True
            if st.button("🗑️ Delete Profile", key="delete_profile", use_container_width=True):
                business_profile_manager.delete_profile(active_profile['id'])
                st.session_state.show_profile_editor = False
                st.rerun()
        else:
            st.info("No business profile set")
            if st.button("➕ Create Profile", key="create_profile", use_container_width=True):
                st.session_state.show_profile_editor = True
        
        st.markdown("---", unsafe_allow_html=True)
        
        # New chat - clears conversation
        if st.button("📝 New Chat", key="new_chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
        
        st.markdown("---", unsafe_allow_html=True)
        
        st.markdown("""
        <div class="sidebar-section" style="padding: 6px 8px; font-size: 11px; font-weight: 500; color: #9CA3AF; text-transform: uppercase; letter-spacing: 0.5px;">
            Recent
        </div>
        """, unsafe_allow_html=True)
        
        # Recent conversations - functional buttons
        if st.button("📋 GDPR Compliance", key="gdpr", use_container_width=True):
            st.session_state.messages.append({
                "role": "assistant", 
                "content": """
                <p><strong>GDPR Compliance for Your Business</strong></p>
                <p>GDPR applies if you handle data of EU citizens. Here's what you need to know:</p>
                <ul>
                    <li>🔒 Data protection officer (if >250 employees)</li>
                    <li>📋 Privacy policy and consent forms</li>
                    <li>🔐 Data breach notification within 72 hours</li>
                    <li>📊 Data processing records</li>
                    <li>🎯 Data protection impact assessments</li>
                </ul>
                <p><em>Would you like me to help you create a GDPR compliance checklist for your specific business?</em></p>
                """
            })
            st.rerun()
        
        if st.button("🔍 License Query", key="license", use_container_width=True):
            st.session_state.messages.append({
                "role": "assistant", 
                "content": """
                <p><strong>Business License Requirements</strong></p>
                <p>Most businesses need these basic licenses:</p>
                <ul>
                    <li>🏢 Business operating license</li>
                    <li>🏭 Industry-specific permits</li>
                    <li>📍 Local zoning permits</li>
                    <li>💳 Seller's permit (if selling goods)</li>
                    <li>🏥 Health department permits (if applicable)</li>
                </ul>
                <p><em>Tell me about your business type and location, and I'll provide specific license requirements!</em></p>
                """
            })
            st.rerun()
        
        if st.button("🧾 Tax Questions", key="tax", use_container_width=True):
            st.session_state.messages.append({
                "role": "assistant", 
                "content": """
                <p><strong>Business Tax Compliance</strong></p>
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
                """
            })
            st.rerun()
        
        if st.button("📝 Registration", key="registration", use_container_width=True):
            st.session_state.messages.append({
                "role": "assistant", 
                "content": """
                <p><strong>Business Registration Requirements</strong></p>
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
                """
            })
            st.rerun()
        
        st.markdown("---", unsafe_allow_html=True)
        
        st.markdown("""
        <div class="sidebar-section" style="padding: 6px 8px; font-size: 11px; font-weight: 500; color: #9CA3AF; text-transform: uppercase; letter-spacing: 0.5px;">
            Tools
        </div>
        """, unsafe_allow_html=True)
        
        # Tools - functional buttons
        if st.button("🔍 License Finder", key="license_finder", use_container_width=True):
            st.session_state.messages.append({
                "role": "assistant", 
                "content": """
                <p><strong>🔍 License Finder Tool</strong></p>
                <p>Let me help you find the right licenses for your business!</p>
                <p><strong>Please provide:</strong></p>
                <ul>
                    <li>🏢 Business type/industry</li>
                    <li>📍 Location (city/state)</li>
                    <li>👥 Business activities</li>
                    <li>💰 Expected revenue</li>
                </ul>
                <p><em>I'll search and provide a comprehensive list of required licenses and permits!</em></p>
                """
            })
            st.rerun()
        
        if st.button("🧮 Tax Calculator", key="tax_calculator", use_container_width=True):
            st.session_state.messages.append({
                "role": "assistant", 
                "content": """
                <p><strong>🧮 Tax Calculator Tool</strong></p>
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
                """
            })
            st.rerun()
        
        if st.button("📝 Registration Helper", key="reg_helper", use_container_width=True):
            st.session_state.messages.append({
                "role": "assistant", 
                "content": """
                <p><strong>📝 Registration Helper Tool</strong></p>
                <p>Step-by-step registration guidance:</p>
                <p><strong>Tell me about:</strong></p>
                <ul>
                    <li>🏢 Business structure you want</li>
                    <li>📍 Where you'll operate</li>
                    <li>💼 Business activities</li>
                    <li>👥 Business partners (if any)</li>
                </ul>
                <p><em>I'll provide a complete registration checklist with forms, fees, and deadlines!</em></p>
                """
            })
            st.rerun()
        
        if st.button("📅 Compliance Calendar", key="calendar", use_container_width=True):
            st.session_state.messages.append({
                "role": "assistant", 
                "content": """
                <p><strong>📅 Compliance Calendar Tool</strong></p>
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
                """
            })
            st.rerun()
    
    # Main Content
    st.markdown('<div class="main-content">', unsafe_allow_html=True)
    
    # Business Profile Editor Modal
    if st.session_state.get('show_profile_editor', False):
        with st.expander("📝 Business Profile", expanded=True):
            active_profile = business_profile_manager.get_active_profile()
            
            with st.form("business_profile_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    business_name = st.text_input(
                        "Business Name*", 
                        value=active_profile['business_name'] if active_profile else "",
                        placeholder="Enter your business name"
                    )
                    registration_number = st.text_input(
                        "Registration Number", 
                        value=active_profile['registration_number'] if active_profile else "",
                        placeholder="Business registration number"
                    )
                    location = st.text_input(
                        "Location*", 
                        value=active_profile['location'] if active_profile else "",
                        placeholder="City, State/Country"
                    )
                
                with col2:
                    industry = st.selectbox(
                        "Industry*", 
                        options=["retail", "technology", "healthcare", "restaurant", "consulting", "manufacturing", "construction"],
                        index=0,
                        format_func=lambda x: x.title()
                    )
                    business_type = st.selectbox(
                        "Business Type*", 
                        options=["LLC", "Corporation", "Sole Proprietorship", "Partnership", "S-Corp", "C-Corp"],
                        index=0
                    )
                    employee_count = st.selectbox(
                        "Employee Count", 
                        options=["1-10", "11-50", "51-100", "101-250", "250+"],
                        index=0
                    )
                
                revenue_range = st.selectbox(
                    "Annual Revenue Range", 
                    options=["Under $50K", "$50K-$100K", "$100K-$500K", "$500K-$1M", "$1M-$5M", "Over $5M"],
                    index=0
                )
                
                col_submit, col_cancel = st.columns(2)
                
                with col_submit:
                    submitted = st.form_submit_button("💾 Save Profile", use_container_width=True)
                
                with col_cancel:
                    if st.form_submit_button("❌ Cancel", use_container_width=True):
                        st.session_state.show_profile_editor = False
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
                        
                        if active_profile:
                            # Update existing profile
                            business_profile_manager.update_profile(active_profile['id'], profile_data)
                            st.success("✅ Business profile updated successfully!")
                        else:
                            # Create new profile
                            profile_id = business_profile_manager.create_profile(profile_data)
                            business_profile_manager.set_active_profile(profile_id)
                            st.success("✅ Business profile created successfully!")
                        
                        st.session_state.show_profile_editor = False
                        st.rerun()
                    else:
                        st.error("❌ Please fill in all required fields (*)")
    
    # Hero Section - ChatGPT Style (No Box)
    if "messages" not in st.session_state or len(st.session_state.messages) == 0:
        st.markdown("""
        <div class="hero-section">
            <h1 class="hero-title">Welcome to BizComply AI</h1>
            <p class="hero-subtitle">Your Business Compliance Copilot</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Chat with business profile integration
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Chat Input with compliance engine
    if prompt := st.chat_input("Ask about licenses, taxes, or filings..."):
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

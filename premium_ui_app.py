#!/usr/bin/env python3
"""
Premium UI - Professional Enterprise Interface with All Improvements
"""

import os
import sys
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional
import json

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Premium UI CSS
def load_css():
    st.markdown("""
    <style>
    /* Premium UI - Professional Enterprise Interface */
    
    /* 1. Sidebar Improvements - Flat & Clean */
    .stSidebar {
        background-color: #0F172A !important;
        border-right: none !important;
    }
    
    .stSidebar .element-container {
        background-color: transparent !important;
        border: none !important;
        padding: 0 !important;
        margin: 0 !important;
    }
    
    .sidebar-header {
        background-color: transparent;
        color: #F8FAFC;
        padding: 20px 16px; /* Reduced padding */
        margin: -16px -16px 16px -16px; /* Reduced spacing */
    }
    
    .sidebar-header h1 {
        margin: 0;
        font-size: 1.5rem;
        font-weight: 600;
        color: #F8FAFC;
    }
    
    .sidebar-header p {
        margin: 4px 0 0 0;
        font-size: 0.875rem;
        color: #94A3B8;
    }
    
    .sidebar-section {
        margin-bottom: 16px; /* Reduced by ~20% */
        padding: 0 16px;
    }
    
    .sidebar-section-title {
        font-size: 0.75rem;
        font-weight: 500;
        color: #94A3B8;
        text-transform: uppercase;
        letter-spacing: 0.6px; /* Increased for premium feel */
        margin-bottom: 10px; /* Reduced spacing */
        padding: 0 4px;
    }
    
    /* New Conversation Button - Transparent Look */
    .new-conversation-btn {
        background-color: #1E293B;
        color: #F8FAFC;
        border: 1px solid #334155;
        border-radius: 6px;
        padding: 12px;
        margin-bottom: 16px; /* Reduced spacing */
        width: 100%;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.15s ease;
        font-size: 0.875rem;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    .new-conversation-btn:hover {
        background-color: #2C3446;
        border-color: #3B4457;
    }
    
    .new-conversation-btn .icon {
        color: #0EA5E9;
    }
    
    /* Recent Conversations - Thinner Borders */
    .conversation-item {
        border-radius: 6px;
        padding: 12px;
        margin-bottom: 6px; /* Reduced spacing */
        cursor: pointer;
        transition: all 0.15s ease;
        border: 1px solid rgba(255,255,255,0.06); /* Thin borders */
    }
    
    .conversation-item.inactive {
        background-color: transparent;
        color: #F8FAFC;
    }
    
    .conversation-item.inactive:hover {
        background-color: #1E293B;
    }
    
    .conversation-item.active {
        background-color: #0EA5E9;
        color: #FFFFFF;
        border-color: #0EA5E9;
    }
    
    .conversation-title {
        font-weight: 500;
        margin-bottom: 4px;
        line-height: 1.4;
        font-size: 0.875rem;
    }
    
    .conversation-meta {
        font-size: 0.75rem;
        opacity: 0.8;
    }
    
    /* Sidebar Stats Section */
    .stats-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 8px;
        border-top: 1px solid rgba(255,255,255,0.06);
        padding-top: 12px; /* Reduced spacing */
        margin-top: 12px; /* Reduced spacing */
    }
    
    .stat-item {
        background-color: transparent;
        border-radius: 6px;
        padding: 12px;
        text-align: center;
    }
    
    .stat-value {
        font-size: 1.25rem;
        font-weight: 600;
        color: #F1F5F9;
        margin-bottom: 2px;
    }
    
    .stat-label {
        font-size: 0.625rem;
        color: #94A3B8;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    /* 2. Top Header - Clean & Minimal */
    .main-header {
        background-color: #FFFFFF;
        padding: 16px 0; /* Reduced height by 40% */
        margin-bottom: 24px;
        border-bottom: 1px solid #E2E8F0;
        text-align: center; /* Center text */
    }
    
    .main-header h1 {
        margin: 0;
        font-size: 28px; /* Updated typography */
        font-weight: 600;
        color: #0F172A;
    }
    
    .main-header p {
        margin: 4px 0 0 0;
        color: #64748B;
        font-size: 14px; /* Updated typography */
        font-weight: 400;
    }
    
    /* Breadcrumb */
    .breadcrumb {
        font-size: 0.75rem;
        color: #64748B;
        margin-bottom: 8px;
        text-align: center;
    }
    
    /* 3. Metric Cards - Premium Consistency */
    .metric-box {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px; /* Updated border radius */
        padding: 24px; /* Increased internal padding */
        text-align: center;
        transition: all 0.15s ease;
    }
    
    .metric-box:hover {
        border-color: #0EA5E9;
        box-shadow: 0 1px 3px rgba(14, 165, 233, 0.1);
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 600;
        color: #0F172A; /* Bold value text */
        margin-bottom: 4px;
    }
    
    .metric-label {
        font-size: 0.75rem;
        color: #64748B; /* Medium label text */
        margin-bottom: 6px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        font-weight: 500;
    }
    
    .metric-trend {
        font-size: 0.75rem;
        font-weight: 500;
    }
    
    .metric-trend.positive {
        color: #16A34A; /* Positive state */
    }
    
    .metric-trend.negative {
        color: #DC2626; /* Negative state */
    }
    
    /* 4. Chat Bubbles - Better Separation */
    .user-message {
        background-color: #F8FAFC; /* Updated bubble bg */
        color: #334155; /* Updated body text */
        border: 1px solid #E2E8F0; /* Updated bubble border */
        padding: 16px 20px; /* Updated padding */
        margin: 24px 0; /* 24px vertical spacing */
        border-radius: 10px; /* Updated border radius */
        max-width: 80%;
        margin-left: auto;
        line-height: 1.6;
        font-size: 0.875rem;
    }
    
    .assistant-message {
        background-color: #F8FAFC; /* Updated bubble bg */
        color: #334155; /* Updated body text */
        border: 1px solid #E2E8F0; /* Updated bubble border */
        padding: 16px 20px; /* Updated padding */
        margin: 24px 0; /* 24px vertical spacing */
        border-radius: 10px; /* Updated border radius */
        max-width: 80%;
        line-height: 1.6;
        font-size: 0.875rem;
    }
    
    .assistant-message strong {
        color: #0F172A; /* Updated header text */
    }
    
    /* 5. Chat Input Bar - Minimal Styling */
    .chat-input-container {
        background-color: #111827; /* Lightened outer area */
        padding: 24px 32px;
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        z-index: 999;
        box-shadow: 0 4px 20px rgba(0,0,0,0.15); /* Soft shadow */
    }
    
    .chat-input-wrapper {
        display: flex;
        align-items: center;
        width: 80%;
        max-width: 800px;
        margin: 0 auto;
        background-color: #1F2937; /* Updated input shell bg */
        border-radius: 9999px;
        border: 1px solid #374151; /* Updated input border */
        padding: 12px 16px; /* Perfect spacing */
        overflow: hidden;
        box-sizing: border-box;
        height: 56px;
    }
    
    .chat-input-field {
        flex: 1;
        background-color: transparent;
        color: #F8FAFC; /* Updated text color */
        border: none;
        outline: none;
        padding: 0;
        margin: 0 14px 0 16px;
        font-size: 0.875rem;
        font-family: inherit;
        line-height: 1;
        height: 100%;
        display: flex;
        align-items: center;
        box-sizing: border-box;
    }
    
    .chat-input-field::placeholder {
        color: #94A3B8; /* Updated placeholder */
    }
    
    .chat-send-button {
        width: 40px; /* Exactly 40px */
        height: 40px; /* Exactly 40px */
        margin-left: 12px; /* Gap: 12px */
        background-color: #FFFFFF; /* Updated send button bg */
        border-radius: 9999px;
        padding: 8px;
        border: none;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all 0.15s ease;
        flex-shrink: 0;
        box-sizing: border-box;
    }
    
    .chat-send-button:hover {
        background-color: #F8FAFC;
        transform: scale(1.05);
    }
    
    .chat-send-button:active {
        transform: scale(0.95);
    }
    
    .send-icon {
        width: 16px;
        height: 16px;
        color: #0F172A; /* Updated send icon */
    }
    
    /* 6. Layout Alignment - Perfect Centering */
    .main-content {
        max-width: 1280px; /* Updated max-width */
        margin: 0 auto; /* Center content */
        padding: 32px; /* Updated padding */
        padding-bottom: 140px; /* Space for fixed input bar */
        background-color: #F8FAFC; /* Updated page background */
    }
    
    /* 7. Typography Hierarchy */
    .headline {
        font-weight: 600;
        font-size: 28px;
        color: #0F172A;
    }
    
    .subtitle {
        font-weight: 400;
        font-size: 14px;
        color: #64748B;
    }
    
    .section-title {
        letter-spacing: 0.6px; /* Updated letter spacing */
    }
    
    .body-text {
        color: #334155; /* Updated body text */
    }
    
    /* Quick Actions */
    .quick-actions {
        background-color: #FFFFFF; /* Updated card bg */
        border: 1px solid #E2E8F0; /* Updated card border */
        padding: 24px;
        border-radius: 12px; /* Updated border radius */
        margin: 24px 0;
    }
    
    .quick-actions h3 {
        margin-top: 0;
        color: #0F172A; /* Updated header text */
        font-size: 1.125rem;
        font-weight: 600;
    }
    
    .quick-actions p {
        color: #334155; /* Updated body text */
        margin-bottom: 16px;
        font-size: 0.875rem;
    }
    
    .action-buttons {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 12px;
    }
    
    .action-btn {
        background-color: #FFFFFF; /* Updated card bg */
        border: 1px solid #E2E8F0; /* Updated card border */
        border-radius: 6px;
        padding: 12px;
        text-align: left;
        cursor: pointer;
        transition: all 0.15s ease;
        font-size: 0.875rem;
        color: #334155; /* Updated body text */
    }
    
    .action-btn:hover {
        background-color: #F8FAFC;
        border-color: #0EA5E9;
    }
    
    /* Streamlit overrides */
    .css-1d391kg {
        background-color: #0F172A !important;
        border-right: none !important;
    }
    
    .css-1d391kg > div {
        padding: 0 !important;
        background-color: transparent !important;
    }
    
    /* Hide Streamlit's default chat input */
    [data-testid="stChatInput"] {
        display: none !important;
    }
    
    .stAlert {
        background-color: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        color: #0F172A !important;
        border-radius: 6px !important;
        padding: 16px !important;
        font-size: 0.875rem !important;
    }
    
    .metric-container {
        background-color: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 8px !important;
        padding: 24px !important;
        color: #0F172A !important;
        font-size: 0.875rem !important;
    }
    
    /* Remove all bright colors */
    * {
        --streamlit-primary-color: #0EA5E9 !important;
        --streamlit-secondary-color: #F8FAFC !important;
        --streamlit-background-color: #F8FAFC !important;
        --streamlit-text-color: #0F172A !important;
        --streamlit-warning-color: #EAB308 !important;
    }
    </style>
    """, unsafe_allow_html=True)

def main():
    """Main application with premium UI"""
    load_css()
    
    # Page configuration
    st.set_page_config(
        page_title="BizComply AI",
        page_icon="🏢",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize session state
    if 'conversations' not in st.session_state:
        st.session_state.conversations = [
            {
                "id": "1",
                "title": "GDPR Compliance Requirements",
                "timestamp": datetime.now() - timedelta(days=1),
                "message_count": 8,
                "messages": [
                    {
                        "id": "1",
                        "content": "What are the key GDPR compliance requirements for my SaaS business?",
                        "is_user": True,
                        "timestamp": datetime.now() - timedelta(hours=1)
                    },
                    {
                        "id": "2",
                        "content": "For GDPR compliance in your SaaS business, you need to focus on:\n\n1. Data Protection Impact Assessments\n2. Lawful Basis for Processing\n3. User Rights implementation\n4. Privacy by Design\n5. Data Processing Agreements\n6. Security Measures\n\nWould you like me to elaborate on any specific area?",
                        "is_user": False,
                        "timestamp": datetime.now() - timedelta(hours=1)
                    }
                ]
            },
            {
                "id": "2", 
                "title": "Financial Reporting Standards",
                "timestamp": datetime.now() - timedelta(days=2),
                "message_count": 5,
                "messages": []
            },
            {
                "id": "3",
                "title": "ISO 27001 Certification Process", 
                "timestamp": datetime.now() - timedelta(days=3),
                "message_count": 12,
                "messages": []
            }
        ]
    
    if 'active_conversation_id' not in st.session_state:
        st.session_state.active_conversation_id = "1"
    
    if 'is_processing' not in st.session_state:
        st.session_state.is_processing = False
    
    if 'chat_input' not in st.session_state:
        st.session_state.chat_input = ""
    
    # Get active conversation
    active_conversation = next(
        (conv for conv in st.session_state.conversations if conv["id"] == st.session_state.active_conversation_id),
        None
    )
    
    # Render premium interface
    render_premium_interface(active_conversation)

def render_premium_interface(active_conversation):
    """Render premium professional interface"""
    
    # Premium Sidebar
    with st.sidebar:
        # Sidebar Header
        st.markdown("""
        <div class="sidebar-header">
            <h1>🏢 BizComply AI</h1>
            <p>Professional Compliance Assistant</p>
        </div>
        """, unsafe_allow_html=True)
        
        # New Conversation Button
        if st.button("➕ New Conversation", key="new_conv", use_container_width=True):
            create_new_conversation()
        
        # Conversations Section
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown('<div class="sidebar-section-title section-title">Recent Conversations</div>', unsafe_allow_html=True)
        
        # Conversation List
        for conv in st.session_state.conversations:
            time_str = conv["timestamp"].strftime("%b %d")
            is_active = conv["id"] == st.session_state.active_conversation_id
            
            if st.button(
                conv['title'],
                key=f"conv_{conv['id']}",
                help=f"{time_str} • {conv['message_count']} messages",
                use_container_width=True
            ):
                st.session_state.active_conversation_id = conv["id"]
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Stats Section
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown('<div class="sidebar-section-title section-title">Quick Stats</div>', unsafe_allow_html=True)
        
        st.markdown("""
        <div class="stats-grid">
            <div class="stat-item">
                <div class="stat-value">24</div>
                <div class="stat-label">Queries</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">1.2s</div>
                <div class="stat-label">Avg Time</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Main content with premium layout
    st.markdown('<div class="main-content">', unsafe_allow_html=True)
    
    # Premium Header with Breadcrumb
    st.markdown('<div class="breadcrumb">AI Assistant › Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="main-header"><h1 class="headline">🏢 BizComply AI</h1><p class="subtitle">Professional Compliance Assistant</p></div>', unsafe_allow_html=True)
    
    # Premium Metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("""
        <div class="metric-box">
            <div class="metric-value">94%</div>
            <div class="metric-label">Compliance Score</div>
            <div class="metric-trend positive">+5% this week</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-box">
            <div class="metric-value">1.2s</div>
            <div class="metric-label">Response Time</div>
            <div class="metric-trend positive">-0.3s improvement</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-box">
            <div class="metric-value">24</div>
            <div class="metric-label">Queries Today</div>
            <div class="metric-trend positive">+12 from yesterday</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-box">
            <div class="metric-value">3</div>
            <div class="metric-label">Active Alerts</div>
            <div class="metric-trend negative">2 resolved today</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Chat messages with premium styling
    if active_conversation and active_conversation["messages"]:
        for message in active_conversation["messages"]:
            if message["is_user"]:
                st.markdown(f'<div class="user-message body-text"><strong>You:</strong> {message["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="assistant-message body-text"><strong>Assistant:</strong> {message["content"]}</div>', unsafe_allow_html=True)
    else:
        # Premium Quick Actions
        st.markdown("""
        <div class="quick-actions">
            <h3>Quick Actions</h3>
            <p class="body-text">Get started with these common compliance topics:</p>
            <div class="action-buttons">
                <div class="action-btn">📋 GDPR Requirements</div>
                <div class="action-btn">💰 Financial Compliance</div>
                <div class="action-btn">🏆 Industry Certifications</div>
                <div class="action-btn">🔍 Compliance Audit</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Alternative quick questions with Streamlit buttons
        st.markdown("### Quick Questions")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📋 GDPR Requirements", key="gdpr_btn"):
                handle_send_message("What are the key GDPR compliance requirements for my business?")
        with col2:
            if st.button("💰 Financial Compliance", key="financial_btn"):
                handle_send_message("How do I ensure financial reporting compliance?")
        
        col3, col4 = st.columns(2)
        with col3:
            if st.button("🏆 Industry Certifications", key="cert_btn"):
                handle_send_message("What certifications do I need for my industry?")
        with col4:
            if st.button("🔍 Compliance Audit", key="audit_btn"):
                handle_send_message("How to conduct a compliance audit?")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Premium Chat Input Bar
    st.markdown("""
    <div class="chat-input-container">
        <div class="chat-input-wrapper">
            <input 
                type="text" 
                placeholder="Ask about compliance, regulations, or your business requirements..."
                class="chat-input-field"
                id="chat-input-field"
            />
            <button class="chat-send-button" onclick="sendMessage()">
                <svg class="send-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"></path>
                </svg>
            </button>
        </div>
    </div>
    
    <script>
        function sendMessage() {
            const input = document.getElementById('chat-input-field');
            const message = input.value.trim();
            if (message) {
                // Store message in session state
                window.parent.postMessage({
                    type: 'streamlit:setComponentValue',
                    key: 'chat_input',
                    value: message
                }, '*');
                
                // Clear input
                input.value = '';
                
                // Trigger rerun
                window.parent.postMessage({
                    type: 'streamlit:setComponentValue',
                    key: 'chat_input_trigger',
                    value: Date.now()
                }, '*');
            }
        }
        
        // Handle Enter key
        document.getElementById('chat-input-field').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });
    </script>
    """, unsafe_allow_html=True)
    
    # Handle chat input from JavaScript
    if 'chat_input' in st.session_state and st.session_state.chat_input:
        message = st.session_state.chat_input
        st.session_state.chat_input = ""
        handle_send_message(message)

def create_new_conversation():
    """Create a new conversation"""
    new_conv = {
        "id": str(int(datetime.now().timestamp())),
        "title": "New Conversation",
        "timestamp": datetime.now(),
        "message_count": 0,
        "messages": []
    }
    st.session_state.conversations.insert(0, new_conv)
    st.session_state.active_conversation_id = new_conv["id"]
    st.rerun()

def handle_send_message(content):
    """Handle sending a message"""
    if not st.session_state.active_conversation_id:
        return
    
    # Add user message
    user_message = {
        "id": str(int(datetime.now().timestamp())),
        "content": content,
        "is_user": True,
        "timestamp": datetime.now()
    }
    
    # Update conversation
    for conv in st.session_state.conversations:
        if conv["id"] == st.session_state.active_conversation_id:
            conv["messages"].append(user_message)
            conv["message_count"] += 1
            if len(conv["messages"]) == 1:
                conv["title"] = content[:50] + ("..." if len(content) > 50 else "")
            break
    
    # Set processing state
    st.session_state.is_processing = True
    st.rerun()
    
    # Simulate AI response
    import time
    time.sleep(1)
    
    ai_response = generate_ai_response(content)
    ai_message = {
        "id": str(int(datetime.now().timestamp()) + 1),
        "content": ai_response,
        "is_user": False,
        "timestamp": datetime.now()
    }
    
    # Add AI response
    for conv in st.session_state.conversations:
        if conv["id"] == st.session_state.active_conversation_id:
            conv["messages"].append(ai_message)
            conv["message_count"] += 1
            break
    
    st.session_state.is_processing = False
    st.rerun()

def generate_ai_response(prompt):
    """Generate AI response for compliance questions"""
    prompt_lower = prompt.lower()
    
    if "gdpr" in prompt_lower:
        return """For GDPR compliance in your SaaS business, focus on:

1. **Data Protection Impact Assessments** - Conduct assessments for high-risk processing
2. **Lawful Basis for Processing** - Ensure you have valid legal basis (consent, contract, etc.)
3. **User Rights** - Implement data access, rectification, erasure, and portability
4. **Privacy by Design** - Integrate data protection into product development
5. **Data Processing Agreements** - Have proper agreements with third-party processors
6. **Security Measures** - Implement appropriate technical and organizational security

Would you like me to elaborate on any specific area?"""
    
    elif "iso" in prompt_lower or "certification" in prompt_lower:
        return """The ISO 27001 certification process involves:

1. **Gap Analysis** - Assess current security controls against requirements
2. **ISMS Implementation** - Establish Information Security Management System
3. **Risk Assessment** - Identify and evaluate information security risks
4. **Control Implementation** - Implement appropriate security controls
5. **Documentation** - Create comprehensive policies and procedures
6. **Internal Audit** - Conduct internal audits to verify compliance
7. **Certification Audit** - Undergo external audit by accredited body
8. **Continuous Improvement** - Maintain and improve the ISMS

Process typically takes 6-12 months depending on organization size."""
    
    elif "financial" in prompt_lower or "reporting" in prompt_lower:
        return """For financial reporting compliance, focus on:

1. **GAAP/IFRS Compliance** - Follow appropriate accounting standards
2. **Internal Controls** - Implement SOX controls if applicable
3. **Audit Trail** - Maintain complete documentation
4. **Regular Audits** - Conduct internal and external audits
5. **Financial Systems** - Ensure proper system controls
6. **Reporting Timelines** - Meet all regulatory filing deadlines
7. **Disclosure Requirements** - Provide accurate and complete disclosures

Your specific requirements depend on your jurisdiction and industry."""
    
    else:
        return """I'm here to help with your compliance and business queries. Based on your question, here's my guidance:

**Key Considerations:**
- Review applicable regulations for your industry
- Assess current compliance status
- Implement necessary controls and processes
- Document everything thoroughly
- Regular training and awareness programs

**Next Steps:**
1. Conduct a compliance assessment
2. Identify gaps and priorities
3. Develop implementation roadmap
4. Create documentation systems
5. Establish monitoring procedures

For more specific guidance, could you provide details about:
- Your business type and industry?
- Specific regulations you're concerned about?
- Current compliance challenges?
- Timeline requirements?

This will help me provide more targeted assistance for your situation."""

if __name__ == "__main__":
    main()

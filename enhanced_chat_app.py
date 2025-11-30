#!/usr/bin/env python3
"""
Enhanced Streamlit app for BizComply - Matching React chat interface design
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

# Enhanced CSS to match React component design
def load_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Styles */
    .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        background-color: #ffffff;
    }
    
    /* Hide Streamlit branding */
    .stDeployButton {
        display: none;
    }
    
    /* Main container */
    .main .block-container {
        padding-top: 0rem;
        padding-bottom: 0rem;
        max-width: 100%;
    }
    
    /* Chat container layout */
    .chat-container {
        display: flex;
        height: 100vh;
        background: #ffffff;
    }
    
    /* Sidebar styling */
    .chat-sidebar {
        width: 320px;
        background: #f8fafc;
        border-right: 1px solid #e2e8f0;
        display: flex;
        flex-direction: column;
        height: 100vh;
    }
    
    .sidebar-header {
        padding: 1.5rem;
        border-bottom: 1px solid #e2e8f0;
    }
    
    .conversation-list {
        flex: 1;
        overflow-y: auto;
        padding: 0.5rem;
    }
    
    .conversation-item {
        padding: 0.75rem 1rem;
        margin-bottom: 0.25rem;
        border-radius: 8px;
        cursor: pointer;
        transition: all 0.2s ease;
        border: 1px solid transparent;
    }
    
    .conversation-item:hover {
        background: #f1f5f9;
        border-color: #e2e8f0;
    }
    
    .conversation-item.active {
        background: #e0f2fe;
        border-color: #0ea5a4;
    }
    
    .conversation-title {
        font-weight: 500;
        color: #0f1720;
        margin-bottom: 0.25rem;
        font-size: 0.875rem;
    }
    
    .conversation-meta {
        font-size: 0.75rem;
        color: #6b7280;
    }
    
    /* Main chat area */
    .chat-main {
        flex: 1;
        display: flex;
        flex-direction: column;
        height: 100vh;
    }
    
    .chat-header {
        padding: 1.5rem;
        border-bottom: 1px solid #e2e8f0;
        background: #ffffff;
    }
    
    .chat-title {
        font-size: 2rem;
        font-weight: 700;
        color: #0f1720;
        margin: 0;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .chat-subtitle {
        color: #6b7280;
        margin: 0.25rem 0 0 0;
        font-size: 0.875rem;
    }
    
    /* Metrics bar */
    .metrics-bar {
        padding: 1.5rem;
        background: #f8fafc;
        border-bottom: 1px solid #e2e8f0;
    }
    
    .metrics-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
    }
    
    .metric-item {
        background: #ffffff;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #e2e8f0;
        text-align: center;
    }
    
    .metric-value {
        font-size: 1.5rem;
        font-weight: 700;
        color: #0ea5a4;
        margin-bottom: 0.25rem;
    }
    
    .metric-label {
        font-size: 0.75rem;
        color: #6b7280;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    /* Chat messages area */
    .chat-messages {
        flex: 1;
        overflow-y: auto;
        padding: 1.5rem;
        background: #ffffff;
    }
    
    .message-container {
        max-width: 4rem;
        margin: 0 auto;
        padding-bottom: 1.5rem;
    }
    
    .message {
        display: flex;
        gap: 0.75rem;
        margin-bottom: 1rem;
    }
    
    .message-avatar {
        width: 2rem;
        height: 2rem;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.875rem;
        font-weight: 600;
        flex-shrink: 0;
    }
    
    .user-avatar {
        background: #0ea5a4;
        color: white;
    }
    
    .assistant-avatar {
        background: #e0f2fe;
        color: #0ea5a4;
        border: 1px solid #0ea5a4;
    }
    
    .message-content {
        flex: 1;
    }
    
    .message-bubble {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 0.5rem;
    }
    
    .user-bubble {
        background: #0ea5a4;
        color: white;
        border-color: #0ea5a4;
    }
    
    .assistant-bubble {
        background: #f8fafc;
        color: #0f1720;
        border-color: #e2e8f0;
    }
    
    .message-time {
        font-size: 0.75rem;
        color: #6b7280;
        margin-left: 0.5rem;
    }
    
    /* Loading indicator */
    .loading-indicator {
        display: flex;
        gap: 0.25rem;
        padding: 1rem;
    }
    
    .loading-dot {
        width: 0.5rem;
        height: 0.5rem;
        background: #0ea5a4;
        border-radius: 50%;
        animation: bounce 1.4s infinite ease-in-out both;
    }
    
    .loading-dot:nth-child(1) { animation-delay: -0.32s; }
    .loading-dot:nth-child(2) { animation-delay: -0.16s; }
    
    @keyframes bounce {
        0%, 80%, 100% { transform: scale(0); }
        40% { transform: scale(1); }
    }
    
    /* Empty state */
    .empty-state {
        display: flex;
        align-items: center;
        justify-content: center;
        height: 100%;
        text-align: center;
    }
    
    .empty-icon {
        width: 4rem;
        height: 4rem;
        border-radius: 16px;
        background: #e0f2fe;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto 1rem;
        border: 1px solid #0ea5a4;
    }
    
    .empty-title {
        font-size: 1.25rem;
        font-weight: 600;
        color: #0f1720;
        margin-bottom: 0.5rem;
    }
    
    .empty-description {
        color: #6b7280;
        margin-bottom: 1.5rem;
    }
    
    .quick-questions {
        display: grid;
        gap: 0.5rem;
        text-align: left;
    }
    
    .quick-question {
        padding: 0.75rem 1rem;
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        text-align: left;
        transition: all 0.2s ease;
        color: #0f1720;
        font-size: 0.875rem;
    }
    
    .quick-question:hover {
        background: #f1f5f9;
        border-color: #cbd5e1;
    }
    
    /* Chat input */
    .chat-input-container {
        padding: 1.5rem;
        border-top: 1px solid #e2e8f0;
        background: #ffffff;
    }
    
    /* Hide default streamlit elements */
    .element-container:has([data-testid="stChatInput"]) {
        padding: 0 !important;
    }
    
    [data-testid="stChatInput"] {
        background: transparent !important;
        border: none !important;
        padding: 0 !important;
    }
    
    [data-testid="stChatInput"] > div {
        background: #f8fafc !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 12px !important;
        padding: 0.75rem 1rem !important;
    }
    
    [data-testid="stChatInput"] input {
        color: #0f1720 !important;
        font-size: 0.875rem !important;
    }
    
    [data-testid="stChatInput"] input::placeholder {
        color: #6b7280 !important;
    }
    </style>
    """, unsafe_allow_html=True)

def main():
    """Main application with enhanced chat interface"""
    load_css()
    
    # Page config
    st.set_page_config(
        page_title="BizComply AI Assistant",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="collapsed"
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
                        "content": "For GDPR compliance in your SaaS business, you need to focus on several key areas:\n\n1. **Data Protection Impact Assessments (DPIA)**: Conduct assessments for high-risk processing activities.\n\n2. **Lawful Basis for Processing**: Ensure you have a valid legal basis (consent, contract, legitimate interest, etc.).\n\n3. **User Rights**: Implement mechanisms for data access, rectification, erasure, and portability.\n\n4. **Privacy by Design**: Integrate data protection into your product development lifecycle.\n\n5. **Data Processing Agreements**: Have proper agreements with all third-party processors.\n\n6. **Security Measures**: Implement appropriate technical and organizational security measures.\n\nWould you like me to elaborate on any specific area?",
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
    
    # Get active conversation
    active_conversation = next(
        (conv for conv in st.session_state.conversations if conv["id"] == st.session_state.active_conversation_id),
        None
    )
    
    # Render chat interface
    render_chat_interface(active_conversation)

def render_chat_interface(active_conversation):
    """Render the enhanced chat interface"""
    
    # Sidebar for conversations
    with st.sidebar:
        st.markdown("""
        <div class="chat-sidebar">
            <div class="sidebar-header">
                <h3 style="margin: 0; color: #0f1720; font-weight: 600;">Conversations</h3>
            </div>
            <div class="conversation-list">
        """, unsafe_allow_html=True)
        
        # New conversation button
        if st.button("➕ New Conversation", key="new_conv", use_container_width=True):
            create_new_conversation()
        
        # Conversation list
        for conv in st.session_state.conversations:
            is_active = conv["id"] == st.session_state.active_conversation_id
            
            # Format timestamp
            time_str = format_timestamp(conv["timestamp"])
            
            # Click handler for conversation selection
            if st.button(
                f"**{conv['title']}**\n\n{time_str} • {conv['message_count']} messages",
                key=f"conv_{conv['id']}",
                use_container_width=True,
                help=f"Conversation from {time_str}"
            ):
                st.session_state.active_conversation_id = conv["id"]
                st.rerun()
        
        st.markdown("""
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Main chat area
    st.markdown("""
    <div class="chat-main">
        <div class="chat-header">
            <h2 class="chat-title">
                <span style="color: #0ea5a4;">✨</span>
                AI Compliance Assistant
            </h2>
            <p class="chat-subtitle">Get instant answers to your business compliance and regulatory questions</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Metrics bar
    render_metrics_bar()
    
    # Chat messages area
    if active_conversation and active_conversation["messages"]:
        render_chat_messages(active_conversation["messages"])
    else:
        render_empty_state()
    
    # Chat input
    render_chat_input()

def render_metrics_bar():
    """Render the metrics bar"""
    st.markdown("""
    <div class="metrics-bar">
        <div class="metrics-grid">
            <div class="metric-item">
                <div class="metric-value">87%</div>
                <div class="metric-label">Compliance Score</div>
            </div>
            <div class="metric-item">
                <div class="metric-value">8</div>
                <div class="metric-label">Active Tasks</div>
            </div>
            <div class="metric-item">
                <div class="metric-value">3</div>
                <div class="metric-label">Upcoming Deadlines</div>
            </div>
            <div class="metric-item">
                <div class="metric-value">24</div>
                <div class="metric-label">Documents Reviewed</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_chat_messages(messages):
    """Render chat messages"""
    st.markdown('<div class="chat-messages">', unsafe_allow_html=True)
    
    for message in messages:
        if message["is_user"]:
            st.markdown(f"""
            <div class="message">
                <div class="message-avatar user-avatar">U</div>
                <div class="message-content">
                    <div class="message-bubble user-bubble">{message['content']}</div>
                    <div class="message-time">{format_timestamp(message['timestamp'])}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="message">
                <div class="message-avatar assistant-avatar">✨</div>
                <div class="message-content">
                    <div class="message-bubble assistant-bubble">{message['content']}</div>
                    <div class="message-time">{format_timestamp(message['timestamp'])}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # Loading indicator
    if st.session_state.is_processing:
        st.markdown("""
        <div class="message">
            <div class="message-avatar assistant-avatar">✨</div>
            <div class="message-content">
                <div class="message-bubble assistant-bubble">
                    <div class="loading-indicator">
                        <div class="loading-dot"></div>
                        <div class="loading-dot"></div>
                        <div class="loading-dot"></div>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_empty_state():
    """Render empty state when no messages"""
    st.markdown("""
    <div class="empty-state">
        <div>
            <div class="empty-icon">
                <span style="font-size: 2rem;">✨</span>
            </div>
            <div class="empty-title">Start a New Conversation</div>
            <div class="empty-description">
                Ask me anything about compliance, regulations, or business processes. I'm here to help!
            </div>
            <div class="quick-questions">
                <button class="quick-question">"What are GDPR data retention requirements?"</button>
                <button class="quick-question">"Explain ISO 27001 certification process"</button>
                <button class="quick-question">"Help with SOC 2 compliance checklist"</button>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_chat_input():
    """Render chat input"""
    st.markdown('<div class="chat-input-container">', unsafe_allow_html=True)
    
    if prompt := st.chat_input("Ask about compliance, regulations, or your business requirements...", disabled=st.session_state.is_processing):
        handle_send_message(prompt)
    
    st.markdown('</div>', unsafe_allow_html=True)

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
    time.sleep(1.5)
    
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
    responses = {
        "gdpr": """For GDPR compliance in your SaaS business, you need to focus on several key areas:

1. **Data Protection Impact Assessments (DPIA)**: Conduct assessments for high-risk processing activities.

2. **Lawful Basis for Processing**: Ensure you have a valid legal basis (consent, contract, legitimate interest, etc.).

3. **User Rights**: Implement mechanisms for data access, rectification, erasure, and portability.

4. **Privacy by Design**: Integrate data protection into your product development lifecycle.

5. **Data Processing Agreements**: Have proper agreements with all third-party processors.

6. **Security Measures**: Implement appropriate technical and organizational security measures.

Would you like me to elaborate on any specific area?""",
        
        "iso": """The ISO 27001 certification process involves several key steps:

1. **Gap Analysis**: Assess your current security controls against ISO 27001 requirements.

2. **Information Security Management System (ISMS)**: Establish and implement an ISMS based on the ISO 27001 standard.

3. **Risk Assessment**: Identify and evaluate information security risks.

4. **Control Implementation**: Implement appropriate security controls based on risk assessment.

5. **Documentation**: Create comprehensive documentation of policies, procedures, and controls.

6. **Internal Audit**: Conduct internal audits to verify compliance.

7. **Certification Audit**: Undergo external audit by accredited certification body.

8. **Continuous Improvement**: Maintain and improve the ISMS through regular reviews.

The process typically takes 6-12 months depending on your organization's size and complexity.""",
        
        "soc": """SOC 2 compliance requires addressing the following key areas:

**Trust Service Criteria:**
1. **Security**: System protection against unauthorized access
2. **Availability**: System is available for operation and use
3. **Processing Integrity**: System processing is complete, accurate, timely, and authorized
4. **Confidentiality**: Information is protected from unauthorized disclosure
5. **Privacy**: Personal information is collected, used, and disclosed appropriately

**Implementation Steps:**
1. **Scope Definition**: Determine systems and processes to include
2. **Risk Assessment**: Identify and evaluate relevant risks
3. **Control Implementation**: Design and implement controls
4. **Documentation**: Create policies, procedures, and evidence
5. **Testing**: Test control effectiveness
6. **Audit**: Undergo SOC 2 audit by licensed CPA firm
7. **Report**: Receive SOC 2 Type I or Type II report

**Common Controls:**
- Access management
- Incident response
- Change management
- Data backup and recovery
- Vendor management
- Employee training

Would you like specific guidance on any of these areas?""",
        
        "default": """I'm here to help with your compliance and business queries. Based on your question, here's my guidance:

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
    }
    
    prompt_lower = prompt.lower()
    for key, response in responses.items():
        if key in prompt_lower:
            return response
    
    return responses["default"]

def format_timestamp(timestamp):
    """Format timestamp for display"""
    now = datetime.now()
    diff = now - timestamp
    
    if diff.days > 0:
        return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"{hours} hour{'s' if hours > 1 else ''} ago"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
    else:
        return "Just now"

if __name__ == "__main__":
    main()

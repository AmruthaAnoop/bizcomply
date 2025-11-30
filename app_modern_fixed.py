import streamlit as st
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List

def main():
    """Main application with modern ChatGPT-style UI"""
    st.set_page_config(
        page_title="BizComply AI",
        page_icon="🏢",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Clean Modern CSS - Working Version
    st.markdown("""
    <style>
    body {
        background-color: white !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    .stApp {
        background-color: white !important;
    }
    [data-testid="stSidebar"] {
        background-color: #F9FAFB !important;
        border-right: 1px solid #E5E7EB !important;
        padding: 20px 16px !important;
    }
    .stChatMessage {
        padding: 12px 16px !important;
        border-radius: 8px !important;
        margin-bottom: 12px !important;
        max-width: 80% !important;
    }
    .stChatMessage[data-testid="stChatMessage"] {
        background-color: #F3F4F6 !important;
        margin-left: auto !important;
        margin-right: 0 !important;
    }
    .stChatMessage[data-testid="stChatMessage"][data-message-role="assistant"] {
        background-color: white !important;
        border: 1px solid #E5E7EB !important;
        margin-left: 0 !important;
        margin-right: auto !important;
    }
    .stChatInput {
        position: fixed !important;
        bottom: 0 !important;
        left: 0 !important;
        right: 0 !important;
        background: white !important;
        padding: 16px !important;
        border-top: 1px solid #E5E7EB !important;
        z-index: 100 !important;
    }
    .stTextInput > div > div > input,
    .stTextInput > div > div > textarea {
        border-radius: 20px !important;
        padding: 10px 16px !important;
        border: 1px solid #E5E7EB !important;
        background-color: #F3F4F6 !important;
        font-size: 14px !important;
        line-height: 1.5 !important;
    }
    .stButton > button {
        border-radius: 50% !important;
        width: 36px !important;
        height: 36px !important;
        min-width: 36px !important;
        padding: 0 !important;
        background-color: #3B82F6 !important;
        border: none !important;
    }
    .stButton > button:hover {
        background-color: #2563EB !important;
    }
    .stApp > header, .stApp > div:first-child {
        display: none !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Initialize session state
    if 'conversations' not in st.session_state:
        st.session_state.conversations = [
            {
                "id": "1",
                "title": "GDPR Compliance Requirements",
                "timestamp": datetime.now() - timedelta(days=1),
                "message_count": 2,
                "messages": [
                    {
                        "id": "1",
                        "content": "What are the key GDPR compliance requirements for my SaaS business?",
                        "is_user": True,
                        "timestamp": datetime.now() - timedelta(days=1, hours=2)
                    },
                    {
                        "id": "2",
                        "content": "<p>For GDPR compliance in your SaaS business, focus on:</p><p><strong>Data Protection Officer (DPO)</strong> – required if you process large-scale data or special categories of data</p><p><strong>Privacy Policy</strong> – must be transparent, concise, and easily accessible</p><p><strong>Lawful Basis</strong> – obtain explicit consent or have another lawful basis for processing</p><p><strong>Data Subject Rights</strong> – implement procedures for requests to access, rectify, erase data</p><p><strong>Breach Notification</strong> – report to authorities within 72 hours of discovery</p><p><strong>Privacy by Design</strong> – build data protection into your systems from the start</p>",
                        "is_user": False,
                        "timestamp": datetime.now() - timedelta(days=1, hours=1, minutes=50)
                    }
                ],
                "backend_id": None
            }
        ]
    
    if 'active_conversation_id' not in st.session_state:
        st.session_state.active_conversation_id = "1"
    
    # Get active conversation
    active_conversation = next(
        (conv for conv in st.session_state.conversations if conv["id"] == st.session_state.active_conversation_id),
        None
    )
    
    # Sidebar
    with st.sidebar:
        st.markdown("### 🏢 BizComply AI")
        st.write("Business Compliance Assistant")
        
        st.markdown("---")
        st.markdown("#### Conversations")
        
        # Sample conversations
        conversations = [
            "License Requirements Query",
            "Tax Compliance Questions", 
            "Business Registration Guide"
        ]
        
        for conv in conversations:
            if st.button(conv, key=f"conv_{conv}", use_container_width=True):
                st.session_state.current_question = conv
                st.rerun()
        
        st.markdown("---")
        st.markdown("#### Tools")
        
        tools = [
            "🔍 License Finder",
            "🧮 Tax Calculator",
            "📝 Registration Helper"
        ]
        
        for tool in tools:
            if st.button(tool, key=f"tool_{tool}", use_container_width=True):
                st.session_state.current_question = f"Help me with {tool.lower()}"
                st.rerun()
    
    # Main content
    if active_conversation and active_conversation["messages"]:
        # Display messages
        for message in active_conversation["messages"]:
            if message["is_user"]:
                st.markdown(f'<div style="background-color: #F3F4F6; padding: 12px 16px; border-radius: 18px; margin: 10px auto; max-width: 440px; text-align: center; color: #1F2937;">{message["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div style="background-color: white; border: 1px solid #E5E7EB; padding: 16px; border-radius: 8px; margin: 10px auto; max-width: 680px; color: #1F2937;">{message["content"]}</div>', unsafe_allow_html=True)
        
        # Suggestion buttons
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("💼 Licenses", use_container_width=True):
                st.session_state.current_question = "Tell me about business licenses"
        with col2:
            if st.button("📑 Filing Checklist", use_container_width=True):
                st.session_state.current_question = "What documents do I need to file?"
        with col3:
            if st.button("🧾 Taxes", use_container_width=True):
                st.session_state.current_question = "Help me with tax compliance"
    else:
        # Welcome message
        st.markdown("""
        <div style="background-color: #F8F9FA; padding: 20px; border-radius: 18px; margin: 40px auto; max-width: 600px; text-align: center; border: 1px solid #E9ECEF;">
            <h1 style="color: #1F2937; margin-bottom: 10px;">🏢 BizComply AI</h1>
            <p style="color: #6B7280; margin: 0;">Simplifying Business Compliance for Small Business Owners</p>
            <p style="color: #6B7280; margin: 10px 0 0 0;">Ask anything about licenses, taxes, registrations, or compliance tasks.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Chat input
    prompt = st.chat_input("Ask about licenses, taxes, registrations, or compliance tasks...")
    if prompt:
        # Add user message
        if active_conversation:
            user_message = {
                "id": str(int(datetime.now().timestamp())),
                "content": prompt,
                "is_user": True,
                "timestamp": datetime.now()
            }
            active_conversation["messages"].append(user_message)
            active_conversation["message_count"] += 1
            
            # Add AI response
            ai_message = {
                "id": str(int(datetime.now().timestamp())),
                "content": f"<p>I understand you're asking about: <strong>{prompt}</strong></p><p>This is a demo response. The clean modern UI is working perfectly!</p><p>Your BizComply AI assistant is ready to help with business compliance questions.</p>",
                "is_user": False,
                "timestamp": datetime.now()
            }
            active_conversation["messages"].append(ai_message)
            active_conversation["message_count"] += 1
            
            st.rerun()

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Modern Enterprise Sidebar - Exact Color Palette
"""

import os
import sys
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional
import json
import requests  # HTTP client for backend API

# New imports for business profile management
from models.compliance_engine import ComplianceEngine
from config.config import BusinessType, Jurisdiction
from models.llm import LLMProvider
from services.regulatory_monitor import RegulatoryMonitor

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Modern Enterprise Sidebar CSS
def load_css():
    st.markdown("""
    <style>
    /* Modern Enterprise Sidebar - Exact Color Palette */
    
    /* CSS Variables for Enterprise Theme */
    :root {
        --sidebar-bg: #0F172A;
        --sidebar-bg-hover: #1E293B;
        --sidebar-bg-active: #0EA5E9;
        
        --sidebar-text: #F8FAFC;
        --sidebar-text-secondary: #94A3B8;
        --sidebar-text-muted: #64748B;
        
        --sidebar-border: #1B2537;
        
        --sidebar-convo-inactive: #1E293B;
        --sidebar-convo-hover: #334155;
        --sidebar-convo-active-bg: #0EA5E9;
        --sidebar-convo-active-text: #FFFFFF;
        
        --sidebar-button-bg: #1E293B;
        --sidebar-button-bg-hover: #2C3446;
        --sidebar-button-border: #334155;
        --sidebar-button-text: #F8FAFC;
        
        --accent: #0EA5E9;
    }
    
    /* 1. App Background */
    .stApp {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        background-color: #F8FAFC;
        color: #0F172A;
    }
    
    /* 2. Modern Enterprise Sidebar */
    .stSidebar {
        background-color: var(--sidebar-bg) !important;
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
        color: var(--sidebar-text);
        padding: 24px;
        margin: -16px -16px 24px -16px;
        border-bottom: 1px solid var(--sidebar-border);
    }
    
    .sidebar-header h1 {
        margin: 0;
        font-size: 1.5rem;
        font-weight: 600;
        color: var(--sidebar-text);
    }
    
    .sidebar-header p {
        margin: 4px 0 0 0;
        font-size: 0.875rem;
        color: var(--sidebar-text-secondary);
    }
    
    .sidebar-section {
        margin-bottom: 24px;
        padding: 0 16px;
    }
    
    .sidebar-section-title {
        font-size: 0.75rem;
        font-weight: 500;
        color: var(--sidebar-text-secondary);
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 12px;
        padding: 0 4px;
    }
    
    /* New Conversation Button - Enterprise Style */
    .new-conversation-btn {
        background-color: var(--sidebar-button-bg);
        color: var(--sidebar-button-text);
        border: 1px solid var(--sidebar-button-border);
        border-radius: 6px;
        padding: 12px;
        margin-bottom: 20px;
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
        background-color: var(--sidebar-button-bg-hover);
        border-color: #3B4457;
    }
    
    .new-conversation-btn .icon {
        color: var(--accent);
    }
    
    /* Recent Conversations - Enterprise Style */
    .conversation-item {
        border-radius: 6px;
        padding: 12px;
        margin-bottom: 8px;
        cursor: pointer;
        transition: all 0.15s ease;
        border: none;
    }
    
    .conversation-item.inactive {
        background-color: var(--sidebar-convo-inactive);
        color: var(--sidebar-text);
    }
    
    .conversation-item.inactive:hover {
        background-color: var(--sidebar-convo-hover);
    }
    
    .conversation-item.active {
        background-color: var(--sidebar-convo-active-bg);
        color: var(--sidebar-convo-active-text);
    }
    
    .conversation-item.active:hover {
        background-color: var(--accent);
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
    
    /* Sidebar Stats Section - Enterprise Style */
    .stats-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 8px;
        border-top: 1px solid rgba(255,255,255,0.06);
        padding-top: 16px;
        margin-top: 16px;
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
        color: var(--sidebar-text-secondary);
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    /* 3. Top Header */
    .main-header {
        background-color: #FFFFFF;
        padding: 24px;
        margin-bottom: 24px;
        border-bottom: 1px solid #E2E8F0;
    }
    
    .main-header h1 {
        margin: 0;
        font-size: 2rem;
        font-weight: 600;
        color: #0F172A;
    }
    
    .main-header p {
        margin: 4px 0 0 0;
        color: #475569;
        font-size: 0.875rem;
    }
    
    /* 5. KPI Cards */
    .metric-box {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 20px;
        text-align: center;
        transition: all 0.15s ease;
    }
    
    .metric-box:hover {
        border-color: var(--accent);
        box-shadow: 0 1px 3px rgba(14, 165, 233, 0.1);
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 600;
        color: #0F172A;
        margin-bottom: 4px;
    }
    
    .metric-label {
        font-size: 0.75rem;
        color: #64748B;
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
        color: #16A34A;
    }
    
    .metric-trend.negative {
        color: #DC2626;
    }
    
    /* 6. User Message Bubble */
    .user-message {
        background-color: #F1F5F9;
        color: #0F172A;
        border: 1px solid #E2E8F0;
        padding: 16px;
        margin: 12px 0;
        border-radius: 8px;
        max-width: 80%;
        margin-left: auto;
        line-height: 1.6;
        font-size: 0.875rem;
    }
    
    /* 7. Assistant Message Bubble */
    .assistant-message {
        background-color: #FFFFFF;
        color: #0F172A;
        border: 1px solid #E2E8F0;
        padding: 16px;
        margin: 12px 0;
        border-radius: 8px;
        max-width: 80%;
        line-height: 1.6;
        font-size: 0.875rem;
    }
    
    .assistant-message strong {
        color: #475569;
    }
    
    /* 8. PERFECT CENTERED CHAT INPUT BAR */
    .chat-input-container {
        background-color: #111418;
        padding: 24px 32px; /* Outer container: py-6 px-8 */
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        z-index: 999;
    }
    
    .chat-input-wrapper {
        display: flex; /* Flex container */
        align-items: center; /* Vertically center children */
        width: 80%; /* Make the gray box narrower */
        max-width: 800px; /* Smaller max-width */
        margin: 0 auto; /* Center the gray box in black container */
        background-color: #2A2D33;
        border-radius: 9999px; /* rounded-full */
        border: 1px solid #3A3D45;
        padding: 12px 16px; /* Symmetric wrapper padding */
        overflow: hidden; /* Button visually sits inside the pill */
        box-sizing: border-box;
        height: 56px; /* Fixed height for perfect centering */
    }
    
    .chat-input-field {
        flex: 1; /* Expand properly */
        background-color: transparent;
        color: #E5E7EB; /* text-gray-200 */
        border: none;
        outline: none;
        padding: 0; /* Remove padding to let flex handle centering */
        margin: 0 14px 0 16px; /* Margin instead of padding: Left: 16px (more right), Right: 14px */
        font-size: 0.875rem;
        font-family: inherit;
        line-height: 1; /* Prevent line-height from affecting centering */
        height: 100%; /* Take full height of wrapper */
        display: flex; /* Flex to center text */
        align-items: center; /* Vertically center text */
        box-sizing: border-box;
    }
    
    .chat-input-field::placeholder {
        color: #9CA3AF; /* placeholder-gray-400 */
    }
    
    .chat-send-button {
        width: 40px; /* Fixed size */
        height: 40px; /* Fixed size */
        margin-left: 12px; /* Fixed margin-left */
        background-color: #FFFFFF;
        border-radius: 9999px; /* rounded-full */
        padding: 8px; /* Inner padding */
        border: none;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05); /* shadow-sm */
        transition: all 0.15s ease;
        flex-shrink: 0; /* Don't shrink */
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
        width: 16px; /* w-4 */
        height: 16px; /* h-4 */
        color: #0F172A;
    }
    
    /* Add bottom padding to main content to avoid overlap with fixed input */
    .main-content {
        padding-bottom: 120px; /* Space for fixed input bar */
    }
    
    /* Quick Actions */
    .quick-actions {
        background-color: #FFFFFF;
        padding: 24px;
        border-radius: 8px;
        border: 1px solid #E2E8F0;
        margin: 24px 0;
    }
    
    .quick-actions h3 {
        margin-top: 0;
        color: #0F172A;
        font-size: 1.125rem;
        font-weight: 600;
    }
    
    .quick-actions p {
        color: #475569;
        margin-bottom: 16px;
        font-size: 0.875rem;
    .action-buttons {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 12px;
    }
```

to 

```python
    }
    
    .action-buttons {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 16px;
    }
```

Here is the full code after making the change:

```python
    
    .action-btn {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 6px;
        padding: 12px;
        text-align: left;
        cursor: pointer;
        transition: all 0.15s ease;
        font-size: 0.875rem;
        color: #0F172A;
    }
    
    .action-btn:hover {
        background-color: #F1F5F9;
        border-color: var(--accent);
    }
    
    /* Sidebar-specific styles */
    .css-1d391kg {
        background-color: var(--sidebar-bg) !important;
        border-right: none !important;
        width: 320px !important;
        min-width: 320px !important;
        max-width: 320px !important;
    }
    
    .css-1d391kg > div {
        padding: 0 !important;
        background-color: transparent !important;
    }
    
    /* COMPLETE SIDEBAR RESET - Remove all styling first EXCEPT header */
    .css-1d391kg *:not(.sidebar-header):not(.sidebar-header *):not(h1):not(p) {
        background-color: transparent !important;
        border: none !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    
    /* MAXIMUM SPECIFICITY - Override everything */
    .css-1d391kg .sidebar-header h1,
    .css-1d391kg .sidebar-header p,
    .css-1d391kg div[data-testid="stVerticalBlock"] > div > div > div h1,
    .css-1d391kg div[data-testid="stVerticalBlock"] > div > div > div p,
    .css-1d391kg > div > div > div > div > div > div h1,
    .css-1d391kg > div > div > div > div > div > div p,
    div[data-testid="stSidebar"] .sidebar-header h1,
    div[data-testid="stSidebar"] .sidebar-header p,
    div[data-testid="stSidebar"] h1,
    div[data-testid="stSidebar"] p {
        color: #FFFFFF !important;
        margin: 0 !important;
        opacity: 1 !important;
        visibility: visible !important;
        display: block !important;
        font-size: inherit !important;
        font-weight: inherit !important;
        background: transparent !important;
        border: none !important;
        padding: 0 !important;
        text-shadow: none !important;
        filter: none !important;
        -webkit-text-fill-color: #FFFFFF !important;
    }
    
    /* Make sure the header container itself is visible */
    .css-1d391kg .sidebar-header,
    .css-1d391kg div[data-testid="stVerticalBlock"] > div > div > div:has(h1):has(p),
    .css-1d391kg > div > div > div > div > div > div:has(h1):has(p),
    div[data-testid="stSidebar"] .sidebar-header {
        display: block !important;
        visibility: visible !important;
        opacity: 1 !important;
        background: transparent !important;
        padding: 16px !important;
        margin: 0 !important;
        border: none !important;
    }
    
    /* Also fix main content header */
    .main-header h1,
    .main-header p {
        color: #0F172A !important;
        opacity: 1 !important;
        visibility: visible !important;
    }
    
    /* Business Profile Section */
    .css-1d391kg div:has(.stForm) {
        background-color: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 8px !important;
        padding: 16px !important;
        margin-bottom: 16px !important;
    }
    
    /* New Conversation Button */
    .css-1d391kg div:has(button[kind="primary"]) {
        background-color: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 8px !important;
        padding: 16px !important;
        margin-bottom: 16px !important;
    }
    
    /* Conversation List Section */
    .css-1d391kg div:has(.sidebar-section-title) {
        background-color: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 8px !important;
        padding: 16px !important;
        margin-bottom: 16px !important;
    }
    
    .css-1d391kg .sidebar-section-title {
        font-size: 0.875rem !important;
        font-weight: 600 !important;
        color: #64748B !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
        margin-bottom: 12px !important;
        padding-bottom: 8px !important;
        border-bottom: 1px solid #E2E8F0 !important;
    }
    
    /* Conversation Buttons */
    .css-1d391kg button[kind="secondary"] {
        background-color: #F8FAFC !important;
        color: #0F172A !important;
        border: 1px solid #E2E8F0 !important;
        text-align: left !important;
        justify-content: flex-start !important;
        padding: 10px 12px !important;
        margin-bottom: 4px !important;
        font-size: 0.875rem !important;
        border-radius: 6px !important;
        width: 100% !important;
        box-sizing: border-box !important;
    }
    
    /* Stats Section */
    .css-1d391kg div:has(.stats-grid) {
        background-color: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 8px !important;
        padding: 16px !important;
        margin-bottom: 16px !important;
    }
    
    /* Hide any div that doesn't have visible content */
    .css-1d391kg div:not(:has(*)):not(.sidebar-header) {
        display: none !important;
    }
    
    .css-1d391kg div:has(> div:empty):not(.sidebar-header) {
        display: none !important;
    }
    
    .sidebar-section-title {
        font-size: 0.875rem;
        font-weight: 600;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 12px;
        padding-bottom: 8px;
        border-bottom: 1px solid #E2E8F0;
    }
    
    /* Business Profile Section */
    .sidebar-section .stForm {
        margin-bottom: 0 !important;
    }
    
    .sidebar-section .stTextInput > div > div > input,
    .sidebar-section .stSelectbox > div > div > select {
        background-color: #F8FAFC !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 6px !important;
        padding: 8px 12px !important;
        font-size: 0.875rem !important;
        width: 100% !important;
        box-sizing: border-box !important;
    }
    
    .sidebar-section .stButton > button {
        width: 100% !important;
        background-color: var(--accent) !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 6px !important;
        padding: 8px 16px !important;
        font-size: 0.875rem !important;
        font-weight: 500 !important;
        margin-top: 8px !important;
        box-sizing: border-box !important;
    }
    
    .sidebar-section .stButton > button:hover {
        background-color: #0F172A !important;
    }
    
    /* Conversation buttons */
    .sidebar-section .stButton > button[kind="secondary"] {
        background-color: #F1F5F9 !important;
        color: #0F172A !important;
        border: 1px solid #E2E8F0 !important;
        text-align: left !important;
        justify-content: flex-start !important;
        padding: 10px 12px !important;
        margin-bottom: 4px !important;
        font-size: 0.875rem !important;
    }
    
    .sidebar-section .stButton > button[kind="secondary"]:hover {
        background-color: #F1F5F9 !important;
        border-color: var(--accent) !important;
    }
    
    /* Stats Grid */
    .stats-grid {
        display: grid !important;
        grid-template-columns: 1fr 1fr !important;
        gap: 8px !important;
        width: 100% !important;
    }
    
    .stat-item {
        background-color: #F8FAFC !important;
        padding: 12px !important;
        border-radius: 6px !important;
        text-align: center !important;
        border: 1px solid #E2E8F0 !important;
    }
    
    .stat-value {
        font-size: 1.25rem !important;
        font-weight: 600 !important;
        color: #0F172A !important;
        margin-bottom: 2px !important;
    }
    
    .stat-label {
        font-size: 0.75rem !important;
        color: #64748B !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
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
        padding: 20px !important;
        color: #0F172A !important;
        font-size: 0.875rem !important;
    }
    
    /* Remove all bright colors */
    * {
        --streamlit-primary-color: var(--accent) !important;
        --streamlit-secondary-color: #F1F5F9 !important;
        --streamlit-background-color: #F8FAFC !important;
        --streamlit-text-color: #0F172A !important;
        --streamlit-warning-color: #EAB308 !important;
    }
    
    /* Fix Quick Questions section visibility */
    .quick-actions, 
    div[data-testid="stVerticalBlock"] > div:has(h3) {
        background-color: #FFFFFF !important;
        color: #0F172A !important;
    }
    
    .quick-actions h3,
    .quick-actions p,
    div[data-testid="stVerticalBlock"] > div h3,
    div[data-testid="stVerticalBlock"] > div p {
        color: #0F172A !important;
    }
    
    /* Ensure Streamlit buttons are visible */
    button[kind="primary"] {
        background-color: var(--accent) !important;
        color: #FFFFFF !important;
    }
    
    button[kind="secondary"] {
        background-color: #F1F5F9 !important;
        color: #0F172A !important;
        border: 1px solid #E2E8F0 !important;
    }
    </style>
    """, unsafe_allow_html=True)

def render_business_profile_section():
    """Render form or display for the business profile in the sidebar."""
    # Ensure compliance engine exists in session
    if 'compliance_engine' not in st.session_state:
        st.session_state.compliance_engine = ComplianceEngine()
    engine: ComplianceEngine = st.session_state.compliance_engine

    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-section-title">Business Profile</div>', unsafe_allow_html=True)

    if 'business_id' not in st.session_state:
        with st.form("business_profile_form", clear_on_submit=False):
            name = st.text_input("Business name")
            business_type = st.selectbox(
                "Business type",
                [bt.value for bt in BusinessType],
                index=0
            )
            jurisdiction = st.selectbox(
                "Jurisdiction",
                [j.value for j in Jurisdiction],
                index=0
            )
            registration_number = st.text_input("Registration number")
            submitted = st.form_submit_button("Save")
            if submitted and name and registration_number:
                profile = engine.create_business_profile(
                    name=name,
                    business_type=business_type,
                    jurisdiction=jurisdiction,
                    registration_number=registration_number,
                    address={},
                    contact={}
                )
                st.session_state.business_id = profile.id
                st.success("Profile saved!")
                st.rerun()
    else:
        profile = engine.get_business_profile(st.session_state.business_id)
        if profile:
            st.markdown(f"**{profile.name}**")
            st.markdown(f"{profile.business_type.value.title()} • {profile.jurisdiction.value.upper()}")
        if st.button("Edit business profile"):
            del st.session_state['business_id']
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)


def render_regulatory_updates_section():
    """Display latest regulatory updates relevant to the saved business profile."""
    if 'business_id' not in st.session_state:
        return
    if 'reg_monitor' not in st.session_state:
        st.session_state.reg_monitor = RegulatoryMonitor()
    monitor: RegulatoryMonitor = st.session_state.reg_monitor
    updates = monitor.get_updates_for_business(
        business_id=st.session_state.business_id,
        limit=5,
        min_relevance=0.3,
        include_read=False,
    )
    if not updates:
        st.info("No recent relevant regulatory updates.")
        return
    st.markdown("### Latest Regulatory Updates")
    for upd in updates:
        with st.expander(f"{upd['title']} ({upd['severity'].title()})"):
            st.markdown(f"**Source:** {upd['source']}")
            st.markdown(upd.get('summary', '')[:500] + ("..." if len(upd.get('summary',''))>500 else ""))
            st.markdown(f"**Relevance:** {upd['impact_score']*100:.0f}%")
            if upd.get('deadline'):
                st.markdown(f"**Deadline:** {upd['deadline']}")
            st.markdown(f"[Read more]({upd['link']})")
    st.markdown("---")


def main():
    """Main application with modern enterprise sidebar"""
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
                        "timestamp": datetime.now() - timedelta(days=1, hours=2)
                    },
                    {
                        "id": "2",
                        "content": "For GDPR compliance in your SaaS business, focus on:\n\n1. **Data Protection Officer (DPO)**: Required if you process large-scale data or special categories of data\n\n2. **Privacy Policy**: Must be transparent, concise, and easily accessible\n\n3. **Lawful Basis**: Obtain explicit consent or have another lawful basis for processing\n\n4. **Data Subject Rights**: Implement procedures for requests to access, rectify, erase data\n\n5. **Breach Notification**: Report to authorities within 72 hours of discovery\n\n6. **Privacy by Design**: Build data protection into your systems from the start\n\n7. **International Transfers**: Use GDPR-compliant mechanisms like Standard Contractual Clauses\n\n8. **Documentation**: Maintain records of processing activities",
                        "is_user": False,
                        "timestamp": datetime.now() - timedelta(days=1, hours=1, minutes=50)
                    }
                ],
                "backend_id": None
            },
            {
                "id": "2",
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
    
    if 'pending_request' not in st.session_state:
        st.session_state.pending_request = None
    
    if 'business_id' not in st.session_state:
        st.session_state.business_id = None
    
    # Process any pending requests
    process_pending_request()
    
    # Get active conversation
    active_conversation = next(
        (conv for conv in st.session_state.conversations if conv["id"] == st.session_state.active_conversation_id),
        None
    )
    
    # Render interface with modern enterprise sidebar
    render_enterprise_sidebar_interface(active_conversation)

def render_enterprise_sidebar_interface(active_conversation):
    """Render interface with modern enterprise sidebar"""
    
    # Modern Enterprise Sidebar
    with st.sidebar:
        # Sidebar Header
        st.markdown("""
        <div class="sidebar-header" style="background: transparent; padding: 16px; margin: 0;">
            <h1 style="color: #FFFFFF !important; margin: 0; padding: 0; opacity: 1; visibility: visible; display: block; text-shadow: none; filter: none; -webkit-text-fill-color: #FFFFFF;">🏢 BizComply AI</h1>
            <p style="color: #FFFFFF !important; margin: 0; padding: 0; opacity: 1; visibility: visible; display: block; text-shadow: none; filter: none; -webkit-text-fill-color: #FFFFFF;">Professional Compliance Assistant</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Business Profile Section
        render_business_profile_section()
        
        # New Conversation Button
        if st.button("➕ New Conversation", key="new_conv", use_container_width=True):
            create_new_conversation()
        
        # Conversations Section
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown('<div class="sidebar-section-title">Recent Conversations</div>', unsafe_allow_html=True)
        
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
        st.markdown('<div class="sidebar-section-title">Quick Stats</div>', unsafe_allow_html=True)
        
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
    
    # Main content with bottom padding
    st.markdown('<div class="main-content">', unsafe_allow_html=True)
    
    # Main content
    st.markdown('<div class="main-header"><h1>🏢 BizComply AI</h1><p>Professional Compliance Assistant</p></div>', unsafe_allow_html=True)
    
    # Professional metrics
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
    
    # Regulatory updates section
    render_regulatory_updates_section()
    
    # Chat messages - ChatGPT Style
    if active_conversation and active_conversation["messages"]:
        for message in active_conversation["messages"]:
            if message["is_user"]:
                st.markdown(f'<div class="user-message">{message["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="assistant-message">{message["content"]}</div>', unsafe_allow_html=True)
    else:
        # Quick Actions Section
        st.markdown("""
        <div class="quick-actions">
            <h3>Quick Actions</h3>
            <p>Get started with these common compliance topics:</p>
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
    
    # --- Chat Input ---
    # Always show chat input when on the chat page
    prompt = st.chat_input("Ask about compliance, regulations, or your business requirements...")
    if prompt:
        # If no active conversation, create one first
        if not active_conversation:
            create_new_conversation()
            active_conversation = next((c for c in st.session_state.conversations if c["id"] == st.session_state.active_conversation_id), None)
        
        if active_conversation:
            handle_send_message(prompt)
        else:
            st.error("Unable to create conversation. Please try again.")

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
    """Handle sending a message with database persistence"""
    if not st.session_state.active_conversation_id:
        return
    
    # Get the current conversation
    conv = None
    for c in st.session_state.conversations:
        if c["id"] == st.session_state.active_conversation_id:
            conv = c
            break
    
    if not conv:
        return
    
    # Store the request in session state for processing after rerun
    st.session_state.pending_request = {
        "conversation_id": conv.get("backend_id"),
        "query": content,
        "mode": "concise",
        "business_id": st.session_state.get("business_id"),
        "conv": conv
    }
    
    # Add user message immediately to show in UI
    user_message = {
        "id": str(int(datetime.now().timestamp())),
        "content": content,
        "is_user": True,
        "timestamp": datetime.now()
    }
    conv["messages"].append(user_message)
    conv["message_count"] += 1
    if len(conv["messages"]) == 1:
        conv["title"] = content[:50] + ("..." if len(content) > 50 else "")
    
    # Set processing state and rerun
    st.session_state.is_processing = True
    st.rerun()

def process_pending_request():
    """Process pending request after rerun"""
    if st.session_state.get("pending_request"):
        pending = st.session_state.pending_request
        backend_url = "http://localhost:8000/api/v1/chatbot/chat"
        
        try:
            response = requests.post(backend_url, json={
                "conversation_id": pending["conversation_id"],
                "query": pending["query"],
                "mode": pending["mode"],
                "business_id": pending["business_id"]
            }, timeout=60)
            
            if response.status_code == 200:
                data = response.json()
                ai_response = data.get("answer", "(no answer)")
                # Save backend conversation id for future turns
                pending["conv"]["backend_id"] = data.get("conversation_id")
                
                # Add AI response to session state
                ai_message = {
                    "id": str(int(datetime.now().timestamp()) + 1),
                    "content": ai_response,
                    "is_user": False,
                    "timestamp": datetime.now()
                }
                pending["conv"]["messages"].append(ai_message)
                pending["conv"]["message_count"] += 1
            else:
                error_message = f"(Backend error {response.status_code})"
                ai_message = {
                    "id": str(int(datetime.now().timestamp()) + 1),
                    "content": error_message,
                    "is_user": False,
                    "timestamp": datetime.now()
                }
                pending["conv"]["messages"].append(ai_message)
                pending["conv"]["message_count"] += 1
        except Exception as e:
            error_message = f"(Backend unreachable: {e})\n" + generate_ai_response(pending["query"])
            ai_message = {
                "id": str(int(datetime.now().timestamp()) + 1),
                "content": error_message,
                "is_user": False,
                "timestamp": datetime.now()
            }
            pending["conv"]["messages"].append(ai_message)
            pending["conv"]["message_count"] += 1
        
        # Clear pending request and reset processing state
        st.session_state.pending_request = None
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

def generate_ai_response(prompt: str) -> str:
    """Generate AI response using configured LLMProvider and business context.
    Falls back to keyword guidance if an LLM is unavailable or errors occur."""
    # Attempt to use the configured LLM
    try:
        llm = LLMProvider.get_llm()

        # Build business profile context
        profile_text = ""
        if 'business_id' in st.session_state:
            engine: ComplianceEngine = st.session_state.compliance_engine
            profile = engine.get_business_profile(st.session_state.business_id)
            if profile:
                profile_text = (
                    f"Business Name: {profile.name}\n"
                    f"Business Type: {profile.business_type.value}\n"
                    f"Jurisdiction: {profile.jurisdiction.value}\n"
                    f"Registration Number: {profile.registration_number}\n"
                )

        # Gather last 10 messages for context
        history_text = ""
        for conv in st.session_state.conversations:
            if conv['id'] == st.session_state.active_conversation_id:
                for msg in conv['messages'][-10:]:
                    speaker = "User" if msg['is_user'] else "Assistant"
                    history_text += f"{speaker}: {msg['content']}\n"
                break

        system_prompt = (
            "You are BizComply AI, an expert compliance assistant. "
            "Provide precise, actionable, and personalised answers. "
            "If information is missing, ask a concise follow-up question."
        )

        full_prompt = (
            f"{system_prompt}\n\n"
            f"Business Profile:\n{profile_text}\n"
            f"Conversation History:\n{history_text}\n"
            f"User: {prompt}\nAssistant:"
        )

        response = llm.invoke(full_prompt)
        if isinstance(response, str):
            return response
        if hasattr(response, 'content'):
            return response.content  # type: ignore[attr-defined]
        return str(response)

    except Exception:
        # Fallback to simple keyword-based guidance if LLM not available
        prompt_lower = prompt.lower()
        if "gdpr" in prompt_lower:
            return (
                "For GDPR compliance in your SaaS business, focus on:\n\n"
                "1. **Data Protection Impact Assessments** - Conduct assessments for high-risk processing\n"
                "2. **Lawful Basis for Processing** - Ensure you have valid legal basis (consent, contract, etc.)\n"
                "3. **User Rights** - Implement data access, rectification, erasure, and portability\n"
                "4. **Privacy by Design** - Integrate data protection into product development\n"
                "5. **Data Processing Agreements** - Have proper agreements with third-party processors\n"
                "6. **Security Measures** - Implement appropriate technical and organisational security\n\n"
                "Would you like me to elaborate on any specific area?"
            )
        elif "iso" in prompt_lower or "certification" in prompt_lower:
            return (
                "The ISO 27001 certification process involves:\n\n"
                "1. **Gap Analysis** - Assess current security controls against requirements\n"
                "2. **ISMS Implementation** - Establish Information Security Management System\n"
                "3. **Risk Assessment** - Identify and evaluate information security risks\n"
                "4. **Control Implementation** - Implement appropriate security controls\n"
                "5. **Documentation** - Create comprehensive policies and procedures\n"
                "6. **Internal Audit** - Conduct internal audits to verify compliance\n"
                "7. **Certification Audit** - Undergo external audit by accredited body\n"
                "8. **Continuous Improvement** - Maintain and improve the ISMS\n\n"
                "Process typically takes 6-12 months depending on organisation size."
            )
        elif "financial" in prompt_lower or "reporting" in prompt_lower:
            return (
                "For financial reporting compliance, focus on:\n\n"
                "1. **GAAP/IFRS Compliance** - Follow appropriate accounting standards\n"
                "2. **Internal Controls** - Implement SOX controls if applicable\n"
                "3. **Audit Trail** - Maintain complete documentation\n"
                "4. **Regular Audits** - Conduct internal and external audits\n"
                "5. **Financial Systems** - Ensure proper system controls\n"
                "6. **Reporting Timelines** - Meet all regulatory filing deadlines\n"
                "7. **Disclosure Requirements** - Provide accurate and complete disclosures\n"
                "\nYour specific requirements depend on your jurisdiction and industry."
            )
        else:
            return (
                "I'm here to help with your compliance and business queries. Based on your question, here's my guidance:\n\n"
                "**Key Considerations:**\n"
                "- Review applicable regulations for your industry\n"
                "- Assess current compliance status\n"
                "- Implement necessary controls and processes\n"
                "- Document everything thoroughly\n"
                "- Regular training and awareness programs\n\n"
                "**Next Steps:**\n"
                "1. Conduct a compliance assessment\n"
                "2. Identify gaps and priorities\n"
                "3. Develop implementation roadmap\n"
                "4. Create documentation systems\n"
                "5. Establish monitoring procedures\n\n"
                "For more specific guidance, could you provide details about your business type, jurisdiction, and current challenges?"
            )


if __name__ == "__main__":
    main()

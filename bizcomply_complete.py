#!/usr/bin/env python3
"""
BizComply AI - Complete Business Compliance Assistant
Solving Small Business Owner Challenges:
- Complicated rules navigation
- Business type-specific steps
- Scattered government information
- Unclear forms
- First-time entrepreneur support
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

# Import compliance components
try:
    from models.chat import ChatRepository
    from models.llm import LLMProvider
    from models.compliance import RequirementStatus, RiskLevel, ComplianceRequirement, BusinessCompliance
    from config.config import BusinessType, Jurisdiction
    COMPLIANCE_AVAILABLE = True
except ImportError:
    COMPLIANCE_AVAILABLE = False
    print("Compliance modules not available, using placeholder implementation")

# Placeholder classes for full functionality
class ComplianceEngine:
    """Complete Compliance Engine for Business Requirements"""
    def __init__(self):
        self.initialized = True
        self.profiles = {}
        self.requirements_db = self._load_requirements()
    
    def _load_requirements(self):
        """Load business requirements by type and jurisdiction"""
        return {
            "sole_proprietorship": {
                "licenses": ["Business License", "Home-Based Business Permit"],
                "taxes": ["Self-Employment Tax", "Income Tax"],
                "registrations": ["Business Name Registration", "EIN Application"],
                "compliance": ["Annual Report", "Record Keeping"]
            },
            "llc": {
                "licenses": ["Business License", "Professional Licenses"],
                "taxes": ["LLC Tax Election", "Employment Taxes"],
                "registrations": ["Articles of Organization", "Operating Agreement"],
                "compliance": ["Annual Report", "Member Meetings", "Tax Filings"]
            },
            "corporation": {
                "licenses": ["Business License", "Industry-Specific Permits"],
                "taxes": ["Corporate Income Tax", "Employment Taxes"],
                "registrations": ["Articles of Incorporation", "Bylaws", "Stock Certificates"],
                "compliance": ["Board Meetings", "Annual Reports", "Shareholder Records"]
            }
        }
    
    def get_requirements(self, business_type, jurisdiction):
        """Get compliance requirements for business type and jurisdiction"""
        return self.requirements_db.get(business_type.lower(), {})
    
    def check_compliance(self, business_profile):
        """Check compliance status for a business profile"""
        requirements = self.get_requirements(
            business_profile.get("business_type", "sole_proprietorship"),
            business_profile.get("jurisdiction", "federal")
        )
        
        completed = business_profile.get("completed_steps", [])
        missing = []
        
        for category, items in requirements.items():
            for item in items:
                if item not in completed:
                    missing.append(f"{category}: {item}")
        
        return {
            "status": "compliant" if not missing else "pending",
            "completed_steps": len(completed),
            "total_steps": sum(len(items) for items in requirements.values()),
            "missing_items": missing
        }
    
    def get_business_profile(self, business_id):
        """Get business profile by ID"""
        return self.profiles.get(business_id, None)
    
    def save_business_profile(self, business_id, profile):
        """Save business profile"""
        self.profiles[business_id] = profile
        return profile
    
    def get_next_steps(self, business_profile):
        """Get next recommended steps for business owner"""
        requirements = self.get_requirements(
            business_profile.get("business_type", "sole_proprietorship"),
            business_profile.get("jurisdiction", "federal")
        )
        
        completed = set(business_profile.get("completed_steps", []))
        next_steps = []
        
        # Priority order for business setup
        priority_order = ["registrations", "licenses", "taxes", "compliance"]
        
        for category in priority_order:
            if category in requirements:
                for item in requirements[category]:
                    if item not in completed:
                        next_steps.append({
                            "category": category,
                            "task": item,
                            "priority": "high" if category in ["registrations", "licenses"] else "medium",
                            "estimated_time": self._estimate_time(category, item),
                            "where_to_start": self._get_guidance(category, item)
                        })
                        if len(next_steps) >= 3:  # Show top 3 next steps
                            break
            if len(next_steps) >= 3:
                break
        
        return next_steps
    
    def _estimate_time(self, category, item):
        """Estimate time required for each task"""
        time_estimates = {
            "registrations": "1-2 weeks",
            "licenses": "2-4 weeks", 
            "taxes": "1-3 days",
            "compliance": "ongoing"
        }
        return time_estimates.get(category, "varies")
    
    def _get_guidance(self, category, item):
        """Get step-by-step guidance for each task"""
        guidance_map = {
            "Business Name Registration": "Check name availability → Register with state → Publish notice if required",
            "EIN Application": "Visit IRS.gov → Fill out SS-4 form → Receive EIN immediately online",
            "Articles of Organization": "Prepare formation document → File with state → Pay filing fee",
            "Business License": "Check local requirements → Apply with city/county → Schedule inspections"
        }
        return guidance_map.get(item, "Research local requirements → Gather documents → Submit application")

def load_comprehensive_css():
    """Load comprehensive CSS for business compliance app"""
    st.markdown("""
    <style>
    /* Comprehensive Business Compliance UI */
    
    /* 1. Professional Sidebar */
    .stSidebar {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%) !important;
        border-right: none !important;
    }
    
    .stSidebar .element-container {
        background-color: transparent !important;
        border: none !important;
        padding: 0 !important;
        margin: 0 !important;
    }
    
    .sidebar-header {
        background: rgba(15, 23, 42, 0.8);
        color: #f8fafc;
        padding: 24px 20px;
        margin: -16px -16px 24px -16px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .sidebar-header h1 {
        margin: 0;
        font-size: 1.5rem;
        font-weight: 700;
        color: #f8fafc;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    .sidebar-header .subtitle {
        font-size: 0.875rem;
        color: #94a3b8;
        margin: 4px 0 0 0;
    }
    
    /* 2. Business Type Cards */
    .business-type-card {
        background: #ffffff;
        border: 2px solid #e2e8f0;
        border-radius: 12px;
        padding: 20px;
        margin: 8px 0;
        cursor: pointer;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .business-type-card:hover {
        border-color: #3b82f6;
        box-shadow: 0 8px 25px rgba(59, 130, 246, 0.15);
        transform: translateY(-2px);
    }
    
    .business-type-card.selected {
        border-color: #3b82f6;
        background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.25);
    }
    
    .business-type-card .icon {
        font-size: 2rem;
        margin-bottom: 12px;
    }
    
    .business-type-card h3 {
        margin: 0 0 8px 0;
        color: #1e293b;
        font-size: 1.125rem;
        font-weight: 600;
    }
    
    .business-type-card p {
        margin: 0;
        color: #64748b;
        font-size: 0.875rem;
        line-height: 1.4;
    }
    
    /* 3. Progress Tracker */
    .progress-container {
        background: #ffffff;
        border-radius: 12px;
        padding: 24px;
        margin: 16px 0;
        border: 1px solid #e2e8f0;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    }
    
    .progress-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 16px;
    }
    
    .progress-bar-bg {
        background: #e2e8f0;
        height: 8px;
        border-radius: 4px;
        overflow: hidden;
        margin: 12px 0;
    }
    
    .progress-bar-fill {
        background: linear-gradient(90deg, #3b82f6 0%, #2563eb 100%);
        height: 100%;
        border-radius: 4px;
        transition: width 0.5s ease;
    }
    
    /* 4. Task Cards */
    .task-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 16px;
        margin: 8px 0;
        border-left: 4px solid #3b82f6;
        transition: all 0.2s ease;
    }
    
    .task-card:hover {
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        transform: translateX(4px);
    }
    
    .task-card.high-priority {
        border-left-color: #ef4444;
        background: linear-gradient(90deg, #fef2f2 0%, #ffffff 100%);
    }
    
    .task-card.medium-priority {
        border-left-color: #f59e0b;
        background: linear-gradient(90deg, #fffbeb 0%, #ffffff 100%);
    }
    
    .task-card h4 {
        margin: 0 0 8px 0;
        color: #1e293b;
        font-size: 1rem;
        font-weight: 600;
    }
    
    .task-card .task-meta {
        display: flex;
        gap: 16px;
        align-items: center;
        margin: 8px 0;
    }
    
    .task-card .task-meta span {
        font-size: 0.75rem;
        color: #64748b;
        background: #f1f5f9;
        padding: 4px 8px;
        border-radius: 4px;
    }
    
    .task-card .guidance {
        font-size: 0.875rem;
        color: #475569;
        margin: 8px 0 0 0;
        line-height: 1.4;
    }
    
    /* 5. Chat Interface */
    .chat-container {
        background: #ffffff;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        height: 500px;
        display: flex;
        flex-direction: column;
        margin: 16px 0;
        overflow: hidden;
    }
    
    .chat-header {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        color: white;
        padding: 16px 20px;
        font-weight: 600;
        border-bottom: 1px solid #e2e8f0;
    }
    
    .chat-messages {
        flex: 1;
        padding: 20px;
        overflow-y: auto;
        background: #f8fafc;
    }
    
    .message {
        margin: 12px 0;
        max-width: 80%;
    }
    
    .user-message {
        background: #3b82f6;
        color: white;
        padding: 12px 16px;
        border-radius: 18px 18px 4px 18px;
        margin-left: auto;
    }
    
    .assistant-message {
        background: #ffffff;
        color: #1e293b;
        padding: 12px 16px;
        border-radius: 18px 18px 18px 4px;
        border: 1px solid #e2e8f0;
    }
    
    .chat-input {
        padding: 16px 20px;
        border-top: 1px solid #e2e8f0;
        background: #ffffff;
    }
    
    /* 6. Quick Actions */
    .quick-actions {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 12px;
        margin: 16px 0;
    }
    
    .quick-action-btn {
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 16px;
        text-align: center;
        cursor: pointer;
        transition: all 0.2s ease;
        text-decoration: none;
        color: #1e293b;
    }
    
    .quick-action-btn:hover {
        background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
        border-color: #3b82f6;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.15);
    }
    
    .quick-action-btn .icon {
        font-size: 1.5rem;
        margin-bottom: 8px;
        display: block;
    }
    
    .quick-action-btn .title {
        font-weight: 600;
        margin-bottom: 4px;
    }
    
    .quick-action-btn .description {
        font-size: 0.75rem;
        color: #64748b;
    }
    
    /* 7. Status Indicators */
    .status-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
    }
    
    .status-badge.compliant {
        background: #dcfce7;
        color: #166534;
    }
    
    .status-badge.pending {
        background: #fef3c7;
        color: #92400e;
    }
    
    .status-badge.overdue {
        background: #fee2e2;
        color: #991b1b;
    }
    
    /* 8. Responsive Design */
    @media (max-width: 768px) {
        .quick-actions {
            grid-template-columns: 1fr;
        }
        
        .task-card .task-meta {
            flex-direction: column;
            align-items: flex-start;
            gap: 8px;
        }
        
        .sidebar-header {
            padding: 16px 12px;
        }
        
        .sidebar-header h1 {
            font-size: 1.25rem;
        }
    }
    
    /* Hide Streamlit defaults */
    .stApp > div {
        padding-top: 0 !important;
    }
    
    [data-testid="stToolbar"] {
        display: none !important;
    }
    </style>
    """, unsafe_allow_html=True)

def initialize_session_state():
    """Initialize comprehensive session state"""
    if 'business_profile' not in st.session_state:
        st.session_state.business_profile = {
            'business_id': f'biz_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
            'business_name': '',
            'business_type': '',
            'jurisdiction': '',
            'stage': 'setup',  # setup, active, compliant
            'completed_steps': [],
            'current_tasks': [],
            'created_at': datetime.now().isoformat(),
            'last_updated': datetime.now().isoformat()
        }
    
    if 'compliance_engine' not in st.session_state:
        st.session_state.compliance_engine = ComplianceEngine()
    
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'setup'

def render_sidebar():
    """Render comprehensive sidebar"""
    with st.sidebar:
        # Header
        st.markdown("""
        <div class="sidebar-header">
            <h1>🏢 BizComply AI</h1>
            <div class="subtitle">Your Business Compliance Assistant</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Business Profile Summary
        profile = st.session_state.business_profile
        if profile['business_name']:
            st.markdown(f"**{profile['business_name']}**")
            if profile['business_type']:
                st.markdown(f"*{profile['business_type'].title()}*")
            
            # Progress
            compliance = st.session_state.compliance_engine.check_compliance(profile)
            progress_percent = (compliance['completed_steps'] / max(compliance['total_steps'], 1)) * 100
            
            st.markdown(f"""
            <div class="progress-container">
                <div class="progress-header">
                    <span>Setup Progress</span>
                    <span>{progress_percent:.0f}%</span>
                </div>
                <div class="progress-bar-bg">
                    <div class="progress-bar-fill" style="width: {progress_percent}%"></div>
                </div>
                <small>{compliance['completed_steps']} of {compliance['total_steps']} steps completed</small>
            </div>
            """, unsafe_allow_html=True)
        
        st.divider()
        
        # Navigation
        pages = [
            ("🚀 Business Setup", "setup"),
            ("📋 Requirements", "requirements"),
            ("💬 AI Assistant", "chat"),
            ("📊 Compliance Check", "compliance"),
            ("📚 Resources", "resources")
        ]
        
        for page_name, page_key in pages:
            if st.button(page_name, key=f"nav_{page_key}", use_container_width=True,
                        type="primary" if st.session_state.current_page == page_key else "secondary"):
                st.session_state.current_page = page_key
        
        st.divider()
        
        # Quick Actions
        st.markdown("**Quick Actions**")
        
        if st.button("📝 Save Progress", key="save_progress", use_container_width=True):
            st.session_state.compliance_engine.save_business_profile(
                profile['business_id'], 
                profile
            )
            st.success("Progress saved!")
        
        if st.button("🔄 Reset Setup", key="reset_setup", use_container_width=True):
            if st.confirm("Are you sure you want to reset your setup?"):
                for key in st.session_state.keys():
                    del st.session_state[key]
                initialize_session_state()
                st.rerun()

def render_business_setup():
    """Render business setup page"""
    st.markdown("## 🚀 Business Setup")
    st.markdown("Let's set up your business compliance profile step by step.")
    
    profile = st.session_state.business_profile
    
    # Business Name
    st.markdown("### Business Information")
    business_name = st.text_input(
        "Business Name",
        value=profile['business_name'],
        placeholder="Enter your business name"
    )
    profile['business_name'] = business_name
    
    # Business Type Selection
    st.markdown("### Business Type")
    st.markdown("Select your business structure to see specific requirements:")
    
    business_types = [
        {
            "type": "sole_proprietorship",
            "name": "Sole Proprietorship",
            "icon": "👤",
            "description": "Simplest structure, personally liable for business debts"
        },
        {
            "type": "llc",
            "name": "LLC",
            "icon": "🏢",
            "description": "Personal liability protection, flexible management"
        },
        {
            "type": "corporation",
            "name": "Corporation",
            "icon": "🏛️",
            "description": "Separate legal entity, formal structure required"
        }
    ]
    
    selected_type = None
    cols = st.columns(3)
    for i, biz_type in enumerate(business_types):
        with cols[i]:
            is_selected = profile['business_type'] == biz_type['type']
            st.markdown(f"""
            <div class="business-type-card {'selected' if is_selected else ''}" 
                 onclick="document.querySelector('[data-testid=\"stButton\"][key=\"select_{biz_type['type']}\"]').click()">
                <div class="icon">{biz_type['icon']}</div>
                <h3>{biz_type['name']}</h3>
                <p>{biz_type['description']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button(f"Select {biz_type['name']}", key=f"select_{biz_type['type']}", use_container_width=True):
                profile['business_type'] = biz_type['type']
                st.rerun()
    
    # Jurisdiction
    st.markdown("### Location & Jurisdiction")
    jurisdiction = st.selectbox(
        "Primary Business Jurisdiction",
        ["Federal", "State", "Local"],
        index=0,
        help="Select your primary business jurisdiction for compliance requirements"
    )
    profile['jurisdiction'] = jurisdiction
    
    # Next Steps Preview
    if profile['business_type']:
        st.markdown("### Your Next Steps")
        next_steps = st.session_state.compliance_engine.get_next_steps(profile)
        
        for step in next_steps:
            priority_class = "high-priority" if step['priority'] == 'high' else "medium-priority"
            st.markdown(f"""
            <div class="task-card {priority_class}">
                <h4>{step['task']}</h4>
                <div class="task-meta">
                    <span>📁 {step['category'].title()}</span>
                    <span>⏱️ {step['estimated_time']}</span>
                    <span>🎯 {step['priority'].title()} Priority</span>
                </div>
                <div class="guidance">
                    <strong>How to start:</strong> {step['where_to_start']}
                </div>
            </div>
            """, unsafe_allow_html=True)

def render_requirements():
    """Render detailed requirements page"""
    st.markdown("## 📋 Compliance Requirements")
    
    profile = st.session_state.business_profile
    
    if not profile['business_type']:
        st.warning("Please complete your business setup first to see requirements.")
        return
    
    requirements = st.session_state.compliance_engine.get_requirements(
        profile['business_type'], 
        profile['jurisdiction']
    )
    
    compliance = st.session_state.compliance_engine.check_compliance(profile)
    
    # Overall Status
    status_class = "compliant" if compliance['status'] == 'compliant' else "pending"
    st.markdown(f"""
    <div class="status-badge {status_class}">
        {compliance['status'].title()}
    </div>
    """, unsafe_allow_html=True)
    
    # Requirements by Category
    for category, items in requirements.items():
        with st.expander(f"📁 {category.title()} ({len(items)} items)", expanded=True):
            for item in items:
                is_completed = item in profile['completed_steps']
                
                col1, col2 = st.columns([1, 4])
                with col1:
                    if st.checkbox("✅", key=f"check_{item}", value=is_completed):
                        if item not in profile['completed_steps']:
                            profile['completed_steps'].append(item)
                    else:
                        if item in profile['completed_steps']:
                            profile['completed_steps'].remove(item)
                
                with col2:
                    st.markdown(f"**{item}**")
                    if is_completed:
                        st.success("Completed ✓")
                    else:
                        st.info("Pending")
    
    # Progress Update
    if st.button("Update Progress", key="update_progress"):
        st.session_state.compliance_engine.save_business_profile(
            profile['business_id'], 
            profile
        )
        st.success("Progress updated!")
        st.rerun()

def render_chat_assistant():
    """Render AI chat assistant"""
    st.markdown("## 💬 AI Compliance Assistant")
    
    # Chat Container
    st.markdown("""
    <div class="chat-container">
        <div class="chat-header">
            🤖 BizComply AI Assistant
        </div>
        <div class="chat-messages">
    """, unsafe_allow_html=True)
    
    # Display Chat History
    for message in st.session_state.chat_history[-10:]:  # Show last 10 messages
        if message['role'] == 'user':
            st.markdown(f"""
            <div class="message user-message">
                <strong>You:</strong> {message['content']}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="message assistant-message">
                <strong>Assistant:</strong> {message['content']}
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("""
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Quick Questions
    st.markdown("### Common Questions")
    quick_questions = [
        "What licenses do I need for my business?",
        "How do I register my business name?",
        "What taxes do I need to pay?",
        "How do I check my compliance status?",
        "What are the next steps for my business?"
    ]
    
    cols = st.columns(3)
    for i, question in enumerate(quick_questions[:6]):
        with cols[i % 3]:
            if st.button(question, key=f"quick_{i}", use_container_width=True):
                st.session_state.chat_history.append({
                    "role": "user", 
                    "content": question,
                    "timestamp": datetime.now().isoformat()
                })
                # Generate AI response
                response = generate_ai_response(question, st.session_state.business_profile)
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": response,
                    "timestamp": datetime.now().isoformat()
                })
                st.rerun()
    
    # Custom Question Input
    user_input = st.text_input(
        "Ask your compliance question:",
        placeholder="Type your question here...",
        key="chat_input"
    )
    
    if st.button("Send", key="send_chat") and user_input:
        st.session_state.chat_history.append({
            "role": "user",
            "content": user_input,
            "timestamp": datetime.now().isoformat()
        })
        
        response = generate_ai_response(user_input, st.session_state.business_profile)
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": response,
            "timestamp": datetime.now().isoformat()
        })
        
        st.rerun()

def generate_ai_response(question, business_profile):
    """Generate AI response for user questions"""
    question_lower = question.lower()
    
    # Business type specific responses
    if business_profile.get('business_type'):
        biz_type = business_profile['business_type']
        if 'license' in question_lower:
            if biz_type == 'sole_proprietorship':
                return "For a sole proprietorship, you'll typically need a business license from your city/county and any professional licenses for your specific industry. Check with your local government office for exact requirements."
            elif biz_type == 'llc':
                return "For an LLC, you'll need a business license, plus any industry-specific permits. Your LLC formation documents may also need to be filed with professional licensing boards for regulated industries."
            elif biz_type == 'corporation':
                return "Corporations need business licenses, industry-specific permits, and potentially professional licenses. Corporate officers may need individual licenses depending on your industry."
        
        if 'tax' in question_lower:
            if biz_type == 'sole_proprietorship':
                return "As a sole proprietor, you'll pay self-employment tax (15.3%) on your net earnings, plus income tax. You'll need to make quarterly estimated tax payments and file Schedule C with your personal tax return."
            elif biz_type == 'llc':
                return "LLCs have flexibility: single-member LLCs are taxed like sole proprietors, multi-member like partnerships. You can also elect corporate taxation. Don't forget employment taxes if you have employees."
            elif biz_type == 'corporation':
                return "Corporations pay corporate income tax (21% federally) and possibly state corporate taxes. If you pay yourself a salary, you'll also deal with payroll taxes and personal income tax on that salary."
    
    # General responses
    if 'register' in question_lower and 'name' in question_lower:
        return "To register your business name: 1) Check name availability with your state, 2) File a DBA ('Doing Business As') if you're a sole proprietor using a different name, 3) For LLCs/corporations, the name is registered during formation. Make sure your name isn't already trademarked!"
    
    if 'compliance' in question_lower and 'status' in question_lower:
        compliance = st.session_state.compliance_engine.check_compliance(business_profile)
        return f"Your current compliance status: {compliance['status']}. You've completed {compliance['completed_steps']} out of {compliance['total_steps']} required steps. Focus on completing your registrations and licenses first."
    
    if 'next step' in question_lower:
        next_steps = st.session_state.compliance_engine.get_next_steps(business_profile)
        if next_steps:
            step = next_steps[0]
            return f"Your next priority step is: {step['task']}. This is a {step['priority']} priority task that typically takes {step['estimated_time']}. Here's how to start: {step['where_to_start']}"
        else:
            return "Great! You're on track. Continue with your current tasks and check back for any new requirements as your business grows."
    
    # Default response
    return "I'm here to help with your business compliance questions. I can assist with licensing requirements, tax obligations, registration processes, and compliance tracking. Could you be more specific about your business type and what you'd like to know?"

def render_compliance_check():
    """Render compliance check page"""
    st.markdown("## 📊 Compliance Status")
    
    profile = st.session_state.business_profile
    
    if not profile['business_type']:
        st.warning("Please complete your business setup first.")
        return
    
    compliance = st.session_state.compliance_engine.check_compliance(profile)
    
    # Overall Status Card
    status_class = "compliant" if compliance['status'] == 'compliant' else "pending"
    st.markdown(f"""
    <div class="progress-container">
        <h3>Overall Compliance Status</h3>
        <div class="status-badge {status_class}" style="font-size: 1rem; padding: 8px 16px;">
            {compliance['status'].title()}
        </div>
        <p>You've completed {compliance['completed_steps']} of {compliance['total_steps']} required compliance steps.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Missing Items
    if compliance['missing_items']:
        st.markdown("### ⚠️ Pending Items")
        for item in compliance['missing_items']:
            st.markdown(f"- {item}")
    
    # Recommendations
    st.markdown("### 🎯 Recommendations")
    
    if compliance['status'] != 'compliant':
        st.markdown("""
        <div class="task-card high-priority">
            <h4>Complete Required Registrations</h4>
            <div class="guidance">
                Focus on completing your business registrations first. This is typically the foundation for all other compliance requirements.
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Timeline
    st.markdown("### 📅 Compliance Timeline")
    
    timeline_data = []
    for i in range(6):
        date = datetime.now() + timedelta(days=i*30)
        timeline_data.append({
            "date": date.strftime("%B %Y"),
            "tasks": f"Monthly compliance check, Tax filing due" if i % 3 == 0 else "Routine compliance review"
        })
    
    timeline_df = pd.DataFrame(timeline_data)
    st.dataframe(timeline_df, use_container_width=True)

def render_resources():
    """Render resources page"""
    st.markdown("## 📚 Business Resources")
    
    # Quick Actions Grid
    st.markdown("### Quick Actions")
    
    resources = [
        {
            "icon": "🏛️",
            "title": "Government Portal",
            "description": "Access official government resources",
            "url": "#"
        },
        {
            "icon": "📄",
            "title": "Form Library",
            "description": "Download required forms",
            "url": "#"
        },
        {
            "icon": "💰",
            "title": "Tax Calculator",
            "description": "Estimate your tax obligations",
            "url": "#"
        },
        {
            "icon": "📅",
            "title": "Deadline Tracker",
            "description": "Track important dates",
            "url": "#"
        },
        {
            "icon": "🎓",
            "title": "Learning Center",
            "description": "Business compliance guides",
            "url": "#"
        },
        {
            "icon": "📞",
            "title": "Expert Help",
            "description": "Get professional assistance",
            "url": "#"
        }
    ]
    
    cols = st.columns(3)
    for i, resource in enumerate(resources):
        with cols[i % 3]:
            st.markdown(f"""
            <div class="quick-action-btn">
                <div class="icon">{resource['icon']}</div>
                <div class="title">{resource['title']}</div>
                <div class="description">{resource['description']}</div>
            </div>
            """, unsafe_allow_html=True)
    
    # Helpful Links
    st.markdown("### Helpful Links")
    
    links = [
        ("IRS Business Center", "https://www.irs.gov/businesses"),
        ("SBA Business Guide", "https://www.sba.gov/business-guide"),
        ("State Business Resources", "#"),
        ("Local Permit Office", "#"),
        ("Professional Licensing", "#"),
        ("Tax Forms Library", "#")
    ]
    
    for name, url in links:
        st.markdown(f"- [{name}]({url})")
    
    # Contact Information
    st.markdown("### Need Help?")
    st.markdown("""
    **Contact Information:**
    - Email: support@bizcomply.ai
    - Phone: 1-800-BIZ-COMPLY
    - Hours: Monday-Friday, 9AM-5PM EST
    
    **Office Locations:**
    - New York: 123 Business Ave, Suite 100
    - Los Angeles: 456 Commerce Blvd, Suite 200
    - Chicago: 789 Corporate Plaza, Suite 300
    """)

def main():
    """Main application"""
    # Initialize
    initialize_session_state()
    load_comprehensive_css()
    
    # Page Configuration
    st.set_page_config(
        page_title="BizComply AI - Business Compliance Assistant",
        page_icon="🏢",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Render Sidebar
    render_sidebar()
    
    # Main Content
    profile = st.session_state.business_profile
    
    # Welcome Header
    if profile['business_name']:
        st.markdown(f"# Welcome, {profile['business_name']}! 👋")
    else:
        st.markdown("# Welcome to BizComply AI! 🏢")
        st.markdown("Your personal business compliance assistant")
    
    # Page Routing
    if st.session_state.current_page == 'setup':
        render_business_setup()
    elif st.session_state.current_page == 'requirements':
        render_requirements()
    elif st.session_state.current_page == 'chat':
        render_chat_assistant()
    elif st.session_state.current_page == 'compliance':
        render_compliance_check()
    elif st.session_state.current_page == 'resources':
        render_resources()
    else:
        render_business_setup()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #64748b; font-size: 0.875rem;'>
        Made with ❤️ for small business owners | © 2024 BizComply AI
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()

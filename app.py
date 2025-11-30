import streamlit as st
import requests
import json
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List

# Import compliance components
from models.chat import ChatRepository
from models.llm import LLMProvider
from models.compliance import RequirementStatus, RiskLevel, ComplianceRequirement, BusinessCompliance
from models.embeddings import EmbeddingProvider
from config.config import BusinessType, Jurisdiction, WEB_SEARCH_ENABLED, RESPONSE_MODES, DEFAULT_RESPONSE_MODE

# Import utilities
from utils.web_search import WebSearch
from utils.document_processor import DocumentProcessor

# Import RAG bot engine
try:
    from bot_engine import get_compliance_answer
    RAG_AVAILABLE = True
except ImportError:
    RAG_AVAILABLE = False
    print("Warning: bot_engine not available. Using fallback responses.")

# RAG Chatbot Components
class ConversationState:
    """Manages conversation state and user profiling"""
    def __init__(self):
        self.current_step = "onboarding"  # onboarding, main_chat
        self.user_profile = {
            "location": "",
            "entity_type": "",
            "industry": "",
            "business_name": "",
            "turnover": "",
            "employees": ""
        }
        self.missing_info = ["location", "entity_type", "industry"]
        self.questionnaire_index = 0
        self.completed_questions = []
    
    def is_profile_complete(self):
        """Check if user profile is complete"""
        return all(self.user_profile.get(key, "") != "" for key in ["location", "entity_type", "industry"])
    
    def get_next_question(self):
        """Get next profiling question"""
        questions = [
            {
                "key": "location",
                "question": "Where is your business located? (City/State)",
                "options": ["Delhi", "Mumbai", "Bangalore", "Hyderabad", "Chennai", "Other"]
            },
            {
                "key": "entity_type", 
                "question": "What type of business entity is it?",
                "options": ["Sole Proprietorship", "Partnership Firm", "LLP", "Private Limited", "OPC"]
            },
            {
                "key": "industry",
                "question": "What industry are you in?",
                "options": ["Food Service", "Retail", "IT Services", "Manufacturing", "Education", "Healthcare", "Other"]
            }
        ]
        
        for i, q in enumerate(questions):
            if q["key"] not in self.completed_questions:
                return q
        
        return None
    
    def update_profile(self, key, value):
        """Update user profile"""
        self.user_profile[key] = value
        if key not in self.completed_questions:
            self.completed_questions.append(key)
        
        if self.is_profile_complete():
            self.current_step = "main_chat"

class KnowledgeRetriever:
    """RAG Knowledge Base for Compliance Rules"""
    def __init__(self):
        self.compliance_data = self._load_compliance_data()
    
    def _load_compliance_data(self):
        """Load compliance knowledge base"""
        try:
            with open('compliance_data.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            # Fallback data if file doesn't exist
            return {
                "industries": {
                    "food_service": {
                        "licenses": [
                            {
                                "name": "FSSAI State License",
                                "mandatory": True,
                                "description": "Required for any business handling food.",
                                "documents": ["ID Proof", "Address Proof"]
                            }
                        ]
                    }
                }
            }
    
    def search_licenses(self, industry, entity_type, location):
        """Search for relevant licenses based on profile"""
        results = []
        
        # Get industry-specific licenses
        if industry.lower() in self.compliance_data.get("industries", {}):
            industry_data = self.compliance_data["industries"][industry.lower()]
            licenses = industry_data.get("licenses", [])
            results.extend(licenses)
        
        # Get entity-specific registrations
        entity_key = entity_type.lower().replace(" ", "_")
        if entity_key in self.compliance_data.get("entity_types", {}):
            entity_data = self.compliance_data["entity_types"][entity_key]
            registrations = entity_data.get("registrations", [])
            
            # Convert registrations to license format
            for reg in registrations:
                results.append({
                    "name": reg["name"],
                    "mandatory": reg.get("mandatory", False),
                    "description": reg.get("description", ""),
                    "documents": reg.get("documents", []),
                    "type": "registration"
                })
        
        return results
    
    def get_tax_info(self, entity_type, turnover=""):
        """Get taxation information"""
        entity_key = entity_type.lower().replace(" ", "_")
        if entity_key in self.compliance_data.get("entity_types", {}):
            return self.compliance_data["entity_types"][entity_key].get("taxation", {})
        return {}
    
    def get_deadlines(self):
        """Get important compliance deadlines"""
        return self.compliance_data.get("deadlines", {})
    
    def get_location_specific(self, location, industry):
        """Get location-specific requirements"""
        location_key = location.lower()
        if location_key in self.compliance_data.get("locations", {}):
            location_data = self.compliance_data["locations"][location_key]
            return location_data.get("specific_requirements", {}).get(industry.lower(), [])
        return []

class ComplianceChatbot:
    """Optimized RAG-based compliance chatbot with web search integration"""
    def __init__(self):
        self.knowledge_retriever = KnowledgeRetriever()
        self.system_prompt = """You are BizComply, an expert Business Compliance Assistant for India.
        
Your Rules:
1. Never guess laws. Use only verified information from the knowledge base.
2. Be Simple. Explain legal terms like you're talking to a 5th grader.
3. Be Proactive. Always suggest the next logical step.
4. Keep answers short. Use bullet points and markdown formatting.
5. Focus on practical, actionable advice."""
        
        # Initialize RAG components
        try:
            self.embedding_model = EmbeddingProvider.get_embedding_model()
            self.document_processor = DocumentProcessor()
            self.rag_enabled = True
        except Exception as e:
            print(f"RAG initialization failed: {e}")
            self.rag_enabled = False
        
        # Initialize Web Search
        try:
            self.web_search = WebSearch()
            self.web_search_enabled = WEB_SEARCH_ENABLED
        except Exception as e:
            print(f"Web search initialization failed: {e}")
            self.web_search_enabled = False
    
    def process_message(self, user_message, conversation_state, response_mode="simple"):
        """Optimized message processing with fast response"""
        # Check if user is in onboarding
        if conversation_state.current_step == "onboarding":
            return self._handle_onboarding_fast(user_message, conversation_state)
        
        # Main chat with optimized keyword matching
        return self._handle_main_chat_fast(user_message, conversation_state, response_mode)
    
    def _handle_onboarding_fast(self, message, state):
        """
        Fast onboarding with explicit step handling.
        """
        
        # --- STEP 1: SAVE THE INCOMING ANSWER ---
        # We look at what is currently MISSING to decide what the user is answering.
        
        if "location" not in state.completed_questions:
            # The user just answered the Location question
            state.update_profile("location", message)
            
        elif "entity_type" not in state.completed_questions:
            # The user just answered the Entity Type question
            state.update_profile("entity_type", message)
            
        elif "industry" not in state.completed_questions:
            # The user just answered the Industry question
            state.update_profile("industry", message)

        # --- STEP 2: DECIDE THE NEXT QUESTION ---
        # Now that we've saved the answer, check what is STILL missing.

        if "entity_type" not in state.completed_questions:
            return "### What type of business entity is it?\n\n- Sole Proprietorship\n- Partnership Firm\n- LLP\n- Private Limited\n- OPC"
            
        elif "industry" not in state.completed_questions:
            return "### What industry are you in?\n\n- Food Service\n- Retail\n- IT Services\n- Manufacturing\n- Education\n- Healthcare\n- Other"
            
        else:
            # If everything is answered, switch to main chat
            state.current_step = "main_chat"
            return f"✅ **Great! I have all your information.**\n\n**Business Profile:**\n- Location: {state.user_profile['location']}\n- Entity Type: {state.user_profile['entity_type']}\n- Industry: {state.user_profile['industry']}\n\nNow I can provide specific compliance guidance. What would you like to know?"
    
    def _search_documents(self, query: str, k: int = 3) -> List[str]:
        """Search documents using RAG embeddings"""
        if not self.rag_enabled:
            return []
        
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.embed_query(query)
            
            # Search through documents (simplified - in production you'd use a vector store)
            documents = self.document_processor.load_documents()
            relevant_docs = []
            
            for doc in documents:
                # Simple similarity check (in production, use proper vector similarity)
                if any(word.lower() in doc.content.lower() for word in query.split()[:3]):
                    relevant_docs.append(doc.content[:500])  # Return first 500 chars
            
            return relevant_docs[:k]
            
        except Exception as e:
            print(f"Document search error: {e}")
            return []
    
    def _perform_web_search(self, query: str) -> List[Dict[str, str]]:
        """Perform web search for current information"""
        if not self.web_search_enabled:
            return []
        
        try:
            results = self.web_search.search(query, num_results=3)
            return results
        except Exception as e:
            print(f"Web search error: {e}")
            return []
    
    def _format_response(self, response: str, mode: str = "simple") -> str:
        """Format response based on mode (concise/detailed)"""
        if mode == "concise":
            # Make response shorter and more direct
            lines = response.split('\n')
            essential_lines = []
            for line in lines:
                if line.strip() and not line.startswith('**Next Step:'):
                    essential_lines.append(line)
                if len(essential_lines) >= 3:  # Limit to 3 key points
                    break
            return '\n'.join(essential_lines)
        elif mode == "detailed":
            # Add more detail and explanations
            return response + "\n\n**Additional Information:**\n- For specific legal advice, consult with a compliance expert.\n- Regulations may vary based on your specific circumstances.\n- Always verify current requirements with relevant authorities."
        else:
            return response
    
    def _handle_main_chat_fast(self, message, state, response_mode="simple"):
        profile = state.user_profile
        message_lower = message.lower()
        
        # --- LOGIC PATCH: Check if user is asking about a different entity ---
        # Create temporary profile if user mentions a specific entity type
        temp_profile = profile.copy()
        
        if "one person company" in message_lower or "opc" in message_lower:
            temp_profile['entity_type'] = "One Person Company"
        elif "private limited" in message_lower or "pvt ltd" in message_lower:
            temp_profile['entity_type'] = "Private Limited Company"
        elif "llp" in message_lower or "limited liability partnership" in message_lower:
            temp_profile['entity_type'] = "LLP"
        elif "sole proprietor" in message_lower or "proprietorship" in message_lower:
            temp_profile['entity_type'] = "Sole Proprietorship"
        elif "partnership firm" in message_lower or "partnership" in message_lower:
            temp_profile['entity_type'] = "Partnership Firm"
        
        # Try RAG engine first if available and user is past onboarding
        if self.rag_enabled and state.current_step == "main_chat":
            try:
                # Search documents first
                doc_results = self._search_documents(message)
                if doc_results:
                    context = "\n".join(doc_results)
                    rag_response = f"Based on compliance documents:\n{context}\n\n{self._handle_main_chat_fallback(message, temp_profile)}"
                    return self._format_response(rag_response, response_mode)
            except Exception as e:
                print(f"RAG engine error: {e}")
        
        # Try web search for current information
        if self.web_search_enabled and ("latest" in message_lower or "current" in message_lower or "new" in message_lower):
            try:
                web_results = self._perform_web_search(message)
                if web_results:
                    web_context = "\n".join([f"**{result['title']}** ({result['source']})\n{result['snippet']}" for result in web_results])
                    web_response = f"Based on current information:\n{web_context}\n\n{self._handle_main_chat_fallback(message, temp_profile)}"
                    return self._format_response(web_response, response_mode)
            except Exception as e:
                print(f"Web search error: {e}")
        
        # Fallback to keyword-based responses for common queries
        base_response = self._handle_main_chat_fallback(message, temp_profile)
        return self._format_response(base_response, response_mode)
    
    def _handle_main_chat_fallback(self, message, profile):
        message_lower = message.lower()
        # License queries (use temp_profile for entity-specific answers)
        if any(keyword in message_lower for keyword in ["license", "registration", "permit"]):
            return self._handle_license_query_fast(message, profile)
        # Tax queries (use temp_profile for entity-specific answers)
        elif any(keyword in message_lower for keyword in ["tax", "gst", "tds", "income tax"]):
            return self._handle_tax_query_fast(message, profile)
        # Deadline queries
        elif any(keyword in message_lower for keyword in ["deadline", "due date", "when"]):
            return self._handle_deadline_query_fast(message, profile)
        # Compliance status (use original profile)
        elif any(keyword in message_lower for keyword in ["compliance", "check", "status"]):
            return self._handle_compliance_status_fast(profile)
        # Startup guidance
        elif any(keyword in message_lower for keyword in ["start", "begin", "setup", "new"]):
            return self._handle_startup_guide_fast(profile)
        # Legal document queries (use RAG if available, otherwise fallback)
        elif any(keyword in message_lower for keyword in ["section", "act", "law", "legal", "punishment", "fraud", "director", "duties"]):
            if RAG_AVAILABLE:
                try:
                    rag_response = get_compliance_answer(message)
                    return rag_response['result']
                except Exception as e:
                    return f"I am having trouble reading the legal documents right now. Please check my API connection. Error: {str(e)}"
            else:
                return self._provide_general_guidance_fast(message, profile)
        # General guidance (use temp_profile)
        else:
            return self._provide_general_guidance_fast(message, profile)
    
    def _handle_license_query_fast(self, message, profile):
        """Fast license query with pre-built responses"""
        industry_key = profile.get("industry", "").lower().replace(" ", "_")
        entity_key = profile.get("entity_type", "").lower().replace(" ", "_")
        
        # Pre-built responses for common combinations
        if "food" in industry_key:
            return """### Required Licenses for Food Service Business:

**Mandatory Licenses:**
- [ ] **FSSAI State License**
  - Required for any food handling business
  - Timeline: 30-60 days | Cost: ₹100-5,000
  - Documents: ID Proof, Kitchen Blueprint, Address Proof

- [ ] **Health Trade License**
  - Local municipal license
  - Timeline: 15-30 days | Cost: ₹500-2,000
  - Documents: Application Form, Address Proof

**Optional:**
- [ ] **GST Registration** (if turnover > ₹20 Lakhs)
  - Timeline: 3-7 days | Cost: Free

**Next Step:** Would you like the step-by-step application process for FSSAI license?"""
        
        elif "retail" in industry_key:
            return """### Required Licenses for Retail Business:

**Mandatory:**
- [ ] **Shop & Establishment Act Registration**
  - Must be obtained within 30 days of starting
  - Timeline: 7-15 days | Cost: ₹300-1,000
  - Documents: Application Form, Address Proof, ID Proof

**Optional:**
- [ ] **GST Registration** (if turnover > ₹40 Lakhs)
  - Timeline: 3-7 days | Cost: Free

**Next Step:** Need help with the Shop Act registration process?"""
        
        elif "it" in industry_key or "software" in industry_key:
            return """### Requirements for IT Services Business:

**Mandatory:**
- [ ] **Shop & Establishment Act Registration**
  - Basic registration for all businesses

**Optional but Recommended:**
- [ ] **GST Registration** (if turnover > ₹20 Lakhs)
  - Timeline: 3-7 days | Cost: Free
  - Documents: PAN, Address Proof, Bank Details

- [ ] **MSME Registration**
  - Benefits: Collateral-free loans, subsidies
  - Cost: Free

**Next Step:** Would you like to know about MSME registration benefits?"""
        
        elif "opc" in entity_key or "one person" in entity_key:
            return """### Requirements for One Person Company (OPC):

**Mandatory Registrations:**
- [ ] **Company Incorporation (MCA)**
  - Required: DIN, DSC, Name Approval
  - Timeline: 10-15 days | Cost: ₹3,000-6,000
  - Documents: Director documents, Address proof

- [ ] **PAN & TAN**
  - Company PAN and Tax Deduction Account Number
  - Timeline: 7-10 days | Cost: ₹107 + ₹64

**Compliance Requirements:**
- [ ] **Annual Filings**: MCA forms, Financial statements
- [ ] **Board Meetings**: Required annually
- [ ] **GST Registration** (if turnover > ₹20 Lakhs)

**Next Step:** Would you like the OPC incorporation process details?"""
        
        else:
            return f"""### Business Licenses for {profile.get('entity_type', 'Your Business')}:

**Basic Requirements:**
- [ ] **Shop & Establishment Act Registration** (mandatory)
- [ ] **PAN Card** (if not already obtained)
- [ ] **Business Bank Account**

**Industry-Specific:**
Please check with local authorities for {profile.get('industry', 'your industry')} specific requirements.

**Next Step:** Would you like help with PAN card application process?"""
    
    def _handle_tax_query_fast(self, message, profile):
        """Fast tax query with accurate information"""
        entity_type = profile.get("entity_type", "").lower()
        
        if "sole proprietor" in entity_type:
            return """### Tax Requirements for Sole Proprietorship:

**Income Tax:**
- Tax Rate: Individual slabs (0% to 30%)
- Due Date: 31st July (individuals)
- Penalty: ₹5,000 for late filing

**GST:**
- Threshold: ₹20 Lakhs (services) / ₹40 Lakhs (goods)
- Registration: Free if turnover below threshold

**TDS:**
- Applicable if: Rent > ₹50,000/month or Professional fees > ₹30,000
- Rate: 10% for rent and professional fees

**Next Step:** Would you like the GST registration process?"""
        
        elif "private limited" in entity_type or "company" in entity_type:
            return """### Tax Requirements for Private Limited Company:

**Income Tax:**
- Tax Rate: 25% (up to ₹400 Cr turnover) / 22% (new companies)
- Due Date: 30th September
- Mandatory: Statutory audit required

**GST:**
- Threshold: ₹20 Lakhs (services) / ₹40 Lakhs (goods)
- Registration: Mandatory for companies

**TDS:**
- Rate: 1% (individual contractors) / 2% (companies)
- Due Date: 7th of next month

**Next Step:** Need help with company incorporation process?"""
        
        elif "llp" in entity_type or "partnership" in entity_type:
            return """### Tax & Compliance Filings for LLP:

**1. MCA Filings (Ministry of Corporate Affairs):**
- [ ] **Form 11 (Annual Return):** Due 30th May.
  - *Penalty:* ₹100 per day of delay (No upper limit!).
- [ ] **Form 8 (Account & Solvency):** Due 30th October.
  - *Penalty:* ₹100 per day of delay.

**2. Income Tax:**
- [ ] **ITR-5:** Due 31st July (if no audit) or 31st October (if audit required).
- *Audit Applicability:* If turnover > ₹40 Lakhs or Contribution > ₹25 Lakhs.

**3. GST (If registered):**
- [ ] **GSTR-1 & 3B:** Monthly returns (11th & 20th).

**Next Step:** Would you like to check if your LLP needs a mandatory audit?"""
        
        else:
            return f"""### Tax Information for {profile.get('entity_type', 'Your Business')}:

**Key Points:**
- Consult a tax professional for specific advice
- Maintain proper bookkeeping
- File returns on time to avoid penalties
- Consider tax planning for savings

**Common Deadlines:**
- Income Tax: 31st July (individuals)
- GST Returns: 20th of next month
- TDS Returns: 7th of next month

**Next Step:** Would you like tax planning tips?"""
    
    def _handle_deadline_query_fast(self, message, profile):
        """Fast deadline information"""
        return """### Important Compliance Deadlines:

**Monthly:**
- [ ] **GST Return GSTR-1** - 11th of next month
- [ ] **GST Return GSTR-3B** - 20th of next month
- [ ] **TDS Return** - 7th of next month

**Quarterly:**
- [ ] **TDS Return** - 31st of quarter end

**Annual:**
- [ ] **Income Tax Return** - 31st July (individuals)
- [ ] **GST Annual Return** - 31st December
- [ ] **Shop License Renewal** - Before expiry date

**Penalties:**
- GST: ₹50 per day delay
- TDS: ₹200 per day delay
- Income Tax: ₹5,000 for late filing

**Next Step:** Would you like a personalized deadline calendar for your business?"""
    
    def _handle_compliance_status_fast(self, profile):
        """Fast compliance status check"""
        return f"""### Compliance Status for Your Business:

**Business Profile:**
- Type: {profile.get('entity_type', 'Not specified')}
- Industry: {profile.get('industry', 'Not specified')}
- Location: {profile.get('location', 'Not specified')}

**Priority Actions:**
1. **Complete Business Registration** (if not done)
2. **Obtain Shop & Establishment License**
3. **Register for GST** (if applicable)
4. **Open Business Bank Account**
5. **Maintain Proper Records**

**Compliance Score:** Setup Phase (0-25%)

**Next Steps:**
- Focus on mandatory registrations first
- Set up accounting system
- Create compliance calendar

**Next Step:** Would you like a detailed compliance checklist?"""
    
    def _handle_startup_guide_fast(self, profile):
        """Fast startup guidance"""
        return """### Quick Startup Guide:

**Phase 1: Basic Setup (Week 1-2)**
- [ ] Register business name
- [ ] Get PAN card (if needed)
- [ ] Open business bank account
- [ ] Register for Shop & Establishment Act

**Phase 2: Tax Registration (Week 2-3)**
- [ ] GST registration (if turnover > threshold)
- [ ] TAN registration (if required)
- [ ] Professional tax registration

**Phase 3: Industry Licenses (Week 3-6)**
- [ ] Industry-specific licenses
- [ ] Municipal permits
- [ ] Safety registrations

**Phase 4: Ongoing Compliance**
- [ ] Monthly GST returns
- [ ] Quarterly TDS returns
- [ ] Annual compliance filings

**Next Step:** Which phase would you like detailed guidance for?"""
    
    def _provide_general_guidance_fast(self, message, profile):
        """Fast general guidance"""
        return f"""### Business Compliance Guidance:

**For {profile.get('entity_type', 'Your Business')} in {profile.get('industry', 'Your Industry')}:

**Immediate Actions:**
1. **Business Registration** - Complete legal formalities
2. **Tax Registration** - GST, PAN, TAN as applicable
3. **Bank Account** - Separate business account
4. **Licenses** - Industry-specific permits

**Common Requirements:**
- Shop & Establishment Act (most businesses)
- GST (if turnover exceeds threshold)
- Professional tax (some states)
- Industry licenses (varies by sector)

**Timeline:** Most registrations take 2-4 weeks

**Cost:** ₹1,000-10,000 for basic setup

**Next Step:** Would you like specific guidance for any of these areas?"""
    
    # Keep the existing detailed methods as fallbacks
    def _handle_license_query(self, message, profile):
        """Handle license-related queries"""
        licenses = self.knowledge_retriever.search_licenses(
            profile["industry"], 
            profile["entity_type"], 
            profile["location"]
        )
        
        if not licenses:
            return "I couldn't find specific license requirements for your business type. Please consult with a local compliance expert."
        
        response = f"### Required Licenses for {profile['entity_type']} in {profile['industry']}:\n\n"
        
        mandatory_licenses = [l for l in licenses if l.get("mandatory", False)]
        optional_licenses = [l for l in licenses if not l.get("mandatory", False)]
        
        if mandatory_licenses:
            response += "**Mandatory Licenses:**\n"
            for license in mandatory_licenses:
                response += f"- [ ] **{license['name']}**\n"
                response += f"  - {license.get('description', '')}\n"
                if license.get('documents'):
                    response += f"  - Documents: {', '.join(license['documents'])}\n"
                if license.get('timeline'):
                    response += f"  - Timeline: {license.get('timeline', 'N/A')}\n"
                if license.get('cost'):
                    response += f"  - Cost: {license.get('cost', 'N/A')}\n"
                response += "\n"
        
        if optional_licenses:
            response += "**Optional Registrations:**\n"
            for license in optional_licenses:
                response += f"- [ ] **{license['name']}**\n"
                response += f"  - {license.get('description', '')}\n"
                response += "\n"
        
        response += "\n**Next Step:** Would you like me to explain the application process for any of these licenses?"
        
        return response
    
    def _handle_tax_query(self, message, profile):
        """Handle tax-related queries"""
        tax_info = self.knowledge_retriever.get_tax_info(profile["entity_type"])
        
        if not tax_info:
            return "I couldn't find specific tax information for your business type. Please consult with a tax professional."
        
        response = f"### Tax Requirements for {profile['entity_type']}:\n\n"
        
        if "gst_threshold" in tax_info:
            response += f"**GST Registration Threshold:** {tax_info['gst_threshold']}\n\n"
        
        if "income_tax" in tax_info:
            response += f"**Income Tax:** {tax_info['income_tax']}\n\n"
        
        if "tds_applicability" in tax_info:
            response += f"**TDS Applicability:** {tax_info['tds_applicability']}\n\n"
        
        response += "**Next Step:** Would you like to know about the tax filing deadlines?"
        
        return response
    
    def _handle_deadline_query(self, message, profile):
        """Handle deadline queries"""
        deadlines = self.knowledge_retriever.get_deadlines()
        
        if not deadlines:
            return "I couldn't find specific deadline information. Please check with your compliance advisor."
        
        response = "### Important Compliance Deadlines:\n\n"
        
        for period, items in deadlines.items():
            response += f"**{period.title()} Deadlines:**\n"
            for item in items:
                response += f"- [ ] **{item['name']}** - **{item['date']}**\n"
                response += f"  - Penalty: {item.get('penalty', 'N/A')}\n"
            response += "\n"
        
        return response
    
    def _handle_compliance_status(self, profile):
        """Handle compliance status queries"""
        licenses = self.knowledge_retriever.search_licenses(
            profile["industry"], 
            profile["entity_type"], 
            profile["location"]
        )
        
        mandatory_count = len([l for l in licenses if l.get("mandatory", False)])
        total_count = len(licenses)
        
        response = f"### Compliance Status for {profile.get('business_name', 'Your Business')}\n\n"
        response += f"**Business Type:** {profile['entity_type']}\n"
        response += f"**Industry:** {profile['industry']}\n"
        response += f"**Location:** {profile['location']}\n\n"
        
        response += f"**Required Items:** {mandatory_count} mandatory, {total_count - mandatory_count} optional\n\n"
        
        response += "**Next Steps:**\n"
        response += "1. Complete all mandatory registrations\n"
        response += "2. Set up tax registrations\n"
        response += "3. Apply for required licenses\n"
        response += "4. Set up compliance calendar\n\n"
        
        response += "**Would you like me to create a detailed compliance checklist for your business?**"
        
        return response
    
    def _provide_general_guidance(self, message, profile):
        """Provide general compliance guidance"""
        response = "### Business Compliance Guidance\n\n"
        
        response += f"Based on your {profile['entity_type']} in the {profile['industry']} industry, here are the key areas to focus on:\n\n"
        
        response += "**Priority 1: Basic Registrations**\n"
        response += "- Business name registration\n"
        response += "- Tax registrations (PAN, GST if applicable)\n"
        response += "- Shop & Establishment Act registration\n\n"
        
        response += "**Priority 2: Industry-Specific Licenses**\n"
        response += "- Check if your industry requires special permits\n"
        response += "- Professional certifications if applicable\n\n"
        
        response += "**Priority 3: Ongoing Compliance**\n"
        response += "- Monthly/Quarterly tax filings\n"
        response += "- Annual returns\n"
        response += "- License renewals\n\n"
        
        response += "**Next Step:** Would you like specific details about any of these areas?"
        
        return response

# Placeholder ComplianceEngine class
class ComplianceEngine:
    """Simple placeholder for ComplianceEngine"""
    def __init__(self):
        self.initialized = True
        self.profiles = {}  # Simple in-memory storage
    
    def get_requirements(self, business_type, jurisdiction):
        """Get compliance requirements for business type and jurisdiction"""
        return []
    
    def check_compliance(self, business_profile):
        """Check compliance status for a business profile"""
        return {"status": "compliant", "issues": []}
    
    def get_business_profile(self, business_id):
        """Get business profile by ID"""
        return self.profiles.get(business_id, None)
    
    def save_business_profile(self, business_id, profile):
        """Save business profile"""
        self.profiles[business_id] = profile
        return profile

def load_modern_css():
    """Load modern, ChatGPT-style CSS"""
    st.markdown("""
    <style>
    /* Modern UI Tokens */
    :root {
        --primary: #2563EB;
        --primary-dark: #1D4ED8;
        --background: #FFFFFF;
        --surface: #FFFFFF;
        --text-primary: #1C1C1C;
        --text-secondary: #6B7280;
        --border: #E5E7EB;
        --sidebar-bg: #F8F9FA;
        --shadow: 0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24);
        --shadow-lg: 0 10px 40px rgba(0,0,0,0.15);
        --radius: 12px;
        --radius-sm: 8px;
    }
    
    /* Global Typography & Spacing */
    body {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif !important;
        font-size: 15px !important;
        line-height: 1.6 !important;
        color: var(--text-primary) !important;
        background-color: #FFFFFF !important;
    }
    
    .stApp {
        background-color: #FFFFFF !important;
    }
    
    /* Modern Sidebar */
    .css-1d391kg {
        background-color: var(--sidebar-bg) !important;
        border-right: 1px solid var(--border) !important;
        width: 300px !important;
        min-width: 300px !important;
        max-width: 300px !important;
        box-shadow: var(--shadow) !important;
    }
    
    /* Modern Header */
    .css-1d391kg .sidebar-header,
    div[data-testid="stSidebar"] .sidebar-header {
        padding: 24px 20px !important;
        margin: 0 !important;
        border-bottom: 1px solid var(--border) !important;
        background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%) !important;
    }
    
    .css-1d391kg .sidebar-header h1,
    .css-1d391kg .sidebar-header p,
    div[data-testid="stSidebar"] .sidebar-header h1,
    div[data-testid="stSidebar"] .sidebar-header p {
        color: #FFFFFF !important;
        margin: 0 !important;
        opacity: 1 !important;
        visibility: visible !important;
        display: block !important;
        font-weight: 600 !important;
        text-shadow: none !important;
        filter: none !important;
        -webkit-text-fill-color: #FFFFFF !important;
    }
    
    .css-1d391kg .sidebar-header h1 {
        font-size: 18px !important;
        margin-bottom: 4px !important;
    }
    
    .css-1d391kg .sidebar-header p {
        font-size: 13px !important;
        opacity: 0.9 !important;
        font-weight: 400 !important;
    }
    
    /* Modern Sidebar Sections - DARK THEME */
    .sidebar-section {
        background-color: #2F2F2F !important;
        border: 1px solid #404040 !important;
        border-radius: var(--radius-sm) !important;
        padding: 16px !important;
        margin: 12px 16px !important;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05) !important;
    }
    
    .sidebar-section-title {
        font-size: 11px !important;
        font-weight: 600 !important;
        color: var(--text-secondary) !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
        margin-bottom: 12px !important;
        padding-bottom: 8px !important;
        border-bottom: 1px solid var(--border) !important;
    }
    
    /* Modern Conversation Buttons */
    .css-1d391kg button[kind="secondary"] {
        background-color: transparent !important;
        color: var(--text-primary) !important;
        border: 1px solid transparent !important;
        text-align: left !important;
        justify-content: flex-start !important;
        padding: 12px 16px !important;
        margin-bottom: 2px !important;
        font-size: 14px !important;
        font-weight: 400 !important;
        border-radius: var(--radius-sm) !important;
        width: 100% !important;
        box-sizing: border-box !important;
        transition: all 0.2s ease !important;
    }
    
    .css-1d391kg button[kind="secondary"]:hover {
        background-color: var(--background) !important;
        color: var(--primary) !important;
        transform: translateX(2px) !important;
    }
    
    /* Modern Primary Buttons */
    .css-1d391kg .stButton > button[kind="primary"],
    .css-1d391kg button:not([kind="secondary"]) {
        background-color: var(--primary) !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: var(--radius-sm) !important;
        padding: 12px 16px !important;
        font-size: 14px !important;
        font-weight: 500 !important;
        margin: 0 !important;
        width: 100% !important;
        box-sizing: border-box !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 2px 4px rgba(37, 99, 235, 0.2) !important;
    }
    
    .css-1d391kg .stButton > button[kind="primary"]:hover,
    .css-1d391kg button:not([kind="secondary"]):hover {
        background-color: var(--primary-dark) !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 8px rgba(37, 99, 235, 0.3) !important;
    }
    
    /* Modern Form Elements */
    .css-1d391kg .stTextInput > div > div > input,
    .css-1d391kg .stSelectbox > div > div > select {
        background-color: var(--surface) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius-sm) !important;
        padding: 8px 12px !important;
        font-size: 13px !important;
        width: 100% !important;
        box-sizing: border-box !important;
        transition: all 0.2s ease !important;
        color: var(--text-primary) !important;
        margin-bottom: 8px !important;
    }
    
    .css-1d391kg .stTextInput > div > div > input:focus,
    .css-1d391kg .stSelectbox > div > div > select:focus {
        border-color: var(--primary) !important;
        box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.1) !important;
        outline: none !important;
    }
    
    /* Remove empty white spaces from forms */
    .css-1d391kg .stForm {
        border: none !important;
        background-color: transparent !important;
        padding: 0 !important;
        margin: 0 !important;
    }
    
    .css-1d391kg .stForm > div {
        background-color: transparent !important;
        padding: 0 !important;
        margin: 0 !important;
    }
    
    .css-1d391kg .stForm > div > div {
        background-color: transparent !important;
        padding: 0 !important;
        margin: 0 !important;
    }
    
    /* Fix form field containers */
    .css-1d391kg .stTextInput > div,
    .css-1d391kg .stSelectbox > div {
        background-color: transparent !important;
        border: none !important;
        padding: 0 !important;
        margin: 0 0 8px 0 !important;
    }
    
    .css-1d391kg .stTextInput > div > div,
    .css-1d391kg .stSelectbox > div > div {
        background-color: var(--surface) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius-sm) !important;
    }
    
    /* NUCLEAR: Remove ALL white backgrounds from sidebar forms */
    div[data-testid="stSidebar"] {
        background: var(--sidebar-bg) !important;
    }

    div[data-testid="stSidebar"] * {
        background-color: transparent !important;
        background: transparent !important;
    }

    /* Override all form containers */
    div[data-testid="stSidebar"] .stForm,
    div[data-testid="stSidebar"] .stForm > div,
    div[data-testid="stSidebar"] .stForm > div > div,
    div[data-testid="stSidebar"] .stForm > div > div > div {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        padding: 0 !important;
        margin: 0 !important;
    }

    /* Override all element containers - REMOVE EMPTY BOXES */
    div[data-testid="stSidebar"] .element-container,
    div[data-testid="stSidebar"] .element-container > div,
    div[data-testid="stSidebar"] .element-container > div > div,
    div[data-testid="stSidebar"] .element-container:empty,
    div[data-testid="stSidebar"] .element-container > div:empty,
    div[data-testid="stSidebar"] .element-container > div > div:empty {
        background: transparent !important;
        border: none !important;
        padding: 0 !important;
        margin: 0 !important;
        display: none !important;
        visibility: hidden !important;
        height: 0 !important;
        width: 0 !important;
        overflow: hidden !important;
    }

    /* Override all Streamlit blocks - REMOVE EMPTY BOXES */
    div[data-testid="stSidebar"] [data-testid="stVerticalBlock"],
    div[data-testid="stSidebar"] [data-testid="stVerticalBlock"] > div,
    div[data-testid="stSidebar"] [data-testid="stVerticalBlockBorderWrapper"],
    div[data-testid="stSidebar"] [data-testid="stVerticalBlock"]:empty,
    div[data-testid="stSidebar"] [data-testid="stVerticalBlock"] > div:empty {
        background: transparent !important;
        border: none !important;
        padding: 0 !important;
        margin: 0 !important;
        display: none !important;
        visibility: hidden !important;
        height: 0 !important;
        width: 0 !important;
        overflow: hidden !important;
    }

    /* Remove any empty divs in sidebar */
    div[data-testid="stSidebar"] div:empty {
        display: none !important;
        visibility: hidden !important;
        height: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
    }

    /* Target specific empty containers */
    div[data-testid="stSidebar"] div[style*="background"],
    div[data-testid="stSidebar"] div[style*="background-color"] {
        background: transparent !important;
        background-color: transparent !important;
    }

    /* Text Input fixes - REMOVE ALL WHITE BOXES */
    div[data-testid="stSidebar"] .stTextInput {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        padding: 0 !important;
        margin: 0 0 8px 0 !important;
    }

    div[data-testid="stSidebar"] .stTextInput > div {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        padding: 0 !important;
        margin: 0 !important;
    }

    div[data-testid="stSidebar"] .stTextInput > div > div {
        background: var(--surface) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius-sm) !important;
        box-shadow: none !important;
        padding: 0 !important;
        margin: 0 !important;
    }

    div[data-testid="stSidebar"] .stTextInput > div > div > input {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        color: var(--text-primary) !important;
        padding: 8px 12px !important;
    }

    /* Selectbox fixes - REMOVE ALL WHITE BOXES */
    div[data-testid="stSidebar"] .stSelectbox {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        padding: 0 !important;
        margin: 0 0 8px 0 !important;
    }

    div[data-testid="stSidebar"] .stSelectbox > div {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        padding: 0 !important;
        margin: 0 !important;
    }

    div[data-testid="stSidebar"] .stSelectbox > div > div {
        background: var(--surface) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius-sm) !important;
        box-shadow: none !important;
        padding: 0 !important;
        margin: 0 !important;
    }

    div[data-testid="stSidebar"] .stSelectbox > div > div > select {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        color: var(--text-primary) !important;
        padding: 8px 12px !important;
    }

    /* Remove any remaining white elements */
    div[data-testid="stSidebar"] div[style*="background-color: rgb(255"],
    div[data-testid="stSidebar"] div[style*="background-color: #fff"],
    div[data-testid="stSidebar"] div[style*="background-color: white"],
    div[data-testid="stSidebar"] div[style*="background: rgb(255"],
    div[data-testid="stSidebar"] div[style*="background: #fff"],
    div[data-testid="stSidebar"] div[style*="background: white"],
    div[data-testid="stSidebar"] div[style*="background-color: rgba(255"],
    div[data-testid="stSidebar"] div[style*="background: rgba(255"] {
        background-color: transparent !important;
        background: transparent !important;
    }

    /* Remove any remaining white elements */
    div[data-testid="stSidebar"] div[style*="background-color: rgb(255"],
    div[data-testid="stSidebar"] div[style*="background-color: #fff"],
    div[data-testid="stSidebar"] div[style*="background-color: white"],
    div[data-testid="stSidebar"] div[style*="background: rgb(255"],
    div[data-testid="stSidebar"] div[style*="background: #fff"],
    div[data-testid="stSidebar"] div[style*="background: white"],
    div[data-testid="stSidebar"] div[style*="background-color: rgba(255"],
    div[data-testid="stSidebar"] div[style*="background: rgba(255"] {
        background-color: transparent !important;
        background: transparent !important;
    }
    
    /* Modern Stats Grid */
    .stats-grid {
        display: grid !important;
        grid-template-columns: 1fr 1fr !important;
        gap: 8px !important;
        width: 100% !important;
    }
    
    .stat-item {
        background-color: #262626 !important;
        padding: 12px !important;
        border-radius: var(--radius-sm) !important;
        text-align: center !important;
        border: 1px solid #404040 !important;
        transition: all 0.2s ease !important;
    }
    
    .stat-item:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2) !important;
    }
    
    .stat-value {
        font-size: 16px !important;
        font-weight: 600 !important;
        color: var(--primary) !important;
        margin-bottom: 2px !important;
    }
    
    .stat-label {
        font-size: 11px !important;
        color: var(--text-secondary) !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
    }
    
    /* Modern Main Content */
    .main .block-container {
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
        max-width: 900px !important;
        margin: 0 auto !important;
    }
    
    /* Modern Header Bar - WHITE THEME */
    .main-header {
        background-color: #FFFFFF !important;
        border: 1px solid #E5E7EB !important;
        border-radius: var(--radius) !important;
        padding: 20px 24px !important;
        margin-bottom: 24px !important;
        box-shadow: 0 1px 2px rgba(0,0,0,0.1) !important;
    }
    
    .main-header h1 {
        font-size: 24px !important;
        font-weight: 700 !important;
        color: var(--text-primary) !important;
        margin: 0 !important;
    }
    
    .main-header p {
        font-size: 14px !important;
        color: var(--text-secondary) !important;
        margin: 4px 0 0 0 !important;
        font-weight: 400 !important;
    }
    
    /* Modern Message Bubbles - ChatGPT Style */
    .user-message {
        background-color: var(--primary) !important;
        color: #FFFFFF !important;
        padding: 12px 16px !important;
        border-radius: var(--radius-sm) !important;
        margin: 8px 0 8px auto !important;
        max-width: 80% !important;
        box-shadow: var(--shadow) !important;
        font-size: 14px !important;
        line-height: 1.5 !important;
    }
    
    .assistant-message {
        background-color: #FFFFFF !important;
        color: var(--text-primary) !important;
        padding: 12px 16px !important;
        border-radius: var(--radius-sm) !important;
        margin: 8px auto 8px 0 !important;
        max-width: 80% !important;
        border: 1px solid var(--border) !important;
        font-size: 14px !important;
        line-height: 1.5 !important;
    }
    
    /* Remove "You:" and "Assistant:" labels */
    .user-message strong:first-child,
    .assistant-message strong:first-child {
        display: none !important;
    }
    
    /* Modern Metrics - WHITE BACKGROUND */
    .metric-box {
        background-color: #FFFFFF !important;
        border: 1px solid #E5E7EB !important;
        border-radius: var(--radius-sm) !important;
        padding: 20px !important;
        text-align: center !important;
        box-shadow: 0 1px 2px rgba(0,0,0,0.1) !important;
        transition: all 0.2s ease !important;
    }
    
    .metric-box:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2) !important;
    }
    
    .metric-value {
        font-size: 24px !important;
        font-weight: 700 !important;
        color: #1C1C1C !important;
        margin-bottom: 4px !important;
    }
    
    .metric-label {
        font-size: 12px !important;
        color: #6B7280 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
        font-weight: 600 !important;
    }
    
    .metric-trend {
        font-size: 11px !important;
        margin-top: 4px !important;
        font-weight: 500 !important;
    }
    
    .metric-trend.positive {
        color: #10B981 !important;
    }
    
    .metric-trend.negative {
        color: #EF4444 !important;
    }
    
    /* Modern Quick Actions - WHITE THEME */
    .quick-actions {
        background-color: #FFFFFF !important;
        border: 1px solid #E5E7EB !important;
        border-radius: var(--radius) !important;
        padding: 24px !important;
        margin: 24px 0 !important;
        box-shadow: 0 1px 2px rgba(0,0,0,0.1) !important;
    }
    
    .quick-actions h3 {
        font-size: 18px !important;
        font-weight: 600 !important;
        color: var(--text-primary) !important;
        margin: 0 0 8px 0 !important;
    }
    
    .quick-actions p {
        font-size: 14px !important;
        color: var(--text-secondary) !important;
        margin-bottom: 20px !important;
        line-height: 1.5 !important;
    }
    
    /* Modern Chat Input */
    .stChatInput > div > div > textarea {
        border-radius: var(--radius) !important;
        border: 1px solid var(--border) !important;
        background-color: var(--surface) !important;
        padding: 12px 16px !important;
        font-size: 14px !important;
        resize: none !important;
    }
    
    .stChatInput > div > div > textarea:focus {
        border-color: var(--primary) !important;
        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1) !important;
    }
    
    /* Micro-animations */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .user-message, .assistant-message {
        animation: fadeIn 0.3s ease-out !important;
    }
    
    /* Responsive Design */
    @media (max-width: 768px) {
        .css-1d391kg {
            width: 280px !important;
            min-width: 280px !important;
            max-width: 280px !important;
        }
        
        .main .block-container {
            padding: 1rem !important;
        }
        
        .user-message, .assistant-message {
            max-width: 90% !important;
        }
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
        # Compact form with no empty spaces
        st.markdown("""
        <style>
        /* NUCLEAR OPTION: Remove ALL backgrounds from sidebar forms */
        div[data-testid="stSidebar"] .stForm,
        div[data-testid="stSidebar"] .stForm > div,
        div[data-testid="stSidebar"] .stForm > div > div,
        div[data-testid="stSidebar"] .stForm > div > div > div,
        div[data-testid="stSidebar"] .element-container,
        div[data-testid="stSidebar"] .element-container > div,
        div[data-testid="stSidebar"] .element-container > div > div,
        div[data-testid="stSidebar"] [data-testid="stVerticalBlock"],
        div[data-testid="stSidebar"] [data-testid="stVerticalBlock"] > div,
        div[data-testid="stSidebar"] [data-testid="stVerticalBlockBorderWrapper"] {
            background: transparent !important;
            background-color: transparent !important;
            border: none !important;
            box-shadow: none !important;
            padding: 0 !important;
            margin: 0 !important;
        }
        
        /* Force remove any white backgrounds */
        div[data-testid="stSidebar"] div[style*="background"] {
            background: transparent !important;
            background-color: transparent !important;
        }
        
        /* Only keep input field styling */
        div[data-testid="stSidebar"] .stTextInput > div > div,
        div[data-testid="stSidebar"] .stSelectbox > div > div {
            background: var(--surface) !important;
            border: 1px solid var(--border) !important;
            border-radius: var(--radius-sm) !important;
            margin: 0 0 8px 0 !important;
        }
        
        div[data-testid="stSidebar"] input,
        div[data-testid="stSidebar"] select {
            background: transparent !important;
            border: none !important;
            color: var(--text-primary) !important;
        }
        </style>
        """, unsafe_allow_html=True)
        
        with st.form("business_profile_form", clear_on_submit=False):
            name = st.text_input("Business name", key="biz_name")
            business_type = st.selectbox(
                "Business type",
                [bt.value for bt in BusinessType],
                index=0,
                key="biz_type"
            )
            jurisdiction = st.selectbox(
                "Jurisdiction",
                [j.value for j in Jurisdiction],
                index=0,
                key="biz_jurisdiction"
            )
            registration_number = st.text_input("Registration number", key="biz_reg")
            
            submitted = st.form_submit_button("Save", use_container_width=True)
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
        if st.button("Edit business profile", use_container_width=True):
            del st.session_state['business_id']
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

def handle_send_message(content):
    """Handle sending a message with RAG chatbot integration"""
    if not st.session_state.active_conversation_id:
        return
    
    # Initialize conversation state if not exists
    if 'conversation_state' not in st.session_state:
        st.session_state.conversation_state = ConversationState()
        st.session_state.chatbot = ComplianceChatbot()
    
    # Get response mode from session state
    response_mode = st.session_state.get('response_mode', 'simple')
    
    # Get the current conversation
    conv = None
    for c in st.session_state.conversations:
        if c["id"] == st.session_state.active_conversation_id:
            conv = c
            break
    
    if not conv:
        return
    
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
    
    # Process message with RAG chatbot
    try:
        chatbot_response = st.session_state.chatbot.process_message(
            content, 
            st.session_state.conversation_state,
            response_mode=response_mode
        )
        
        # Add assistant response
        assistant_message = {
            "id": str(int(datetime.now().timestamp()) + 1),
            "content": chatbot_response,
            "is_user": False,
            "timestamp": datetime.now()
        }
        conv["messages"].append(assistant_message)
        conv["message_count"] += 1
        
    except Exception as e:
        # Fallback response if chatbot fails
        error_message = {
            "id": str(int(datetime.now().timestamp()) + 1),
            "content": f"I apologize, but I encountered an error: {str(e)}. Please try rephrasing your question.",
            "is_user": False,
            "timestamp": datetime.now()
        }
        conv["messages"].append(error_message)
        conv["message_count"] += 1
    
    # Update conversation state in session
    st.session_state.conversation_state = st.session_state.conversation_state

def process_pending_request():
    """Process pending chat request after rerun"""
    if st.session_state.get("pending_request") and not st.session_state.get("is_processing"):
        request = st.session_state.pending_request
        st.session_state.pending_request = None
        
        try:
            # Call backend API
            response = requests.post(
                "http://localhost:8000/api/v1/chatbot/chat",
                json={
                    "query": request["query"],
                    "mode": request["mode"],
                    "business_id": request["business_id"],
                    "conversation_id": request["conversation_id"]
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                ai_message = {
                    "id": str(int(datetime.now().timestamp())),
                    "content": data.get("response", "Sorry, I couldn't process that request."),
                    "is_user": False,
                    "timestamp": datetime.now()
                }
                request["conv"]["messages"].append(ai_message)
                request["conv"]["message_count"] += 1
                
                # Store backend conversation ID if available
                if data.get("conversation_id"):
                    request["conv"]["backend_id"] = data["conversation_id"]
            else:
                error_message = {
                    "id": str(int(datetime.now().timestamp())),
                    "content": f"Error: {response.status_code} - {response.text}",
                    "is_user": False,
                    "timestamp": datetime.now()
                }
                request["conv"]["messages"].append(error_message)
                
        except Exception as e:
            error_message = {
                "id": str(int(datetime.now().timestamp())),
                "content": f"Connection error: {str(e)}",
                "is_user": False,
                "timestamp": datetime.now()
            }
            request["conv"]["messages"].append(error_message)
        
        st.rerun()

def create_new_conversation():
    """Create a new conversation"""
    new_conv = {
        "id": str(int(datetime.now().timestamp())),
        "title": "New Conversation",
        "timestamp": datetime.now(),
        "message_count": 0,
        "messages": [],
        "backend_id": None
    }
    st.session_state.conversations.insert(0, new_conv)
    st.session_state.active_conversation_id = new_conv["id"]
    st.rerun()

def main():
    """Main application with modern ChatGPT-style UI"""
    load_modern_css()
    
    # Page configuration
    st.set_page_config(
        page_title="BizComply AI",
        page_icon="🏢",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize session state
    if 'conversations' not in st.session_state:
        st.session_state.conversations = []
    
    if 'active_conversation_id' not in st.session_state:
        # Create initial conversation with onboarding
        create_new_conversation()
    
    if 'is_processing' not in st.session_state:
        st.session_state.is_processing = False
    
    if 'pending_request' not in st.session_state:
        st.session_state.pending_request = None
    
    if 'business_id' not in st.session_state:
        st.session_state.business_id = None
    
    # Initialize RAG chatbot components
    if 'conversation_state' not in st.session_state:
        st.session_state.conversation_state = ConversationState()
        st.session_state.chatbot = ComplianceChatbot()
        
        # Add welcome message to first conversation
        if st.session_state.conversations:
            first_conv = st.session_state.conversations[0]
            if not first_conv.get("messages"):
                welcome_message = {
                    "id": "0",
                    "content": "👋 Welcome to BizComply AI! I'm your expert Business Compliance Assistant for India.\n\nTo provide you with accurate compliance guidance, I need to understand your business first. Let me ask you a few quick questions:\n\n### Where is your business located? (City/State)\n\n- Delhi\n- Mumbai\n- Bangalore\n- Hyderabad\n- Chennai\n- Other\n\nPlease select one option or type your answer.",
                    "is_user": False,
                    "timestamp": datetime.now()
                }
                first_conv["messages"].append(welcome_message)
                first_conv["message_count"] = 1
                first_conv["title"] = "Business Compliance Setup"
    
    # Process any pending requests
    process_pending_request()
    
    # Get active conversation
    active_conversation = next(
        (conv for conv in st.session_state.conversations if conv["id"] == st.session_state.active_conversation_id),
        None
    )
    
    # Render modern sidebar
    with st.sidebar:
        # Modern Header
        st.markdown("""
        <div class="sidebar-header">
            <h1>🏢 BizComply AI</h1>
            <p>Professional Compliance Assistant</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Business Profile Section
        render_business_profile_section()
        
        # Response Mode Section
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown('<div class="sidebar-section-title">Response Mode</div>', unsafe_allow_html=True)
        
        # Initialize response mode in session state
        if 'response_mode' not in st.session_state:
            st.session_state.response_mode = DEFAULT_RESPONSE_MODE
        
        response_mode = st.selectbox(
            "Choose response style:",
            options=["concise", "simple", "detailed"],
            index=["concise", "simple", "detailed"].index(st.session_state.response_mode),
            key="response_mode_selector",
            help="Concise: Short answers\nSimple: Standard responses\nDetailed: In-depth explanations"
        )
        
        st.session_state.response_mode = response_mode
        st.markdown('</div>', unsafe_allow_html=True)
        
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
    
    # Main content area
    # Modern Header
    st.markdown("""
    <div class="main-header">
        <h1>🏢 BizComply AI</h1>
        <p>Professional Compliance Assistant</p>
    </div>
    """, unsafe_allow_html=True)
    
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
        </div>
        """, unsafe_allow_html=True)
        
        # Modern quick action buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📋 GDPR Requirements", key="gdpr_btn"):
                handle_send_message("What are the key GDPR compliance requirements for my business?")
                st.rerun()
            if st.button("💰 Financial Compliance", key="financial_btn"):
                handle_send_message("What are the main financial compliance requirements?")
                st.rerun()
        
        with col2:
            if st.button("🏆 Industry Certifications", key="cert_btn"):
                handle_send_message("What industry certifications should I consider?")
                st.rerun()
            if st.button("🔍 Compliance Audit", key="audit_btn"):
                handle_send_message("How do I conduct a compliance audit?")
                st.rerun()
    
    # Modern Chat Input
    prompt = st.chat_input("Ask about compliance, regulations, or your business requirements...")
    if prompt:
        # If no active conversation, create one first
        if not active_conversation:
            create_new_conversation()
            # Re-fetch the conversation object after creation
            active_conversation = next((c for c in st.session_state.conversations if c["id"] == st.session_state.active_conversation_id), None)
        
        if active_conversation:
            handle_send_message(prompt)
            # CRITICAL FIX: Rerun the app to display the new message immediately
            st.rerun()
        else:
            st.error("Unable to create conversation. Please try again.")

if __name__ == "__main__":
    main()

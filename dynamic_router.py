"""
Dynamic Semantic Router for Compliance Chatbot
Replaces manual keyword matching with intelligent LLM-powered routing
"""

import os
from typing import Dict, Any, List
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from config.config import OPENAI_API_KEY, GROQ_API_KEY, LLM_PROVIDER
from utils.web_search import WebSearch
from models.embeddings import EmbeddingProvider
from utils.document_processor import DocumentProcessor

class DynamicRouter:
    """
    Intelligent router that uses LLM to understand user intent
    and automatically selects the right tool/action
    """
    
    def __init__(self):
        # Initialize LLM for routing decisions
        if LLM_PROVIDER == "openai" and OPENAI_API_KEY:
            self.llm = ChatOpenAI(
                model="gpt-3.5-turbo",
                temperature=0,
                api_key=OPENAI_API_KEY
            )
        elif GROQ_API_KEY:
            from langchain_groq import ChatGroq
            self.llm = ChatGroq(
                model="llama-3.1-8b-instant",
                temperature=0,
                api_key=GROQ_API_KEY
            )
        else:
            raise ValueError("No valid LLM API key found")
        
        # Initialize tools
        self.web_search = WebSearch()
        try:
            self.embedding_model = EmbeddingProvider.get_embedding_model()
            self.document_processor = DocumentProcessor()
            self.rag_enabled = True
        except Exception as e:
            print(f"RAG initialization failed: {e}")
            self.rag_enabled = False
        
        # Define routing prompt
        self.router_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an intelligent compliance assistant router. Your job is to understand the user's intent and classify it into one of these categories:

1. **compliance_query** - The user is asking about business compliance, licenses, regulations, taxes, deadlines, or legal requirements
2. **general_chat** - The user is making general conversation, greetings, or asking non-compliance questions
3. **off_topic** - The user is asking about completely unrelated topics

User Profile Context: {profile_context}

Respond with ONLY the category name (compliance_query, general_chat, or off_topic)."""),
            ("human", "{user_message}")
        ])
        
        # Define compliance action prompt
        self.compliance_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are BizComply, an expert Business Compliance Assistant for India.

User Profile: {profile_context}

Your Rules:
1. Use the provided context to answer accurately
2. If context doesn't contain the answer, say so clearly
3. Be practical and actionable
4. Use bullet points and clear formatting
5. Always suggest the next logical step

Context:
{context}

Answer the user's question based on the context above."""),
            ("human", "{user_message}")
        ])
    
    def route_and_respond(self, user_message: str, user_profile: Dict[str, str]) -> str:
        """
        Main method that routes the request and generates response
        """
        try:
            # Step 1: Determine intent
            intent = self._classify_intent(user_message, user_profile)
            
            # Step 2: Route to appropriate handler
            if intent == "compliance_query":
                return self._handle_compliance_query(user_message, user_profile)
            elif intent == "general_chat":
                return self._handle_general_chat(user_message, user_profile)
            elif intent == "off_topic":
                return self._handle_off_topic(user_message, user_profile)
            else:
                return "I'm not sure how to help with that. Could you ask about business compliance instead?"
                
        except Exception as e:
            return f"⚠️ Router Error: {str(e)}"
    
    def _classify_intent(self, user_message: str, user_profile: Dict[str, str]) -> str:
        """
        Use LLM to classify user intent
        """
        profile_context = self._format_profile_context(user_profile)
        
        try:
            messages = self.router_prompt.format_messages(
                profile_context=profile_context,
                user_message=user_message
            )
            
            response = self.llm(messages)
            intent = response.content.strip().lower()
            
            # Validate intent
            valid_intents = ["compliance_query", "general_chat", "off_topic"]
            return intent if intent in valid_intents else "general_chat"
            
        except Exception as e:
            print(f"Intent classification error: {e}")
            return "general_chat"
    
    def _handle_compliance_query(self, user_message: str, user_profile: Dict[str, str]) -> str:
        """
        Handle compliance-related queries with RAG + Web Search
        """
        context_parts = []
        
        # Step 1: Search documents (RAG)
        if self.rag_enabled:
            try:
                doc_results = self._search_documents(user_message, k=3)
                if doc_results:
                    context_parts.append("Document Search Results:")
                    context_parts.extend([f"- {doc}" for doc in doc_results])
            except Exception as e:
                print(f"Document search error: {e}")
        
        # Step 2: Web search for current information
        try:
            web_results = self.web_search.search(user_message, num_results=2)
            if web_results:
                context_parts.append("\nCurrent Information (Web Search):")
                for result in web_results:
                    context_parts.append(f"- {result['title']}: {result['snippet']}")
        except Exception as e:
            print(f"Web search error: {e}")
        
        # Step 3: Generate response using LLM with context
        context = "\n".join(context_parts) if context_parts else "No specific information found. Please consult with a compliance expert."
        
        try:
            profile_context = self._format_profile_context(user_profile)
            messages = self.compliance_prompt.format_messages(
                profile_context=profile_context,
                context=context,
                user_message=user_message
            )
            
            response = self.llm(messages)
            return response.content
            
        except Exception as e:
            return f"⚠️ Response generation error: {str(e)}"
    
    def _handle_general_chat(self, user_message: str, user_profile: Dict[str, str]) -> str:
        """
        Handle general conversation
        """
        profile_context = self._format_profile_context(user_profile)
        
        general_prompt = ChatPromptTemplate.from_messages([
            ("system", f"""You are BizComply, a friendly compliance assistant.

User Profile: {profile_context}

Be helpful and conversational. If the user seems to be drifting toward compliance topics, gently guide them back."""),
            ("human", "{user_message}")
        ])
        
        try:
            messages = general_prompt.format_messages(user_message=user_message)
            response = self.llm(messages)
            return response.content
        except Exception as e:
            return "I'm here to help with business compliance questions. What would you like to know?"
    
    def _handle_off_topic(self, user_message: str, user_profile: Dict[str, str]) -> str:
        """
        Handle off-topic questions politely
        """
        return """I'm specifically designed to help with business compliance and regulatory guidance.

I can assist with:
- Business licenses and registrations
- Tax compliance requirements
- Legal deadlines and filings
- Industry-specific regulations
- Compliance best practices

Would you like to ask about any of these topics instead?"""
    
    def _search_documents(self, query: str, k: int = 3) -> List[str]:
        """
        Search documents using RAG embeddings
        """
        if not self.rag_enabled:
            return []
        
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.embed_query(query)
            
            # Search through documents
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
    
    def _format_profile_context(self, user_profile: Dict[str, str]) -> str:
        """
        Format user profile for LLM context
        """
        if not user_profile:
            return "No user profile available"
        
        context_parts = []
        for key, value in user_profile.items():
            if value:
                context_parts.append(f"{key.replace('_', ' ').title()}: {value}")
        
        return " | ".join(context_parts) if context_parts else "No user profile available"

# Streamlit Integration for Corrective RAG
# Replace your existing bot_engine import with this

import streamlit as st
from corrective_rag_engine_working import get_corrective_rag_answer

def display_corrective_rag_response(question: str):
    """
    Display the verified answer with citations and verification status
    """
    with st.spinner("🔍 Searching and verifying legal information..."):
        result = get_corrective_rag_answer(question)
    
    # Display verification status
    if result['verified']:
        st.success("✅ **Answer Verified**: This response has been checked for accuracy against the source documents.")
    else:
        st.warning("⚠️ **Verification Failed**: This response could not be fully verified. Please consult official sources.")
    
    # Display the answer
    st.markdown("### 📋 Legal Answer")
    st.markdown(result['answer'])
    
    # Display citations if available
    if result['citations']:
        st.markdown("### 📚 Sources & Citations")
        for i, citation in enumerate(result['citations'], 1):
            with st.expander(f"Source {citation['source_id']}"):
                st.markdown(f"**Quote:** {citation['quote']}")
                st.markdown(f"**Document:** {result['sources'][citation['source_id']-1] if citation['source_id']-1 < len(result['sources']) else 'Unknown'}")
    
    # Display verification details
    with st.expander("🔍 Verification Details"):
        st.markdown(f"- **Verification Status**: {'✅ Passed' if result['verified'] else '❌ Failed'}")
        st.markdown(f"- **Sources Used**: {len(result['citations'])}")
        st.markdown(f"- **Documents Searched**: {len(result['sources'])}")
        st.markdown("- **Method**: Hybrid Search (Keyword + Semantic) + Hallucination Detection")

# Usage in your Streamlit app:
# Replace your existing handle_send_message function with:
#
# def handle_send_message():
#     if user_input := st.session_state.user_input.strip():
#         # Add user message
#         st.session_state.messages.append({"role": "user", "content": user_input})
#         
#         # Get verified response
#         display_corrective_rag_response(user_input)
#         
#         # Clear input
#         st.session_state.user_input = ""

if __name__ == "__main__":
    # Quick test
    test_question = "What is the punishment for fraud under Section 447?"
    print(f"Testing: {test_question}")
    result = get_corrective_rag_answer(test_question)
    print(f"Verified: {result['verified']}")
    print(f"Answer: {result['answer'][:200]}...")

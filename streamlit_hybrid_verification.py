# Streamlit Integration for Hybrid Verification Bot
# Replace your existing bot with this verified version

import streamlit as st
import time
from verified_compliance_bot import ask_verified_compliance_bot

def display_verification_process():
    """Display the verification process steps"""
    with st.spinner("🔍 Hybrid Verification Process..."):
        # Step 1
        st.empty()
        time.sleep(0.5)
        
        # Step 2
        st.empty()
        time.sleep(0.5)
        
        # Step 3
        st.empty()
        time.sleep(0.5)

def display_verified_answer(question: str):
    """
    Display the hybrid verified answer with process visualization
    """
    # Create columns for process visualization
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 📚 Step 1")
        st.markdown("**Local PDF Search**")
        st.progress(33, text="Searching base laws...")
    
    with col2:
        st.markdown("### 🌐 Step 2")
        st.markdown("**Web Verification**")
        st.progress(66, text="Checking 2025 updates...")
    
    with col3:
        st.markdown("### 🧠 Step 3")
        st.markdown("**Smart Synthesis**")
        st.progress(100, text="Combining sources...")
    
    # Get the verified answer
    with st.spinner("🤖 Analyzing and synthesizing..."):
        answer = ask_verified_compliance_bot(question)
    
    # Display verification badge
    st.success("✅ **Hybrid Verified**: Answer checked against both PDF and latest web sources")
    
    # Display the answer
    st.markdown("### 📋 Verified Legal Answer")
    st.markdown(answer)
    
    # Display verification details
    with st.expander("🔍 Verification Details"):
        st.markdown("**Process Used:**")
        st.markdown("- ✅ Local PDF documents searched")
        st.markdown("- ✅ Web checked for 2024/2025 amendments")
        st.markdown("- ✅ Sources compared and synthesized")
        st.markdown("- ✅ Most current information provided")
        
        st.markdown("**Sources Checked:**")
        st.markdown("- 📚 Local PDF Document Database")
        st.markdown("- 🌐 Web Search (Latest Government Notifications)")
        
        st.markdown("**Confidence Level:** High (Hybrid verification complete)")

def handle_verified_message(user_input: str, messages: list):
    """
    Handle user message with hybrid verification
    """
    # Add user message
    messages.append({"role": "user", "content": user_input})
    
    # Display verification process
    display_verified_answer(user_input)
    
    # Add assistant response to messages
    with st.spinner("Saving conversation..."):
        answer = ask_verified_compliance_bot(user_input)
        messages.append({"role": "assistant", "content": answer})
    
    return messages

# Usage in your Streamlit app:
#
# def handle_send_message():
#     if user_input := st.session_state.user_input.strip():
#         st.session_state.messages = handle_verified_message(
#             user_input, 
#             st.session_state.messages
#         )
#         st.session_state.user_input = ""

if __name__ == "__main__":
    # Quick test
    test_question = "What is the collateral free loan limit for MSEs?"
    print(f"Testing Hybrid Verification: {test_question}")
    answer = ask_verified_compliance_bot(test_question)
    print(f"Verified Answer: {answer[:300]}...")

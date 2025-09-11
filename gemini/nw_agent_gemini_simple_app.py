"""
Simple Streamlit app for Google Gemini Water Assistant
Uses direct Google Generative AI without LangChain dependencies
"""

import streamlit as st
import os
import time
from typing import Optional

# Try to import the simple Gemini agent
try:
    from nw_agent_gemini_simple import SimpleWaterAgentGemini
    GEMINI_AVAILABLE = True
except ImportError as e:
    GEMINI_AVAILABLE = False
    IMPORT_ERROR = str(e)

def initialize_session_state():
    """Initialize Streamlit session state"""
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'agent' not in st.session_state:
        st.session_state.agent = None
    if 'agent_initialized' not in st.session_state:
        st.session_state.agent_initialized = False

def init_agent(api_key: str, model_name: str = "gemini-1.5-flash") -> bool:
    """Initialize the Gemini agent"""
    try:
        st.session_state.agent = SimpleWaterAgentGemini(
            google_api_key=api_key,
            model_name=model_name
        )
        st.session_state.agent_initialized = True
        return True
    except Exception as e:
        st.error(f"Failed to initialize agent: {str(e)}")
        return False

def main():
    st.set_page_config(
        page_title="Simple Gemini Water Assistant",
        page_icon="🌊",
        layout="wide"
    )
    
    st.title("🌊 Simple Gemini Water Assistant")
    st.markdown("*Guwahati Water Network Analysis powered by Google Gemini*")
    
    initialize_session_state()
    
    # Check if Gemini is available
    if not GEMINI_AVAILABLE:
        st.error("❌ Google Gemini integration not available")
        st.code(f"Import Error: {IMPORT_ERROR}")
        st.info("Please ensure all dependencies are installed correctly")
        return
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("🔧 Configuration")
        
        # API Key input
        api_key = st.text_input(
            "Google API Key",
            type="password",
            value=os.getenv('GOOGLE_API_KEY', ''),
            help="Get your API key from https://makersuite.google.com/app/apikey"
        )
        
        # Model selection
        model_name = st.selectbox(
            "Model",
            options=["gemini-1.5-flash", "gemini-1.5-pro", "gemini-pro"],
            index=0,
            help="Choose the Gemini model to use"
        )
        
        # Initialize agent button
        if st.button("Initialize Agent", type="primary"):
            if not api_key:
                st.error("Please provide a Google API key")
            else:
                with st.spinner("Initializing Gemini agent..."):
                    if init_agent(api_key, model_name):
                        st.success("Agent initialized successfully! 🎉")
                    else:
                        st.error("Failed to initialize agent")
        
        # Agent status
        if st.session_state.agent_initialized:
            st.success("✅ Agent Ready")
            st.info(f"Model: {model_name}")
        else:
            st.warning("⚠️ Agent not initialized")
        
        # Clear conversation
        if st.button("Clear Conversation"):
            st.session_state.messages = []
            if st.session_state.agent:
                st.session_state.agent.conversation_history = []
            st.rerun()
        
        # Help section
        st.header("💡 Sample Questions")
        st.markdown("""
        - What locations are in the water system?
        - Show me a summary of the network
        - What's the hierarchy structure?
        - How many nodes are there?
        - List all pipes in the system
        - What's connected to node X?
        """)
    
    # Main chat interface
    if not st.session_state.agent_initialized:
        st.info("👈 Please configure and initialize the agent in the sidebar to start chatting")
        return
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            # Handle error messages
            if message.get("error"):
                st.error(message["content"])
            else:
                st.markdown(message["content"])
            
            # Show tool results if available
            if message.get("tool_results"):
                with st.expander("🔧 Tool Results"):
                    st.json(message["tool_results"])
    
    # Chat input
    if prompt := st.chat_input("Ask about the water network..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                start_time = time.time()
                
                try:
                    response = st.session_state.agent.invoke(prompt)
                    
                    # Check for errors
                    if response.get('error'):
                        st.error(f"⚠️ {response['content']}")
                        
                        # Still show tool results if available
                        if response.get('tool_results'):
                            with st.expander("🔧 Retrieved Data", expanded=True):
                                st.json(response['tool_results'])
                    else:
                        # Display successful response
                        st.markdown(response['content'])
                    
                    # Show processing time
                    processing_time = time.time() - start_time
                    
                    # Performance footer
                    col1, col2, col3 = st.columns([2, 1, 1])
                    with col1:
                        st.caption(f"⏱️ {processing_time:.2f}s")
                    with col2:
                        if response.get('tool_results'):
                            st.caption(f"🔧 {len(response['tool_results'])} tools")
                    with col3:
                        st.caption(f"🤖 {response.get('model', 'gemini')}")
                    
                    # Add assistant message to history
                    assistant_message = {
                        "role": "assistant", 
                        "content": response['content'],
                        "processing_time": processing_time
                    }
                    
                    if response.get('tool_results'):
                        assistant_message["tool_results"] = response['tool_results']
                    
                    if response.get('error'):
                        assistant_message["error"] = True
                    
                    st.session_state.messages.append(assistant_message)
                
                except Exception as e:
                    error_msg = f"❌ Error: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})
    
    # Footer
    st.markdown("---")
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.caption("🌊 Guwahati Water Network Assistant")
    with col2:
        st.caption(f"💬 {len(st.session_state.messages)} messages")
    with col3:
        if st.session_state.agent and hasattr(st.session_state.agent, 'conversation_history'):
            st.caption(f"🧠 {len(st.session_state.agent.conversation_history)} in memory")

if __name__ == "__main__":
    main()

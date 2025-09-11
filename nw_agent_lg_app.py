import streamlit as st
import time
import uuid

from nw_agent_langgraph import WaterAgentLangGraph

# Configure page layout and custom CSS for wider chat
st.set_page_config(page_title="Netilion Water Assistant (LangGraph Memory)", layout="wide")

# Custom CSS to make chat widget wider
st.markdown("""
<style>
    .stChatMessage {
        max-width: 90% !important;
    }
    
    .stChatInputContainer {
        max-width: 90% !important;
    }
    
    /* Make the main content area wider */
    .main .block-container {
        max-width: 1200px !important;
        padding-top: 2rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
    }
    
    /* Adjust chat message container width */
    .stChatMessage > div {
        max-width: none !important;
    }
    
    /* Style for memory indicator */
    .memory-indicator {
        background-color: #e8f5e8;
        border: 1px solid #4CAF50;
        border-radius: 5px;
        padding: 8px;
        margin: 10px 0;
        font-size: 0.9em;
        color: #2e7d32;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def get_water_agent():
    """Get or create the WaterAgentLangGraph instance"""
    return WaterAgentLangGraph()

# Title on the page
st.markdown(
    "<h2 style='text-align: center; color: #4CAF50; font-family: Arial;'>💧Peter's Netilion Water Assistant (LangGraph Memory)💧</h2>",
    unsafe_allow_html=True,
)

# Initialize the agent
try:
    agent = get_water_agent()
except Exception as e:
    st.error(f"Error initializing WaterAgentLangGraph: {e}")
    st.stop()

if not agent.is_ready():
    st.error("Failed to initialize the agent. Please check if Ollama is running.")
    st.stop()

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": agent.start_message}
    ]

# Initialize thread ID for conversation memory
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())


# Add sidebar with memory controls
with st.sidebar:
    st.header("💬 Conversation Controls")
    
    if st.button("🔄 New Conversation", help="Start a fresh conversation with new memory"):
        st.session_state.thread_id = str(uuid.uuid4())
        st.session_state.messages = [
            {"role": "assistant", "content": agent.start_message}
        ]
        st.rerun()
    
    st.markdown(f"**Current Thread:** `{st.session_state.thread_id[:8]}...`")
    

# Display the chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Handle user input
if user_input := st.chat_input("What to do next?"):
    # Add user message to session state
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Generate assistant response
    with st.chat_message("assistant"):
        try:
            with st.spinner("Thinking with memory..."):
                # Use LangGraph invoke with thread_id for memory
                result = agent.invoke(user_input, thread_id=st.session_state.thread_id)
                
                # Handle both old and new response formats
                if isinstance(result, dict):
                    response_content = result["content"]
                    execution_time = result["execution_time"]
                    tools_called = result["tools_called"]
                else:
                    # Fallback for old format
                    response_content = result
                    execution_time = 0
                    tools_called = []
                
                # Print timing information to console
                print(f"🕐 LangGraph Agent execution time: {execution_time:.2f} seconds")
                print(f"📝 Query: {user_input}")
                print(f"🧠 Thread ID: {st.session_state.thread_id}")
                print(f"💬 Response length: {len(response_content)} characters")
                print(f"🔧 Tools called: {tools_called}")
                print("-" * 50)
                
            # Display the response
            st.markdown(response_content)
            
            # Display footer with execution info
            if execution_time > 0 or tools_called:
                st.markdown("---")
                
                # Format tools called
                if tools_called:
                    tools_text = ", ".join(tools_called)
                    tools_info = f"🔧 <strong>Tools used:</strong> {tools_text}"
                else:
                    tools_info = "🔧 <strong>Tools used:</strong> None"
                
                # Create footer message
                footer_message = f"""
<div style='font-size: 0.85em; color: #666; background-color: #f8f9fa; padding: 8px; border-radius: 5px; margin-top: 10px;'>
    ⏱️ <strong>Execution time:</strong> {execution_time:.2f} seconds<br>
    {tools_info}
</div>
"""
                st.markdown(footer_message, unsafe_allow_html=True)
            
            # Add assistant response to session state
            st.session_state.messages.append({"role": "assistant", "content": response_content})
            
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            st.error(error_msg)
            st.session_state.messages.append({"role": "assistant", "content": error_msg})

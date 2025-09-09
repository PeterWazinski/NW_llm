import streamlit as st
import time

from nw_agent import WaterAgent

# Configure page layout and custom CSS for wider chat
st.set_page_config(page_title="Netilion Water Assistant", layout="wide")

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
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def get_water_agent():
    """Get or create the WaterAgent instance"""
    return WaterAgent()

# Title on the page
st.markdown(
    "<h2 style='text-align: center; color: #4CAF50; font-family: Arial;'>💧Peter's Netilion Water Assistant💧</h2>",
    unsafe_allow_html=True,
)

# Initialize the agent
try:
    agent = WaterAgent()
except Exception as e:
    st.error(f"Error initializing WaterAgent: {e}")

if not agent.is_ready():
    st.error("Failed to initialize the agent. Please check if Ollama is running.")
    st.stop()

agent_executor = agent.get_executor()

#Initialize message history in session state
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": agent.start_message}
    ]

#Display the chat history
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
            with st.spinner("Thinking..."):
                # Measure execution time
                start_time = time.time()
                response = agent_executor.invoke({"input": user_input})
                end_time = time.time()
                execution_time = end_time - start_time
                
                out = response["output"]
                
                # Print timing information to console
                print(f"🕐 Agent execution time: {execution_time:.2f} seconds")
                print(f"📝 Query: {user_input}")
                print(f"💬 Response length: {len(out)} characters")
                print("-" * 50)
                
            st.markdown(out)
            
            # Add assistant response to session state
            st.session_state.messages.append({"role": "assistant", "content": out})
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            st.error(error_msg)
            st.session_state.messages.append({"role": "assistant", "content": error_msg})
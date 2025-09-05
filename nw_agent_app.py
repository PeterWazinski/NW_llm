import streamlit as st

from nw_agent import WaterAgent

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
water_agent = get_water_agent()

if not water_agent.is_ready():
    st.error("Failed to initialize the agent. Please check if Ollama is running.")
    st.stop()

agent_executor = water_agent.get_executor()

#Initialize message history in session state
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hi, I am your personal Netilion Water Assistant! How may I help you?"}
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
                response = agent_executor.invoke({"input": user_input})
                out = response["output"]
            st.markdown(out)
            
            # Add assistant response to session state
            st.session_state.messages.append({"role": "assistant", "content": out})
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            st.error(error_msg)
            st.session_state.messages.append({"role": "assistant", "content": error_msg})
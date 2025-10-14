import streamlit as st
import time
import uuid
import sys
import argparse

from nw_agent_langgraph import WaterAgentLangGraph

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

def parse_command_line_args():
    """Parse command line arguments for Ollama configuration"""
    # Create a new parser for our specific arguments
    parser = argparse.ArgumentParser(description='Netilion Water Assistant', add_help=False)
    parser.add_argument('--local', action='store_true', help='Use local Ollama server')
    parser.add_argument('--remote', action='store_true', help='Use remote Ollama server')
    parser.add_argument('--ollama-url', type=str, help='Custom Ollama server URL')
    parser.add_argument('--model', type=str, default="qwen2.5:7b-instruct-q4_K_M", help='LLM model to use')
    
    # Parse only known args to avoid conflicts with Streamlit's args
    args, unknown = parser.parse_known_args()
    
    # Determine run_locally setting
    run_locally = None
    if args.local and args.remote:
        st.error("Cannot specify both --local and --remote flags")
        st.stop()
    elif args.local:
        run_locally = True
    elif args.remote:
        run_locally = False
    
    return {
        'run_locally': run_locally,
        'ollama_url': args.ollama_url,
        'model': args.model
    }

@st.cache_resource
def get_water_agent(llm_model: str = "qwen2.5:7b-instruct-q4_K_M", run_locally: bool = None, ollama_url: str = None):
    """Get or create the WaterAgentLangGraph instance with specified configuration"""
    return WaterAgentLangGraph(llm_model=llm_model, run_locally=run_locally, ollama_base_url=ollama_url)

def init_app():
    """Initialize the Streamlit app with title, agent, and session state"""
    
    # Use global command line arguments
    cmd_args = CMD_LINE_ARGS
    
    # Title on the page
    server_info = "🏠 Local" if cmd_args['run_locally'] else "🌐 Remote" if cmd_args['run_locally'] is False else "⚙️ Auto"
    st.markdown(
        f"<h2 style='text-align: center; color: #4CAF50; font-family: Arial;'>💧Peter's Netilion Water Assistant💧</h2>",
        unsafe_allow_html=True,
    )
    st.markdown(f"<p style='text-align: center; color: #666;'>Ollama Server: {server_info}</p>", unsafe_allow_html=True)

    # Initialize the agent with command line configuration
    try:
        # Use command line model or fallback to session state
        model_to_use = cmd_args['model'] if cmd_args['model'] != "qwen2.5:7b-instruct-q4_K_M" else st.session_state.get('selected_model', cmd_args['model'])
        agent = get_water_agent(
            llm_model=model_to_use,
            run_locally=cmd_args['run_locally'],
            ollama_url=cmd_args['ollama_url']
        )
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

    # Initialize selected model
    if "selected_model" not in st.session_state:
        st.session_state.selected_model = "qwen2.5:7b-instruct-q4_K_M"
    
    return agent

def render_conversation_memory_section(agent):
    """Render the conversation memory section in the sidebar"""
    st.header("💬 Conversation Memory")
    
    if st.button("🔄 New Conversation", help="Start a fresh conversation with new memory", key="new_conversation_btn"):
        st.session_state.thread_id = str(uuid.uuid4())
        st.session_state.messages = [
            {"role": "assistant", "content": agent.start_message}
        ]
        # Don't clear logs on new conversation - keep them for analysis
        st.rerun()

def render_llm_selection_section(agent):
    """Render the LLM selection section in the sidebar"""
    st.header("🤖 Select LLM")
    
    try:
        # Get available models from the current agent
        available_models = agent.available_llms()
        
        # Create selectbox for model selection
        selected_model = st.selectbox(
            "Choose LLM Model:",
            options=available_models,
            index=available_models.index(st.session_state.selected_model) if st.session_state.selected_model in available_models else 0,
            help="Select a different LLM model to use"
        )
        
        # Check if model selection has changed
        if selected_model != st.session_state.selected_model:
            st.session_state.selected_model = selected_model
            
            # Clear the cache and recreate agent with new model
            st.cache_resource.clear()
            
            # Show loading message
            with st.spinner(f"Loading model {selected_model}..."):
                try:
                    # Use global command line args for new agent
                    cmd_args = CMD_LINE_ARGS
                    # Create new agent with selected model and command line config
                    new_agent = get_water_agent(
                        llm_model=selected_model,
                        run_locally=cmd_args['run_locally'],
                        ollama_url=cmd_args['ollama_url']
                    )
                    
                    # Update session state
                    st.session_state.thread_id = str(uuid.uuid4())
                    st.session_state.messages = [
                        {"role": "assistant", "content": new_agent.start_message}
                    ]
                    
                    st.success(f"✅ Switched to model: {selected_model}")
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Failed to load model {selected_model}: {e}")
                    # Revert to previous model
                    st.session_state.selected_model = agent.current_model
        
        # Display current model info
        #st.markdown(f"**Current Model:** `{st.session_state.selected_model}`")
        
    except Exception as e:
        st.error(f"Error loading available models: {e}")
        st.markdown(f"**Current Model:** `{agent.current_model if hasattr(agent, 'current_model') else 'Unknown'}`")
    

def render_sidebar(agent):
    """Render the complete sidebar with all sections"""
    with st.sidebar:
        render_conversation_memory_section(agent)
        render_llm_selection_section(agent)

def display_chat_history():
    """Display the chat history messages"""
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            # Display the main content
            st.markdown(message["content"], unsafe_allow_html=True)
            
            # Display footer if it exists (only for assistant messages)
            if message["role"] == "assistant" and "footer" in message:
                st.markdown(message["footer"], unsafe_allow_html=True)

def log_execution_info(user_input, execution_time, tools_called, response_length):
    """Log execution information to console"""
    print(f"🕐 LangGraph Agent execution time: {execution_time:.2f} seconds")
    print(f"📝 Query: {user_input}")
    print(f"🧠 Current Model: {st.session_state.selected_model}")
    print(f"💬 Response length: {response_length} characters")
    print(f"🔧 Tools called: {tools_called}")
    print("-" * 50)

def generate_execution_footer(execution_time, tools_called):
    """Generate execution information footer HTML"""
    if execution_time > 0 or tools_called:
        # Format tools called
        if tools_called:
            tools_text = ", ".join(tools_called)
            tools_info = f"🔧 <strong>Tools used:</strong> {tools_text}"
        else:
            tools_info = f"🔧 <strong>Tools used:</strong> None"
        
        # Get server information from global command line args
        cmd_args = CMD_LINE_ARGS
        if cmd_args['run_locally'] is True:
            server_info = "🏠 <strong>Server:</strong> Local"
        elif cmd_args['run_locally'] is False:
            server_url = cmd_args['ollama_url'] or "Remote (default)"
            server_info = f"🌐 <strong>Server:</strong> {server_url}"
        else:
            server_info = "⚙️ <strong>Server:</strong> Auto-detected"
        
        # Create footer message
        footer_message = f"""

---

<div style='font-size: 0.85em; color: #666; background-color: #f8f9fa; padding: 8px; border-radius: 5px; margin-top: 10px;'>
    🤖 <strong>Model:</strong> {st.session_state.selected_model}<br>
    {server_info}<br>
    ⏱️ <strong>Execution time:</strong> {execution_time:.2f} seconds<br>
    {tools_info}
</div>
"""
        return footer_message
    return ""

def display_execution_footer(execution_time, tools_called):
    """Display execution information footer in the chat"""
    footer_html = generate_execution_footer(execution_time, tools_called)
    if footer_html:
        st.markdown(footer_html, unsafe_allow_html=True)

def process_agent_response(agent, user_input):
    """Process the agent response and handle the complete interaction"""
    # Variables to store response data
    response_content = ""
    execution_time = 0
    tools_called = []
    
    with st.spinner("Thinking ..."):
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
    
    # Log execution information to console
    log_execution_info(user_input, execution_time, tools_called, len(response_content))
    
    # Generate footer HTML
    footer_html = generate_execution_footer(execution_time, tools_called)
    
    # Display the response content
    st.markdown(response_content, unsafe_allow_html=True)
    
    # Display the footer
    if footer_html:
        st.markdown(footer_html, unsafe_allow_html=True)
    
    # Add assistant response to session state (content and footer stored separately)
    message_data = {"role": "assistant", "content": response_content}
    if footer_html:
        message_data["footer"] = footer_html
    
    st.session_state.messages.append(message_data)

def handle_chat_input(agent):
    """Handle user input and generate assistant response"""
    if user_input := st.chat_input("What to do next?"):
        # Add user message to session state
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        # Generate assistant response
        with st.chat_message("assistant"):
            try:
                process_agent_response(agent, user_input)
            except Exception as e:
                error_msg = f"Error: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})



# Parse command line arguments globally
CMD_LINE_ARGS = parse_command_line_args()

# Initialize the app and get the agent
agent = init_app()

# Render the application UI
render_sidebar(agent)
display_chat_history()
handle_chat_input(agent)

from langchain.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver
from typing_extensions import TypedDict
from typing import Annotated, List
import time
import os

from Guwahati import Guwahati
from nw_water_tools import NWWaterTools

# Import our HTTP interception tools
try:
    from ollama_interceptor import InterceptingChatOllama, setup_global_httpx_interception
    INTERCEPTION_AVAILABLE = True
    print("🔍 HTTP interception tools loaded successfully")
except ImportError:
    INTERCEPTION_AVAILABLE = False
    print("⚠️ HTTP interception tools not available")

# "C:\Users\i09300076\OneDrive - Endress+Hauser\DEV\Python3-heroku\NW_llm\ollama_env\Scripts\activate.bat"
# streamlit run nw_agent_lg_app.py   
# streamlit run nw_agent_lg_app.py -- --remote
# streamlit run nw_agent_lg_app.py -- --intercept-http --remote

# Define the state structure for LangGraph
class AgentState(TypedDict):
    messages: Annotated[List, "The conversation messages"]
    next: str  # The next step to take

class WaterAgentLangGraph:
    """A class to manage the water assistant agent using LangGraph with built-in memory"""
    # Configuration flags (can be overridden at runtime)
    run_ollama_locally = True  # Set to True for local, False for remote server
    
    # Model configurations
    local_ollama_model = "qwen2.5:7b-instruct-q4_K_M"  # Local model
    remote_ollama_model = "llama3.1:8b"  # Remote model
    remote_ollama_base_url = "http://10.58.145.210:11434"  # Remote server URL

    def __init__(self, ollama_base_url: str = None, llm_model: str = "qwen2.5:7b-instruct-q4_K_M", run_locally: bool = None, enable_http_interception: bool = False):
        self.model = None
        self.tools = None
        self.app = None
        self.enable_http_interception = enable_http_interception
        
        # Allow runtime override of the class variable
        if run_locally is not None:
            self.run_ollama_locally = run_locally
        
        # Determine which server to use based on configuration
        if self.run_ollama_locally:
            # Use provided URL, environment variable, or default to None (local server)
            self.ollama_base_url = None  # Force local for local mode
            self.server_type = "local"
        else:
            # Use provided URL, environment variable, or default remote URL
            self.ollama_base_url = ollama_base_url or os.getenv('OLLAMA_BASE_URL') or self.remote_ollama_base_url
            self.server_type = "remote"
            
        if self.ollama_base_url:
            print(f"🌐 Using Ollama server at: {self.ollama_base_url}")
        else:
            print(f"🏠 Using local Ollama server")
            
        # Validate that the requested model is available
        available_models = self.available_llms()
        if llm_model not in available_models:
            available_model_list = ", ".join(available_models)
            raise ValueError(f"Model '{llm_model}' is not available on the Ollama server. Available models: {available_model_list}")
            
        self.current_model = llm_model
        print(f"🤖 Using model: {self.current_model}")

        self.memory = MemorySaver()  # LangGraph's memory saver
        self.start_message = f"Hi, I am your personal Netilion Water Assistant running on the {self.current_model} language model! I can give you insights about your plant. How may I help you?"
        self.guwahati_hierarchy = Guwahati.create_hierarchy()
        self.water_tools = NWWaterTools(self.guwahati_hierarchy)
        self._initialize_components()
    
    def available_llms(self) -> list:
        """Get a list of available LLM models from the Ollama server"""
        import requests
        
        try:
            if self.ollama_base_url:
                # Remote server
                url = f"{self.ollama_base_url}/api/tags"
            else:
                # Local server
                url = "http://localhost:11434/api/tags"
                
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            models = [model['name'] for model in data.get('models', [])]
            
            # Sort models alphabetically
            models.sort()
            
            print(f"📦 Found {len(models)} available models: {', '.join(models)}")
            return models
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Error connecting to Ollama server: {e}")
            # Return fallback models based on configuration
            if self.run_ollama_locally:
                return [self.local_ollama_model]
            else:
                return [self.remote_ollama_model]
        except Exception as e:
            print(f"❌ Unexpected error querying available models: {e}")
            # Return fallback models based on configuration
            if self.run_ollama_locally:
                return [self.local_ollama_model]
            else:
                return [self.remote_ollama_model]

    def _initialize_components(self):
        """Initialize all agent components with LangGraph"""
        try:
            self.tools = self.water_tools.create_tools()
            
            # Initialize ChatOllama with appropriate configuration and optional HTTP interception
            if self.enable_http_interception and INTERCEPTION_AVAILABLE:
                print("🔍 Enabling HTTP request interception for Ollama...")
                try:
                    if self.run_ollama_locally:
                        # Local Ollama server with interception - use default local URL
                        self.model = InterceptingChatOllama(
                            model=self.current_model,
                            base_url="http://localhost:11434",
                            validate_model_on_init=True
                        )
                    else:
                        # Remote Ollama server with interception
                        self.model = InterceptingChatOllama(
                            model=self.current_model, 
                            base_url=self.ollama_base_url,
                            validate_model_on_init=True
                        )
                except Exception as e:
                    print(f"⚠️ Failed to initialize HTTP interception: {e}")
                    print("🔄 Falling back to standard ChatOllama...")
                    # Fallback to standard ChatOllama
                    if self.run_ollama_locally:
                        self.model = ChatOllama(
                            model=self.current_model, 
                            validate_model_on_init=True
                        )
                    else:
                        self.model = ChatOllama(
                            model=self.current_model, 
                            base_url=self.ollama_base_url,
                            validate_model_on_init=True
                        )
            else:
                # Standard ChatOllama without interception
                if self.run_ollama_locally:
                    # Local Ollama server (default configuration)
                    self.model = ChatOllama(
                        model=self.current_model, 
                        validate_model_on_init=True
                    )
                else:
                    # Remote Ollama server
                    self.model = ChatOllama(
                        model=self.current_model, 
                        base_url=self.ollama_base_url,
                        validate_model_on_init=True
                    )


            
            # Bind tools to the model
            self.model_with_tools = self.model.bind_tools(self.tools)
            
            # Create the LangGraph workflow
            self._create_langgraph_workflow()
            
        except Exception as e:
            self.app = None
            raise e


    def _create_langgraph_workflow(self):
        """Create the LangGraph workflow with state management"""
        
        def should_continue(state: AgentState):
            """Determine if we should continue or end"""
            last_message = state["messages"][-1]
            # If there are tool calls, continue to tools
            if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
                return "tools"
            # Otherwise, end
            return END
        
        def call_model(state: AgentState):
            """Call the model with the current state"""
            system_prompt = self.water_tools.get_system_prompt()
            
            # Create messages with system prompt
            messages = [("system", system_prompt)] + state["messages"]
            
            response = self.model_with_tools.invoke(messages)
            return {"messages": state["messages"] + [response]}
        
        # Create the workflow
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("agent", call_model)
        workflow.add_node("tools", ToolNode(self.tools))
        
        # Set entry point
        workflow.set_entry_point("agent")
        
        # Add conditional edges
        workflow.add_conditional_edges("agent", should_continue)
        workflow.add_edge("tools", "agent")
        
        # Compile with memory
        self.app = workflow.compile(checkpointer=self.memory)

    def invoke(self, message: str, thread_id: str = "default"):
        """Invoke the agent with a message and thread ID for memory"""
        config = {"configurable": {"thread_id": thread_id}}
        
        # Reset called tools for this execution
        self.water_tools.reset_tool_tracking()
        
        # Time the execution
        start_time = time.time()
        
        try:
            result = self.app.invoke(
                {"messages": [("human", message)]},
                config=config
            )
            
            end_time = time.time()
            execution_time = end_time - start_time
            
            # Get called tools from the tools instance
            called_tools = self.water_tools.get_called_tools()
            
            print(f"🤖 Agent execution completed in {execution_time:.3f}s")
            print(f"🔧 Tools called: {called_tools}")
            
            # Return the last message (assistant's response) and tool info
            response_content = result["messages"][-1].content
            return {
                "content": response_content,
                "execution_time": execution_time,
                "tools_called": called_tools
            }
            
        except Exception as e:
            end_time = time.time()
            execution_time = end_time - start_time
            print(f"❌ Agent execution failed after {execution_time:.3f}s: {str(e)}")
            raise e
    
    def get_executor(self):
        """Get the LangGraph app (replaces agent_executor)"""
        return self.app
    
    def is_ready(self):
        """Check if the agent is ready to use"""
        return self.app is not None

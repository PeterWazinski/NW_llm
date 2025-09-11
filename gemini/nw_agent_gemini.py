from langchain.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
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

# Define the state structure for LangGraph
class AgentState(TypedDict):
    messages: Annotated[List, "The conversation messages"]
    next: str  # The next step to take

class WaterAgentGemini:
    """A class to manage the water assistant agent using LangGraph with Google Gemini"""
    gemini_model = "gemini-1.5-flash"  # or "gemini-1.5-pro" for more advanced tasks

    def __init__(self, google_api_key: str = None):
        self.model = None
        self.tools = None
        self.app = None
        
        # Use provided API key or environment variable
        self.google_api_key = google_api_key or os.getenv('GOOGLE_API_KEY')
        if not self.google_api_key:
            raise ValueError("Google API key is required. Set GOOGLE_API_KEY environment variable or pass it as parameter.")
        
        print(f"🔑 Using Google Gemini API with model: {self.gemini_model}")

        self.memory = MemorySaver()  # LangGraph's memory saver
        self.start_message = f"Hi, I am your personal Netilion Water Assistant powered by Google {self.gemini_model}! I can give you insights about your plant. How may I help you?"
        self.guwahati_hierarchy = Guwahati.create_hierarchy()
        self.water_tools = NWWaterTools(self.guwahati_hierarchy)
        self._initialize_components()

        
    
    def _initialize_components(self):
        """Initialize all agent components with LangGraph"""
        try:
            self.tools = self.water_tools.create_tools()
            
            # Initialize ChatGoogleGenerativeAI with API key
            self.model = ChatGoogleGenerativeAI(
                model=self.gemini_model,
                google_api_key=self.google_api_key,
                temperature=0.1,  # Lower temperature for more consistent responses
                convert_system_message_to_human=True  # Gemini doesn't support system messages natively
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

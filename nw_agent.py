from langchain.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama
from langchain.tools import tool
from langchain.memory import ConversationBufferMemory
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
import streamlit as st

from Guwahati import Guwahati


class WaterAgent:
    """A class to manage the water assistant agent and its components"""
    
    def __init__(self):
        self.model = None
        self.tools = None
        self.prompt = None
        self.agent_executor = None
        self.memory = None
        self.guwahati_hierarchy = Guwahati.create_hierarchy()
        self._initialize_components()
    
    def _initialize_components(self):
        """Initialize all agent components"""
        try:
            # Import product functions

            self.tools = self.create_tools()

            # Create prompt template
            self.prompt = ChatPromptTemplate.from_messages([
                ("system", self.get_system_prompt()),
                ("placeholder", "{chat_history}"),
                ("human", "{input}"),
                ("placeholder", "{agent_scratchpad}")
            ])
            
            # Create model
            self.model = ChatOllama(model="qwen2.5:3b-instruct", validate_model_on_init=True)
            
            # Create memory
            self.memory = ConversationBufferMemory(
                memory_key="chat_history", 
                return_messages=True
            )
            
            # Create agent executor
            agent = create_tool_calling_agent(self.model, self.tools, self.prompt)
            self.agent_executor = AgentExecutor(
                agent=agent, 
                tools=self.tools, 
                memory=self.memory, 
                verbose=False
            )
            
        except Exception as e:
            st.error(f"Error initializing WaterAgent: {e}")
            self.agent_executor = None

    def create_tools(self):
        """ Return a list of tool functions for the agent to use.  """
        
        @tool
        def get_all_locations():
            """Get all location nodes in the water system hierarchy.
            
            Returns:
                list: All location nodes with their details (id, name, type)
            """
            return self.guwahati_hierarchy.all_locations
        
        @tool
        def get_all_applications():
            """Get all application nodes (water_abstraction, water_distribution, effluent_discharge) in the hierarchy.
            
            Returns:
                list: All application nodes with their details (id, name, type)
            """
            return self.guwahati_hierarchy.all_applications
        
        @tool
        def get_all_modules():
            """Get all module nodes (source_module, storage_module, etc.) in the hierarchy.
            
            Returns:
                list: All module nodes with their details (id, name, type)
            """
            return self.guwahati_hierarchy.all_modules
        
        @tool
        def get_all_instrumentations():
            """Get all instrumentation/instrument nodes in the hierarchy.
            
            Returns:
                list: All instrumentation nodes with their details (id, name/tag, type, primary_val_key, value_keys)
            """
            return self.guwahati_hierarchy.all_instrumentations
        
        @tool
        def get_all_assets():
            """Get all asset nodes in the hierarchy.
            
            Returns:
                list: All asset nodes with their details (id, name/serial, product info)
            """
            return self.guwahati_hierarchy.all_assets
        
        @tool
        def get_assets_for_instrument(instrumentation):
            """Get all asset nodes for a specific instrumentation.
            
            Returns:
                list: All asset nodes for the given instrumentation
            """
            return self.guwahati_hierarchy.get_assets(instrumentation)
        
        @tool
        def get_applications_for_location(location):
            """Get all application nodes for a specific location.
            
            Args:
                location: The location node to get applications for
            
            Returns:
                list: All application nodes for the given location
            """
            return self.guwahati_hierarchy.get_applications(location)
        
        @tool
        def get_modules_for_application(application):
            """Get all module nodes for a specific application.
            
            Args:
                application: The application node to get modules for
            
            Returns:
                list: All module nodes for the given application
            """
            return self.guwahati_hierarchy.get_modules(application)
        
        @tool
        def get_instruments_for_module(module):
            """Get all instrumentation nodes for a specific module.
            
            Args:
                module: The module node to get instrumentations for
            
            Returns:
                list: All instrumentation nodes for the given module
            """
            return self.guwahati_hierarchy.get_instrumentations(module)

        return [
            get_all_locations,
            get_all_applications,
            get_all_modules,
            get_all_instrumentations,
            get_all_assets,
            get_assets_for_instrument,
            get_applications_for_location,
            get_modules_for_application,
            get_instruments_for_module
        ]

    def get_system_prompt(self):
        """Initialize the system prompt"""
        return """
Context:
You are an Assistant that helps the user to analyze a customer's Netilion Water software application. 
A customer runs a Netilion water plant application which consists of various components that are hierarchically ordered:
- each component has a unique ID, a name and a type
- locations are the highest level of the hierarchy. there is only one type "location". they have one or more children called applications.
- Each application is of type water abstraction, water distribution or effluent discharge. Each application can have one or more modules.
- Each module is of type outlet, inlet, storage, desinfection, source, transfer or quality control.
there can be one or more locations.
- Each module can have one or more instrumentations or shorthand instruments 
- An instrument is a measurement device that has one or more measurement time series. 
each time series is identified by a value key. 
The name of an instrument is also called a "tag". 
Each instrument is of type Flow, Pump, Analysis, Pressure or Voltage. 
Each instrument may has a primary key and an upper and/or lower limit for each value key.

It is important to know what the children of a component are and what are the defined attributes of a component.
A user will query the system for information about these components and their relationships.

"""

    def get_executor(self):
        """Get the agent executor"""
        return self.agent_executor
    
    def is_ready(self):
        """Check if the agent is ready to use"""
        return self.agent_executor is not None

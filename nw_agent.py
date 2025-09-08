from langchain.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama
from langchain.tools import tool
from langchain.memory import ConversationBufferMemory
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
import logging

from Guwahati import Guwahati

# Enable debug logging for LangChain
#logging.basicConfig(level=logging.DEBUG)
#langchain_logger = logging.getLogger("langchain")
#langchain_logger.setLevel(logging.DEBUG)


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
                verbose=True  # Enable verbose output for debugging
            )
            
        except Exception as e:
            # Let the exception bubble up to be handled by the calling application
            self.agent_executor = None
            raise e
    
    def safe_int_parse(self, value):
        """Parse string to int, return None on error"""
        try:
            return int(value)
        except (ValueError, TypeError):
            return None

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
        def get_assets_for_instrument(inst_id_or_name: str) -> list:
            """Get all asset nodes for a specific instrumentation by ID or name.
            
            Args:
                inst_id_or_name: The ID (as string) or name of the instrumentation
            
            Returns:
                list: All asset nodes for the given instrumentation
            """

            print(f"get_assets_for_instrument called with instrumentation_id: {inst_id_or_name}, type: {type(inst_id_or_name)}   ")
            try:
                # Find the instrumentation by ID or name
                id = self.safe_int_parse(inst_id_or_name)
                instrumentation = None
                if id is not None:
                    instrumentation = self.guwahati_hierarchy.nodes.get(id, None)
                else:
                    for inst in self.guwahati_hierarchy.all_instrumentations:
                        if inst['name'] == inst_id_or_name:
                            instrumentation = inst
                            break

                if instrumentation is None:
                    return f"No instrumentation found with ID or name: {inst_id_or_name}"
                else:
                    return self.guwahati_hierarchy.get_assets(instrumentation)
            except Exception as e:
                return f"Error getting assets for instrumentation {inst_id_or_name}: {str(e)}"

        @tool
        def get_applications_for_location(location_id_or_name: str) -> list:
            """Get all application nodes for a specific location by ID or name.
            
            Args:
                location_id_or_name: The ID (as string) or name of the location
            
            Returns:
                list: All application nodes for the given location
            """
            print(f"get_applications_for_location called with location_id_or_name: {location_id_or_name}, type: {type(location_id_or_name)}")
            try:
                # Find the location by ID or name
                id = self.safe_int_parse(location_id_or_name)
                location = None
                if id is not None:
                    location = self.guwahati_hierarchy.nodes.get(id, None)
                else:
                    for loc in self.guwahati_hierarchy.all_locations:
                        if loc.name == location_id_or_name:
                            location = loc
                            break

                if location is None:
                    return f"No location found with ID or name: {location_id_or_name}"
                else:
                    return self.guwahati_hierarchy.get_applications(location)
            except Exception as e:
                return f"Error getting applications for location {location_id_or_name}: {str(e)}"
        
        @tool
        def get_modules_for_application(application_id_or_name: str) -> list:
            """Get all module nodes for a specific application by ID or name.
            
            Args:
                application_id_or_name: The ID (as string) or name of the application
            
            Returns:
                list: All module nodes for the given application
            """

            print(f"get_modules_for_application called with application_id_or_name: {application_id_or_name}, type: {type(application_id_or_name)}")    
            try:
                # Find the application by ID or name
                id = self.safe_int_parse(application_id_or_name)
                application = None
                if id is not None:
                    application = self.guwahati_hierarchy.nodes.get(id, None)
                else:
                    for app in self.guwahati_hierarchy.all_applications:
                        if app.name == application_id_or_name:
                            application = app
                            break

                if application is None:
                    return f"No application found with ID or name: {application_id_or_name}"
                else:
                    return self.guwahati_hierarchy.get_modules(application)
            except Exception as e:
                return f"Error getting modules for application {application_id_or_name}: {str(e)}"
        
        @tool
        def get_instruments_for_module(module_id_or_name: str):
            """Get all instrumentation nodes for a specific module by ID or name.
            
            Args:
                module_id_or_name: The ID (as string) or name of the module
            
            Returns:
                list: All instrumentation nodes for the given module
            """
            print(f"get_instruments_for_module called with module_id_or_name: {module_id_or_name}, type: {type(module_id_or_name)}")

            try:
                # Find the module by ID or name
                id = self.safe_int_parse(module_id_or_name)
                module = None
                if id is not None:
                    module = self.guwahati_hierarchy.nodes.get(id, None)
                else:
                    for mod in self.guwahati_hierarchy.all_modules:
                        if mod.name == module_id_or_name:
                            module = mod
                            break

                if module is None:
                    return f"No module found with ID or name: {module_id_or_name}"
                else:
                 return self.guwahati_hierarchy.get_instrumentations(module)
            except Exception as e:
                return f"Error getting instruments for module {module_id_or_name}: {str(e)}"

        @tool
        def pprint_hierarchy():
            """Pretty prints the entire water system hierarchy. returns a formatted string."""
            try:
                return self.guwahati_hierarchy.pprint(show_summary=True)
            except Exception as e:
                return f"Error printing hierarchy: {str(e)}"

        @tool
        def pprint_hierarchy_md():
            """Pretty prints the entire water system hierarchy in markdown format for better LLM processing."""
            try:
                return self.guwahati_hierarchy.pprint_md(show_summary=True)
            except Exception as e:
                return f"Error printing markdown hierarchy: {str(e)}"

        @tool
        def get_summary():
            """Get a summary of the hierarchy with node counts in a structured format."""
            try:
                return self.guwahati_hierarchy.print_summary()
            except Exception as e:
                return f"Error getting summary: {str(e)}"

        @tool
        def get_md_summary():
            """Get a summary of the hierarchy with node counts in markdown format for better LLM processing."""
            try:
                return self.guwahati_hierarchy.print_md_summary()
            except Exception as e:
                return f"Error getting markdown summary: {str(e)}"
            
        return [
                get_all_locations,  
                get_all_applications,
                get_all_modules,
                get_all_instrumentations,   
                get_all_assets,
                get_assets_for_instrument,
                get_applications_for_location,
                get_modules_for_application,
                get_instruments_for_module,
                pprint_hierarchy,
                pprint_hierarchy_md,
                get_summary,
                get_md_summary
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
- there can be one or more locations.
- Each module can have one or more instrumentations or shorthand instruments 

- An instrument is a measurement device that has one or more measurement time series.
- Each time series is identified by a value key (attribute value_keys).
- The name of an instrument is also called a "tag".
- Each instrument is of type Flow, Pump, Analysis, Pressure or Voltage.
- Each instrument may has a primary key (attribute primary_val_key) and upper and/or lower thresholds (attribute thresholds) for the value keys.

It is important to know what the children of a component are and what are the defined attributes of a component.
A user will query the system for information about these components and their relationships.

There are a couple of tools availabe to query the hierarchy and the components:

These tools list the components of the water system hierarchy without any filtering or selection, 
they don't need any input parameters:
- get_all_locations: Get all location nodes in the water system hierarchy.
- get_all_applications: Get all application nodes (water_abstraction, water_distribution, effluent_discharge) in the hierarchy.
- get_all_modules: Get all module nodes (source_module, storage_module, etc.) in the hierarchy.
- get_all_instrumentations: Get all instrumentation/instrument nodes in the hierarchy.
- get_all_assets: Get all asset nodes in the hierarchy.

These tools provide hierarchy summaries and visualization:
- get_summary: Get a formatted summary with counts of all component types.
- get_md_summary: Get a markdown-formatted summary with counts (better for structured analysis).
- pprint_hierarchy: Get a complete hierarchical view of all components with emojis and indentation.
- pprint_hierarchy_md: Get a complete hierarchical view in markdown format (better for LLM processing).

When using the tools below, you must provide the ID of the component as a string, e.g. all applications for location with ID "1". All of these tools also accept names instead of IDs:
- get_assets_for_instrument: Get all asset nodes for a specific instrumentation (accepts ID or name).    
- get_applications_for_location: Get all application nodes for a specific location (accepts ID or name).
- get_modules_for_application: Get all module nodes for a specific application (accepts ID or name).
- get_instruments_for_module: Get all instrumentation nodes for a specific module (accepts ID or name).

Examples of how to use the tools:

Example 1 - Query by ID:
User: "What instruments are in module 100?"
Assistant: I'll find the instruments for module 100.
Tool call: get_instruments_for_module("100")

Example 2 - Query by name:
User: "What instruments are in the Source module?"
Assistant: I'll find the instruments for the Source module.
Tool call: get_instruments_for_module("Source")

Example 3 - Query by application name:
User: "What modules are in the Abstraction application?"
Assistant: I'll find the modules for the Abstraction application.
Tool call: get_modules_for_application("Abstraction")

Example 4 - Query by location name:
User: "What applications are in Nijeshwari PWSS?"
Assistant: I'll find the applications for Nijeshwari PWSS location.
Tool call: get_applications_for_location("Nijeshwari PWSS")

Example 5 - Query by instrument name:
User: "What assets are connected to the Borewell level instrument?"
Assistant: I'll find the assets for the Borewell level instrument.
Tool call: get_assets_for_instrument("Borewell level")

Example 6 - Request for structured summary:
User: "Give me a summary of the water system hierarchy"
Assistant: I'll get a structured summary of the hierarchy.
Tool call: get_md_summary()

Example 7 - Request for detailed hierarchy view:
User: "Show me the complete hierarchy structure in a structured format"
Assistant: I'll get the complete hierarchy in markdown format for better analysis.
Tool call: pprint_hierarchy()
Tool call: get_assets_for_instrument("Borewell level")


You should use these tools to answer the user's questions about the water system hierarchy.
You should always answer in a concise manner and only use the tools if necessary.
When giving answers, refer to components by their ID and name and type
If you don't know the answer, just say you don't know. Do not try to make up an answer.

"""

    def get_executor(self):
        """Get the agent executor"""
        return self.agent_executor
    
    def is_ready(self):
        """Check if the agent is ready to use"""
        return self.agent_executor is not None

import streamlit as st

from langchain.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama
from langchain.tools import tool
from langchain.memory import ConversationBufferMemory
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate


class WaterAgent:
    """A class to manage the water assistant agent and its components"""
    
    def __init__(self):
        self.model = None
        self.tools = None
        self.prompt = None
        self.agent_executor = None
        self.memory = None
        self._initialize_components()
    
    def _initialize_components(self):
        """Initialize all agent components"""
        try:
            # Import product functions
            from product import list_products, select_products, delete_product, create_product
            
            # Create tools
            list_products_tool = tool(list_products, description="List all products in the database")
            select_products_tool = tool(select_products, description="Select products by category")
            delete_product_tool = tool(delete_product, description="Delete a product by its ID")
            create_product_tool = tool(create_product, description="Create a new product with name, price and category")
            self.tools = [list_products_tool, select_products_tool, delete_product_tool, create_product_tool]
            
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

    def get_system_prompt(self):
        """Initialize the system prompt"""
        return """
You are an Assistant that helps the user to analyze the Netilion Water software application. 
A Netilion Water application consists of various components that are hierarchically ordered:
- each component has a unique ID, a name and a type
- locations are the highest level of the hierarchy. there is only one type "location". they have one or more children called applications.
- Each application is of type water abstraction, water distribution or effluent discharge. Each application can have one or more modules.
- Each module is of type outlet, inlet, storage, desinfection, source, transfer or quality control.
there can be one or more locations.
- Each module can have one or more instrumentations or instruments (devices) that have one or more measurment values. 
Each instrument is of type Flow, Pump, Analysis, Pressure or Voltage

It is important to know what the children of a component are and what are the defined attributes of a component.

"""

    def get_executor(self):
        """Get the agent executor"""
        return self.agent_executor
    
    def is_ready(self):
        """Check if the agent is ready to use"""
        return self.agent_executor is not None


@st.cache_resource
def get_water_agent():
    """Get or create the WaterAgent instance"""
    return WaterAgent()

# Title on the page
st.markdown(
    "<h2 style='text-align: center; color: #4CAF50; font-family: Arial;'>Peter's Netilion Water Assistant💧</h2>",
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
        {"role": "assistant", "content": "Hi, I am your personal product Assistant! How may I help you?"}
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
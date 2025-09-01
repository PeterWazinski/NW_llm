import streamlit as st

from langchain.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama
from langchain.tools import tool
from langchain.memory import ConversationBufferMemory
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate



@st.cache_resource
def create_agent_components():
    """Create and cache the agent components (model, tools, prompt)"""
    try:
        from product import list_products, select_products, delete_product, create_product
        list_products_tool = tool(list_products, description="List all products in the database")
        select_products_tool = tool(select_products, description="Select products by category")
        delete_product_tool = tool(delete_product, description="Delete a product by its ID")
        create_product_tool = tool(create_product, description="Create a new product with name, price and category")
        all_tools = [list_products_tool, select_products_tool, delete_product_tool, create_product_tool]
        
        agent_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an Assistant that helps the user querying the products database. 
Each product has the fields:
- name
- price
- category
- id (internal usage)"""),
            ("placeholder", "{chat_history}"),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}")
        ])
        
        model = ChatOllama(model="qwen2.5:3b-instruct", validate_model_on_init=True)
        return model, all_tools, agent_prompt
    except Exception as e:
        st.error(f"Error creating agent components: {e}")
        return None, None, None

def get_agent_executor():
    """Get or create agent executor with persistent memory"""
    if "agent_executor" not in st.session_state:
        model, tools, prompt = create_agent_components()
        if model is None:
            return None
            
        # Create memory that persists in session state
        memory = ConversationBufferMemory(
            memory_key="chat_history", 
            return_messages=True
        )
        
        agent = create_tool_calling_agent(model, tools, prompt)
        st.session_state.agent_executor = AgentExecutor(
            agent=agent, 
            tools=tools, 
            memory=memory, 
            verbose=False
        )
    
    return st.session_state.agent_executor

# Title on the page
st.markdown(
    "<h2 style='text-align: center; color: #4CAF50; font-family: Arial;'>Peter's Product Assistant🪶</h2>",
    unsafe_allow_html=True,
)

# Initialize the agent
agent_executor = get_agent_executor()

if agent_executor is None:
    st.error("Failed to initialize the agent. Please check if Ollama is running.")
    st.stop()

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
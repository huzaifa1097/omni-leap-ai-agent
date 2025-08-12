import os
from dotenv import load_dotenv
from langchain import hub
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.chat_history import BaseChatMessageHistory
from langchain.memory import ConversationBufferWindowMemory
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder

# Tool Imports
from app.core.tools.weather import weather_tool
from app.core.tools.calendar_tool import calendar_tool
from app.core.tools.wikipedia import wikipedia_tool
from app.core.tools.news import news_tool
from app.core.tools.financial_data import get_daily_stock_prices
from app.core.tools.code_interpreter import code_interpreter_tool
from langchain_community.tools import DuckDuckGoSearchRun

# Import the function to search the user's memory
from app.services.vector_db_service import search_user_memory

load_dotenv()

def get_groq_llm():
    """
    Initialize Groq LLM with proper error handling.
    """
    groq_api_key = os.getenv("GROQ_API_KEY")
    
    if not groq_api_key:
        raise Exception("GROQ_API_KEY not found in .env file.")
    
    try:
        llm = ChatGroq(
            groq_api_key=groq_api_key,
            model_name="llama3-8b-8192", # Using a faster model for better UX
            temperature=0.7,
            max_retries=3
        )
        print("✅ Using Groq (Llama 3 8B) for agent.")
        return llm
    except ImportError:
        raise Exception("Could not import langchain-groq. Please run: pip install langchain-groq")
    except Exception as e:
        raise Exception(f"Failed to initialize Groq LLM: {str(e)}")

# Initialize the LLM
try:
    llm = get_groq_llm()
except Exception as e:
    print(f"❌ LLM initialization failed: {e}")
    llm = None

# Instantiate the general search tool
search_tool = DuckDuckGoSearchRun()

# Gather all the tools for the main agent
tools = [
    search_tool,
    weather_tool,
    calendar_tool,
    wikipedia_tool,
    news_tool,
    get_daily_stock_prices,
    code_interpreter_tool
]

# Create agent only if LLM is available
agent = None
if llm:
    try:
        prompt = hub.pull("hwchase17/react-chat")
        agent = create_react_agent(llm, tools, prompt)
        print("✅ Agent initialized successfully with LangChain Hub prompt.")
    except Exception as e:
        print(f"⚠ Hub prompt failed, using custom fallback prompt: {e}")
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful AI assistant. You have access to a variety of tools to help you answer questions accurately."),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        agent = create_react_agent(llm, tools, prompt)
        print("✅ Agent initialized with custom prompt.")

SESSION_STORE = {}

def get_session_history(session_id: str) -> BaseChatMessageHistory:
    """Retrieves or creates a session history for the current conversation."""
    if session_id not in SESSION_STORE:
        SESSION_STORE[session_id] = ConversationBufferWindowMemory(
            k=5, 
            memory_key="chat_history", 
            return_messages=True
        ).chat_memory
    return SESSION_STORE[session_id]

def run_agent(user_input: str, session_id: str, user_id: str) -> dict:
    """Runs the agent executor with RAG, short-term memory, and robust error handling."""
    
    if agent is None or llm is None:
        return {"output": "❌ Agent not initialized. Please check your GROQ_API_KEY and restart the server."}
    
    try:
        memory = get_session_history(session_id)
        relevant_memories = search_user_memory(user_id, user_input)
        
        if relevant_memories:
            memory_context = "\n".join(relevant_memories)
            enhanced_input = (
                f"Here is some relevant context from our past conversations:\n"
                f"<CONTEXT>\n{memory_context}\n</CONTEXT>\n\n"
                f"Now, please answer the following question:\n{user_input}"
            )
        else:
            enhanced_input = user_input
            
        agent_executor = AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=5,
            max_execution_time=60
        )
        
        result = agent_executor.invoke({
            "input": enhanced_input,
            "chat_history": memory.messages,
        })
        
        memory.add_user_message(user_input)
        memory.add_ai_message(result.get("output", ""))
        
        return result
        
    except Exception as e:
        error_msg = f"❌ Agent execution failed: {str(e)}"
        print(error_msg)
        
        # Fallback to direct LLM call if the agent fails
        try:
            print("🔄 Falling back to direct LLM call...")
            response = llm.invoke(user_input)
            return {"output": response.content}
        except Exception as fallback_error:
            return {"output": f"I encountered an error while processing your request: {str(e)}"}

from langchain_core.prompts import ChatPromptTemplate

SYSTEM_PROMPT = """
You are OmniLeap, a powerful, multimodal AI assistant based in Lucknow, India.
You are friendly, helpful, and an expert at using your available tools to answer questions and complete tasks.
You can think step-by-step to solve complex problems.
When asked about the current location, you are in Lucknow, Uttar Pradesh.
Be concise unless the user asks for details.
"""

def create_agent_prompt():
    return ChatPromptTemplate.from_messages(
        [
            ("system", SYSTEM_PROMPT),
            ("placeholder", "{chat_history}"), # For conversation memory
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}"), # Where the agent's thoughts and tool outputs go
        ]
    )
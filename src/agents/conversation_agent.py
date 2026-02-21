from langchain.tools import tool
from src.chains.agent_chains import create_conversation_chain

# Create chain instance
conversation_chain = create_conversation_chain()

@tool
def conversation_agent_tool(question: str, conversation_memory: str):
    """
    Retrieves how similar guest questions were previously answered
    in real customer-care conversations.
    """
    return conversation_chain.invoke({
        "query": question,
        "chat_history": conversation_memory
    })["result"]
from langchain.tools import tool
from src.chains.agent_chains import create_policy_chain

# Create chain instance
policy_chain = create_policy_chain()

@tool
def policy_agent_tool(question: str, guest_type: str, loyalty: str, city: str, chat_history: list):
    """
    Answers questions using official policy documents.
    """
    return policy_chain.invoke({
        "question": question,
        "chat_history": chat_history,
        "guest_type": guest_type,
        "loyalty": loyalty,
        "city": city
    })["answer"]
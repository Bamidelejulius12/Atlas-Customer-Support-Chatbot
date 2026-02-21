import asyncio
from src.agents.policy_agent import policy_agent_tool
from src.agents.conversation_agent import conversation_agent_tool
from src.chains.agent_chains import create_aggregator_chain
from src.database.memory_db import ConversationMemory

# Create instances
aggregator_chain = create_aggregator_chain()
memory_db = ConversationMemory()

async def run_agents_parallel(question, guest_type, loyalty, city, chat_history_tuples, chat_history_text):
    policy_task = asyncio.to_thread(
        policy_agent_tool.run,
        {
            "question": question,
            "guest_type": guest_type,
            "loyalty": loyalty,
            "city": city,
            "chat_history": chat_history_tuples
        }
    )
    
    conversation_task = asyncio.to_thread(
        conversation_agent_tool.run,
        {
            "question": question,
            "conversation_memory": chat_history_text
        }
    )
    
    return await asyncio.gather(policy_task, conversation_task)

async def agentic_rag_answer(question, guest_type, loyalty, city, session_id):
    # Get conversation history
    chat_history_tuples = memory_db.get_chat_history_tuples(session_id)
    chat_history_text = memory_db.get_chat_history_text(session_id)
    
    # Run agents in parallel
    policy_output, conversation_output = await run_agents_parallel(
        question,
        guest_type,
        loyalty,
        city,
        chat_history_tuples,
        chat_history_text
    )
    
    # Aggregate results
    final_answer = aggregator_chain.invoke({
        "policy_output": policy_output,
        "conversation_output": conversation_output,
        "question": question
    })
    
    # Store in memory
    memory_db.store_memory(session_id, "user", question)
    memory_db.store_memory(session_id, "assistant", final_answer["text"])
    
    return {
        "answer": final_answer["text"],
        "session_id": session_id,
        "policy_output": policy_output,
        "conversation_output": conversation_output
    }
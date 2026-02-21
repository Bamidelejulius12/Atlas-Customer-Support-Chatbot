from langchain.chains import ConversationalRetrievalChain, RetrievalQA, LLMChain
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from src.utils.config import get_config
from src.vector_store.pinecone_client import get_policy_vectorstore, get_conversation_vectorstore

def get_llm():
    config = get_config()
    return ChatOpenAI(
        model=config["OPENAI_MODEL"],
        temperature=0,
        openai_api_key=config["OPENAI_API_KEY"]
    )

def create_policy_chain():
    llm = get_llm()
    policy_vectorstore = get_policy_vectorstore()
    
    policy_prompt = PromptTemplate(
        input_variables=["context", "question", "guest_type", "loyalty", "city"],
        template="""
        You are a POLICY INTERPRETATION AGENT for Atlas Horizon Hospitality.

        ROLE
        - Interpret hotel policies strictly and conservatively
        - Use ONLY the retrieved policy text
        - Never infer or soften policy language

        CONTEXT
        Guest Type: {guest_type}
        Loyalty Tier: {loyalty}
        City: {city}

        POLICY DOCUMENTS
        {context}

        USER QUESTION
        {question}

        OUTPUT FORMAT (JSON ONLY):
        {{
          "policy_facts": [string],
          "limitations": [string],
          "applicability": string,
          "confidence": number
        }}
        """
    )
    
    return ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=policy_vectorstore.as_retriever(),
        combine_docs_chain_kwargs={"prompt": policy_prompt},
        return_source_documents=False
    )









def create_conversation_chain():
    llm = get_llm()
    conversation_vectorstore = get_conversation_vectorstore()
    
    conversation_prompt = PromptTemplate(
        input_variables=["context", "question"],
        template="""
        You are an agent that analyses historical conversations, read through how the agent handled similar questions in the past,
        and answer your USER QUESTION based on that.

        ROLE
        - Analyze how similar guest questions were historically handled
        - Focus on tone, escalation patterns, uncertainty handling
        - Also get how the questions were resolved by analyzing the conversations relating to the question
        - DO NOT invent policy

        HISTORICAL CONVERSATIONS
        {context}

        USER QUESTION
        {question}

        OUTPUT FORMAT (JSON ONLY):
        {{
          "observed_patterns": string,
          "response_style": string,
          "conversation": string,
          "confidence": number
        }}
        """
    )
    
    return RetrievalQA.from_chain_type(
        llm=llm,
        retriever=conversation_vectorstore.as_retriever(),
        chain_type_kwargs={"prompt": conversation_prompt},
        return_source_documents=False
    )






def create_aggregator_chain():
    llm = get_llm()
    
    aggregator_prompt = PromptTemplate(
        input_variables=["policy_output", "conversation_output", "question"],
        template="""
        You are the FINAL RESPONSE AGENT for Atlas Horizon.
        Your role is to generate the best possible customer-facing answer by combining policy rules with real historical agent–guest conversations.
        Ensure that your final answer is in English.

        CORE PRINCIPLES
        - Policy output defines what is allowed and disallowed. Never violate it.
        - Conversation output provides real-world context, explanations, exceptions, and phrasing that may not be explicitly stated in the policy.
        - If the conversation output contains additional details not present in the policy, you may use them only if they do not contradict policy.
        - When policy is unclear or confidence is below 0.7, adopt careful, conditional language.
        - If conversation and policy differ, policy always overrides facts, but conversation can still guide tone and explanation depth.
        - If ambiguity remains, recommend confirming with support or the property.

        INPUTS
        Policy Agent Output (authoritative rules):
        {policy_output}

        Conversation Agent Output (how similar questions were answered in real customer-care interactions):
        {conversation_output}

        User Question:
        {question}

        TASK
        Synthesize a final response that:
        - Is factually compliant with policy
        - Reflects how agents have historically explained or handled this situation
        - Sounds natural, human, and helpful
        - Includes clarifications or caveats when needed

        FINAL ANSWER REQUIREMENTS
        - Length: 2–4 sentences
        - Tone: clear, calm, customer-friendly
        - Do not mention internal agents, policies, or confidence scores
        - If uncertainty exists, gently suggest confirmation

        FINAL ANSWER:
        """
    )
    
    return LLMChain(llm=llm, prompt=aggregator_prompt)
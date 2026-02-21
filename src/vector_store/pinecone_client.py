from pinecone import Pinecone
from langchain_pinecone import PineconeVectorStore
from src.utils.config import get_config
from src.vector_store.embeddings import get_embeddings

def init_pinecone():
    config = get_config()
    pc = Pinecone(api_key=config["PINECONE_API_KEY"])
    return pc

def get_policy_vectorstore():
    config = get_config()
    embeddings = get_embeddings()
    pc = init_pinecone()
    
    # Check if index exists
    if config["PINECONE_INDEX_NAME"] not in [i.name for i in pc.list_indexes()]:
        pc.create_index(
            name=config["PINECONE_INDEX_NAME"],
            dimension=1536,
            metric="cosine"
        )
    
    return PineconeVectorStore.from_existing_index(
        index_name=config["PINECONE_INDEX_NAME"],
        embedding=embeddings
    )

def get_conversation_vectorstore():
    config = get_config()
    embeddings = get_embeddings()
    pc = init_pinecone()
    
    # Check if index exists
    if config["PINECONE_CONVERSATION_INDEX"] not in [i.name for i in pc.list_indexes()]:
        pc.create_index(
            name=config["PINECONE_CONVERSATION_INDEX"],
            dimension=1536,
            metric="cosine"
        )
    
    return PineconeVectorStore.from_existing_index(
        index_name=config["PINECONE_CONVERSATION_INDEX"],
        embedding=embeddings
    )
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uvicorn
from src.agents.aggregator_agent import agentic_rag_answer
from src.database.memory_db import ConversationMemory

app = FastAPI(title="Hotel Chatbot API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8501",
        "http://127.0.0.1:8501",
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class ChatRequest(BaseModel):
    question: str
    guest_type: str
    loyalty: str
    city: str
    session_id: str

class ChatResponse(BaseModel):
    answer: str
    session_id: str
    success: bool

class ClearMemoryRequest(BaseModel):
    session_id: str

# Initialize memory database
memory_db = ConversationMemory()

@app.get("/")
async def root():
    return {"message": "Hotel Chatbot API is running"}

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        result = await agentic_rag_answer(
            question=request.question,
            guest_type=request.guest_type,
            loyalty=request.loyalty,
            city=request.city,
            session_id=request.session_id
        )
        
        return ChatResponse(
            answer=result["answer"],
            session_id=request.session_id,
            success=True
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/history/{session_id}")
async def get_history(session_id: str):
    try:
        history_tuples = memory_db.get_chat_history_tuples(session_id)
        history_text = memory_db.get_chat_history_text(session_id)
        
        return {
            "session_id": session_id,
            "history_tuples": history_tuples,
            "history_text": history_text,
            "success": True
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/clear_memory")
async def clear_memory(request: ClearMemoryRequest):
    try:
        memory_db.clear_memory(request.session_id)
        return {"message": "Memory cleared", "session_id": request.session_id, "success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
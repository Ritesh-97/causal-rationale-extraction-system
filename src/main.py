"""
Main application entry point for the Causal Rationale Extraction System
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
from dotenv import load_dotenv
from .system import get_system

load_dotenv()

app = FastAPI(
    title="Causal Rationale Extraction System",
    description="System for extracting causal rationales from conversational data",
    version="1.0.0"
)


class QueryRequest(BaseModel):
    query: str
    conversation_id: Optional[str] = None
    context: Optional[List[Dict[str, Any]]] = None


class QueryResponse(BaseModel):
    response: str
    evidence: List[Dict[str, Any]]
    conversation_id: str
    metadata: Optional[Dict[str, Any]] = None


@app.on_event("startup")
async def startup_event():
    """Initialize system on startup"""
    # Initialize system (lazy loading) - non-blocking
    try:
        # Don't block startup - system will initialize on first request
        pass
    except Exception as e:
        print(f"Warning: System initialization error: {e}")


@app.get("/")
async def root():
    return {
        "message": "Causal Rationale Extraction System API",
        "version": "1.0.0",
        "endpoints": {
            "/query": "Process a query (Task 1 or Task 2)",
            "/query/follow-up": "Process a follow-up query (Task 2)",
            "/health": "Health check"
        }
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """
    Process a natural language query about business events.
    Supports both Task 1 (initial queries) and Task 2 (follow-up queries).
    """
    try:
        system = get_system()
        result = system.process_query(
            query=request.query,
            conversation_id=request.conversation_id,
            context=request.context
        )
        
        # Extract conversation ID from result or generate one
        conversation_id = result.get('metadata', {}).get('conversation_id')
        if not conversation_id:
            conversation_id = request.conversation_id or "default"
        
        return QueryResponse(
            response=result.get('response', ''),
            evidence=result.get('evidence', []),
            conversation_id=conversation_id,
            metadata=result.get('metadata', {})
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")


@app.post("/query/follow-up", response_model=QueryResponse)
async def process_followup(request: QueryRequest):
    """
    Process a follow-up query with context from previous conversation.
    """
    if not request.conversation_id:
        raise HTTPException(
            status_code=400,
            detail="conversation_id is required for follow-up queries"
        )
    
    try:
        system = get_system()
        result = system.process_followup(
            query=request.query,
            conversation_id=request.conversation_id,
            context=request.context
        )
        
        formatted = system.followup_processor.format_response(result)
        
        return QueryResponse(
            response=formatted.get('response', ''),
            evidence=formatted.get('evidence', []),
            conversation_id=request.conversation_id,
            metadata=formatted.get('metadata', {})
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing follow-up: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


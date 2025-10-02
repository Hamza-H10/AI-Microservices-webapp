"""
Conversational AI Microservice
FastAPI service for chatbot functionality using LangChain, LangGraph, and Gemini AI
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uvicorn
from datetime import datetime
import psutil
import time
import os
from collections import defaultdict
import asyncio

# LangChain and LangGraph imports
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from typing_extensions import Annotated, TypedDict

# Initialize FastAPI app
app = FastAPI(
    title="Conversational AI Service",
    description="FastAPI microservice for conversational AI using LangChain, LangGraph, and Gemini",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["*"],
)

# Global variables
llm = None
chat_graph = None

# Metrics tracking
metrics = {
    "total_messages": 0,
    "total_conversations": 0,
    "total_processing_time": 0.0,
    "average_response_time": 0.0,
    "startup_time": time.time()
}

# Pydantic models


class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str
    timestamp: Optional[str] = None


class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    chat_history: Optional[List[ChatMessage]] = []


class ChatResponse(BaseModel):
    message: str
    conversation_id: str
    timestamp: str
    processing_time: float


class ConversationState(TypedDict):
    messages: Annotated[list, add_messages]
    conversation_id: str

# LangGraph state and nodes


class ChatBot:
    def __init__(self, model: ChatGoogleGenerativeAI):
        self.model = model
        self.system_prompt = """You are a helpful, friendly, and knowledgeable AI assistant. 
        You provide accurate, helpful responses while maintaining a conversational tone. 
        You can discuss a wide range of topics and help users with various tasks.
        
        Key guidelines:
        - Be helpful and informative
        - Maintain context from previous messages in the conversation
        - Ask clarifying questions when needed
        - Provide step-by-step explanations for complex topics
        - Be concise but thorough in your responses
        """

    async def chat_node(self, state: ConversationState) -> ConversationState:
        """Main chat processing node"""
        messages = state["messages"]

        # Add system message if this is the start of conversation
        if len(messages) == 1:  # Only user message
            system_msg = SystemMessage(content=self.system_prompt)
            messages = [system_msg] + messages

        # Get response from LLM
        response = await self.model.ainvoke(messages)

        # Update state with AI response
        updated_messages = messages + [response]

        return {
            "messages": updated_messages,
            "conversation_id": state["conversation_id"]
        }


def create_chat_graph(llm_model: ChatGoogleGenerativeAI) -> StateGraph:
    """Create the LangGraph chat workflow"""
    chatbot = ChatBot(llm_model)

    # Create the graph
    workflow = StateGraph(ConversationState)

    # Add nodes
    workflow.add_node("chat", chatbot.chat_node)

    # Set entry point
    workflow.set_entry_point("chat")

    # Add edges
    workflow.add_edge("chat", END)

    # Compile the graph
    return workflow.compile()


@app.on_event("startup")
async def startup_event():
    """Initialize the conversational AI model and graph on startup."""
    global llm, chat_graph

    print("🤖 Initializing Conversational AI service...")

    # Get Gemini API key from environment
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        print("⚠️  Warning: GEMINI_API_KEY not found in environment variables")
        print("   Please set your Gemini API key to use the chatbot functionality")
        return

    try:
        # Initialize Gemini LLM
        llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=gemini_api_key,
            temperature=0.7,
            max_tokens=1000,
            timeout=30
        )

        # Create LangGraph workflow
        chat_graph = create_chat_graph(llm)

        print("✅ Conversational AI model loaded successfully!")
        print("🔗 AI Service ready! Web interface: http://localhost:3000")

    except Exception as e:
        print(f"❌ Failed to initialize Conversational AI: {str(e)}")
        llm = None
        chat_graph = None


@app.get("/")
async def root():
    """Root endpoint returning basic AI service info."""
    return {
        "service": "Conversational AI Microservice",
        "version": "1.0.0",
        "status": "active",
        "model": "gemini-1.5-flash",
        "framework": "LangChain + LangGraph",
        "model_loaded": llm is not None,
        "endpoints": {
            "chat": "/chat - POST: Send message to chatbot",
            "health": "/health - GET: Check API health",
            "metrics": "/metrics - GET: Performance metrics",
            "docs": "/docs - GET: API documentation"
        },
        "note": "This is a conversational AI microservice. Web interface available at http://localhost:3000"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for microservices monitoring."""
    return {
        "status": "healthy",
        "service": "Conversational AI Microservice",
        "model_loaded": llm is not None,
        "graph_ready": chat_graph is not None,
        "gemini_configured": os.getenv("GEMINI_API_KEY") is not None,
        "timestamp": datetime.now().isoformat(),
        "web_interface": "http://localhost:3000"
    }


@app.get("/metrics")
async def get_metrics():
    """Get system metrics and performance stats."""
    # Get system metrics
    cpu_percent = psutil.cpu_percent(interval=0.1)
    memory = psutil.virtual_memory()

    # Calculate uptime
    uptime_seconds = time.time() - metrics["startup_time"]

    return {
        "timestamp": datetime.now().isoformat(),
        "uptime_seconds": round(uptime_seconds, 2),
        "system": {
            "cpu_percent": cpu_percent,
            "memory_total_gb": round(memory.total / (1024**3), 2),
            "memory_used_gb": round(memory.used / (1024**3), 2),
            "memory_percent": memory.percent
        },
        "performance": {
            "total_messages": metrics["total_messages"],
            "total_conversations": metrics["total_conversations"],
            "total_processing_time": round(metrics["total_processing_time"], 3),
            "average_response_time": round(metrics["average_response_time"], 3),
            "messages_per_second": round(metrics["total_messages"] / max(uptime_seconds, 1), 2)
        },
        "model": {
            "name": "gemini-1.5-flash",
            "provider": "Google Generative AI",
            "framework": "LangChain + LangGraph",
            "loaded": llm is not None,
            "graph_ready": chat_graph is not None
        }
    }


@app.post("/chat", response_model=ChatResponse)
async def chat_with_ai(request: ChatRequest):
    """Chat with the AI assistant using LangGraph workflow."""
    if llm is None or chat_graph is None:
        raise HTTPException(
            status_code=503,
            detail="Conversational AI model not loaded. Please check if GEMINI_API_KEY is set."
        )

    start_time = time.time()

    try:
        # Generate conversation ID if not provided
        conversation_id = request.conversation_id or f"conv_{int(time.time())}_{id(request)}"

        # Convert chat history to LangChain messages
        messages = []
        for msg in request.chat_history:
            if msg.role == "user":
                messages.append(HumanMessage(content=msg.content))
            elif msg.role == "assistant":
                messages.append(AIMessage(content=msg.content))

        # Add current user message
        messages.append(HumanMessage(content=request.message))

        # Create initial state
        initial_state = ConversationState(
            messages=messages,
            conversation_id=conversation_id
        )

        # Run the LangGraph workflow
        result = await chat_graph.ainvoke(initial_state)

        # Extract AI response
        ai_message = result["messages"][-1].content

        # Update metrics
        processing_time = time.time() - start_time
        metrics["total_messages"] += 1
        metrics["total_processing_time"] += processing_time
        if request.conversation_id is None:
            metrics["total_conversations"] += 1
        metrics["average_response_time"] = metrics["total_processing_time"] / \
            metrics["total_messages"]

        return ChatResponse(
            message=ai_message,
            conversation_id=conversation_id,
            timestamp=datetime.now().isoformat(),
            processing_time=round(processing_time, 3)
        )

    except Exception as e:
        print(f"Error in chat processing: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error processing chat: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )

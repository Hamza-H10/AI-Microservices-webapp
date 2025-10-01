from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from transformers import pipeline
import torch
from typing import List
import uvicorn
from datetime import datetime

# Initialize FastAPI app for microservices
app = FastAPI(
    title="Sentiment Analysis AI Service",
    description="FastAPI microservice for GPU-accelerated sentiment analysis",
    version="1.0.0"
)

# Add CORS middleware for Node.js communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Global variable to store the model
classifier = None


class TextInput(BaseModel):
    text: str


class SentimentResponse(BaseModel):
    text: str
    sentiment: str
    confidence: float
    timestamp: str


class BatchTextInput(BaseModel):
    texts: List[str]


@app.on_event("startup")
async def startup_event():
    """Initialize the sentiment analysis model on startup."""
    global classifier
    print("🤖 Loading sentiment analysis model...")
    classifier = pipeline(
        task="sentiment-analysis",
        model="distilbert-base-uncased-finetuned-sst-2-english",
        device=0 if torch.cuda.is_available() else -1
    )
    device_name = "GPU (CUDA)" if torch.cuda.is_available() else "CPU"
    print(f"✅ Model loaded successfully on {device_name}!")
    print(f"🔗 AI Service ready! Web interface: http://localhost:3000")


@app.get("/")
async def root():
    """Root endpoint returning basic AI service info."""
    return {
        "service": "Sentiment Analysis AI Microservice",
        "version": "1.0.0",
        "status": "active",
        "model": "distilbert-base-uncased-finetuned-sst-2-english",
        "device": "GPU (CUDA)" if torch.cuda.is_available() else "CPU",
        "endpoints": {
            "analyze": "/analyze - POST: Analyze single text",
            "batch_analyze": "/batch-analyze - POST: Analyze multiple texts",
            "health": "/health - GET: Check API health",
            "docs": "/docs - GET: API documentation"
        },
        "note": "This is an AI microservice. Web interface available at http://localhost:3000"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for microservices monitoring."""
    return {
        "status": "healthy",
        "service": "AI Microservice",
        "model_loaded": classifier is not None,
        "cuda_available": torch.cuda.is_available(),
        "gpu_device": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
        "timestamp": datetime.now().isoformat(),
        "web_interface": "http://localhost:3000"
    }


@app.post("/analyze", response_model=SentimentResponse)
async def analyze_sentiment(text_input: TextInput):
    """Analyze sentiment of a single text."""
    if classifier is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    try:
        result = classifier(text_input.text)[0]

        return SentimentResponse(
            text=text_input.text,
            sentiment=result['label'],
            confidence=result['score'],
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Analysis failed: {str(e)}")


@app.post("/batch-analyze")
async def batch_analyze_sentiment(batch_input: BatchTextInput):
    """Analyze sentiment of multiple texts."""
    if classifier is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    if len(batch_input.texts) > 100:
        raise HTTPException(
            status_code=400, detail="Maximum 100 texts allowed per batch")

    try:
        results = classifier(batch_input.texts)
        timestamp = datetime.now().isoformat()

        responses = []
        for i, result in enumerate(results):
            responses.append(SentimentResponse(
                text=batch_input.texts[i],
                sentiment=result['label'],
                confidence=result['score'],
                timestamp=timestamp
            ))

        return {"results": responses, "count": len(responses)}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Batch analysis failed: {str(e)}")

if __name__ == "__main__":
    print("🚀 Starting FastAPI AI Microservice...")
    print("🌐 Web interface will be available at: http://localhost:3000")
    print("🤖 AI service will be available at: http://localhost:8000")
    print("📚 API docs will be available at: http://localhost:8000/docs")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

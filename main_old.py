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
    print("Loading sentiment analysis model...")
    classifier = pipeline(
        task="sentiment-analysis",
        model="distilbert-base-uncased-finetuned-sst-2-english",
        device=0 if torch.cuda.is_available() else -1
    )
    device_name = "GPU (CUDA)" if torch.cuda.is_available() else "CPU"
    print(f"Model loaded successfully on {device_name}!")


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
            "health": "/health - GET: Check API health"
        },
        "note": "This is an AI microservice. Web interface available at http://localhost:3000"
    }
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


@app.get("/web", response_class=HTMLResponse)
async def get_web_interface():
    """Serve the web interface."""
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Sentiment Analysis Tool</title>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
            }
            .container {
                background: white;
                border-radius: 15px;
                padding: 30px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            }
            h1 {
                text-align: center;
                color: #333;
                margin-bottom: 30px;
            }
            .input-section {
                margin-bottom: 30px;
            }
            textarea {
                width: 100%;
                padding: 15px;
                border: 2px solid #ddd;
                border-radius: 10px;
                font-size: 16px;
                resize: vertical;
                min-height: 100px;
                box-sizing: border-box;
            }
            button {
                background: linear-gradient(45deg, #667eea, #764ba2);
                color: white;
                border: none;
                padding: 12px 30px;
                border-radius: 25px;
                font-size: 16px;
                cursor: pointer;
                margin: 10px 5px;
                transition: transform 0.2s;
            }
            button:hover {
                transform: translateY(-2px);
            }
            button:disabled {
                opacity: 0.6;
                cursor: not-allowed;
            }
            .result {
                margin: 20px 0;
                padding: 20px;
                border-radius: 10px;
                border-left: 5px solid;
            }
            .positive {
                background: #d4edda;
                border-color: #28a745;
                color: #155724;
            }
            .negative {
                background: #f8d7da;
                border-color: #dc3545;
                color: #721c24;
            }
            .charts-container {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 20px;
                margin-top: 30px;
            }
            .chart-box {
                background: #f8f9fa;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            .history {
                margin-top: 30px;
            }
            .history-item {
                padding: 10px;
                margin: 10px 0;
                background: #f8f9fa;
                border-radius: 8px;
                border-left: 4px solid;
            }
            .loading {
                text-align: center;
                color: #666;
            }
            @media (max-width: 768px) {
                .charts-container {
                    grid-template-columns: 1fr;
                }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Sentiment Analysis Tool</h1>
            
            <div class="input-section">
                <textarea id="textInput" placeholder="Enter your text here to analyze sentiment..."></textarea>
                <br>
                <button onclick="analyzeSentiment()" id="analyzeBtn">🔍 Analyze Sentiment</button>
                <button onclick="clearAll()" id="clearBtn">🗑️ Clear All</button>
                <button onclick="addSampleTexts()" id="sampleBtn">📝 Load Samples</button>
            </div>
            
            <div id="result"></div>
            
            <div class="charts-container">
                <div class="chart-box">
                    <h3>Sentiment Distribution</h3>
                    <canvas id="sentimentChart" width="400" height="200"></canvas>
                </div>
                <div class="chart-box">
                    <h3>Confidence Over Time</h3>
                    <canvas id="confidenceChart" width="400" height="200"></canvas>
                </div>
            </div>
            
            <div class="history">
                <h3>Analysis History</h3>
                <div id="historyContainer"></div>
            </div>
        </div>
\\
        <script>
            let analysisHistory = [];
            let sentimentChart, confidenceChart;

            // Initialize charts
            function initCharts() {
                const sentimentCtx = document.getElementById('sentimentChart').getContext('2d');
                sentimentChart = new Chart(sentimentCtx, {
                    type: 'doughnut',
                    data: {
                        labels: ['Positive', 'Negative'],
                        datasets: [{
                            data: [0, 0],
                            backgroundColor: ['#28a745', '#dc3545'],
                            borderWidth: 2,
                            borderColor: '#fff'
                        }]
                    },
                    options: {
                        responsive: true,
                        plugins: {
                            legend: {
                                position: 'bottom'
                            }
                        }
                    }
                });

                const confidenceCtx = document.getElementById('confidenceChart').getContext('2d');
                confidenceChart = new Chart(confidenceCtx, {
                    type: 'line',
                    data: {
                        labels: [],
                        datasets: [{
                            label: 'Confidence Score',
                            data: [],
                            borderColor: '#667eea',
                            backgroundColor: 'rgba(102, 126, 234, 0.1)',
                            tension: 0.4,
                            fill: true
                        }]
                    },
                    options: {
                        responsive: true,
                        scales: {
                            y: {
                                beginAtZero: true,
                                max: 1
                            }
                        }
                    }
                });
            }

            // Analyze sentiment
            async function analyzeSentiment() {
                const text = document.getElementById('textInput').value.trim();
                if (!text) {
                    alert('Please enter some text to analyze!');
                    return;
                }

                const btn = document.getElementById('analyzeBtn');
                btn.disabled = true;
                btn.textContent = '🔄 Analyzing...';

                try {
                    const response = await fetch('/analyze', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({ text: text })
                    });

                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }

                    const result = await response.json();
                    displayResult(result);
                    addToHistory(result);
                    updateCharts();

                } catch (error) {
                    document.getElementById('result').innerHTML = 
                        `<div class="result negative">❌ Error: ${error.message}</div>`;
                } finally {
                    btn.disabled = false;
                    btn.textContent = '🔍 Analyze Sentiment';
                }
            }

            // Display result
            function displayResult(result) {
                const emoji = result.sentiment === 'POSITIVE' ? '😊' : '😞';
                const className = result.sentiment.toLowerCase();
                const confidence = (result.confidence * 100).toFixed(1);
                
                document.getElementById('result').innerHTML = `
                    <div class="result ${className}">
                        <h3>${emoji} ${result.sentiment}</h3>
                        <p><strong>Text:</strong> "${result.text}"</p>
                        <p><strong>Confidence:</strong> ${confidence}%</p>
                        <p><strong>Score:</strong> ${result.confidence.toFixed(4)}</p>
                    </div>
                `;
            }

            // Add to history
            function addToHistory(result) {
                analysisHistory.push(result);
                
                const historyContainer = document.getElementById('historyContainer');
                const emoji = result.sentiment === 'POSITIVE' ? '😊' : '😞';
                const className = result.sentiment.toLowerCase();
                
                const historyItem = document.createElement('div');
                historyItem.className = `history-item ${className}`;
                historyItem.style.borderLeftColor = result.sentiment === 'POSITIVE' ? '#28a745' : '#dc3545';
                historyItem.innerHTML = `
                    <strong>${emoji} ${result.sentiment}</strong> (${(result.confidence * 100).toFixed(1)}%) - 
                    "${result.text.substring(0, 100)}${result.text.length > 100 ? '...' : ''}"
                `;
                
                historyContainer.insertBefore(historyItem, historyContainer.firstChild);
                
                // Keep only last 10 items in display
                if (historyContainer.children.length > 10) {
                    historyContainer.removeChild(historyContainer.lastChild);
                }
            }

            // Update charts
            function updateCharts() {
                // Update sentiment distribution
                const positive = analysisHistory.filter(r => r.sentiment === 'POSITIVE').length;
                const negative = analysisHistory.filter(r => r.sentiment === 'NEGATIVE').length;
                
                sentimentChart.data.datasets[0].data = [positive, negative];
                sentimentChart.update();

                // Update confidence chart
                const recentData = analysisHistory.slice(-10);
                confidenceChart.data.labels = recentData.map((_, i) => `#${i + 1}`);
                confidenceChart.data.datasets[0].data = recentData.map(r => r.confidence);
                confidenceChart.update();
            }

            // Clear all data
            function clearAll() {
                if (confirm('Are you sure you want to clear all data?')) {
                    analysisHistory = [];
                    document.getElementById('textInput').value = '';
                    document.getElementById('result').innerHTML = '';
                    document.getElementById('historyContainer').innerHTML = '';
                    
                    sentimentChart.data.datasets[0].data = [0, 0];
                    sentimentChart.update();
                    
                    confidenceChart.data.labels = [];
                    confidenceChart.data.datasets[0].data = [];
                    confidenceChart.update();
                }
            }

            // Add sample texts
            function addSampleTexts() {
                const samples = [
                    "I love using this amazing tool!",
                    "This is terrible and doesn't work.",
                    "The weather is okay today.",
                    "Absolutely fantastic experience!",
                    "I'm feeling a bit sad.",
                    "This is the best day ever!"
                ];
                
                const randomSample = samples[Math.floor(Math.random() * samples.length)];
                document.getElementById('textInput').value = randomSample;
            }

            // Enter key to analyze
            document.getElementById('textInput').addEventListener('keypress', function(e) {
                if (e.key === 'Enter' && e.ctrlKey) {
                    analyzeSentiment();
                }
            });

            // Initialize when page loads
            window.addEventListener('load', function() {
                initCharts();
            });
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

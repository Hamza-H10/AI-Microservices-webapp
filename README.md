# AI Microservices Webapp - Conversational AI & Sentiment Analysis

A modern microservices-based web application featuring conversational AI chatbot and sentiment analysis, built with Node.js/Express frontend and FastAPI AI backends with GPU acceleration.

## 🚀 Features

### Conversational AI Chatbot

- **ChatGPT-style Interface**: Modern chat interface with typing indicators and message threading
- **LangChain & LangGraph**: Advanced conversational AI workflow management
- **Google Gemini Integration**: Powered by Google's Gemini 1.5 Flash model
- **Persistent Chat History**: Browser-based localStorage for conversation continuity
- **Real-time Streaming**: Live response generation with typing indicators

### Sentiment Analysis

- **Real-time Analysis**: Instant sentiment analysis with confidence scores
- **Batch Processing**: Analyze multiple texts simultaneously
- **GPU-Accelerated AI**: CUDA-enabled PyTorch for fast processing
- **Interactive Visualization**: Charts and metrics display

### Platform Features

- **Microservices Architecture**: Scalable service-oriented design
- **Modern Web Interface**: Responsive HTML5 frontend with navigation
- **Health Monitoring**: Service health checks and status endpoints
- **CORS Support**: Cross-origin resource sharing for seamless API communication

## 🏗️ Project Structure

```
AI-Microservices-webapp/
├── microservices/
│   ├── sentiment-analysis/          # Sentiment Analysis AI Microservice
│   │   ├── main.py                  # FastAPI application
│   │   ├── sentiment_analysis.py    # Core sentiment analysis logic
│   │   ├── gpu_benchmark.py         # GPU performance testing
│   │   ├── requirements.txt         # Python dependencies
│   │   ├── Dockerfile              # Container configuration
│   │   └── README.md               # Service documentation
│   └── conversational-ai/          # Conversational AI Microservice
│       ├── main.py                  # FastAPI chatbot application
│       ├── requirements.txt         # Python AI dependencies
│       └── Dockerfile              # Container configuration
├── web-service/                    # Node.js Web Service
│   ├── src/
│   │   └── server.ts               # Express server with API routing
│   ├── public/
│   │   ├── index.html              # Conversational AI chat interface
│   │   └── sentiment.html          # Sentiment analysis interface
│   ├── package.json                # Node.js dependencies
│   ├── tsconfig.json              # TypeScript configuration
│   └── Dockerfile                 # Container configuration
├── docker-compose.yml             # Multi-service orchestration
├── .env.example                   # Environment variables template
├── README.md                      # Main documentation
└── models/                        # Model cache (created at runtime)
```

## 🏗️ Architecture

```
┌─────────────────┐
│   Chat UI       │    HTTP/REST     ┌─────────────────┐
│ (index.html)    │ ◄──────────────► │  Node.js/Express│
└─────────────────┘                  │   Web Gateway   │
                                     │   (Port 3000)   │
┌─────────────────┐                  └─────────┬───────┘
│ Sentiment UI    │                            │
│(sentiment.html) │ ◄──────────────────────────┘
└─────────────────┘                            │
                                               │ Proxy APIs
                         ┌─────────────────────┼─────────────────────┐
                         ▼                     ▼                     ▼
               ┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐
               │Conversational AI│   │ Sentiment Analysis│   │  Future Services│
               │  Microservice   │   │   Microservice   │   │      (TBD)      │
               │   (Port 8001)   │   │   (Port 8000)   │   │                 │
               │ LangChain+Gemini│   │  GPU-Accelerated │   │                 │
               └─────────────────┘   └─────────────────┘   └─────────────────┘
```

### Microservices Overview

- **Web Gateway** (`web-service/`): Node.js/Express frontend with TypeScript and API routing
- **Conversational AI** (`microservices/conversational-ai/`): FastAPI chatbot with LangChain, LangGraph, and Google Gemini
- **Sentiment Analysis** (`microservices/sentiment-analysis/`): FastAPI AI service with transformer models
- **Future Services**: Architecture ready for additional microservices (e.g., text summarization, translation, etc.)

## 📋 Prerequisites

- **Node.js** (v16 or higher)
- **Python** (3.11 recommended)
- **Google Gemini API Key** ([Get it here](https://makersuite.google.com/app/apikey))
- **CUDA-compatible GPU** (optional, for GPU acceleration)
- **Git**

## 🛠️ Installation

### 1. Clone the Repository

```bash
git clone https://github.com/Hamza-H10/AI-Microservices-webapp.git
cd AI-Microservices-webapp
```

### 2. Set Up Environment Variables

```bash
# Copy the environment template
cp .env.example .env

# Edit .env and add your Google Gemini API key
# GEMINI_API_KEY=your_actual_api_key_here
```

### 3. Install Dependencies

#### Web Service (Node.js)

```bash
cd web-service
npm install
```

#### Sentiment Analysis Microservice (Python)

```bash
cd microservices/sentiment-analysis
pip install -r requirements.txt
```

#### Conversational AI Microservice (Python)

```bash
cd microservices/conversational-ai
pip install -r requirements.txt
```

## 🚀 Running the Application

### Option 1: Docker (Recommended)

Run the entire application with one command:

```bash
docker-compose up --build
```

Services will be available at:

- **Web Interface**: `http://localhost:3000`
- **Sentiment Analysis API**: `http://localhost:8000`
- **API Documentation**: `http://localhost:8000/docs`

### Option 2: Development Mode

1. **Start the Sentiment Analysis Microservice**:

   ```bash
   cd microservices/sentiment-analysis
   python main.py
   ```

   The AI service will be available at `http://localhost:8000`

2. **Start the Web Server**:
   ```bash
   cd web-service
   npm run dev
   ```
   The web application will be available at `http://localhost:3000`

### Option 3: Production Mode

1. **Build and Start Web Service**:

   ```bash
   cd web-service
   npm run build
   npm start
   ```

2. **Start the AI Service**:

   ```bash
   cd microservices/sentiment-analysis
   python main.py
   ```

3. **Start the Web Server**:

   ```bash

   ```

## 🔧 Available Scripts

### Web Service (Node.js)

```bash
cd web-service
npm run dev      # Start development server with hot reload
npm run build    # Build TypeScript to JavaScript
npm start        # Start production server
npm run watch    # Watch TypeScript files for changes
```

### Sentiment Analysis Microservice (Python)

```bash
cd microservices/sentiment-analysis
python main.py                  # Start FastAPI microservice
python sentiment_analysis.py    # Standalone sentiment analysis
python gpu_benchmark.py         # GPU performance benchmarking
```

### Docker Commands

```bash
# Start all services
docker-compose up --build

# Start in background
docker-compose up -d

# Stop all services
docker-compose down

# View logs
docker-compose logs -f

# Individual service logs
docker-compose logs -f sentiment-analysis
docker-compose logs -f web-service
```

## 📚 API Endpoints

### Sentiment Analysis Microservice (Port 8000)

| Endpoint   | Method | Description                    |
| ---------- | ------ | ------------------------------ |
| `/`        | GET    | Service information            |
| `/health`  | GET    | Health check                   |
| `/metrics` | GET    | System and performance metrics |
| `/analyze` | POST   | Single text sentiment analysis |
| `/batch`   | POST   | Batch text sentiment analysis  |
| `/docs`    | GET    | Interactive API documentation  |

#### Example API Usage

**Single Analysis**:

```bash
curl -X POST "http://localhost:8000/analyze" \
     -H "Content-Type: application/json" \
     -d '{"text": "I love this product!"}'
```

**Batch Analysis**:

```bash
curl -X POST "http://localhost:8000/batch" \
     -H "Content-Type: application/json" \
     -d '{"texts": ["Great product!", "Terrible service", "Average experience"]}'
```

### Node.js Web Service (Port 3000)

| Endpoint       | Method | Description             |
| -------------- | ------ | ----------------------- |
| `/`            | GET    | Web interface           |
| `/api/health`  | GET    | Combined health check   |
| `/api/analyze` | POST   | Proxy to AI service     |
| `/api/batch`   | POST   | Proxy to batch analysis |

## 🔬 Technology Stack

### Frontend

- **HTML5/CSS3/JavaScript**: Modern web interface
- **Chart.js**: Data visualization
- **Responsive Design**: Mobile-friendly UI

### Backend (Node.js)

- **Express.js**: Web framework
- **TypeScript**: Type-safe JavaScript
- **Axios**: HTTP client for API communication
- **CORS**: Cross-origin resource sharing
- **Helmet**: Security middleware
- **Morgan**: HTTP request logger

### AI Service (Python)

- **FastAPI**: Modern Python web framework
- **Transformers**: Hugging Face transformers library
- **PyTorch**: Deep learning framework with CUDA support
- **Pydantic**: Data validation using Python type annotations
- **Uvicorn**: ASGI server

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the root directory:

```env
# Node.js Web Server
PORT=3000
NODE_ENV=development

# FastAPI AI Service
AI_SERVICE_URL=http://localhost:8000
FASTAPI_PORT=8000

# GPU Settings
CUDA_VISIBLE_DEVICES=0
```

### GPU Configuration

The application automatically detects and uses CUDA-enabled GPUs when available. For CPU-only mode, the system will fall back gracefully.

## 📊 Performance

- **GPU Acceleration**: Up to 10x faster inference with CUDA
- **Batch Processing**: Efficient handling of multiple texts
- **Asynchronous Processing**: Non-blocking API calls
- **Connection Pooling**: Optimized HTTP client connections

## 🧪 Testing

### Test the AI Service

```bash
python -c "import torch; print(f'CUDA Available: {torch.cuda.is_available()}')"
python gpu_benchmark.py
```

### Test the Web Service

Visit `http://localhost:3000` and try the sentiment analysis interface.

## 🐳 Docker Support

### Prerequisites for Docker

- **Docker** (v20.10 or higher)
- **Docker Compose** (v2.0 or higher)
- **NVIDIA Docker** (for GPU support) - Install [nvidia-container-toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html)

### Quick Start with Docker

1. **Clone and navigate to the project**:

   ```bash
   git clone https://github.com/Hamza-H10/AI-Microservices-webapp.git
   cd AI-Microservices-webapp
   ```

2. **Build and run with Docker Compose**:

   ```bash
   docker-compose up --build
   ```

3. **Access the services**:
   - Web Interface: `http://localhost:3000`
   - AI API: `http://localhost:8000`
   - API Docs: `http://localhost:8000/docs`

### Docker Commands

```bash
# Build and start all services
docker-compose up --build

# Start services in background
docker-compose up -d

# Stop all services
docker-compose down

# View logs
docker-compose logs -f

# View logs for specific service
docker-compose logs -f ai-service
docker-compose logs -f web-service

# Rebuild specific service
docker-compose build ai-service
docker-compose build web-service

# Run without GPU support (CPU only)
docker-compose -f docker-compose.yml up --build
```

### Individual Service Builds

**AI Service (FastAPI)**:

```bash
docker build -f Dockerfile.ai -t sentiment-ai-service .
docker run -p 8000:8000 --gpus all sentiment-ai-service
```

**Web Service (Node.js)**:

```bash
docker build -f Dockerfile.web -t sentiment-web-service .
docker run -p 3000:3000 sentiment-web-service
```

### Docker Architecture

The application uses a multi-container setup:

- **`ai-service`**: Python FastAPI with CUDA support (Dockerfile.ai)
- **`web-service`**: Node.js/Express with TypeScript (Dockerfile.web)
- **Network**: Bridge network for inter-service communication
- **Volumes**: Model caching for improved performance
- **Health Checks**: Automatic service health monitoring

### GPU Support in Docker

The configuration includes NVIDIA GPU support for accelerated inference:

```yaml
deploy:
  resources:
    reservations:
      devices:
        - driver: nvidia
          count: 1
          capabilities: [gpu]
```

For CPU-only deployment, remove the `deploy` section from `docker-compose.yml`.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Troubleshooting

### Common Issues

1. **CUDA Out of Memory**:

   - Reduce batch size in the AI service
   - Use CPU mode by setting `CUDA_VISIBLE_DEVICES=""`

2. **Port Already in Use**:

   - Check if ports 3000 or 8000 are occupied
   - Modify port configuration in scripts

3. **Dependencies Issues**:
   - Ensure Python 3.11 and Node.js v16+ are installed
   - Try clearing npm cache: `npm cache clean --force`

### Support

For issues and questions, please open an issue in the GitHub repository.

---

**Happy Analyzing! 🚀📊**

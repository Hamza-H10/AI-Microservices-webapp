# AI Microservices Webapp - Sentiment Analysis

A modern microservices-based web application for sentiment analysis, featuring a Node.js/Express frontend and a FastAPI AI backend with GPU acceleration.

## 🚀 Features

- **Microservices Architecture**: Separate Node.js web server and FastAPI AI service
- **GPU-Accelerated AI**: CUDA-enabled PyTorch for fast sentiment analysis
- **Real-time Analysis**: Instant sentiment analysis with confidence scores
- **Batch Processing**: Analyze multiple texts simultaneously
- **Modern Web Interface**: Interactive HTML5 frontend with charts and visualization
- **Health Monitoring**: Service health checks and status endpoints
- **CORS Support**: Cross-origin resource sharing for seamless API communication

## 🏗️ Architecture

```
┌─────────────────┐    HTTP/REST    ┌─────────────────┐
│   Frontend      │ ◄────────────── │  Node.js/Express│
│   (HTML/JS)     │                 │   Web Server    │
└─────────────────┘                 │   (Port 3000)   │
                                    └─────────┬───────┘
                                              │ HTTP API
                                              ▼
                                    ┌─────────────────┐
                                    │   FastAPI AI    │
                                    │   Microservice  │
                                    │   (Port 8000)   │
                                    │  GPU-Accelerated │
                                    └─────────────────┘
```

## 📋 Prerequisites

- **Node.js** (v16 or higher)
- **Python** (3.11 recommended)
- **CUDA-compatible GPU** (optional, for GPU acceleration)
- **Git**

## 🛠️ Installation

### 1. Clone the Repository

```bash
git clone https://github.com/Hamza-H10/AI-Microservices-webapp.git
cd AI-Microservices-webapp
```

### 2. Install Node.js Dependencies

```bash
npm install
```

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

## 🚀 Running the Application

### Option 1: Development Mode (Recommended)

1. **Start the AI Microservice (FastAPI)**:

   ```bash
   python main.py
   ```

   The AI service will be available at `http://localhost:8000`

2. **Start the Web Server (Node.js)**:
   ```bash
   npm run dev
   ```
   The web application will be available at `http://localhost:3000`

### Option 2: Production Mode

1. **Build the TypeScript**:

   ```bash
   npm run build
   ```

2. **Start the AI Service**:

   ```bash
   python main.py
   ```

3. **Start the Web Server**:
   ```bash
   npm start
   ```

## 🔧 Available Scripts

### Node.js Scripts

- `npm run dev` - Start development server with hot reload
- `npm run build` - Build TypeScript to JavaScript
- `npm start` - Start production server
- `npm run watch` - Watch TypeScript files for changes

### Python Scripts

- `python main.py` - Start FastAPI AI microservice
- `python sentiment_analysis.py` - Standalone sentiment analysis script
- `python gpu_benchmark.py` - GPU performance benchmarking

## 📚 API Endpoints

### FastAPI AI Service (Port 8000)

| Endpoint   | Method | Description                    |
| ---------- | ------ | ------------------------------ |
| `/`        | GET    | Service information            |
| `/health`  | GET    | Health check                   |
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

### Docker Compose (Recommended)

```yaml
version: "3.8"
services:
  ai-service:
    build: .
    ports:
      - "8000:8000"
    command: python main.py

  web-service:
    build: .
    ports:
      - "3000:3000"
    command: npm start
    depends_on:
      - ai-service
```

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

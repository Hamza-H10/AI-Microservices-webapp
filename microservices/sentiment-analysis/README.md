# Sentiment Analysis Microservice

A FastAPI-based microservice for GPU-accelerated sentiment analysis using transformer models.

## 🚀 Features

- **High-Performance**: GPU acceleration with CUDA support
- **Transformer Models**: Uses DistilBERT for sentiment classification
- **RESTful API**: FastAPI with automatic OpenAPI documentation
- **Metrics Monitoring**: Built-in performance and system metrics
- **Health Checks**: Service health monitoring endpoints
- **Scalable**: Designed for microservices architecture

## 📋 API Endpoints

| Endpoint   | Method | Description                    |
| ---------- | ------ | ------------------------------ |
| `/`        | GET    | Service information            |
| `/health`  | GET    | Health check                   |
| `/metrics` | GET    | System and performance metrics |
| `/analyze` | POST   | Single text sentiment analysis |
| `/batch`   | POST   | Batch text sentiment analysis  |
| `/docs`    | GET    | Interactive API documentation  |

## 🔧 Installation

### Local Development

1. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

2. **Run the service**:
   ```bash
   python main.py
   ```

### Docker

1. **Build the image**:

   ```bash
   docker build -t sentiment-analysis .
   ```

2. **Run the container**:

   ```bash
   # CPU only
   docker run -p 8000:8000 sentiment-analysis

   # With GPU support
   docker run --gpus all -p 8000:8000 sentiment-analysis
   ```

## 📊 Usage Examples

### Single Text Analysis

```bash
curl -X POST "http://localhost:8000/analyze" \
     -H "Content-Type: application/json" \
     -d '{"text": "I love this product!"}'
```

Response:

```json
{
  "text": "I love this product!",
  "sentiment": "POSITIVE",
  "confidence": 0.9998,
  "timestamp": "2025-10-02T10:30:00"
}
```

### Batch Analysis

```bash
curl -X POST "http://localhost:8000/batch" \
     -H "Content-Type: application/json" \
     -d '{"texts": ["Great service!", "Terrible experience", "Average quality"]}'
```

### Health Check

```bash
curl "http://localhost:8000/health"
```

### System Metrics

```bash
curl "http://localhost:8000/metrics"
```

## ⚙️ Configuration

### Environment Variables

- `CUDA_VISIBLE_DEVICES`: GPU device selection (default: 0)
- `MODEL_NAME`: Transformer model name (default: distilbert-base-uncased-finetuned-sst-2-english)
- `MAX_LENGTH`: Maximum text length (default: 512)
- `BATCH_SIZE`: Batch processing size (default: 8)

### Model Configuration

The service uses DistilBERT by default, but can be configured to use other transformer models:

```python
# In main.py
classifier = pipeline(
    task="sentiment-analysis",
    model="distilbert-base-uncased-finetuned-sst-2-english",
    device=0 if torch.cuda.is_available() else -1
)
```

## 📈 Performance

- **GPU Acceleration**: Up to 10x faster inference with CUDA
- **Batch Processing**: Efficient handling of multiple texts
- **Memory Optimization**: Automatic memory management
- **Caching**: Model caching for faster startup

## 🔍 Monitoring

The service provides comprehensive metrics:

- **System Metrics**: CPU, Memory, GPU utilization
- **Performance Metrics**: Request count, response times, throughput
- **Model Metrics**: Token processing, inference times
- **Health Status**: Service availability and model status

## 🐳 Docker Support

### CPU-only Image

```dockerfile
FROM ubuntu:22.04
# ... rest of Dockerfile
```

### GPU-enabled Image

```dockerfile
FROM nvidia/cuda:11.8-devel-ubuntu22.04
# ... rest of Dockerfile
```

## 🧪 Testing

```bash
# Run basic tests
python -m pytest

# Test with sample data
python sentiment_analysis.py

# GPU benchmark
python gpu_benchmark.py
```

## 🔧 Development

### Adding New Models

1. Update the model name in `main.py`
2. Install model-specific dependencies
3. Test the model performance
4. Update the API documentation

### Scaling

The microservice is designed to scale horizontally:

- Stateless design
- Health check endpoints
- Resource monitoring
- Container-ready

## 📝 License

This microservice is part of the AI-Microservices-webapp project and follows the same license terms.

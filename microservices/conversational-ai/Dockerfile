# Conversational AI Microservice Dockerfile
# Docker configuration for LangChain, LangGraph, and Gemini integration

# Use Ubuntu base image
FROM ubuntu:22.04

# Metadata
LABEL maintainer="AI-Microservices-webapp"
LABEL description="Conversational AI Microservice with LangChain, LangGraph, and Gemini"
LABEL version="1.0.0"

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONPATH=/app

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-dev \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN python3 -m pip install --upgrade pip

# Copy requirements first for better Docker layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy application code
COPY main.py .

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash app && \
    chown -R app:app /app
USER app

# Expose port
EXPOSE 8001

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8001/health || exit 1

# Run the FastAPI application
CMD ["python3", "main.py"]
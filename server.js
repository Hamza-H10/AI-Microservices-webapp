const express = require('express');
const axios = require('axios');
const cors = require('cors');
const helmet = require('helmet');
const morgan = require('morgan');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3000;
const FASTAPI_URL = process.env.FASTAPI_URL || 'http://localhost:8000';

// Middleware
app.use(helmet({
    contentSecurityPolicy: {
        directives: {
            defaultSrc: ["'self'"],
            styleSrc: ["'self'", "'unsafe-inline'", "https://cdn.jsdelivr.net"],
            scriptSrc: ["'self'", "'unsafe-inline'", "https://cdn.jsdelivr.net"],
            imgSrc: ["'self'", "data:", "https:"],
        },
    },
}));
app.use(cors());
app.use(morgan('combined'));
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true }));

// Serve static files
app.use(express.static(path.join(__dirname, 'public')));

// Health check for Node.js service
app.get('/health', (req, res) => {
    res.json({
        status: 'healthy',
        service: 'Node.js/Express Web Server',
        timestamp: new Date().toISOString(),
        fastapi_url: FASTAPI_URL
    });
});

// Proxy route for FastAPI health check
app.get('/api/health', async (req, res) => {
    try {
        const response = await axios.get(`${FASTAPI_URL}/health`, {
            timeout: 5000
        });
        res.json({
            web_service: 'healthy',
            ai_service: response.data
        });
    } catch (error) {
        res.status(503).json({
            web_service: 'healthy',
            ai_service: 'unavailable',
            error: error.message
        });
    }
});

// Proxy route for sentiment analysis
app.post('/api/analyze', async (req, res) => {
    try {
        const { text } = req.body;
        
        if (!text || text.trim().length === 0) {
            return res.status(400).json({
                error: 'Text is required and cannot be empty'
            });
        }

        if (text.length > 5000) {
            return res.status(400).json({
                error: 'Text too long. Maximum 5000 characters allowed.'
            });
        }

        // Forward request to FastAPI service
        const response = await axios.post(`${FASTAPI_URL}/analyze`, {
            text: text.trim()
        }, {
            timeout: 30000,
            headers: {
                'Content-Type': 'application/json'
            }
        });

        // Log the analysis for monitoring
        console.log(`[${new Date().toISOString()}] Analyzed text: "${text.substring(0, 50)}..." -> ${response.data.sentiment} (${response.data.confidence.toFixed(4)})`);

        res.json(response.data);

    } catch (error) {
        console.error('Error calling FastAPI service:', error.message);
        
        if (error.code === 'ECONNREFUSED') {
            return res.status(503).json({
                error: 'AI service is currently unavailable. Please try again later.',
                details: 'Unable to connect to sentiment analysis service'
            });
        }

        if (error.response) {
            // FastAPI returned an error
            return res.status(error.response.status).json({
                error: 'AI service error',
                details: error.response.data
            });
        }

        if (error.code === 'ENOTFOUND') {
            return res.status(503).json({
                error: 'AI service configuration error',
                details: 'Cannot resolve AI service hostname'
            });
        }

        res.status(500).json({
            error: 'Internal server error',
            details: 'An unexpected error occurred while processing your request'
        });
    }
});

// Proxy route for batch analysis
app.post('/api/batch-analyze', async (req, res) => {
    try {
        const { texts } = req.body;
        
        if (!Array.isArray(texts) || texts.length === 0) {
            return res.status(400).json({
                error: 'Texts array is required and cannot be empty'
            });
        }

        if (texts.length > 100) {
            return res.status(400).json({
                error: 'Too many texts. Maximum 100 texts allowed per batch.'
            });
        }

        // Validate each text
        for (let i = 0; i < texts.length; i++) {
            if (typeof texts[i] !== 'string' || texts[i].trim().length === 0) {
                return res.status(400).json({
                    error: `Text at index ${i} is invalid or empty`
                });
            }
        }

        // Forward request to FastAPI service
        const response = await axios.post(`${FASTAPI_URL}/batch-analyze`, {
            texts: texts.map(text => text.trim())
        }, {
            timeout: 60000,
            headers: {
                'Content-Type': 'application/json'
            }
        });

        console.log(`[${new Date().toISOString()}] Batch analyzed ${texts.length} texts`);

        res.json(response.data);

    } catch (error) {
        console.error('Error calling FastAPI batch service:', error.message);
        
        if (error.code === 'ECONNREFUSED') {
            return res.status(503).json({
                error: 'AI service is currently unavailable. Please try again later.',
                details: 'Unable to connect to sentiment analysis service'
            });
        }

        if (error.response) {
            return res.status(error.response.status).json({
                error: 'AI service error',
                details: error.response.data
            });
        }

        res.status(500).json({
            error: 'Internal server error',
            details: 'An unexpected error occurred while processing batch request'
        });
    }
});

// Serve main web interface
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// API information endpoint
app.get('/api', (req, res) => {
    res.json({
        service: 'Sentiment Analysis Web Service',
        version: '1.0.0',
        endpoints: {
            'GET /': 'Web interface',
            'GET /health': 'Node.js service health',
            'GET /api/health': 'Combined health check (Node.js + FastAPI)',
            'POST /api/analyze': 'Analyze single text sentiment',
            'POST /api/batch-analyze': 'Analyze multiple texts sentiment'
        },
        microservices: {
            web_service: `http://localhost:${PORT}`,
            ai_service: FASTAPI_URL
        }
    });
});

// 404 handler
app.use('*', (req, res) => {
    res.status(404).json({
        error: 'Not Found',
        message: `The requested endpoint ${req.originalUrl} was not found`,
        available_endpoints: [
            'GET /',
            'GET /health',
            'GET /api',
            'GET /api/health',
            'POST /api/analyze',
            'POST /api/batch-analyze'
        ]
    });
});

// Error handler
app.use((err, req, res, next) => {
    console.error('Unhandled error:', err);
    res.status(500).json({
        error: 'Internal Server Error',
        message: 'An unexpected error occurred'
    });
});

// Start server
app.listen(PORT, () => {
    console.log(`🚀 Node.js/Express Web Server running on http://localhost:${PORT}`);
    console.log(`🔗 FastAPI AI Service URL: ${FASTAPI_URL}`);
    console.log(`📊 Web Interface: http://localhost:${PORT}`);
    console.log(`🏥 Health Check: http://localhost:${PORT}/health`);
    console.log(`🤖 AI Health Check: http://localhost:${PORT}/api/health`);
    console.log('\n📋 Microservices Architecture:');
    console.log(`   ├── Web Service (Node.js): :${PORT}`);
    console.log(`   └── AI Service (FastAPI): :8000`);
    console.log('\n🛠️  Make sure FastAPI service is running on port 8000!');
});

module.exports = app;
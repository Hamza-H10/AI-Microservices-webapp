import express, { Request, Response, NextFunction, Application } from 'express';
import axios, { AxiosError } from 'axios';
import cors from 'cors';
import helmet from 'helmet';
import morgan from 'morgan';
import path from 'path';

// Types
interface HealthResponse {
    status: string;
    service: string;
    timestamp: string;
    fastapi_url?: string;
}

interface CombinedHealthResponse {
    web_service: string;
    ai_service: any;
    error?: string;
}

interface AnalyzeRequest {
    text: string;
}

interface AnalyzeResponse {
    sentiment: string;
    confidence: number;
    text: string;
}

interface BatchAnalyzeRequest {
    texts: string[];
}

interface BatchAnalyzeResponse {
    results: AnalyzeResponse[];
    processed_count: number;
}

interface ErrorResponse {
    error: string;
    details?: string;
    message?: string;
    available_endpoints?: string[];
}

interface ApiInfoResponse {
    service: string;
    version: string;
    endpoints: Record<string, string>;
    microservices: {
        web_service: string;
        sentiment_analysis: string;
        conversational_ai: string;
    };
}

const app: Application = express();
const PORT: number = parseInt(process.env.PORT || '3000', 10);
const SENTIMENT_ANALYSIS_URL: string = process.env.AI_SERVICE_URL || process.env.FASTAPI_URL || 'http://localhost:8000';
const CONVERSATIONAL_AI_URL: string = process.env.CONVERSATIONAL_AI_URL || 'http://localhost:8001';

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
app.use(express.static(path.join(__dirname, '../public')));

// Health check for Node.js service
app.get('/health', (req: Request, res: Response): void => {
    const healthResponse: HealthResponse = {
        status: 'healthy',
        service: 'Node.js/Express Web Server',
        timestamp: new Date().toISOString(),
        fastapi_url: SENTIMENT_ANALYSIS_URL
    };
    res.json(healthResponse);
});

// Proxy route for FastAPI health check
app.get('/api/health', async (req: Request, res: Response): Promise<void> => {
    try {
        const response = await axios.get(`${SENTIMENT_ANALYSIS_URL}/health`, {
            timeout: 5000
        });
        const healthResponse: CombinedHealthResponse = {
            web_service: 'healthy',
            ai_service: response.data
        };
        res.json(healthResponse);
    } catch (error) {
        const axiosError = error as AxiosError;
        const errorResponse: CombinedHealthResponse = {
            web_service: 'healthy',
            ai_service: 'unavailable',
            error: axiosError.message
        };
        res.status(503).json(errorResponse);
    }
});

// Proxy route for metrics
app.get('/api/metrics', async (req: Request, res: Response): Promise<void> => {
    try {
        const response = await axios.get(`${SENTIMENT_ANALYSIS_URL}/metrics`, {
            timeout: 5000
        });
        res.json(response.data);
    } catch (error) {
        const axiosError = error as AxiosError;
        const errorResponse = {
            error: 'Failed to fetch metrics from AI service',
            details: axiosError.message,
            timestamp: new Date().toISOString()
        };
        res.status(503).json(errorResponse);
    }
});

// Proxy route for conversational AI chat
app.post('/api/chat', async (req: Request, res: Response): Promise<void> => {
    try {
        const response = await axios.post(`${CONVERSATIONAL_AI_URL}/chat`, req.body, {
            timeout: 30000,
            headers: {
                'Content-Type': 'application/json'
            }
        });
        res.json(response.data);
    } catch (error) {
        const axiosError = error as AxiosError;
        const errorResponse = {
            error: 'Failed to communicate with conversational AI service',
            details: axiosError.message,
            timestamp: new Date().toISOString()
        };
        res.status(503).json(errorResponse);
    }
});

// Proxy route for sentiment analysis
app.post('/api/analyze', async (req: Request, res: Response): Promise<void> => {
    try {
        const { text }: AnalyzeRequest = req.body;

        if (!text || text.trim().length === 0) {
            const errorResponse: ErrorResponse = {
                error: 'Text is required and cannot be empty'
            };
            res.status(400).json(errorResponse);
            return;
        }

        if (text.length > 5000) {
            const errorResponse: ErrorResponse = {
                error: 'Text too long. Maximum 5000 characters allowed.'
            };
            res.status(400).json(errorResponse);
            return;
        }

        // Forward request to FastAPI service
        const response = await axios.post<AnalyzeResponse>(`${SENTIMENT_ANALYSIS_URL}/analyze`, {
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
        const axiosError = error as AxiosError;
        console.error('Error calling FastAPI service:', axiosError.message);

        if (axiosError.code === 'ECONNREFUSED') {
            const errorResponse: ErrorResponse = {
                error: 'AI service is currently unavailable. Please try again later.',
                details: 'Unable to connect to sentiment analysis service'
            };
            res.status(503).json(errorResponse);
            return;
        }

        if (axiosError.response) {
            // FastAPI returned an error
            const errorResponse: ErrorResponse = {
                error: 'AI service error',
                details: axiosError.response.data as string
            };
            res.status(axiosError.response.status).json(errorResponse);
            return;
        }

        if (axiosError.code === 'ENOTFOUND') {
            const errorResponse: ErrorResponse = {
                error: 'AI service configuration error',
                details: 'Cannot resolve AI service hostname'
            };
            res.status(503).json(errorResponse);
            return;
        }

        const errorResponse: ErrorResponse = {
            error: 'Internal server error',
            details: 'An unexpected error occurred while processing your request'
        };
        res.status(500).json(errorResponse);
    }
});

// Proxy route for batch analysis
app.post('/api/batch-analyze', async (req: Request, res: Response): Promise<void> => {
    try {
        const { texts }: BatchAnalyzeRequest = req.body;

        if (!Array.isArray(texts) || texts.length === 0) {
            const errorResponse: ErrorResponse = {
                error: 'Texts array is required and cannot be empty'
            };
            res.status(400).json(errorResponse);
            return;
        }

        if (texts.length > 100) {
            const errorResponse: ErrorResponse = {
                error: 'Too many texts. Maximum 100 texts allowed per batch.'
            };
            res.status(400).json(errorResponse);
            return;
        }

        // Validate each text
        for (let i = 0; i < texts.length; i++) {
            if (typeof texts[i] !== 'string' || texts[i].trim().length === 0) {
                const errorResponse: ErrorResponse = {
                    error: `Text at index ${i} is invalid or empty`
                };
                res.status(400).json(errorResponse);
                return;
            }
        }

        // Forward request to FastAPI service
        const response = await axios.post<BatchAnalyzeResponse>(`${SENTIMENT_ANALYSIS_URL}/batch-analyze`, {
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
        const axiosError = error as AxiosError;
        console.error('Error calling FastAPI batch service:', axiosError.message);

        if (axiosError.code === 'ECONNREFUSED') {
            const errorResponse: ErrorResponse = {
                error: 'AI service is currently unavailable. Please try again later.',
                details: 'Unable to connect to sentiment analysis service'
            };
            res.status(503).json(errorResponse);
            return;
        }

        if (axiosError.response) {
            const errorResponse: ErrorResponse = {
                error: 'AI service error',
                details: axiosError.response.data as string
            };
            res.status(axiosError.response.status).json(errorResponse);
            return;
        }

        const errorResponse: ErrorResponse = {
            error: 'Internal server error',
            details: 'An unexpected error occurred while processing batch request'
        };
        res.status(500).json(errorResponse);
    }
});

// Serve main web interface (Chat page)
app.get('/', (req: Request, res: Response): void => {
    res.sendFile(path.join(__dirname, '../public', 'index.html'));
});

// Serve sentiment analysis page
app.get('/sentiment', (req: Request, res: Response): void => {
    res.sendFile(path.join(__dirname, '../public', 'sentiment.html'));
});

// API information endpoint
app.get('/api', (req: Request, res: Response): void => {
    const apiInfo: ApiInfoResponse = {
        service: 'AI Microservices Web Gateway',
        version: '1.0.0',
        endpoints: {
            'GET /': 'Conversational AI Chat Interface',
            'GET /sentiment': 'Sentiment Analysis Tool',
            'GET /health': 'Node.js service health',
            'GET /api/health': 'Combined health check (Node.js + FastAPI)',
            'POST /api/chat': 'Conversational AI chat endpoint',
            'POST /api/analyze': 'Analyze single text sentiment',
            'POST /api/batch-analyze': 'Analyze multiple texts sentiment'
        },
        microservices: {
            web_service: `http://localhost:${PORT}`,
            sentiment_analysis: SENTIMENT_ANALYSIS_URL,
            conversational_ai: CONVERSATIONAL_AI_URL
        }
    };
    res.json(apiInfo);
});

// 404 handler
app.use('*', (req: Request, res: Response): void => {
    const errorResponse: ErrorResponse = {
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
    };
    res.status(404).json(errorResponse);
});

// Error handler
app.use((err: Error, req: Request, res: Response, next: NextFunction): void => {
    console.error('Unhandled error:', err);
    const errorResponse: ErrorResponse = {
        error: 'Internal Server Error',
        message: 'An unexpected error occurred'
    };
    res.status(500).json(errorResponse);
});

// Start server
app.listen(PORT, (): void => {
    console.log(`🚀 Node.js/Express Web Server running on http://localhost:${PORT}`);
    console.log(`🔗 Sentiment Analysis Service URL: ${SENTIMENT_ANALYSIS_URL}`);
    console.log(`🤖 Conversational AI Service URL: ${CONVERSATIONAL_AI_URL}`);
    console.log(`📊 Chat Interface: http://localhost:${PORT}`);
    console.log(`📈 Sentiment Analysis: http://localhost:${PORT}/sentiment`);
    console.log(`🏥 Health Check: http://localhost:${PORT}/health`);
    console.log(`🤖 AI Health Check: http://localhost:${PORT}/api/health`);
    console.log('\n📋 Microservices Architecture:');
    console.log(`   ├── Web Service (Node.js): :${PORT}`);
    console.log(`   ├── Sentiment Analysis (FastAPI): :8000`);
    console.log(`   └── Conversational AI (FastAPI): :8001`);
    console.log('\n🛠️  Make sure both FastAPI services are running!');
});

export default app;
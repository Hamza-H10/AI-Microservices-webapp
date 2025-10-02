# Web Service Dockerfile
# Docker configuration for Node.js/Express web service

# Use official Node.js runtime as base image
FROM node:20-alpine

# Metadata
LABEL maintainer="AI-Microservices-webapp"
LABEL description="Web Service for AI Microservices webapp"
LABEL version="1.0.0"

# Set environment variables
ENV NODE_ENV=production

# Set working directory
WORKDIR /app

# Install system dependencies for building native modules
RUN apk add --no-cache python3 make g++

# Copy package files first for better caching
COPY package*.json ./
COPY tsconfig.json ./

# Install all dependencies (including dev dependencies for building)
RUN npm ci --include=dev

# Install TypeScript globally to ensure it's available
RUN npm install -g typescript

# Copy TypeScript source code
COPY src/ ./src/
COPY public/ ./public/

# Build TypeScript - now tsc should be globally available
RUN tsc

# Remove development dependencies to reduce image size
RUN npm prune --production

# Remove development dependencies to reduce image size
RUN npm prune --production

# Create non-root user for security
RUN addgroup -g 1001 -S nodejs
RUN adduser -S nextjs -u 1001

# Change ownership of the app directory
RUN chown -R nextjs:nodejs /app
USER nextjs

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=20s --retries=3 \
    CMD curl -f http://localhost:3000/api/health || exit 1

# Start the application
CMD ["npm", "start"]
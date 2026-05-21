# Stage 1: Build React frontend
FROM node:20-alpine AS frontend-builder
WORKDIR /app
COPY frontend/package*.json ./frontend/
RUN cd frontend && npm ci
COPY frontend/ ./frontend/
RUN cd frontend && npm run build

# Stage 2: Python runtime
FROM python:3.11-slim

# Install ffmpeg (required for audio extraction)
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy built frontend
COPY --from=frontend-builder /app/frontend/dist /app/frontend/dist

# Copy backend code
COPY api/ /app/api/
COPY database/ /app/database/
COPY modules/ /app/modules/
COPY utils/ /app/utils/

# Copy requirements and install
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Download spaCy model
RUN python -m spacy download en_core_web_sm

# HF Spaces: use /data for persistent storage (DB + uploads)
ENV DATABASE_PATH=/data/app.db
ENV UPLOAD_DIR=/data/uploads
ENV TEMP_DIR=/data/temp
ENV REPORTS_DIR=/data/reports

# Create data directories
RUN mkdir -p /data/uploads /data/temp /data/reports

# Listen on HF's PORT env var (default 7860)
EXPOSE 7860
ENV PORT=7860

CMD uvicorn api.server:app --host 0.0.0.0 --port $PORT

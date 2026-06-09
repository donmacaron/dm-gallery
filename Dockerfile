FROM python:3.12-slim

# Install ffmpeg (for video thumbnails in Phase 2)
RUN apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install dependencies first (leverages Docker layer cache)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/
COPY migrations/ ./migrations/
COPY alembic.ini .

# Create data directories (will be overridden by Docker volumes)
RUN mkdir -p /app/data/media /app/data/db /app/data/zips /app/data/originals

# Run DB migrations then start the server
# Increased timeout (600s) for large file uploads, 2 workers for better concurrency
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2 --timeout-keep-alive 600 "]

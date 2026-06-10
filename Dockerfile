FROM python:3.12-slim

WORKDIR /app

# Build tools + Pillow system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ libjpeg-dev zlib1g-dev libpng-dev libfreetype6-dev \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip first to avoid resolver issues
RUN pip install --upgrade pip

COPY requirements.txt .

# Install with verbose logging so Cloud Logging captures the exact failure
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080

# Use uvicorn to serve the FastAPI upload app
CMD ["sh", "-c", "uvicorn app:app --host 0.0.0.0 --port ${PORT:-8080}"]

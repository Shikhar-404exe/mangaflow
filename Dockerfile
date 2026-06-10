FROM python:3.12-slim

WORKDIR /app

# Install system build tools + Pillow dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ \
    libjpeg-dev zlib1g-dev libpng-dev libfreetype6-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Use verbose pip so Cloud Build logs show exactly which package fails
RUN pip install --no-cache-dir -v -r requirements.txt 2>&1

COPY . .

EXPOSE 8080

CMD ["sh", "-c", "adk web agents/ --host 0.0.0.0 --port ${PORT:-8080} --no-reload --session_service_uri=memory://"]

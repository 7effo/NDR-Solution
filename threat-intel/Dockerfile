FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY config/ ./config/

# Create data directory
RUN mkdir -p /app/data

ENV PYTHONPATH=/app

CMD ["python", "-m", "src.main"]

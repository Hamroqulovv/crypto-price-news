FROM python:3.11-slim

# Install minimal deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy only requirements first to take advantage of Docker layer cache
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the app
COPY . /app

# Expose port if you use webhooks (not necessary for polling bot)
# EXPOSE 8080

# Default env var file location (can be overridden by docker-compose or docker run --env-file)
ENV PYTHONUNBUFFERED=1

# Run the bot
CMD ["python", "main.py"]

# Project Validation Service Docker Image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the validation service
COPY . .

# Create placeholder for app_analyzer (will be available via shared volume or import)
RUN touch app_analyzer.py

# Create non-root user
RUN useradd -m -u 1000 validator && chown -R validator:validator /app
USER validator

# Expose port
EXPOSE 8002

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8002/ || exit 1

# Run the service
CMD ["python", "main.py"]

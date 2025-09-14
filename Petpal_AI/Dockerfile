# Minimal, production-friendly Django image
FROM python:3.11-slim

# Prevent Python from writing .pyc files / buffering stdout
ENV PYTHONDONTWRITEBYTECODE=1     PYTHONUNBUFFERED=1

# System deps for mysqlclient and build tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    default-libmysqlclient-dev \
    pkg-config \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Workdir inside the container
WORKDIR /app

# Install Python deps first (better layer caching)
COPY requirements.txt /app/requirements.txt
RUN python -m pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /app/requirements.txt

# Copy the rest of the project
COPY . /app

# Expose Django default port
EXPOSE 8000

# Default command is set from docker-compose.yml

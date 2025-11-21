# Minimal, production-friendly Django image
FROM python:3.11-slim

# Prevent Python from writing .pyc files / buffering stdout
ENV PYTHONDONTWRITEBYTECODE=1     PYTHONUNBUFFERED=1

# --- vvvv นี่คือ Block ที่แก้ไข vvvv ---
# System deps + Node.js
RUN apt-get update && apt-get install -y --no-install-recommends \
    # 1. System deps (จากไฟล์เดิมของคุณ)
    build-essential \
    default-libmysqlclient-dev \
    pkg-config \
    curl \
    # 2. เพิ่ม gpg (จำเป็นสำหรับ NodeSource)
    gpg \
    && \
    # 3. เพิ่ม Node.js 20.x repository (LTS)
    curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | gpg --dearmor -o /usr/share/keyrings/nodesource.gpg && \
    echo "deb [signed-by=/usr/share/keyrings/nodesource.gpg] https://deb.nodesource.com/node_20.x nodistro main" | tee /etc/apt/sources.list.d/nodesource.list && \
    # 4. อัปเดต list อีกครั้ง และติดตั้ง nodejs
    apt-get update && apt-get install -y --no-install-recommends \
    nodejs \
    && \
    # 5. ล้าง cache (จากไฟล์เดิม)
    rm -rf /var/lib/apt/lists/*
# --- ^^^^ สิ้นสุด Block ที่แก้ไข ^^^^ ---


# Workdir inside the container
WORKDIR /app

# Install Python deps first (better layer caching)
COPY requirements.txt /app/requirements.txt 
RUN python -m pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /app/requirements.txt

# Copy the rest of the project
COPY . /app

WORKDIR /app/theme/static_src
RUN npm install
WORKDIR /app


# Expose Django default port
EXPOSE 8000

# Default command is set from docker-compose.yml

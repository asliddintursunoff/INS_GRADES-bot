# -----------------------------
# Base image
# -----------------------------
FROM python:3.12-slim

# -----------------------------
# Set environment variables
# -----------------------------
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1

# -----------------------------
# Set work directory
# -----------------------------
WORKDIR /app

# -----------------------------
# Copy project files
# -----------------------------
COPY . /app

# -----------------------------
# Install dependencies
# -----------------------------
RUN apt-get update && apt-get install -y \
    build-essential \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

RUN python -m pip install --upgrade pip setuptools wheel

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# -----------------------------
# Expose port (not strictly needed for Telegram bot)
# -----------------------------
EXPOSE 8080

# -----------------------------
# Run bot
# -----------------------------
CMD ["python", "bot.py"]

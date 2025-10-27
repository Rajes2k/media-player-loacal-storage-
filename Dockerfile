# Use an official Python image with Debian (we control system packages)
FROM python:3.11-slim

# Install ffmpeg and build tools required by some wheels
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential ffmpeg libsm6 libxext6 && \
    rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy requirements first (for better caching)
COPY requirements.txt /app/requirements.txt

# Upgrade pip and install dependencies
RUN python -m pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# Copy app source
COPY . /app

# Expose port
EXPOSE 10000

# Start
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:10000", "--workers", "2"]

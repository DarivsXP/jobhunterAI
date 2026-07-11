# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Install system dependencies for Playwright
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers
RUN playwright install chromium
RUN playwright install-deps chromium

# Create persistent data directory.
# On Hugging Face Spaces, mount /data as a persistent volume in Space settings.
# Locally this just acts as a regular folder.
RUN mkdir -p /data

# Copy the rest of the application code
COPY . .

# Expose the port Hugging Face Spaces expects (7860)
EXPOSE 7860

# Set DATABASE_PATH to the persistent volume location.
# Override this with an HF Space Secret if you want a different path.
ENV DATABASE_PATH=/data/jobs.db

# Auto-restart wrapper: if Python crashes, wait 5 s and relaunch
CMD ["sh", "-c", "while true; do python web_server.py; echo 'Server exited — restarting in 5s...'; sleep 5; done"]

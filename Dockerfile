# POD Automation System Dockerfile

FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY . /app

# Install Python dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt

# Expose Streamlit dashboard port
EXPOSE 8501

# Set environment variables (override at runtime)
ENV PYTHONUNBUFFERED=1

# Default command: run the dashboard
CMD ["python3", "-m", "pod_automation.dashboard"]

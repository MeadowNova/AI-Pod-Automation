# Multi-stage build for POD Automation System

# Build stage
FROM python:3.12 as builder
WORKDIR /app
COPY requirements.txt .
RUN pip wheel --no-cache-dir -r requirements.txt

# Runtime stage
FROM python:3.12-slim
WORKDIR /app

# Create non-root user
RUN addgroup --system app && adduser --system --ingroup app appuser

# Copy wheels and install dependencies
COPY --from=builder /app /wheels
RUN pip install --no-index /wheels/*

# Copy application code
COPY . .

# Set non-root user
USER appuser

# Healthcheck endpoint (adjust port/path as needed)
HEALTHCHECK --interval=30s --timeout=3s CMD curl -f http://localhost:8000/health || exit 1

# Default command
CMD ["python", "main.py"]

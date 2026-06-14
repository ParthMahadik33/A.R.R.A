FROM python:3.12-slim

WORKDIR /app

# Install system dependencies (required for eventlet / greenlet compilation if needed)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend files
COPY backend/ ./backend/

# Expose port 7860 (Hugging Face Spaces default container port)
EXPOSE 7860

# Set environment variables
ENV HOST=0.0.0.0
ENV PORT=7860
ENV PYTHONUNBUFFERED=1

# Run the backend server
CMD ["python", "backend/main.py"]

# Use Python 3.11 slim image as base
FROM python:3.11-slim

# Set working directory in container
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy setup.py and requirements file first (if they exist)
COPY setup.py* requirements.txt* ./

# Copy source code (needed for setup.py)
COPY . .

# Install the package in development mode
RUN pip install --no-cache-dir -e .

# Install additional dependencies if requirements.txt exists
RUN if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi

# Expose the port the app runs on
EXPOSE 8000


# Command to run the application
CMD ["uvicorn", "examples.fastapi_server:app", "--host", "0.0.0.0", "--port", "8000"]


# gcloud builds submit -t us-central1-docker.pkg.dev/slamsportsai/slams/agui_adk

# gcloud run deploy agui-adk --image us-central1-docker.pkg.dev/slamsportsai/slams/agui_adk --platform managed --region us-central1 --allow-unauthenticated
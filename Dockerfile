FROM python:3.11-slim

WORKDIR /workspace

# Install system dependencies, including OpenMP (libomp) required by LightGBM and XGBoost
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libomp-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy and install python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application and reference assets
COPY app/ app/
COPY data/ data/
COPY training/ training/

# Expose ports for FastAPI (8000)
EXPOSE 8000

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV HOST=0.0.0.0
ENV PORT=8000

# Run FastAPI app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

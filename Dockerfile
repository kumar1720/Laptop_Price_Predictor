FROM python:3.11-slim

WORKDIR /workspace

# Install system dependencies, including OpenMP (libomp) required by LightGBM and XGBoost,
# as well as redis-server and curl for the unified single-server deployment.
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libomp-dev \
    redis-server \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy and install python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application and reference assets
COPY app/ app/
COPY data/ data/
COPY training/ training/
COPY app.py .
COPY start.sh .

# Make start.sh executable
RUN chmod +x start.sh

# Expose ports for FastAPI (8000 - local internal) and Streamlit (8501/Render public port)
EXPOSE 8000
EXPOSE 8501

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV HOST=0.0.0.0

# Run unified startup script
CMD ["./start.sh"]

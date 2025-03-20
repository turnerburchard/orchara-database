FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    python3-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy the ETL module first
COPY etl/ ./etl/

# Copy index files
COPY index/index.py index/index.py
COPY index/test_search.py index/test_search.py

# Copy requirements
COPY requirements.txt requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

# Add the current directory to PYTHONPATH
ENV PYTHONPATH=/app

CMD ["python", "index/index.py"]

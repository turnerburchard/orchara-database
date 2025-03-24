FROM python:3.13

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy ETL code
COPY etl/ ./etl/

CMD ["python", "etl/etl.py"]

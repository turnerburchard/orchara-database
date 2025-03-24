FROM python:3.13

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy code
COPY etl/ ./etl/
COPY common/ ./common/

CMD ["python", "etl/etl.py"]

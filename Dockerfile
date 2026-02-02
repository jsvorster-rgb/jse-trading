# Dockerfile for JSE Trading Project
FROM python:3.12-slim
WORKDIR /app

# Install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
env TP_SITE_ENV
COPY . .

# Default command: run the Sharenet scraper (override as needed)
CMD ["python3", "src/etl/sharenet_scraper.py"]

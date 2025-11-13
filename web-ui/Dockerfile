FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app.py .
COPY static/ ./static/
COPY templates/ ./templates/

EXPOSE 8080

CMD ["python", "-u", "app.py"]


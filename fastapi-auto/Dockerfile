FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .
EXPOSE 8001
CMD ["opentelemetry-instrument", "--traces_exporter", "otlp", "--service_name", "fastapi-app2", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8001"]
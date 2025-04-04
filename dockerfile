FROM python:3.9-slim

WORKDIR /app


COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir -p /app/model_cache && chmod 777 /app/model_cache

COPY . .

ENV TRANSFORMERS_CACHE=/app/model_cache

CMD ["python", "main.py"]

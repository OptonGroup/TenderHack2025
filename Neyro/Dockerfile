FROM python:3.10-slim

WORKDIR /app

# Устанавливаем необходимые пакеты
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Копируем файлы зависимостей
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем остальные файлы проекта
COPY . .

# Переменные среды
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DATABASE_URL="postgresql://postgres:postgres@db:5432/tenderhack"
ENV MODEL_PATH="/app/models"

# Открываем порт для API
EXPOSE 8000

# Запускаем API сервер
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"] 
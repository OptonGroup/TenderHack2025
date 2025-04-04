FROM python:3.10-slim

WORKDIR /app

# Установка необходимых системных пакетов
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Копирование файлов проекта
COPY requirements.txt .
COPY Backend/ ./Backend/

# Установка зависимостей
RUN pip install --no-cache-dir -r requirements.txt

# Создание директории для загрузки файлов
RUN mkdir -p /app/uploads/tenders

# Указываем переменные окружения по умолчанию
ENV DATABASE_URL=postgresql://admin:MI_TOCHNO_POBEDIM@109.73.195.217:5432/default_db
ENV DB_POOL_SIZE=5
ENV DB_MAX_OVERFLOW=10
ENV DB_POOL_TIMEOUT=30
ENV DB_POOL_RECYCLE=1800
ENV DEBUG=False
ENV LOG_LEVEL=INFO
ENV TG_BOT_TOKEN=""
ENV WEBHOOK_URL=""
ENV PORT=8000

# Создаем entrypoint скрипт для запуска сервера и бота
RUN echo '#!/bin/bash\n\
cd /app\n\
python -m Backend.server & SERVER_PID=$!\n\
python -m Backend.bot & BOT_PID=$!\n\
\n\
# Обработка сигналов завершения\n\
trap "kill $SERVER_PID $BOT_PID; exit" SIGINT SIGTERM\n\
\n\
# Ожидание завершения процессов\n\
wait $SERVER_PID $BOT_PID\n\
' > /app/entrypoint.sh

# Делаем скрипт исполняемым
RUN chmod +x /app/entrypoint.sh

# Открываем порт для FastAPI
EXPOSE $PORT

# Запускаем сервер и бота
CMD ["/app/entrypoint.sh"] 
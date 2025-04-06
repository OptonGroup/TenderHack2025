FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV TG_BOT_TOKEN=""
ENV API_URL="http://neyro:7777"
ENV DATABASE_URL="postgresql://postgres:postgres@db:5432/tenderhack"
CMD ["python", "bot.py"] 
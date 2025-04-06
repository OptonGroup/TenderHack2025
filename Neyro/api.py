import os
from typing import Dict, Any, Optional, List

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from sqlalchemy.orm import Session
import logging

from model import get_model, query_model
from database import SessionLocal, engine, Base

# Инициализация логгера
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Инициализация FastAPI приложения
app = FastAPI(title="TenderHack AI API")

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Настройка OAuth2 для авторизации
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Модели данных
class AIQuery(BaseModel):
    query: str

class AIResponse(BaseModel):
    answer: str
    needs_operator: bool = False

class ChatHistoryItem(BaseModel):
    user_id: int
    chat_id: str
    message: str
    is_bot: bool

class OperatorRequest(BaseModel):
    chat_id: str

# Зависимость для получения сессии БД
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Функция для проверки токена доступа
async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    # Здесь должна быть проверка токена
    # В рамках заготовки просто проверяем наличие токена
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Необходима авторизация",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"token": token}

# Инициализация модели
@app.on_event("startup")
async def startup_event():
    try:
        get_model()
        logger.info("Модель успешно загружена")
    except Exception as e:
        logger.error(f"Ошибка при загрузке модели: {e}")

# Роут для AI запросов
@app.post("/api/ai-query", response_model=AIResponse)
async def ai_query(query: AIQuery, current_user: Dict = Depends(get_current_user)):
    try:
        logger.info(f"Получен запрос: {query.query}")
        
        # Обработка запроса моделью
        answer, needs_operator = query_model(query.query)
        
        return AIResponse(answer=answer, needs_operator=needs_operator)
    except Exception as e:
        logger.error(f"Ошибка при обработке запроса: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при обработке запроса"
        )

# Роут для сохранения истории чата
@app.post("/api/chat-history")
async def save_chat_history(
    item: ChatHistoryItem,
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        # Реализация сохранения истории чата
        # Здесь должен быть код для сохранения в БД
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Ошибка при сохранении истории чата: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при сохранении истории чата"
        )

# Роут для получения истории чата
@app.get("/api/chat-history")
async def get_chat_history(
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        # Получение списка чатов
        # Здесь должен быть код для получения списка из БД
        return ["Чат 1", "Чат 2", "Чат 3"]  # Временная заглушка
    except Exception as e:
        logger.error(f"Ошибка при получении истории чата: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при получении истории чата"
        )

# Роут для вызова оператора
@app.post("/api/call-operator")
async def call_operator(
    request: OperatorRequest,
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        # Логика вызова оператора
        # Здесь должен быть код для записи запроса в БД или отправки уведомления
        return {"status": "success", "message": "Запрос оператора создан"}
    except Exception as e:
        logger.error(f"Ошибка при вызове оператора: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при вызове оператора"
        )

# Проверка работоспособности
@app.get("/api/health")
async def health_check():
    return {"status": "ok", "message": "Сервис работает"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True) 
from fastapi import FastAPI, Depends, HTTPException, status, File, UploadFile, Form, Path, Query, Body, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy.future import select
from sqlalchemy import func
from typing import List, Optional, Dict, Any
import uvicorn
from datetime import timedelta, datetime
import os
import shutil
from uuid import uuid4
import jwt
from jose import JWTError
from passlib.context import CryptContext
from pydantic import validate_arguments

from database import get_db, init_db
import models
import schemas
from auth import authenticate_user, create_access_token, get_current_active_user, ACCESS_TOKEN_EXPIRE_MINUTES, get_password_hash
from load_parquet_to_data import load_parquet_to_data

app = FastAPI(title="TenderHack API", version="1.0.0")


@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Эндпоинт для получения токена доступа через форму OAuth2
    """
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверное имя пользователя или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/api/login", response_model=schemas.LoginResponse)
async def login(login_data: schemas.LoginRequest, db: Session = Depends(get_db)):
    """
    Эндпоинт для входа пользователя через JSON
    """
    user = authenticate_user(db, login_data.username, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверное имя пользователя или пароль"
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.id,
        "username": user.username,
        "email": user.email
    }


@app.post("/api/register", response_model=schemas.User)
async def register_user(user_data: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Эндпоинт для регистрации нового пользователя
    """
    # Проверяем, существует ли пользователь с таким же username
    existing_user = db.query(models.User).filter(models.User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким именем уже существует"
        )
    
    # Проверяем, существует ли пользователь с таким же email
    existing_email = db.query(models.User).filter(models.User.email == user_data.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким email уже существует"
        )
    
    # Создаем нового пользователя
    hashed_password = get_password_hash(user_data.password)
    new_user = models.User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password,
        is_active=True
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user


@app.get("/api/users/me", response_model=schemas.User)
async def read_users_me(current_user: models.User = Depends(get_current_active_user)):
    """
    Получение информации о текущем пользователе
    """
    return current_user


@app.get("/api/users/{user_id}", response_model=schemas.User)
async def get_user_by_id(user_id: int, db: Session = Depends(get_db)):
    """
    Получение пользователя по ID
    """
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    return user


# Эндпоинты для работы с категориями
@app.get("/api/categories", response_model=List[schemas.Category])
async def get_categories(db: Session = Depends(get_db)):
    """
    Получение списка всех категорий
    """
    categories = db.query(models.Category).all()
    return categories


@app.post("/api/categories", response_model=schemas.Category)
async def create_category(category: schemas.CategoryCreate, 
                         current_user: models.User = Depends(get_current_active_user), 
                         db: Session = Depends(get_db)):
    """
    Создание новой категории
    """
    new_category = models.Category(**category.dict())
    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    return new_category


@app.get("/api/categories/{category_id}", response_model=schemas.Category)
async def get_category(category_id: int, db: Session = Depends(get_db)):
    """
    Получение категории по ID
    """
    category = db.query(models.Category).filter(models.Category.id == category_id).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Категория не найдена"
        )
    return category


# Эндпоинты для работы с тендерами
@app.get("/api/tenders", response_model=List[schemas.Tender])
async def get_tenders(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Получение списка всех тендеров
    """
    tenders = db.query(models.Tender).offset(skip).limit(limit).all()
    return tenders


@app.post("/api/tenders", response_model=schemas.Tender)
async def create_tender(tender: schemas.TenderCreate, 
                       current_user: models.User = Depends(get_current_active_user), 
                       db: Session = Depends(get_db)):
    """
    Создание нового тендера
    """
    new_tender = models.Tender(**tender.dict(), creator_id=current_user.id)
    db.add(new_tender)
    db.commit()
    db.refresh(new_tender)
    return new_tender


@app.get("/api/tenders/{tender_id}", response_model=schemas.TenderDetail)
async def get_tender(tender_id: int, db: Session = Depends(get_db)):
    """
    Получение информации о тендере по ID
    """
    tender = db.query(models.Tender).filter(models.Tender.id == tender_id).first()
    if not tender:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Тендер не найден"
        )
    return tender


@app.put("/api/tenders/{tender_id}", response_model=schemas.Tender)
async def update_tender(tender_id: int, 
                       tender_data: schemas.TenderUpdate, 
                       current_user: models.User = Depends(get_current_active_user), 
                       db: Session = Depends(get_db)):
    """
    Обновление информации о тендере
    """
    tender = db.query(models.Tender).filter(models.Tender.id == tender_id).first()
    if not tender:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Тендер не найден"
        )
    
    # Проверяем, что пользователь является создателем тендера
    if tender.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="У вас нет прав для обновления этого тендера"
        )
    
    # Обновляем поля тендера, если они предоставлены
    update_data = tender_data.dict(exclude_unset=True)
    
    if "category_id" in update_data:
        # Проверяем, существует ли указанная категория
        category = db.query(models.Category).filter(models.Category.id == update_data["category_id"]).first()
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Указанная категория не найдена"
            )
    
    for key, value in update_data.items():
        setattr(tender, key, value)
    
    db.commit()
    db.refresh(tender)
    
    return tender


# Эндпоинты для работы с заявками
@app.get("/api/bids", response_model=List[schemas.Bid])
async def get_user_bids(current_user: models.User = Depends(get_current_active_user), 
                       db: Session = Depends(get_db)):
    """
    Получение списка заявок текущего пользователя
    """
    bids = db.query(models.Bid).filter(models.Bid.bidder_id == current_user.id).all()
    return bids


@app.post("/api/bids", response_model=schemas.Bid)
async def create_bid(bid: schemas.BidCreate, 
                    current_user: models.User = Depends(get_current_active_user), 
                    db: Session = Depends(get_db)):
    """
    Создание новой заявки на тендер
    """
    new_bid = models.Bid(**bid.dict(), bidder_id=current_user.id)
    db.add(new_bid)
    db.commit()
    db.refresh(new_bid)
    return new_bid


@app.get("/api/tenders/{tender_id}/bids", response_model=List[schemas.Bid])
async def get_tender_bids(tender_id: int, 
                         current_user: models.User = Depends(get_current_active_user), 
                         db: Session = Depends(get_db)):
    """
    Получение списка заявок на тендер
    """
    tender = db.query(models.Tender).filter(models.Tender.id == tender_id).first()
    if not tender:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Тендер не найден"
        )
    
    # Проверяем, является ли пользователь создателем тендера
    if tender.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="У вас нет прав для просмотра заявок на этот тендер"
        )
    
    bids = db.query(models.Bid).filter(models.Bid.tender_id == tender_id).all()
    return bids


@app.put("/api/bids/{bid_id}/status", response_model=schemas.Bid)
async def update_bid_status(bid_id: int, 
                           status: str, 
                           current_user: models.User = Depends(get_current_active_user), 
                           db: Session = Depends(get_db)):
    """
    Обновление статуса заявки
    """
    bid = db.query(models.Bid).filter(models.Bid.id == bid_id).first()
    if not bid:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Заявка не найдена"
        )
    
    tender = db.query(models.Tender).filter(models.Tender.id == bid.tender_id).first()
    
    # Проверяем, является ли пользователь создателем тендера
    if tender.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="У вас нет прав для изменения статуса этой заявки"
        )
    
    # Проверяем валидность статуса
    if status not in ["pending", "accepted", "rejected"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Недопустимый статус заявки"
        )
    
    bid.status = status
    db.commit()
    db.refresh(bid)
    return bid


# Эндпоинты для работы с документами
@app.post("/api/documents", response_model=schemas.Document)
async def upload_document(
    tender_id: int = Form(...),
    file: UploadFile = File(...),
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Загрузка документа для тендера
    """
    tender = db.query(models.Tender).filter(models.Tender.id == tender_id).first()
    if not tender:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Указанный тендер не найден"
        )
    
    if tender.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="У вас нет прав для загрузки документов к этому тендеру"
        )
    
    upload_dir = f"uploads/tenders/{tender_id}"
    os.makedirs(upload_dir, exist_ok=True)
    
    # Генерируем уникальное имя файла
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid4()}{file_extension}"
    file_path = f"{upload_dir}/{unique_filename}"
    
    # Сохраняем файл
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при сохранении файла: {str(e)}"
        )
    
    # Создаем запись о документе в базе данных
    new_document = models.Document(
        filename=file.filename,
        file_path=file_path,
        file_type=file.content_type,
        file_size=os.path.getsize(file_path),
        tender_id=tender_id
    )
    
    db.add(new_document)
    db.commit()
    db.refresh(new_document)
    
    return new_document


@app.get("/api/documents/{document_id}", response_model=schemas.Document)
async def get_document(document_id: int, db: Session = Depends(get_db)):
    """
    Получение информации о документе по ID
    """
    document = db.query(models.Document).filter(models.Document.id == document_id).first()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Документ не найден"
        )
    
    return document


@app.get("/api/tenders/{tender_id}/documents", response_model=List[schemas.Document])
async def get_tender_documents(tender_id: int, db: Session = Depends(get_db)):
    """
    Получение списка документов для тендера
    """
    tender = db.query(models.Tender).filter(models.Tender.id == tender_id).first()
    if not tender:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Тендер не найден"
        )
    
    documents = db.query(models.Document).filter(models.Document.tender_id == tender_id).all()
    return documents


@app.on_event("startup")
async def startup_event():
    """
    Инициализация базы данных при запуске приложения
    """
    init_db()
    
    # Создаем директорию для загрузки файлов
    os.makedirs("uploads/tenders", exist_ok=True)


# Эндпоинты для работы с историей чатов
@app.post("/api/chat-history", response_model=schemas.ChatHistory)
async def create_chat_message(
    chat_message: schemas.ChatHistoryCreate,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Создание нового сообщения в истории чата
    """
    # Проверяем, что текущий пользователь имеет право добавлять сообщение
    if chat_message.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Вы можете добавлять сообщения только для своего пользователя"
        )
    
    # Создаем новую запись в истории чата
    new_message = models.ChatHistory(**chat_message.dict())
    db.add(new_message)
    db.commit()
    db.refresh(new_message)
    
    return new_message


@app.get("/api/chat-history/{chat_id}", response_model=schemas.ChatConversation)
async def get_chat_conversation(
    chat_id: str,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Получение истории сообщений для конкретного чата
    """
    # Проверяем, что пользователь имеет доступ к этому чату
    messages = db.query(models.ChatHistory).filter(
        models.ChatHistory.chat_id == chat_id,
        models.ChatHistory.user_id == current_user.id
    ).order_by(models.ChatHistory.timestamp).all()
    
    return schemas.ChatConversation(
        chat_id=chat_id,
        messages=messages
    )


@app.get("/api/chat-history", response_model=List[str])
async def get_user_chats(
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Получение списка всех чатов пользователя
    """
    # Получаем уникальные идентификаторы чатов пользователя
    chats = db.query(models.ChatHistory.chat_id).filter(
        models.ChatHistory.user_id == current_user.id
    ).distinct().all()
    
    return [chat[0] for chat in chats]


@app.delete("/api/chat-history/{chat_id}", response_model=Dict[str, Any])
async def delete_chat_history(
    chat_id: str,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Удаление истории сообщений для конкретного чата
    """
    # Удаляем все сообщения текущего пользователя в этом чате
    deleted = db.query(models.ChatHistory).filter(
        models.ChatHistory.chat_id == chat_id,
        models.ChatHistory.user_id == current_user.id
    ).delete()
    
    db.commit()
    
    return {
        "success": True,
        "deleted_messages": deleted,
        "message": f"История чата с ID {chat_id} успешно удалена"
    }


# Эндпоинты для работы с моделью Data
@app.get("/api/data", response_model=List[schemas.Data])
async def get_all_data(
    skip: int = 0, 
    limit: int = 100, 
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Получение списка всех записей Data с пагинацией и поиском
    """
    query = db.query(models.Data)
    
    # Применяем поиск по заголовку и описанию, если он указан
    if search:
        query = query.filter(
            (models.Data.title.ilike(f"%{search}%")) | 
            (models.Data.description.ilike(f"%{search}%"))
        )
    
    # Применяем пагинацию
    data = query.order_by(models.Data.created_at.desc()).offset(skip).limit(limit).all()
    return data


@app.post("/api/data", response_model=schemas.Data)
async def create_data(
    data: schemas.DataCreate,
    db: Session = Depends(get_db)
):
    """
    Создание новой записи Data
    """
    new_data = models.Data(**data.dict())
    db.add(new_data)
    db.commit()
    db.refresh(new_data)
    return new_data


@app.get("/api/data/{data_id}", response_model=schemas.Data)
async def get_data_by_id(
    data_id: int,
    db: Session = Depends(get_db)
):
    """
    Получение записи Data по ID
    """
    data = db.query(models.Data).filter(models.Data.id == data_id).first()
    if not data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Запись не найдена"
        )
    return data


@app.put("/api/data/{data_id}", response_model=schemas.Data)
async def update_data(
    data_id: int,
    data_update: schemas.DataUpdate,
    db: Session = Depends(get_db)
):
    """
    Обновление записи Data
    """
    data = db.query(models.Data).filter(models.Data.id == data_id).first()
    if not data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Запись не найдена"
        )
    
    # Обновляем только предоставленные поля
    update_data = data_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(data, key, value)
    
    db.commit()
    db.refresh(data)
    return data


@app.delete("/api/data/{data_id}", response_model=Dict[str, Any])
async def delete_data(
    data_id: int,
    db: Session = Depends(get_db)
):
    """
    Удаление записи Data
    """
    data = db.query(models.Data).filter(models.Data.id == data_id).first()
    if not data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Запись не найдена"
        )
    
    db.delete(data)
    db.commit()
    
    return {
        "success": True,
        "message": f"Запись с ID {data_id} успешно удалена"
    }


# Эндпоинт для импорта данных из parquet-файла
@app.post("/api/import-parquet", response_model=Dict[str, Any])
async def import_parquet(
    background_tasks: BackgroundTasks,
    parquet_path: str = Body("docs/dataset.parquet", description="Путь к parquet-файлу"),
    title_column: Optional[str] = Body(None, description="Название столбца для поля title"),
    description_column: Optional[str] = Body(None, description="Название столбца для поля description"),
    batch_size: int = Body(1000, description="Размер пакета для загрузки"),
    current_user: models.User = Depends(get_current_active_user),
):
    """
    Импорт данных из parquet-файла в таблицу Data
    """
    # Функция для выполнения импорта в фоновом режиме
    def run_import():
        try:
            result = load_parquet_to_data(
                parquet_path=parquet_path,
                title_column=title_column,
                description_column=description_column,
                batch_size=batch_size
            )
            print(f"Импорт завершен: {result['message']}")
        except Exception as e:
            print(f"Ошибка при импорте: {str(e)}")
    
    # Запускаем импорт в фоновом режиме
    background_tasks.add_task(run_import)
    
    return {
        "success": True,
        "message": "Импорт данных запущен в фоновом режиме",
        "params": {
            "parquet_path": parquet_path,
            "title_column": title_column,
            "description_column": description_column,
            "batch_size": batch_size
        }
    }


if __name__ == '__main__':
    uvicorn.run(
        app="server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        workers=4
    )
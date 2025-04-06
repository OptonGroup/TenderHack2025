from fastapi import FastAPI, Depends, HTTPException, status, File, UploadFile, Form, Path, Query, Body, BackgroundTasks, Request, Cookie, Security
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy.future import select
from sqlalchemy import func, Boolean, distinct
from typing import List, Optional, Dict, Any
import uvicorn
from datetime import timedelta, datetime
import os
import shutil
from uuid import uuid4
from jose import jwt, JWTError
from passlib.context import CryptContext
from pydantic import validate_arguments
import pandas as pd
import logging
import json
import requests
import urllib.parse

from database import get_db, init_db
import models
import schemas
from auth import authenticate_user, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES, get_password_hash, SECRET_KEY, ALGORITHM, get_current_active_user
from load_parquet_to_data import load_parquet_to_data

app = FastAPI(title="TenderHack API", version="1.0.0")

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Определяем абсолютные пути для статических файлов и шаблонов
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "templates")
UPLOADS_DIR = os.path.join(os.path.dirname(__file__), "uploads")

# Создаем директории, если они не существуют
os.makedirs(STATIC_DIR, exist_ok=True)
os.makedirs(TEMPLATES_DIR, exist_ok=True)
os.makedirs(UPLOADS_DIR, exist_ok=True)

# Настройка статических файлов и шаблонов
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATES_DIR)

# Настройка OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Настройка JWT
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 дней

# Настройка логгера
logger = logging.getLogger("app")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)

# Функция для проверки роли пользователя
def check_user_role(required_roles: List[str]):
    """
    Создает зависимость для проверки роли пользователя
    """
    async def role_checker(current_user: models.User = Depends(get_current_active_user)):
        if current_user.role not in required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="У вас недостаточно прав для выполнения этой операции"
            )
        return current_user
    return role_checker

# Зависимости для различных ролей
get_admin_user = check_user_role(["admin"])
get_operator_user = check_user_role(["admin", "operator"])

# Зависимость для получения текущего активного пользователя с ролью оператора или администратора
async def get_operator_user(
    current_user: models.User = Depends(get_current_active_user),
) -> models.User:
    if current_user.role not in ["operator", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Для этого действия требуются права оператора или администратора",
        )
    return current_user

# Зависимость для получения текущего активного пользователя с ролью администратора
async def get_admin_user(
    current_user: models.User = Depends(get_current_active_user),
) -> models.User:
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Для этого действия требуются права администратора",
        )
    return current_user

# Маршруты для веб-страниц
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request, db: Session = Depends(get_db)):
    """
    Главная страница - доступна для всех, но авторизованные пользователи видят свои данные
    """
    try:
        # Пробуем получить пользователя из cookie
        user = await get_api_user(request, None, db)
        # Если пользователь найден, показываем главную с информацией о пользователе
        return templates.TemplateResponse("index.html", {"request": request, "user": user})
    except:
        # Для неавторизованных пользователей показываем обычную главную страницу
        return templates.TemplateResponse("index.html", {"request": request})

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

# Получение текущего активного пользователя для API запросов
# Это позволяет более гибко получать пользователя как из header, так и из cookie
async def get_api_user(
    request: Request,
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Получение пользователя для API запросов, поддерживает как Bearer токен, так и cookie
    """
    # Если есть токен в заголовке Authorization, используем его
    if token:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username = payload.get("sub")
            if username:
                user = db.query(models.User).filter(models.User.username == username).first()
                if user and user.is_active:
                    return user
        except Exception as e:
            print(f"Ошибка декодирования токена из заголовка: {e}")
    
    # Если токен в заголовке не валиден или отсутствует, проверяем cookie
    try:
        cookie_token = request.cookies.get("token")
        if cookie_token:
            payload = jwt.decode(cookie_token, SECRET_KEY, algorithms=[ALGORITHM])
            username = payload.get("sub")
            if username:
                user = db.query(models.User).filter(models.User.username == username).first()
                if user and user.is_active:
                    return user
    except Exception as e:
        print(f"Ошибка декодирования токена из cookie: {e}")
    
    # Если не нашли пользователя ни по заголовку, ни по cookie
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Необходима авторизация",
        headers={"WWW-Authenticate": "Bearer"},
    )

@app.get("/profile", response_class=HTMLResponse)
async def profile_page(request: Request, db: Session = Depends(get_db)):
    """
    Страница профиля пользователя
    """
    try:
        # Пробуем получить пользователя из cookie
        user = await get_api_user(request, None, db)
        
        # Если пользователь найден, показываем страницу профиля
        return templates.TemplateResponse("profile.html", {"request": request, "user": user})
    except:
        # Если пользователь не найден, перенаправляем на страницу входа
        return RedirectResponse(url="/login")

@app.get("/chat", response_class=HTMLResponse)
async def chat_page(request: Request, db: Session = Depends(get_db)):
    """
    Страница AI-чата
    """
    try:
        # Пробуем получить пользователя из cookie
        user = await get_api_user(request, None, db)
        
        # Если пользователь найден, показываем страницу чата
        return templates.TemplateResponse("chat.html", {"request": request, "user": user})
    except:
        # Если пользователь не найден, перенаправляем на страницу входа
        return RedirectResponse(url="/login")

@app.get("/knowledge", response_class=HTMLResponse)
async def knowledge_page(request: Request, db: Session = Depends(get_db)):
    """
    Страница базы знаний - доступна для всех, но авторизованные пользователи видят свои данные
    """
    try:
        # Пробуем получить пользователя из cookie
        user = await get_api_user(request, None, db)
        # Если пользователь найден, показываем страницу с информацией о пользователе
        return templates.TemplateResponse("knowledge.html", {"request": request, "user": user})
    except:
        # Для неавторизованных пользователей показываем обычную страницу
        return templates.TemplateResponse("knowledge.html", {"request": request})

@app.get("/logout")
async def logout():
    """
    Маршрут для выхода из системы
    """
    response = RedirectResponse(url="/login")
    response.delete_cookie(key="token")
    return response

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
    Эндпоинт для входа пользователя через JSON API
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
    
    # Создаем JSON-ответ с cookie
    response_data = {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role
    }
    
    # Создаем response объект
    response = JSONResponse(content=response_data)
    
    # Устанавливаем cookie с токеном
    expires = datetime.utcnow() + access_token_expires
    response.set_cookie(
        key="token",
        value=access_token,
        httponly=True,
        secure=False,  # В продакшн сделать True
        samesite="lax",
        expires=expires.strftime("%a, %d %b %Y %H:%M:%S GMT")
    )
    
    return response


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
    # Check if user has the right role to create tenders (only regular users and admins)
    if current_user.role == "operator":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Операторы не могут создавать тендеры"
        )
    
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
    Инициализация базы данных и создание тестовых данных при запуске
    """
    init_db()
    
    # Проверяем наличие директории для загрузок
    os.makedirs(UPLOADS_DIR, exist_ok=True)
    
    try:
        # Создаем тестового пользователя, если он не существует
        db = next(get_db())
        
        admin_user = db.query(models.User).filter(models.User.username == "admin").first()
        if not admin_user:
            hashed_password = get_password_hash("admin123")
            admin_user = models.User(
                username="admin",
                email="admin@example.com",
                hashed_password=hashed_password,
                is_active=True
            )
            db.add(admin_user)
            db.commit()
            db.refresh(admin_user)
            print("Created admin user")
        
        # Создаем категории, если они не существуют
        categories = ["Строительство", "IT", "Консалтинг", "Поставка", "Услуги"]
        for category_name in categories:
            category = db.query(models.Category).filter(models.Category.name == category_name).first()
            if not category:
                category = models.Category(name=category_name)
                db.add(category)
        
        db.commit()
        print("Initialized categories")
    except Exception as e:
        print(f"Error during startup: {e}")
    finally:
        db.close()


# Эндпоинты для работы с историей чатов
@app.post("/api/chat-history", response_model=schemas.ChatHistory)
async def create_chat_message(
    request: Request,
    chat_message: schemas.ChatHistoryCreate,
    current_user: models.User = Depends(get_api_user),
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
    
    try:
        logger.info(f"Создание сообщения в чате {chat_message.chat_id} от пользователя {current_user.id}")
        # Создаем новую запись в истории чата
        new_message = models.ChatHistory(**chat_message.dict())
        db.add(new_message)
        db.commit()
        db.refresh(new_message)
        
        logger.info(f"Сообщение успешно создано: {new_message.id}")
        return new_message
    except Exception as e:
        logger.error(f"Ошибка при создании сообщения: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при создании сообщения: {str(e)}"
        )

@app.get("/api/chat-history/{chat_id}", response_model=schemas.ChatConversation)
async def get_chat_conversation(
    request: Request,
    chat_id: str,
    current_user: models.User = Depends(get_api_user),
    db: Session = Depends(get_db)
):
    """
    Получение истории сообщений для конкретного чата
    """
    try:
        logger.info(f"Получение истории чата {chat_id} для пользователя {current_user.id}")
        # Проверяем, что пользователь имеет доступ к этому чату
        messages = db.query(models.ChatHistory).filter(
            models.ChatHistory.chat_id == chat_id,
            models.ChatHistory.user_id == current_user.id
        ).order_by(models.ChatHistory.timestamp).all()
        
        logger.info(f"Найдено {len(messages)} сообщений в чате {chat_id}")
        
        # Сначала создаем словарь для конвертации в Pydantic модель
        chat_data = {
            "chat_id": chat_id,
            "messages": [
                {
                    "id": msg.id,
                    "user_id": msg.user_id,
                    "chat_id": msg.chat_id,
                    "message": msg.message,
                    "is_bot": msg.is_bot,
                    "timestamp": msg.timestamp,
                    "message_metadata": msg.message_metadata
                } for msg in messages
            ]
        }
        
        # Затем создаем Pydantic модель из словаря
        return schemas.ChatConversation(**chat_data)
    except Exception as e:
        logger.error(f"Ошибка при получении истории чата: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении истории чата: {str(e)}"
        )

@app.get("/api/chat-history", response_model=List[str])
async def get_user_chats(
    request: Request,
    current_user: models.User = Depends(get_api_user),
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
    request: Request,
    chat_id: str,
    current_user: models.User = Depends(get_api_user),
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


@app.patch("/api/chat-history/{message_id}", response_model=schemas.ChatHistory)
async def update_chat_message(
    request: Request,
    message_id: int,
    message_update: schemas.ChatHistoryUpdate,
    current_user: models.User = Depends(get_api_user),
    db: Session = Depends(get_db)
):
    """
    Обновляет сообщение чата - используется для добавления обратной связи
    """
    # Проверяем, существует ли сообщение
    message = db.query(models.ChatHistory).filter(models.ChatHistory.id == message_id).first()
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Сообщение не найдено"
        )
    
    # Проверяем, принадлежит ли чат текущему пользователю
    if message.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="У вас нет доступа к этому сообщению"
        )
    
    # Обновляем сообщение
    update_data = message_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(message, key, value)
    
    db.commit()
    db.refresh(message)
    
    return message


@app.post("/api/chat-history/{chat_id}/finish", response_model=Dict[str, Any])
async def finish_chat(chat_id: str, rating_data: dict, current_user: models.User = Depends(get_api_user), db: Session = Depends(get_db)):
    try:
        # Проверяем существование чата
        chat_history = db.query(models.ChatHistory).filter(
            models.ChatHistory.chat_id == chat_id,
            models.ChatHistory.user_id == current_user.id
        ).first()
        
        if not chat_history:
            # Если чат не найден, создаем запись о завершении
            logger.warning(f"Попытка завершить несуществующий чат {chat_id} пользователем {current_user.id}")
            return {"success": True, "message": "Чат успешно завершен (новая запись)"}
        
        # Обновляем статус чата и добавляем оценку
        chat_history.is_completed = True
        chat_history.rating = rating_data.get("rating", 0)
        chat_history.feedback = rating_data.get("comment", "")
        
        db.commit()
        
        return {"success": True, "message": "Чат успешно завершен"}
    except Exception as e:
        logger.error(f"Ошибка при завершении чата {chat_id}: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка при завершении чата: {str(e)}")


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


# Эндпоинт для запроса к AI
@app.post("/api/ai-query", response_model=schemas.AIQueryResponse)
async def query_ai_service(
    request: Request,
    payload: Dict[str, str] = Body(...),
    current_user: models.User = Depends(get_api_user)
):
    """
    Отправляет запрос пользователя к внешнему AI-сервису и возвращает ответ.
    """
    user_query = payload.get("query")
    if not user_query:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Параметр 'query' обязателен."
        )

    ai_service_url = "http://localhost:7777/query"
    encoded_query = urllib.parse.quote(user_query)
    full_url = f"{ai_service_url}?query={encoded_query}"

    logger.info(f"Запрос к AI сервису: {full_url} от пользователя {current_user.id}")

    try:
        response = requests.get(full_url, headers={'accept': 'application/json'}, timeout=30)
        response.raise_for_status()

        ai_response = response.json()
        answer = ai_response.get("answer", "Извините, не удалось получить ответ от AI.")
        # Получаем флаг needs_operator из ответа AI сервиса
        needs_operator_flag = ai_response.get("query_analysis", {}).get("needs_operator", False)

        logger.info(f"Успешный ответ от AI сервиса для пользователя {current_user.id}. Needs Operator: {needs_operator_flag}")
        return {"answer": answer, "needs_operator": needs_operator_flag}

    except requests.exceptions.Timeout:
        logger.error(f"Ошибка: Таймаут при запросе к AI сервису {full_url}")
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="AI сервис не ответил вовремя."
        )
    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка при запросе к AI сервису {full_url}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Не удалось связаться с AI сервисом: {str(e)}"
        )
    except json.JSONDecodeError:
        logger.error(f"Ошибка: Невалидный JSON ответ от AI сервиса {full_url}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="AI сервис вернул некорректный ответ."
        )
    except Exception as e:
        logger.error(f"Непредвиденная ошибка при запросе к AI сервису: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Внутренняя ошибка сервера при обработке запроса к AI: {str(e)}"
        )


# Эндпоинты для импорта данных
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


@app.post("/api/call-operator")
async def call_operator(
    request: Request,
    call_data: dict = Body(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Зарегистрировать запрос на помощь оператора
    """
    try:
        chat_id = call_data.get("chat_id")
        if not chat_id:
            return JSONResponse(
                status_code=400,
                content={"detail": "chat_id is required"}
            )

        # Создание системного сообщения с метаданными для оператора
        metadata = {
            "operator_request": True,  # Использовать Python булево значение
            "resolved": False,         # Использовать Python булево значение
            "request_time": datetime.utcnow().isoformat(),
            "requestor_id": current_user.id,
            "requestor_name": current_user.username
        }
        
        # Преобразуем метаданные в JSON для хранения
        metadata_json = json.dumps(metadata)
        
        logger.info(f"Создание запроса оператора от пользователя {current_user.username} для чата {chat_id}")
        logger.info(f"Метаданные запроса: {metadata_json}")
        
        # Добавляем системное сообщение, указывающее на запрос оператора
        system_message = models.ChatHistory(
            chat_id=chat_id,
            user_id=None,  # Системное сообщение
            message="Запрос на соединение с оператором зарегистрирован. Оператор свяжется с вами в ближайшее время.",
            is_bot=True,
            message_metadata=metadata_json
        )
        
        # Add the message to the database session
        db.add(system_message)
        # Commit the transaction
        db.commit()
        
        # Проверяем, что запрос действительно попал в базу
        # и имеет правильные метаданные
        saved_message = db.query(models.ChatHistory).filter(
            models.ChatHistory.id == system_message.id
        ).first()
        
        logger.info(f"Системное сообщение создано с ID {saved_message.id}")
        
        if saved_message:
            try:
                loaded_metadata = json.loads(saved_message.message_metadata) if saved_message.message_metadata else {}
                logger.info(f"Сохраненные метаданные: {loaded_metadata}")
                
                # Проверка, что метаданные содержат флаг оператора
                if loaded_metadata.get("operator_request") is True:
                    logger.info("Метаданные содержат флаг запроса оператора = True")
                else:
                    logger.warning(f"Проблема с метаданными: operator_request = {loaded_metadata.get('operator_request')}")
            except Exception as e:
                logger.error(f"Ошибка при проверке метаданных сообщения: {e}")
        
        # Проверяем, сколько всего активных запросов оператора
        try:
            active_requests_query = db.query(models.ChatHistory).filter(
                models.ChatHistory.message_metadata.isnot(None)
            )
            active_requests_count = 0
            
            for msg in active_requests_query.all():
                try:
                    msg_metadata = json.loads(msg.message_metadata) if msg.message_metadata else {}
                    if msg_metadata.get("operator_request") is True and msg_metadata.get("resolved") is not True:
                        active_requests_count += 1
                except:
                    pass
            
            logger.info(f"Всего активных запросов оператора после добавления: {active_requests_count}")
        except Exception as e:
            logger.error(f"Ошибка при подсчете запросов оператора: {e}")
        
        # Возвращаем ответ пользователю
        return {
            "success": True,
            "message": "Запрос на помощь оператора зарегистрирован",
            "estimated_wait_time": "5-10 минут"
        }
    except Exception as e:
        logger.error(f"Ошибка при регистрации запроса оператора: {e}")
        return JSONResponse(
            status_code=500,
            content={"detail": f"Ошибка при регистрации запроса оператора: {str(e)}"}
        )

@app.get("/api/support-requests")
async def get_support_requests(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Получить активные заявки на помощь от пользователей (для операторов и администраторов)
    """
    try:
        # PRINT: Начало получения заявок
        print(f"[DEBUG] Запрос заявок на помощь от {current_user.username} (роль: {current_user.role})")
        
        # Проверяем, есть ли у пользователя права на доступ к заявкам
        if current_user.role not in ['admin', 'operator']:
            logger.warning(f"Пользователь {current_user.username} (роль: {current_user.role}) пытается получить заявки на помощь")
            return JSONResponse(
                status_code=403,
                content={"detail": "Нет доступа к заявкам на помощь"}
            )
        
        logger.info(f"Запрос заявок на помощь от пользователя {current_user.username} (роль: {current_user.role})")
        
        # Находим все сообщения с метаданными о запросах оператора, используя запрос
        # с более точными условиями
        operator_messages = db.query(models.ChatHistory).filter(
            models.ChatHistory.message_metadata.isnot(None)
        ).order_by(models.ChatHistory.timestamp.desc()).all()
        
        print(f"[DEBUG] Найдено {len(operator_messages)} сообщений с метаданными")
        
        active_requests = []
        chat_ids_processed = set()
        
        for message in operator_messages:
            try:
                # Пропускаем сообщения без метаданных
                if not message.message_metadata:
                    continue
                
                try:
                    # Парсим метаданные
                    metadata = json.loads(message.message_metadata)
                    
                    # PRINT: Выводим информацию о метаданных каждого сообщения
                    print(f"[DEBUG] Метаданные сообщения {message.id}: {metadata}")
                    
                    # Проверяем, что это запрос оператора и он не решен
                    is_operator_request = metadata.get("operator_request") is True
                    is_resolved = metadata.get("resolved") is True
                    
                    print(f"[DEBUG] Сообщение {message.id}: operator_request={is_operator_request}, resolved={is_resolved}")
                    
                    # Пропускаем сообщения, которые не являются активными запросами оператора
                    if not is_operator_request or is_resolved:
                        continue
                    
                    # Пропускаем дубликаты чатов
                    if message.chat_id in chat_ids_processed:
                        continue
                    
                    # Находим пользователя, связанного с запросом
                    user_id = metadata.get("requestor_id")
                    user = db.query(models.User).filter(models.User.id == user_id).first() if user_id else None
                    
                    if not user:
                        # Ищем пользователя по сообщениям в чате
                        chat_user_message = db.query(models.ChatHistory).filter(
                            models.ChatHistory.chat_id == message.chat_id,
                            models.ChatHistory.user_id.isnot(None),
                            models.ChatHistory.is_bot.is_(False)
                        ).first()
                        
                        if chat_user_message:
                            user_id = chat_user_message.user_id
                            user = db.query(models.User).filter(models.User.id == user_id).first()
                    
                    print(f"[DEBUG] Пользователь для заявки: {user.username if user else 'Не найден'}")
                    
                    # Считаем сообщения в чате
                    message_count = db.query(models.ChatHistory).filter(
                        models.ChatHistory.chat_id == message.chat_id
                    ).count()
                    
                    # Формируем данные запроса
                    request_data = {
                        "chat_id": message.chat_id,
                        "message_id": message.id,
                        "created_at": message.timestamp.isoformat(),
                        "request_time": metadata.get("request_time"),
                        "message_count": message_count,
                        "user": {
                            "id": user.id if user else None,
                            "username": user.username if user else "Unknown User",
                            "email": user.email if user else None
                        } if user else {
                            "id": None,
                            "username": metadata.get("requestor_name", "Unknown User"),
                            "email": None
                        }
                    }
                    
                    active_requests.append(request_data)
                    chat_ids_processed.add(message.chat_id)
                    print(f"[DEBUG] Добавлен активный запрос: chat_id={message.chat_id}")
                    
                except json.JSONDecodeError as e:
                    print(f"[DEBUG] Ошибка парсинга JSON метаданных для сообщения {message.id}: {e}")
                    continue
            except Exception as e:
                print(f"[DEBUG] Ошибка при обработке сообщения {message.id}: {e}")
        
        print(f"[DEBUG] Найдено {len(active_requests)} активных заявок, данные: {active_requests}")
        
        # Сортируем по времени создания (сначала новые)
        active_requests.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        
        # Логируем первый запрос для отладки
        if active_requests:
            print(f"[DEBUG] Пример первого запроса: {active_requests[0]}")
        
        print(f"\n\n********** КОЛИЧЕСТВО АКТИВНЫХ ЗАЯВОК: {len(active_requests)} **********\n\n")
        
        return active_requests
    except Exception as e:
        print(f"[DEBUG] ОШИБКА при получении заявок: {e}")
        logger.error(f"Ошибка при получении заявок на помощь: {e}")
        return JSONResponse(
            status_code=500,
            content={"detail": f"Ошибка при получении заявок на помощь: {str(e)}"}
        )

@app.get("/api/debug/operator-requests")
async def debug_operator_requests(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Отладочный эндпоинт для проверки всех сообщений с метаданными оператора
    """
    if current_user.role not in ['admin', 'operator']:
        return JSONResponse(
            status_code=403,
            content={"detail": "Доступ запрещен"}
        )
    
    try:
        # Получаем последние 50 сообщений с любыми метаданными
        messages = db.query(models.ChatHistory).filter(
            models.ChatHistory.message_metadata.isnot(None)
        ).order_by(models.ChatHistory.created_at.desc()).limit(50).all()
        
        result = []
        for msg in messages:
            metadata = {}
            try:
                metadata = json.loads(msg.message_metadata) if msg.message_metadata else {}
            except:
                metadata = {"error": "Failed to parse metadata"}
            
            # Включаем информацию о том, является ли это запросом оператора
            operator_request = metadata.get("operator_request")
            resolved = metadata.get("resolved")
            
            result.append({
                "id": msg.id,
                "chat_id": msg.chat_id,
                "user_id": msg.user_id,
                "is_bot": msg.is_bot,
                "created_at": msg.created_at.isoformat(),
                "message": msg.message[:100] + "..." if len(msg.message) > 100 else msg.message,
                "raw_metadata": msg.message_metadata,
                "parsed_metadata": metadata,
                "is_operator_request": operator_request is True,
                "is_resolved": resolved is True
            })
        
        return {
            "count": len(result),
            "messages": result
        }
    except Exception as e:
        logger.error(f"Ошибка при отладке запросов оператора: {e}")
        return JSONResponse(
            status_code=500,
            content={"detail": f"Ошибка при отладке запросов оператора: {str(e)}"}
        )

@app.get("/admin", response_class=HTMLResponse)
async def admin_page(request: Request, db: Session = Depends(get_db)):
    """
    Административная панель (только для администраторов)
    """
    try:
        # Get user from cookie token
        user = await get_api_user(request, None, db)
        
        # Check if user has admin role
        if user.role != "admin":
            # If user doesn't have admin role, redirect to main page
            return RedirectResponse(url="/")
        
        # Получаем статистику для отображения на панели
        user_count = db.query(func.count(models.User.id)).scalar() or 0
        tender_count = db.query(func.count(models.Tender.id)).scalar() or 0
        operator_count = db.query(func.count(models.User.id)).filter(models.User.role == "operator").scalar() or 0
        
        # Получаем количество активных заявок на поддержку
        support_request_count = db.query(func.count(models.ChatHistory.id))\
            .filter(models.ChatHistory.message_metadata.op('->>')('operator_request') == 'true')\
            .filter((models.ChatHistory.message_metadata.op('->>')('resolved').is_(None)) | 
                   (models.ChatHistory.message_metadata.op('->>')('resolved') != 'true'))\
            .scalar() or 0
        
        # Получаем недавно зарегистрированных пользователей
        recent_users = db.query(models.User)\
            .order_by(models.User.created_at.desc())\
            .limit(10)\
            .all()
        
        return templates.TemplateResponse(
            "admin.html",
            {
                "request": request,
                "user": user,
                "user_count": user_count,
                "tender_count": tender_count,
                "operator_count": operator_count,
                "support_request_count": support_request_count,
                "recent_users": recent_users
            }
        )
    except Exception as e:
        logger.error(f"Error accessing admin page: {str(e)}")
        # If not authenticated, redirect to login
        return RedirectResponse(url="/login")

@app.get("/support-requests", response_class=HTMLResponse)
async def support_requests_page(request: Request, db: Session = Depends(get_db)):
    """
    Страница заявок на поддержку (для операторов и администраторов)
    """
    try:
        # Get user from cookie token
        user = await get_api_user(request, None, db)
        
        # Check if user has proper role
        if user.role not in ["operator", "admin"]:
            # If user doesn't have operator or admin role, redirect to main page
            return RedirectResponse(url="/")
        
        return templates.TemplateResponse(
            "support_requests.html",
            {
                "request": request,
                "user": user
            }
        )
    except Exception as e:
        logger.error(f"Error accessing support requests page: {str(e)}")
        # If not authenticated, redirect to login
        return RedirectResponse(url="/login")

@app.post("/api/users/{user_id}/role", response_model=schemas.User)
async def update_user_role(
    user_id: int,
    role: str = Body(..., embed=True),
    current_user: models.User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Изменение роли пользователя (только для администраторов)
    """
    # Проверяем, что роль указана корректно
    if role not in ["user", "operator", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Указана неверная роль. Допустимые роли: user, operator, admin"
        )
    
    # Получаем пользователя, которому меняем роль
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    
    # Запрещаем администратору понижать собственную роль
    if user.id == current_user.id and role != "admin":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Администратор не может понизить свою роль"
        )
    
    # Обновляем роль пользователя
    user.role = role
    db.commit()
    db.refresh(user)
    
    return user

@app.post("/api/support-requests/{chat_id}/resolve")
async def resolve_support_request(
    chat_id: str,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Отметить заявку на поддержку как решенную
    """
    try:
        # Проверяем, что пользователь имеет нужную роль
        if current_user.role not in ['admin', 'operator']:
            logger.warning(f"Пользователь {current_user.username} без необходимых прав пытается разрешить заявку")
            return JSONResponse(
                status_code=403,
                content={"detail": "Нет прав на разрешение заявок"}
            )
        
        logger.info(f"Запрос на разрешение заявки {chat_id} от пользователя {current_user.username}")
        
        # Находим все сообщения с запросом оператора в этом чате
        operator_messages = db.query(models.ChatHistory).filter(
            models.ChatHistory.chat_id == chat_id,
            models.ChatHistory.message_metadata.isnot(None)
        ).all()
        
        updated_count = 0
        
        for message in operator_messages:
            try:
                if not message.message_metadata:
                    continue
                
                metadata = json.loads(message.message_metadata)
                
                # Проверяем, является ли сообщение запросом оператора и не разрешено
                if metadata.get("operator_request") is True and metadata.get("resolved") is not True:
                    # Обновляем метаданные - помечаем как разрешенное
                    metadata["resolved"] = True
                    metadata["resolved_by"] = current_user.id
                    metadata["resolved_by_username"] = current_user.username
                    metadata["resolved_at"] = datetime.utcnow().isoformat()
                    
                    # Сохраняем обновленные метаданные
                    message.message_metadata = json.dumps(metadata)
                    updated_count += 1
                    
                    logger.info(f"Запрос оператора в сообщении {message.id} отмечен как разрешенный")
            except Exception as e:
                logger.error(f"Ошибка при обработке сообщения {message.id}: {e}")
        
        # Если обновлены какие-либо сообщения, сохраняем изменения
        if updated_count > 0:
            # Добавляем системное сообщение о решении
            system_message = models.ChatHistory(
                chat_id=chat_id,
                user_id=None,  # Системное сообщение
                message=f"Запрос оператора разрешен пользователем {current_user.username}.",
                is_bot=True,
                message_metadata=json.dumps({
                    "type": "system",
                    "resolved_by": current_user.id,
                    "resolved_by_username": current_user.username,
                    "timestamp": datetime.utcnow().isoformat()
                })
            )
            db.add(system_message)
            db.commit()
            
            logger.info(f"Заявка {chat_id} успешно разрешена, обновлено {updated_count} сообщений")
            return {"success": True, "message": "Заявка успешно отмечена как решенная"}
        else:
            logger.warning(f"Заявка {chat_id} не найдена или уже разрешена")
            return {"success": False, "message": "Заявка не найдена или уже разрешена"}
    except Exception as e:
        logger.error(f"Ошибка при разрешении заявки {chat_id}: {e}")
        db.rollback()
        return JSONResponse(
            status_code=500,
            content={"detail": f"Ошибка при разрешении заявки: {str(e)}"}
        )

@app.get("/api/operator/chats", response_model=List[str], tags=["Operator"])
async def get_all_chats_for_operator(
    current_user: models.User = Depends(get_operator_user), # Проверяем роль оператора/админа
    db: Session = Depends(get_db)
):
    """
    Получение списка ВСЕХ уникальных chat_id для оператора/администратора.
    """
    try:
        # Используем select и distinct для получения уникальных chat_id со всей таблицы
        stmt = select(models.ChatHistory.chat_id).distinct()
        result = await db.execute(stmt)
        all_chat_ids = [row[0] for row in result.fetchall()]
        logger.info(f"Оператор {current_user.username} запросил список всех чатов. Найдено: {len(all_chat_ids)}.")
        return all_chat_ids
    except Exception as e:
        logger.error(f"Ошибка при получении списка всех чатов для оператора {current_user.username}: {e}")
        raise HTTPException(status_code=500, detail="Ошибка сервера при получении списка всех чатов")

@app.get("/api/operator/chats/{chat_id}", response_model=schemas.ChatConversation, tags=["Operator"])
def get_specific_chat_for_operator(
    chat_id: str,
    current_user: models.User = Depends(get_operator_user), # Проверяем роль оператора/админа
    db: Session = Depends(get_db)
):
    """
    Получение полной истории сообщений для указанного chat_id оператором/администратором.
    """
    try:
        # Получаем историю чата без проверки user_id, убираем await
        stmt = select(models.ChatHistory).where(models.ChatHistory.chat_id == chat_id).order_by(models.ChatHistory.timestamp)
        result = db.execute(stmt) # Убираем await
        history_orm = result.scalars().all()

        if not history_orm:
            logger.warning(f"Оператор {current_user.username} запросил несуществующий чат: {chat_id}")
            raise HTTPException(status_code=404, detail="Чат не найден")
        
        # Получаем информацию о пользователе, которому принадлежит чат
        # Ищем первое сообщение с user_id, чтобы определить владельца
        chat_owner_id = None
        for msg in history_orm:
            if msg.user_id is not None:
                chat_owner_id = msg.user_id
                break 
        
        chat_owner_username = "Неизвестный пользователь"
        if chat_owner_id:
             chat_owner = db.get(models.User, chat_owner_id) # Убираем await
             if chat_owner:
                 chat_owner_username = chat_owner.username

        # Преобразуем в Pydantic модель - оставляем history, схема ожидает messages
        messages = [schemas.ChatHistory.from_orm(msg) for msg in history_orm]
        
        logger.info(f"Оператор {current_user.username} просмотрел чат {chat_id} пользователя {chat_owner_username}. Сообщений: {len(messages)}.")
        
        # Возвращаем данные в формате ChatConversation
        return schemas.ChatConversation(
            # user_id=chat_owner_id, # Убираем, так как нет в схеме
            # username=chat_owner_username, # Убираем, так как нет в схеме
            chat_id=chat_id,
            messages=messages # Переименовали history в messages
        )
    except HTTPException as http_exc:
        raise http_exc # Пробрасываем HTTP исключения дальше
    except Exception as e:
        # Добавляем traceback для лучшей диагностики
        import traceback
        logger.error(f"Ошибка при получении чата {chat_id} для оператора {current_user.username}: {e}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="Ошибка сервера при получении истории чата")

@app.post("/api/operator/chats/{chat_id}/message", response_model=schemas.ChatHistory, tags=["Operator"])
async def post_message_by_operator(
    chat_id: str,
    message_data: schemas.OperatorMessageCreate,
    current_operator: models.User = Depends(get_operator_user), # Гарантирует, что это оператор или админ
    db: Session = Depends(get_db)
):
    """
    Отправка сообщения оператором в указанный чат.
    Сообщение сохраняется в базе данных, но user_id будет None, 
    а в метаданных будет указан ID оператора.
    """
    try:
        # Находим пользователя, которому принадлежит чат, чтобы убедиться, что чат существует
        # Это также поможет правильно отобразить сообщение у пользователя
        original_message = db.query(models.ChatHistory).filter(
            models.ChatHistory.chat_id == chat_id,
            models.ChatHistory.user_id.isnot(None) # Находим любое сообщение от пользователя в этом чате
        ).first()
        
        if not original_message:
            logger.error(f"Оператор {current_operator.username} попытался отправить сообщение в несуществующий чат {chat_id}")
            raise HTTPException(status_code=404, detail="Чат не найден или в нем нет сообщений от пользователя")
            
        # Определяем user_id, к которому относится чат
        target_user_id = original_message.user_id

        # Создаем метаданные для сообщения оператора
        metadata = {
            "is_operator_message": True,
            "operator_id": current_operator.id,
            "operator_username": current_operator.username
        }

        # Создаем новое сообщение в истории чата
        new_message = models.ChatHistory(
            chat_id=chat_id,
            user_id=target_user_id,  # Привязываем к пользователю чата
            message=message_data.message,
            is_bot=False, # Сообщение не от бота, а от человека-оператора
            message_metadata=json.dumps(metadata) # Сохраняем метаданные как JSON
        )
        
        db.add(new_message)
        db.commit()
        db.refresh(new_message)
        
        logger.info(f"Оператор {current_operator.username} отправил сообщение в чат {chat_id} пользователя {target_user_id}. ID сообщения: {new_message.id}")
        
        return new_message
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        db.rollback()
        logger.error(f"Ошибка при отправке сообщения оператором {current_operator.username} в чат {chat_id}: {e}")
        raise HTTPException(status_code=500, detail="Ошибка сервера при отправке сообщения оператором")

@app.get("/operator-chat/{chat_id}", response_class=HTMLResponse, tags=["Operator"])
async def operator_chat_page(
    request: Request, 
    chat_id: str, 
    current_user: models.User = Depends(get_operator_user), # Ensure operator/admin access
    db: Session = Depends(get_db)
):
    """
    Страница чата для оператора для общения с конкретным пользователем.
    """
    # Проверяем, существует ли чат (хотя бы одно сообщение от пользователя)
    chat_exists = db.query(models.ChatHistory).filter(
        models.ChatHistory.chat_id == chat_id,
        models.ChatHistory.user_id.isnot(None) 
    ).first()
    
    if not chat_exists:
        # Можно вернуть 404 страницу или редирект с сообщением
        # Пока просто вернем 404 ошибку FastAPI
        raise HTTPException(status_code=404, detail="Чат не найден или не содержит сообщений пользователя")

    # Получаем имя пользователя, которому принадлежит чат
    user_id = chat_exists.user_id
    chat_user = db.query(models.User).filter(models.User.id == user_id).first()
    chat_username = chat_user.username if chat_user else "Unknown User"

    return templates.TemplateResponse(
        "operator_chat.html", 
        {
            "request": request, 
            "user": current_user, # Текущий оператор/админ
            "chat_id": chat_id,
            "chat_username": chat_username # Имя пользователя, с которым общается оператор
        }
    )

# Добавляем новый тег для документации Swagger/OpenAPI
tags_metadata = app.openapi().get("tags", [])
tags_metadata.append({"name": "Operator", "description": "Операции, доступные для операторов и администраторов"})
app.openapi_tags = tags_metadata

if __name__ == '__main__':
    uvicorn.run(
        app="server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        workers=4
    )
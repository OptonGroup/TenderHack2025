from fastapi import APIRouter, Request, Depends, HTTPException, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import os
from sqlalchemy.orm import Session

import models
from database import get_db
from auth import get_current_active_user

# Настройка шаблонов - используем абсолютный путь
TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "templates")
templates = Jinja2Templates(directory=TEMPLATES_DIR)

# Создаем роутер для веб-страниц
router = APIRouter()

# Публичные страницы
@router.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@router.get("/knowledge", response_class=HTMLResponse)
async def knowledge_page(request: Request):
    return templates.TemplateResponse("knowledge.html", {"request": request})

# Защищенные страницы (требующие авторизации)
@router.get("/profile", response_class=HTMLResponse)
async def profile_page(
    request: Request,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    return templates.TemplateResponse("profile.html", {
        "request": request,
        "user": current_user
    })

@router.get("/chat", response_class=HTMLResponse)
async def chat_page(
    request: Request,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    return templates.TemplateResponse("chat.html", {
        "request": request,
        "user": current_user
    }) 
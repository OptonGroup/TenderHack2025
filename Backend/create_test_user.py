#!/usr/bin/env python
"""
Скрипт для создания тестового пользователя в базе данных
"""
import os
import sys
from sqlalchemy.orm import Session

# Добавляем текущую директорию в путь поиска модулей
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal, init_db
from models import User
from auth import get_password_hash


def create_test_user(db: Session) -> None:
    """
    Создает тестового пользователя, если он еще не существует
    """
    test_username = "admin"
    existing_user = db.query(User).filter(User.username == test_username).first()
    
    if existing_user:
        print(f"Пользователь с именем '{test_username}' уже существует!")
        return
    
    # Создаем тестового пользователя
    test_user = User(
        username=test_username,
        email="admin@tender.hack",
        hashed_password=get_password_hash("admin123"),
        is_active=True
    )
    
    db.add(test_user)
    db.commit()
    db.refresh(test_user)
    
    print(f"Тестовый пользователь создан:")
    print(f"  - Имя пользователя: {test_user.username}")
    print(f"  - Email: {test_user.email}")
    print(f"  - Пароль: admin123")
    print(f"  - ID: {test_user.id}")


if __name__ == "__main__":
    # Инициализируем базу данных
    init_db()
    
    # Создаем сессию
    db = SessionLocal()
    try:
        create_test_user(db)
    finally:
        db.close() 
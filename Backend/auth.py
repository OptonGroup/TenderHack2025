from datetime import datetime, timedelta
from typing import Optional, Union, Dict, Any

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlalchemy.orm import Session

import models
from database import get_db

# Конфигурация безопасности
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 дней

# Настройка хеширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Проверяет соответствие пароля хешированному значению
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Создает хеш пароля
    """
    return pwd_context.hash(password)


def get_user(db: Session, username: str) -> Optional[models.User]:
    """
    Получает пользователя из базы данных по имени пользователя
    """
    return db.query(models.User).filter(models.User.username == username).first()


def authenticate_user(db: Session, username: str, password: str) -> Union[models.User, bool]:
    """
    Аутентифицирует пользователя
    """
    user = get_user(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Создает JWT токен доступа
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_token_from_cookie(request: Request) -> Optional[str]:
    """Вспомогательная функция для извлечения токена из cookie"""
    return request.cookies.get("token")


async def get_current_user(
    request: Request, 
    db: Session = Depends(get_db)
) -> models.User:
    """
    Получает текущего пользователя по токену из заголовка Authorization (Bearer) ИЛИ из cookie 'token'.
    Теперь проверяет заголовок и cookie вручную через объект request.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Необходима авторизация. Пожалуйста, войдите в систему.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token: Optional[str] = None
    source: Optional[str] = None

    # 1. Проверяем заголовок Authorization
    auth_header = request.headers.get("Authorization")
    if auth_header:
        parts = auth_header.split()
        if len(parts) == 2 and parts[0].lower() == "bearer":
            token = parts[1]
            source = "header"
        else:
            print(f"Некорректный формат заголовка Authorization: {auth_header}")
            # Не вызываем ошибку сразу, может быть токен в cookie

    # 2. Если в заголовке нет, проверяем cookie
    if token is None:
        token = get_token_from_cookie(request)
        source = "cookie"

    # 3. Если токен так и не найден
    if token is None:
        print("Токен не найден ни в заголовке Authorization, ни в cookie 'token'")
        raise credentials_exception

    # 4. Декодируем найденный токен
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            print(f"Имя пользователя (sub) не найдено в токене (источник: {source})")
            raise credentials_exception
    except JWTError as e:
        print(f"Ошибка декодирования JWT (источник: {source}): {e}. Токен: {token[:10]}...{token[-10:] if len(token)>20 else ''}")
        raise credentials_exception
    
    # 5. Ищем пользователя
    user = get_user(db, username=username)
    if user is None:
        print(f"Пользователь '{username}' из токена (источник: {source}) не найден в базе данных")
        raise credentials_exception
    
    return user


async def get_current_active_user(current_user: models.User = Depends(get_current_user)) -> models.User:
    """
    Проверяет, что пользователь активен
    """
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Пользователь неактивен")
    return current_user 
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime


class Token(BaseModel):
    """Модель токена доступа"""
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Данные, хранящиеся в токене"""
    username: Optional[str] = None


class UserBase(BaseModel):
    """Базовые данные пользователя"""
    username: str
    email: EmailStr
    is_active: Optional[bool] = True


class UserCreate(UserBase):
    """Данные для создания пользователя"""
    password: str = Field(..., min_length=8)


class User(UserBase):
    """Полная модель пользователя"""
    id: int
    created_at: datetime
    
    class Config:
        orm_mode = True


class UserInDB(User):
    """Пользователь, как он хранится в базе данных"""
    hashed_password: str
    
    class Config:
        orm_mode = True


class LoginRequest(BaseModel):
    """Запрос на вход в систему"""
    username: str
    password: str


class LoginResponse(BaseModel):
    """Ответ при успешном входе"""
    access_token: str
    token_type: str
    user_id: int
    username: str
    email: EmailStr 
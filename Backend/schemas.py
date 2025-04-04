from typing import Optional, List, Dict, Any
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


# Схемы для категорий
class CategoryBase(BaseModel):
    """Базовые данные категории"""
    name: str
    description: Optional[str] = None


class CategoryCreate(CategoryBase):
    """Данные для создания категории"""
    pass


class Category(CategoryBase):
    """Полная модель категории"""
    id: int
    
    class Config:
        orm_mode = True


# Схемы для тендеров
class TenderBase(BaseModel):
    """Базовые данные тендера"""
    title: str
    description: str
    budget_min: Optional[float] = None
    budget_max: Optional[float] = None
    deadline: datetime
    category_id: int


class TenderCreate(TenderBase):
    """Данные для создания тендера"""
    pass


class TenderUpdate(BaseModel):
    """Данные для обновления тендера"""
    title: Optional[str] = None
    description: Optional[str] = None
    budget_min: Optional[float] = None
    budget_max: Optional[float] = None
    deadline: Optional[datetime] = None
    status: Optional[str] = None
    category_id: Optional[int] = None


class Tender(TenderBase):
    """Полная модель тендера"""
    id: int
    created_at: datetime
    status: str
    creator_id: int
    
    class Config:
        orm_mode = True


class TenderDetail(Tender):
    """Детальная информация о тендере с связанными данными"""
    creator: User
    category: Category
    bids: List['Bid'] = []
    documents: List['Document'] = []
    
    class Config:
        orm_mode = True


# Схемы для заявок на тендеры
class BidBase(BaseModel):
    """Базовые данные заявки"""
    price: float
    proposal: str
    tender_id: int


class BidCreate(BidBase):
    """Данные для создания заявки"""
    pass


class BidUpdate(BaseModel):
    """Данные для обновления заявки"""
    price: Optional[float] = None
    proposal: Optional[str] = None
    status: Optional[str] = None


class Bid(BidBase):
    """Полная модель заявки"""
    id: int
    created_at: datetime
    status: str
    bidder_id: int
    
    class Config:
        orm_mode = True


class BidDetail(Bid):
    """Детальная информация о заявке с связанными данными"""
    tender: Tender
    bidder: User
    
    class Config:
        orm_mode = True


# Схемы для документов
class DocumentBase(BaseModel):
    """Базовые данные документа"""
    filename: str
    file_path: str
    file_type: Optional[str] = None
    file_size: Optional[int] = None
    tender_id: int


class DocumentCreate(DocumentBase):
    """Данные для создания документа"""
    pass


class Document(DocumentBase):
    """Полная модель документа"""
    id: int
    upload_date: datetime
    
    class Config:
        orm_mode = True


# Схемы для ChatHistory
class ChatHistoryBase(BaseModel):
    """Базовые данные истории чата"""
    user_id: int
    chat_id: str
    message: str
    is_bot: bool = False
    message_metadata: Optional[Dict[str, Any]] = None


class ChatHistoryCreate(ChatHistoryBase):
    """Данные для создания записи в истории чата"""
    pass


class ChatHistory(ChatHistoryBase):
    """Полная модель истории чата"""
    id: int
    timestamp: datetime
    
    class Config:
        orm_mode = True


class ChatConversation(BaseModel):
    """Модель для получения всей истории конкретного чата"""
    chat_id: str
    messages: List[ChatHistory]
    
    class Config:
        orm_mode = True


# Схемы для новой модели Data
class DataBase(BaseModel):
    """Базовые данные модели Data"""
    title: str
    description: Optional[str] = None


class DataCreate(DataBase):
    """Данные для создания записи в модели Data"""
    pass


class DataUpdate(BaseModel):
    """Данные для обновления записи в модели Data"""
    title: Optional[str] = None
    description: Optional[str] = None


class Data(DataBase):
    """Полная модель Data"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True


# Решаем проблему циклических ссылок
TenderDetail.update_forward_refs() 
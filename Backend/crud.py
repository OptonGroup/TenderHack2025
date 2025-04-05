from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

import models
import schemas
from auth import get_password_hash, verify_password

# Функции для работы с пользователями
def get_user(db: Session, user_id: int) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_username(db: Session, username: str) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.username == username).first()

def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[models.User]:
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, user_id: int, user_data: schemas.UserUpdate) -> Optional[models.User]:
    db_user = get_user(db, user_id)
    if not db_user:
        return None
    
    # Обновляем только переданные поля
    data_to_update = user_data.dict(exclude_unset=True)
    
    # Если передан пароль, хешируем его
    if "password" in data_to_update:
        data_to_update["hashed_password"] = get_password_hash(data_to_update.pop("password"))
    
    for key, value in data_to_update.items():
        setattr(db_user, key, value)
    
    db.commit()
    db.refresh(db_user)
    return db_user

# Функции для работы с категориями
def get_category(db: Session, category_id: int) -> Optional[models.Category]:
    return db.query(models.Category).filter(models.Category.id == category_id).first()

def get_category_by_name(db: Session, name: str) -> Optional[models.Category]:
    return db.query(models.Category).filter(models.Category.name == name).first()

def get_categories(db: Session, skip: int = 0, limit: int = 100) -> List[models.Category]:
    return db.query(models.Category).offset(skip).limit(limit).all()

def create_category(db: Session, category: schemas.CategoryCreate) -> models.Category:
    db_category = models.Category(name=category.name)
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

# Функции для работы с тендерами
def get_tender(db: Session, tender_id: int) -> Optional[models.Tender]:
    return db.query(models.Tender).filter(models.Tender.id == tender_id).first()

def get_tenders(db: Session, skip: int = 0, limit: int = 100) -> List[models.Tender]:
    return db.query(models.Tender).offset(skip).limit(limit).all()

def create_tender(db: Session, tender: schemas.TenderCreate, user_id: int) -> models.Tender:
    db_tender = models.Tender(
        title=tender.title,
        description=tender.description,
        start_date=tender.start_date,
        end_date=tender.end_date,
        budget=tender.budget,
        status=tender.status,
        category_id=tender.category_id,
        user_id=user_id
    )
    db.add(db_tender)
    db.commit()
    db.refresh(db_tender)
    return db_tender

def update_tender(db: Session, tender_id: int, tender_data: schemas.TenderUpdate) -> Optional[models.Tender]:
    db_tender = get_tender(db, tender_id)
    if not db_tender:
        return None
    
    data_to_update = tender_data.dict(exclude_unset=True)
    for key, value in data_to_update.items():
        setattr(db_tender, key, value)
    
    db.commit()
    db.refresh(db_tender)
    return db_tender

# Функции для работы с заявками (bids)
def get_bid(db: Session, bid_id: int) -> Optional[models.Bid]:
    return db.query(models.Bid).filter(models.Bid.id == bid_id).first()

def get_bids_by_tender(db: Session, tender_id: int) -> List[models.Bid]:
    return db.query(models.Bid).filter(models.Bid.tender_id == tender_id).all()

def get_bids_by_user(db: Session, user_id: int) -> List[models.Bid]:
    return db.query(models.Bid).filter(models.Bid.user_id == user_id).all()

def create_bid(db: Session, bid: schemas.BidCreate, user_id: int) -> models.Bid:
    db_bid = models.Bid(
        tender_id=bid.tender_id,
        user_id=user_id,
        amount=bid.amount,
        description=bid.description,
        status="pending"
    )
    db.add(db_bid)
    db.commit()
    db.refresh(db_bid)
    return db_bid

def update_bid_status(db: Session, bid_id: int, status: str) -> Optional[models.Bid]:
    db_bid = get_bid(db, bid_id)
    if not db_bid:
        return None
    
    db_bid.status = status
    db_bid.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(db_bid)
    return db_bid

# Функции для работы с документами
def get_document(db: Session, document_id: int) -> Optional[models.Document]:
    return db.query(models.Document).filter(models.Document.id == document_id).first()

def get_documents_by_tender(db: Session, tender_id: int) -> List[models.Document]:
    return db.query(models.Document).filter(models.Document.tender_id == tender_id).all()

def create_document(db: Session, document: schemas.DocumentCreate, user_id: int) -> models.Document:
    db_document = models.Document(
        tender_id=document.tender_id,
        user_id=user_id,
        filename=document.filename,
        filepath=document.filepath,
        file_type=document.file_type,
        file_size=document.file_size
    )
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    return db_document

# Функции для работы с историей чата
def get_chat_history(db: Session, chat_id: str) -> List[models.ChatHistory]:
    return db.query(models.ChatHistory).filter(models.ChatHistory.chat_id == chat_id).order_by(models.ChatHistory.created_at).all()

def get_user_chats(db: Session, user_id: int) -> List[str]:
    # Получаем уникальные chat_id для пользователя
    chat_ids = db.query(models.ChatHistory.chat_id).filter(
        models.ChatHistory.user_id == user_id
    ).distinct().all()
    
    return [chat_id[0] for chat_id in chat_ids]

def create_chat_message(db: Session, chat_message: schemas.ChatHistoryCreate) -> models.ChatHistory:
    db_message = models.ChatHistory(
        chat_id=chat_message.chat_id,
        user_id=chat_message.user_id,
        message=chat_message.message,
        is_bot=chat_message.is_bot
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message

def update_chat_message(db: Session, message_id: int, message_data: schemas.ChatHistoryUpdate) -> Optional[models.ChatHistory]:
    db_message = db.query(models.ChatHistory).filter(models.ChatHistory.id == message_id).first()
    if not db_message:
        return None
    
    data_to_update = message_data.dict(exclude_unset=True)
    for key, value in data_to_update.items():
        setattr(db_message, key, value)
    
    db.commit()
    db.refresh(db_message)
    return db_message

def delete_chat_history(db: Session, chat_id: str, user_id: int) -> bool:
    # Проверяем, что чат принадлежит пользователю
    chat_messages = get_chat_history(db, chat_id)
    if not chat_messages or chat_messages[0].user_id != user_id:
        return False
    
    db.query(models.ChatHistory).filter(models.ChatHistory.chat_id == chat_id).delete()
    db.commit()
    return True 
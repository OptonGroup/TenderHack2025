from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Boolean, Text, JSON
from sqlalchemy.orm import relationship
from database import Base
import datetime


class User(Base):
    """
    Модель пользователя системы
    """
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    tenders = relationship("Tender", back_populates="creator", cascade="all, delete-orphan")
    bids = relationship("Bid", back_populates="bidder", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="uploader", cascade="all, delete-orphan")
    chat_history = relationship("ChatHistory", back_populates="user", cascade="all, delete-orphan")
    chat_ratings = relationship("ChatRating", back_populates="user", cascade="all, delete-orphan")


class Category(Base):
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    tenders = relationship("Tender", back_populates="category")


class Tender(Base):
    __tablename__ = "tenders"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=False)
    budget_min = Column(Float, nullable=True)
    budget_max = Column(Float, nullable=True)
    deadline = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    status = Column(String(20), default="active")
    creator_id = Column(Integer, ForeignKey("users.id"))
    category_id = Column(Integer, ForeignKey("categories.id"))
    
    creator = relationship("User", back_populates="tenders")
    category = relationship("Category", back_populates="tenders")
    bids = relationship("Bid", back_populates="tender")
    documents = relationship("Document", back_populates="tender")


class Bid(Base):
    __tablename__ = "bids"
    
    id = Column(Integer, primary_key=True, index=True)
    price = Column(Float, nullable=False)
    proposal = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    status = Column(String(20), default="pending")
    tender_id = Column(Integer, ForeignKey("tenders.id"))
    bidder_id = Column(Integer, ForeignKey("users.id"))
    
    tender = relationship("Tender", back_populates="bids")
    bidder = relationship("User", back_populates="bids")


class Document(Base):
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(512), nullable=False)
    upload_date = Column(DateTime, default=datetime.datetime.utcnow)
    file_type = Column(String(50), nullable=True)
    file_size = Column(Integer, nullable=True)
    tender_id = Column(Integer, ForeignKey("tenders.id"))
    tender = relationship("Tender", back_populates="documents")


class ChatHistory(Base):
    """
    Модель для хранения истории чата
    """
    __tablename__ = "chat_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    chat_id = Column(String, index=True)
    message = Column(String)
    is_bot = Column(Boolean, default=False)
    message_metadata = Column(JSON, nullable=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    
    user = relationship("User", back_populates="chat_history")


class ChatRating(Base):
    """
    Модель для хранения оценок чатов
    """
    __tablename__ = "chat_ratings"
    
    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(String, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    rating = Column(Integer)  # Оценка от 1 до 5
    comment = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    
    user = relationship("User", back_populates="chat_ratings")


class Data(Base):
    """Модель для хранения данных с заголовком и описанием"""
    __tablename__ = "data"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(Text, nullable=False, index=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow) 
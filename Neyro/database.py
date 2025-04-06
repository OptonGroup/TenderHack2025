import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

# Получение URL базы данных из переменных окружения
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./tenderhack.db")

# Создание движка SQLAlchemy
engine = create_engine(DATABASE_URL)

# Создание фабрики сеансов
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Создание базового класса для моделей
Base = declarative_base() 
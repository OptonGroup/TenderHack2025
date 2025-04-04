from typing import Generator, Optional
import os
from sqlalchemy import create_engine, Engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from dotenv import load_dotenv
import urllib.parse


load_dotenv()

Base = declarative_base()

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://admin:MI_TOCHNO_POBEDIM@109.73.195.217:5432/default_db"  # Запасное значение на случай отсутствия .env
)

DB_POOL_SIZE = int(os.environ.get("DB_POOL_SIZE", "5"))
DB_MAX_OVERFLOW = int(os.environ.get("DB_MAX_OVERFLOW", "10"))
DB_POOL_TIMEOUT = int(os.environ.get("DB_POOL_TIMEOUT", "30"))
DB_POOL_RECYCLE = int(os.environ.get("DB_POOL_RECYCLE", "1800"))
DB_ECHO = os.environ.get("DEBUG", "False").lower() == "true"


engine: Engine = create_engine(
    DATABASE_URL,
    pool_size=DB_POOL_SIZE,
    max_overflow=DB_MAX_OVERFLOW,
    pool_timeout=DB_POOL_TIMEOUT,
    pool_recycle=DB_POOL_RECYCLE,
    poolclass=QueuePool,
    echo=DB_ECHO,
)


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    class TestDb(Base):
        __tablename__ = 'testik'
        id = Column(Integer, primary_key=True)
        name = Column(String(50))

    Base.metadata.create_all(bind=engine)


def get_engine() -> Engine:
    return engine


if __name__ == "__main__":
    # Тестовое подключение
    try:
        with engine.connect() as connection:
            print("Соединение с БД успешно установлено!")
            result = connection.execute("SELECT 1 as test")
            print(f"Тестовый запрос: {result.fetchone()}")
    except Exception as e:
        print(f"Ошибка подключения к БД: {e}")


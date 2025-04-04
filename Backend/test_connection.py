#!/usr/bin/env python

import psycopg2
from dotenv import load_dotenv
import os

def test_psycopg2_connection():
    """
    Тестирует прямое подключение к базе данных через psycopg2
    """
    try:
        # Прямое подключение с указанными учетными данными
        conn = psycopg2.connect(
            host="109.73.195.217",
            database="default_db",
            user="admin",
            password="MI_TOCHNO_POBEDIM"
        )
        
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        db_version = cursor.fetchone()
        
        print("Успешное подключение к PostgreSQL!")
        print(f"Версия PostgreSQL: {db_version[0]}")
        
        cursor.close()
        conn.close()
        print("Соединение закрыто.")
        
        return True
    
    except Exception as e:
        print(f"Ошибка при подключении к PostgreSQL через psycopg2: {e}")
        return False


def test_env_connection():
    """
    Тестирует подключение с использованием переменных из .env файла
    """
    try:
        # Загрузка переменных окружения
        load_dotenv()
        
        # Получение данных из переменных окружения
        db_url = os.environ.get("DATABASE_URL")
        
        if not db_url:
            print("Ошибка: Не найдена переменная окружения DATABASE_URL")
            return False
        
        print(f"Найдена строка подключения в .env: {db_url}")
        
        # Парсинг строки подключения
        # postgresql://admin:MI_TOCHNO_POBEDIM@109.73.195.217:5432/default_db
        parts = db_url.replace("postgresql://", "").split("@")
        auth = parts[0].split(":")
        host_db = parts[1].split("/")
        host_port = host_db[0].split(":")
        
        user = auth[0]
        password = auth[1]
        host = host_port[0]
        port = int(host_port[1]) if len(host_port) > 1 else 5432
        database = host_db[1]
        
        # Подключение с данными из .env
        conn = psycopg2.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password
        )
        
        cursor = conn.cursor()
        cursor.execute("SELECT current_database();")
        db_name = cursor.fetchone()
        
        print("Успешное подключение к PostgreSQL из .env файла!")
        print(f"Имя базы данных: {db_name[0]}")
        
        cursor.close()
        conn.close()
        print("Соединение закрыто.")
        
        return True
        
    except Exception as e:
        print(f"Ошибка при подключении с использованием данных из .env: {e}")
        return False


if __name__ == "__main__":
    print("Тестирование прямого подключения к PostgreSQL...")
    direct_result = test_psycopg2_connection()
    
    print("\nТестирование подключения с использованием данных из .env файла...")
    env_result = test_env_connection()
    
    if direct_result and env_result:
        print("\nВсе тесты подключения успешно пройдены!")
    else:
        print("\nНе все тесты подключения успешны. Проверьте ошибки выше.") 
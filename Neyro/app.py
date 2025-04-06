"""
Приложение для ответов на вопросы пользователей с использованием гибридного подхода
"""

import os
import time
import pandas as pd
from model import Model
import fastapi
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
import uvicorn

app = fastapi.FastAPI()

# Добавляем middleware для CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class HybridAssistant:
    """
    Класс для работы с гибридной моделью ответов на вопросы пользователей.
    Предназначен для интеграции в бэкенд-приложения.
    """
    
    def __init__(self, model_path="model.pkl", dataset_path="docs/dataset.parquet", retrain=False):
        """
        Инициализация ассистента
        
        Args:
            model_path (str): Путь к файлу модели
            dataset_path (str): Путь к файлу с данными
            retrain (bool): Флаг необходимости переобучения модели
        """
        self.model_path = model_path
        self.dataset_path = dataset_path
        self.model = None
        self.is_initialized = False
        
        # Инициализация модели при создании объекта
        if retrain:
            self.retrain_model()
        else:
            self.initialize_model()
    
    def initialize_model(self):
        """
        Инициализация модели из существующего файла
        
        Returns:
            bool: Успешность инициализации
        """
        if not os.path.exists(self.dataset_path):
            raise FileNotFoundError(f"Файл с данными {self.dataset_path} не найден!")
        
        start_time = time.time()
        
        if not os.path.exists(self.model_path):
            return self.retrain_model()
        
        try:
            self.model = Model.load_model(self.model_path)
            self.is_initialized = True
            return True
        except Exception as e:
            self.is_initialized = False
            raise RuntimeError(f"Ошибка при загрузке модели: {e}")
    
    def retrain_model(self):
        """
        Создание и обучение новой модели
        
        Returns:
            bool: Успешность обучения
        """
        if not os.path.exists(self.dataset_path):
            raise FileNotFoundError(f"Файл с данными {self.dataset_path} не найден!")
        
        start_time = time.time()
        
        try:
            self.model = Model(self.dataset_path, use_bert=True, use_llm=True)
            self.model.train()
            self.model.save_model(self.model_path)
            self.is_initialized = True
            return True
        except Exception as e:
            self.is_initialized = False
            raise RuntimeError(f"Ошибка при создании модели: {e}")
    
    def analyze_query(self, query):
        """
        Анализ запроса пользователя
        
        Args:
            query (str): Запрос пользователя
            
        Returns:
            dict: Результаты анализа запроса
        """
        if not self.is_initialized:
            raise RuntimeError("Модель не инициализирована")
        
        return self.model.text_processor.classify_query(query)
    
    def get_answer(self, query, top_n=5, top_k_fragments=7):
        """
        Получение ответа на запрос пользователя
        
        Args:
            query (str): Запрос пользователя
            top_n (int): Количество релевантных документов для поиска
            top_k_fragments (int): Количество фрагментов для анализа
            
        Returns:
            dict: Ответ на запрос с метаданными
        """
        if not self.is_initialized:
            raise RuntimeError("Модель не инициализирована")
        
        if not query.strip():
            return {"answer": "Пустой запрос", "fragments": [], "sources": []}
        
        start_time = time.time()
        
        # Анализ запроса
        query_analysis = self.analyze_query(query)
        
        # Генерация ответа
        answer_data = self.model.generate_answer(query, top_n=top_n, top_k_fragments=top_k_fragments)
        
        # Добавляем время выполнения и анализ запроса
        answer_data["execution_time"] = time.time() - start_time
        answer_data["query_analysis"] = query_analysis
        
        return answer_data

assistant = HybridAssistant()

@app.get("/query")
async def get_answer_endpoint(query: str):
    """Основной эндпоинт для получения сгенерированного ответа."""
    return assistant.get_answer(query)

@app.get("/recommendations")
async def get_recommendations_endpoint(query: str, top_n: int = 10):
    """Эндпоинт для получения релевантных статей с промежуточными оценками."""
    if not assistant.is_initialized:
        raise fastapi.HTTPException(status_code=503, detail="Модель не инициализирована")
    
    if not query.strip():
        raise fastapi.HTTPException(status_code=400, detail="Пустой запрос")
        
    try:
        # Используем метод get_recommendations напрямую
        recommendations_df = assistant.model.get_recommendations(query, top_n=top_n)
        # Преобразуем DataFrame в список словарей для JSON-ответа
        # Обрабатываем NaN значения, чтобы избежать ошибок сериализации
        recommendations_list = recommendations_df.replace({np.nan: None}).to_dict('records')
        return {"recommendations": recommendations_list}
    except Exception as e:
        # Логируем ошибку на сервере (опционально)
        # print(f"Ошибка при получении рекомендаций: {e}")
        raise fastapi.HTTPException(status_code=500, detail=f"Ошибка при обработке запроса: {e}")

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=7777)

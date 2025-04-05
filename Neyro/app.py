"""
Приложение для ответов на вопросы пользователей с использованием гибридного подхода
"""

import os
import time
import pandas as pd
from model import Model

def main():
    """
    Основная функция для запуска приложения
    """
    model_path = "model.pkl"
    dataset_path = "docs/dataset.parquet"
    retrain = False
    
    print("Запуск гибридной модели для ответов на вопросы пользователей...")
    print("=" * 80)
    
    # Проверка наличия файлов
    if not os.path.exists(dataset_path):
        print(f"ОШИБКА: Файл с данными {dataset_path} не найден!")
        return
    
    start_time = time.time()
    
    # Загрузка или создание модели
    if retrain or not os.path.exists(model_path):
        print(f"Создание и обучение новой модели...")
        try:
            model = Model(dataset_path, use_bert=True, use_llm=True)
            print(f"Время загрузки данных: {time.time() - start_time:.2f} с")
            
            # Обучение модели
            model_train_start = time.time()
            model.train()
            print(f"Время обучения модели: {time.time() - model_train_start:.2f} с")
            
            # Сохранение модели
            model.save_model(model_path)
            print(f"Модель сохранена в {model_path}")
        except Exception as e:
            print(f"Ошибка при создании модели: {e}")
            return
    else:
        try:
            print(f"Загрузка существующей модели из {model_path}")
            model = Model.load_model(model_path)
            print(f"Время загрузки модели: {time.time() - start_time:.2f} с")
        except Exception as e:
            print(f"Ошибка при загрузке модели: {e}")
            print("Попробуйте установить retrain=True для создания новой модели")
            return
    
    print("\nМодель успешно загружена!")
    print("=" * 80)
    print("Для выхода введите 'exit' или 'выход'")
    
    # Основной цикл приложения
    while True:
        try:
            # Получение запроса от пользователя
            query = input("\nВведите ваш вопрос: ")
            
            # Проверка на выход
            if query.lower() in ['exit', 'выход', 'quit', 'q']:
                print("Завершение работы...")
                break
                
            if not query.strip():
                continue
                
            # Замер времени
            query_start_time = time.time()
            
            # Анализ запроса
            query_analysis = model.text_processor.classify_query(query)
            print(f"\nАнализ запроса:")
            print(f"  Тип запроса: {query_analysis['query_type']}")
            if query_analysis['user_role']:
                print(f"  Роль пользователя: {query_analysis['user_role']}")
            if query_analysis['component']:
                print(f"  Компонент: {query_analysis['component']}")
            
            # Генерация ответа с использованием гибридного подхода
            print("\nПоиск релевантной информации...")
            answer_data = model.generate_answer(query, top_n=5, top_k_fragments=7)
            
            # Вывод ответа
            print("\nОТВЕТ:\n" + "=" * 50)
            print(answer_data["answer"])
            print("=" * 50)
            
            # Вывод источников
            if answer_data["sources"]:
                print("\nИсточники:")
                for i, source in enumerate(answer_data["sources"], 1):
                    print(f"{i}. {source}")
            
            # Вывод времени выполнения
            print(f"\nВремя выполнения: {time.time() - query_start_time:.2f} с")
            
        except KeyboardInterrupt:
            print("\nРабота программы прервана пользователем")
            break
        except Exception as e:
            print(f"\nПроизошла ошибка: {e}")

if __name__ == "__main__":
    main() 
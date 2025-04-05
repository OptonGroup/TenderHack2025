"""
Модуль для поиска релевантных статей в базе знаний Портала поставщиков
"""

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import TruncatedSVD
import pickle
import torch
from sentence_transformers import SentenceTransformer
import re
import os
import time
from typing import List, Dict, Tuple, Optional, Any, Union

# Импортируем TextProcessor из utils
import utils

class Model:
    """
    Модель для семантического поиска релевантных статей в базе знаний
    Портала поставщиков на основе запросов пользователей.
    
    Использует комбинацию TF-IDF и BERT для достижения наилучших результатов.
    """
    def __init__(self, dataset_path: str, use_bert: bool = True):
        """
        Инициализация модели поиска
        
        Args:
            dataset_path (str): Путь к файлу с базой знаний (parquet)
            use_bert (bool): Использовать ли BERT для семантического поиска
        """
        # Загрузка датасета
        self.dataset = pd.read_parquet(dataset_path)
        
        # Обработчик текста
        self.text_processor = utils.TextProcessor()
        
        # TF-IDF векторизатор с улучшенными параметрами
        self.vectorizer = TfidfVectorizer(
            ngram_range=(1, 3),  # Униграммы, биграммы и триграммы
            max_features=20000,
            min_df=2,            # Игнорировать редкие термины
            use_idf=True,
            smooth_idf=True,
            sublinear_tf=True    # Логарифмическое масштабирование частот
        )
        
        # SVD для снижения размерности и латентно-семантического индексирования
        self.svd = TruncatedSVD(n_components=100, random_state=42)
        
        # Параметры модели
        self.use_bert = use_bert
        self.bert_model = None
        self.bert_embeddings = None
        self.tfidf_matrix = None
        self.lsa_matrix = None
        
        # Инициализация BERT модели для семантического поиска
        if self.use_bert:
            try:
                self.bert_model = SentenceTransformer('DeepPavlov/rubert-base-cased-sentence')
            except Exception as e:
                print(f"Не удалось загрузить BERT модель: {e}")
                self.use_bert = False
        
        # Дополнительные атрибуты для классификации и анализа запросов
        self.document_categories = {}  # Категории документов
        self.document_roles = {}       # Роли пользователей для документов
        self.document_topics = {}      # Темы документов

    def train(self):
        """
        Обучение модели поиска на датасете
        """
        print("Начало обучения модели...")
        
        # Объединяем заголовок и описание для лучшего поиска
        self.dataset['combined_text'] = self.dataset['Заголовок статьи'] + ' ' + self.dataset['Описание'].fillna('')
        
        # Классификация документов по типам
        print("Классификация документов...")
        self._classify_documents()
        
        # Построение словаря для исправления опечаток и извлечения аббревиатур
        print("Создание словаря терминов...")
        self.text_processor.build_vocabulary(self.dataset['combined_text'])
        
        # Предобработка текстов
        print("Предобработка текстов...")
        self.dataset['processed_text'] = self.dataset['combined_text'].apply(
            self.text_processor.preprocess_text
        )
        
        # Обучение TF-IDF векторизатора
        print("Обучение TF-IDF векторизатора...")
        self.tfidf_matrix = self.vectorizer.fit_transform(self.dataset['processed_text'])
        
        # Применение LSA (Латентно-семантического анализа)
        print("Применение LSA...")
        try:
            self.lsa_matrix = self.svd.fit_transform(self.tfidf_matrix)
            print(f"Объяснённая дисперсия LSA: {sum(self.svd.explained_variance_ratio_):.2f}")
        except Exception as e:
            print(f"Ошибка при применении LSA: {e}")
            self.lsa_matrix = None
        
        # Если используем BERT, создаем семантические эмбеддинги
        if self.use_bert:
            try:
                print("Создание BERT эмбеддингов...")
                self.bert_embeddings = self.bert_model.encode(
                    self.dataset['combined_text'].tolist(),
                    show_progress_bar=True,
                    batch_size=16
                )
                print(f"BERT эмбеддинги созданы, размер: {self.bert_embeddings.shape}")
            except Exception as e:
                print(f"Ошибка при создании BERT эмбеддингов: {e}")
                self.use_bert = False
        
        print("Обучение модели завершено")

    def _classify_documents(self):
        """
        Классификация документов из базы знаний по типам,
        ролям пользователей и темам
        """
        for idx, row in self.dataset.iterrows():
            text = row['combined_text'].lower()
            
            # Классификация документа
            classification = self.text_processor.classify_query(text)
            
            # Сохранение классификации
            self.document_categories[idx] = classification['query_type']
            self.document_roles[idx] = classification['user_role']
            self.document_topics[idx] = classification['component']
            
            # Добавление меток в датасет
            self.dataset.at[idx, 'query_type'] = classification['query_type']
            self.dataset.at[idx, 'user_role'] = classification['user_role']
            self.dataset.at[idx, 'component'] = classification['component']
            
            # Определение, является ли документ об ошибке
            self.dataset.at[idx, 'is_error'] = 1 if classification['query_type'] == 'error' else 0

    def predict(self, text: str) -> np.ndarray:
        """
        Вычисление релевантности между запросом и документами
        
        Args:
            text (str): Текст запроса
            
        Returns:
            np.ndarray: Массив значений релевантности для каждого документа
        """
        # Классификация запроса
        classification = self.text_processor.classify_query(text)
        query_type = classification['query_type']
        user_role = classification['user_role']
        component = classification['component']
        
        # Предобработка запроса
        processed_text = self.text_processor.preprocess_text(text)
        
        # Расширение запроса вариантами (для улучшения поиска)
        query_variants = self._generate_query_variants(text, classification)
        
        # Вычисление релевантности для всех вариантов запроса
        all_similarities = []
        
        for query, weight in query_variants:
            # Векторизация текста с помощью TF-IDF
            query_vector = self.vectorizer.transform([query])
            
            # TF-IDF сходство
            tfidf_similarity = cosine_similarity(query_vector, self.tfidf_matrix)[0]
            
            # LSA сходство (если доступно)
            lsa_similarity = np.zeros_like(tfidf_similarity)
            if self.lsa_matrix is not None:
                query_lsa = self.svd.transform(query_vector)
                lsa_similarity = cosine_similarity(query_lsa, self.lsa_matrix)[0]
            
            # BERT семантическое сходство (если доступно)
            bert_similarity = np.zeros_like(tfidf_similarity)
            if self.use_bert and self.bert_embeddings is not None:
                try:
                    # Получаем BERT эмбеддинг для запроса
                    query_embedding = self.bert_model.encode(text)
                    bert_similarity = cosine_similarity(
                        [query_embedding],
                        self.bert_embeddings
                    )[0]
                except Exception as e:
                    print(f"Ошибка при вычислении BERT сходства: {e}")
            
            # Комбинированное сходство с весами
            combined_similarity = 0.3 * tfidf_similarity + 0.2 * lsa_similarity
            if self.use_bert:
                combined_similarity += 0.5 * bert_similarity
            
            # Применение контекстных весов на основе классификации
            similarity = self._apply_context_weights(
                combined_similarity, 
                query_type, 
                user_role, 
                component
            )
            
            # Применение веса варианта запроса
            similarity = similarity * weight
            all_similarities.append(similarity)
        
        # Выбираем максимальное значение релевантности для каждого документа
        max_similarity = np.max(all_similarities, axis=0)
        
        return max_similarity

    def _generate_query_variants(self, text: str, classification: Dict[str, Any]) -> List[Tuple[str, float]]:
        """
        Генерация вариантов запроса для улучшения поиска
        
        Args:
            text (str): Исходный текст запроса
            classification (Dict[str, Any]): Результат классификации запроса
            
        Returns:
            List[Tuple[str, float]]: Список пар (вариант запроса, вес)
        """
        query_type = classification['query_type']
        user_role = classification['user_role']
        component = classification['component']
        
        # Базовый предобработанный запрос
        base_query = self.text_processor.preprocess_text(text)
        variants = [(base_query, 1.0)]
        
        # Разделение запроса на части (по знакам препинания)
        parts = re.split(r'[,.;:!?]', text)
        parts = [part.strip() for part in parts if part.strip()]
        
        # Если запрос можно разделить, добавляем основную часть
        if len(parts) > 1:
            main_part = parts[0]
            main_query = self.text_processor.preprocess_text(main_part)
            variants.append((main_query, 0.8))
        
        # Если определена роль пользователя, добавляем запрос с явным указанием роли
        if user_role:
            role_query = self.text_processor.preprocess_text(f"{text} {user_role}")
            variants.append((role_query, 1.2))
        
        # Если определен компонент, добавляем запрос с явным указанием компонента
        if component:
            component_query = self.text_processor.preprocess_text(f"{text} {component}")
            variants.append((component_query, 1.1))
        
        # Для запросов об ошибках добавляем усиленный вариант
        if query_type == 'error':
            error_terms = ['ошибка', 'проблема', 'не работает']
            if not any(term in text.lower() for term in error_terms):
                error_query = self.text_processor.preprocess_text(f"ошибка {text}")
                variants.append((error_query, 0.9))
        
        # Если в запросе есть указание на действие, добавляем вариант с усилением действия
        for action in classification['actions']:
            action_query = self.text_processor.preprocess_text(f"{action} {component or ''}")
            variants.append((action_query, 0.9))
        
        return variants

    def _apply_context_weights(
        self, 
        similarity: np.ndarray, 
        query_type: str, 
        user_role: Optional[str], 
        component: Optional[str]
    ) -> np.ndarray:
        """
        Применение весовых коэффициентов на основе контекста запроса
        
        Args:
            similarity (np.ndarray): Исходная релевантность
            query_type (str): Тип запроса (error/instruction/info)
            user_role (Optional[str]): Роль пользователя
            component (Optional[str]): Компонент системы
            
        Returns:
            np.ndarray: Модифицированная релевантность с учетом контекста
        """
        weighted_similarity = similarity.copy()
        
        # Применение весов по типу запроса
        for i in range(len(self.dataset)):
            doc_type = self.document_categories.get(i)
            if doc_type == query_type:
                weighted_similarity[i] += 0.2
        
        # Применение весов по роли пользователя
        if user_role:
            for i in range(len(self.dataset)):
                doc_role = self.document_roles.get(i)
                if doc_role == user_role:
                    weighted_similarity[i] += 0.3
        
        # Применение весов по компоненту системы
        if component:
            for i in range(len(self.dataset)):
                doc_topic = self.document_topics.get(i)
                if doc_topic == component:
                    weighted_similarity[i] += 0.25
        
        return weighted_similarity

    def get_recommendations(self, text: str, top_n: int = 5) -> pd.DataFrame:
        """
        Получение top_n наиболее релевантных документов
        
        Args:
            text (str): Текст запроса
            top_n (int): Количество документов для вывода
            
        Returns:
            pd.DataFrame: Датафрейм с найденными документами и их релевантностью
        """
        # Вычисление релевантности
        similarity = self.predict(text)
        
        # Получение индексов наиболее релевантных документов
        indices = np.argsort(similarity)[::-1][:top_n]
        
        # Формирование результата
        result = self.dataset.iloc[indices][['Заголовок статьи', 'Описание']].copy()
        result['релевантность'] = similarity[indices]
        
        # Добавление контекстной информации
        result['тип'] = [self.document_categories.get(i, '') for i in indices]
        result['роль'] = [self.document_roles.get(i, '') for i in indices]
        result['компонент'] = [self.document_topics.get(i, '') for i in indices]
        
        return result

    def save_model(self, model_path: str) -> None:
        """
        Сохранение модели в файл
        
        Args:
            model_path (str): Путь для сохранения модели
        """
        # Временно отключаем BERT модель для сериализации
        bert_model_tmp = None
        if self.use_bert:
            bert_model_tmp = self.bert_model
            self.bert_model = None
        
        # Сохранение модели
        with open(model_path, 'wb') as f:
            pickle.dump(self, f)
        
        # Восстановление BERT модели
        if bert_model_tmp is not None:
            self.bert_model = bert_model_tmp
        
        print(f"Модель сохранена в {model_path}")

    @staticmethod
    def load_model(model_path: str) -> 'Model':
        """
        Загрузка модели из файла
        
        Args:
            model_path (str): Путь к файлу с моделью
            
        Returns:
            Model: Загруженная модель
        """
        # Загрузка модели
        with open(model_path, 'rb') as f:
            model = pickle.load(f)
        
        # Если нужно, восстанавливаем BERT модель
        if model.use_bert:
            try:
                model.bert_model = SentenceTransformer('DeepPavlov/rubert-base-cased-sentence')
            except Exception as e:
                print(f"Не удалось загрузить BERT модель: {e}")
                model.use_bert = False
        
        return model


if __name__ == "__main__":
    import argparse
    
    # Создание парсера аргументов командной строки
    parser = argparse.ArgumentParser(description='Запуск модели поиска в базе знаний')
    parser.add_argument('--retrain', action='store_true', help='Переобучить модель')
    parser.add_argument('--query', type=str, default="Разблокировать участника компании", 
                        help='Поисковый запрос')
    parser.add_argument('--model_path', type=str, default="model.pkl", 
                        help='Путь к файлу модели')
    parser.add_argument('--dataset_path', type=str, default="docs/dataset.parquet", 
                        help='Путь к набору данных')
    parser.add_argument('--top_n', type=int, default=10, 
                        help='Количество результатов для вывода')
    
    # Разбор аргументов
    args = parser.parse_args()
    
    try:
        start_time = time.time()
        
        # Проверка необходимости переобучения модели
        if args.retrain or not os.path.exists(args.model_path):
            print(f"Создание и обучение новой модели...")
            # Создание модели
            model = Model(args.dataset_path, use_bert=True)
            print(f"Время загрузки данных: {time.time() - start_time:.2f} с")
            
            # Обучение модели
            start_time = time.time()
            model.train()
            print(f"Время обучения модели: {time.time() - start_time:.2f} с")
            
            # Сохранение модели
            model.save_model(args.model_path)
        else:
            print(f"Загрузка существующей модели из {args.model_path}")
            model = Model.load_model(args.model_path)
            print(f"Время загрузки модели: {time.time() - start_time:.2f} с")
        
        # Выполнение поиска
        start_time = time.time()
        print(f"\nЗапрос: '{args.query}'")
        
        # Анализ запроса
        query_analysis = model.text_processor.classify_query(args.query)
        print(f"Анализ запроса:")
        print(f"  Тип запроса: {query_analysis['query_type']}")
        print(f"  Роль пользователя: {query_analysis['user_role']}")
        print(f"  Компонент: {query_analysis['component']}")
        
        # Получение результатов
        recommendations = model.get_recommendations(args.query, top_n=args.top_n)
        
        # Вывод результатов
        print("\nНайденные статьи:")
        for i, (title, desc, rel, q_type, role, comp) in enumerate(zip(
            recommendations['Заголовок статьи'], 
            recommendations['Описание'], 
            recommendations['релевантность'],
            recommendations['тип'],
            recommendations['роль'],
            recommendations['компонент']
        )):
            print(f"{i+1}. {title} (релевантность: {rel:.4f})")
            print(f"   Тип: {q_type}, Роль: {role}, Компонент: {comp}")
            if not pd.isna(desc):
                print(f"   {desc[:100]}..." if len(str(desc)) > 100 else f"   {desc}")
            print()
        
        print(f"Время выполнения поиска: {time.time() - start_time:.2f} с")
    
    except Exception as e:
        print(f"Произошла ошибка: {e}")

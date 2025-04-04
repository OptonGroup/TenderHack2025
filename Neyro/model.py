import numpy as np  # Для работы с числовыми массивами
import pandas as pd  # Для работы с табличными данными
from sklearn.feature_extraction.text import TfidfVectorizer  # Для векторизации текста с помощью TF-IDF
from sklearn.metrics.pairwise import cosine_similarity  # Для расчета косинусного сходства между векторами
import pickle  # Для сериализации и десериализации объектов Python
import torch
from sentence_transformers import SentenceTransformer
from sklearn.ensemble import VotingClassifier
import re

# Импортируем TextProcessor из utils
import utils  # Используем абсолютный импорт вместо относительного

class Model:
    """
    Класс для создания и использования модели поиска похожих тендеров
    с улучшенной векторизацией и предобработкой текста
    """
    def __init__(self, dataset_path, use_bert=True):
        self.dataset = pd.read_parquet(dataset_path)  # Загрузка датасета из файла parquet
        # Улучшенный TF-IDF векторизатор с поддержкой n-грамм
        self.vectorizer = TfidfVectorizer(
            ngram_range=(1, 3),  # Униграммы, биграммы и триграммы
            max_features=20000,
            min_df=2
        )
        self.text_processor = utils.TextProcessor()  # Создание экземпляра обработчика текста
        self.model_tfidf = None
        self.use_bert = use_bert
        
        # Инициализируем трансформер, если используем BERT
        if self.use_bert:
            try:
                self.bert_model = SentenceTransformer('DeepPavlov/rubert-base-cased-sentence')
                self.bert_embeddings = None
            except Exception as e:
                print(f"Не удалось загрузить BERT модель: {e}")
                self.use_bert = False

    def train(self):   
        """
        Метод для обучения модели
        """
        # Объединяем заголовок и описание для лучшего поиска
        self.dataset['combined_text'] = self.dataset['Заголовок статьи'] + ' ' + self.dataset['Описание'].fillna('')
        
        # Добавляем метки для классификации типа запроса
        self.dataset['is_error'] = self.dataset['combined_text'].apply(
            lambda x: 1 if any(term in x.lower() for term in ['ошибка', 'проблема', 'не работает', 'не удается']) else 0
        )
        
        # Создаем словарь для исправления опечаток и извлечения аббревиатур
        self.text_processor.build_vocabulary(self.dataset['combined_text'])
        
        # Выводим найденные аббревиатуры
        if self.text_processor.abbreviations:
            print(f"Найдено {len(self.text_processor.abbreviations)} аббревиатур:")
            for abbr, full_form in list(self.text_processor.abbreviations.items())[:10]:
                print(f"  {abbr} -> {full_form}")
            if len(self.text_processor.abbreviations) > 10:
                print(f"  ... и еще {len(self.text_processor.abbreviations) - 10}")
        
        # Предобработка объединенного текста с улучшенными методами
        self.dataset['processed_text'] = self.dataset['combined_text'].apply(self.text_processor.preprocess_text)
        
        # Обогащаем данные: добавляем аббревиатуры к документам с полными формами и наоборот
        self._enrich_dataset_with_abbreviations()
        
        # Обучаем TF-IDF векторизатор
        self.model_tfidf = self.vectorizer.fit_transform(self.dataset['processed_text'])
        
        # Если используем BERT, вычисляем эмбеддинги для всех документов
        if self.use_bert:
            try:
                print("Создание BERT эмбеддингов для документов...")
                self.bert_embeddings = self.bert_model.encode(
                    self.dataset['combined_text'].tolist(), 
                    show_progress_bar=True, 
                    batch_size=16
                )
                print(f"BERT эмбеддинги созданы, размер: {self.bert_embeddings.shape}")
            except Exception as e:
                print(f"Ошибка при создании BERT эмбеддингов: {e}")
                self.use_bert = False

    def _enrich_dataset_with_abbreviations(self):
        """
        Обогащает данные, добавляя аббревиатуры и полные формы к соответствующим документам
        """
        enriched_processed_text = []
        
        for text, processed_text in zip(self.dataset['combined_text'], self.dataset['processed_text']):
            enriched_text = processed_text
            
            # Ищем аббревиатуры в тексте и добавляем их полные формы
            for abbr, full_form in self.text_processor.abbreviations.items():
                if abbr in text.upper():
                    enriched_text += f" {full_form.replace(' ', '_')}"
            
            # Ищем полные формы в тексте и добавляем их аббревиатуры
            for full_form, abbr in self.text_processor.full_forms.items():
                if full_form in text.lower():
                    enriched_text += f" {abbr}"
                    
            enriched_processed_text.append(enriched_text)
            
        # Заменяем обработанный текст на обогащенный
        self.dataset['processed_text'] = enriched_processed_text

    def _extract_intent(self, text):
        """
        Определяет намерение запроса (ошибка/инструкция/справка)
        """
        error_terms = ['ошибка', 'проблема', 'не работает', 'не удается', 'не могу', 'не получается']
        
        # Проверяем наличие терминов, связанных с ошибками
        is_error = any(term in text.lower() for term in error_terms)
        
        return 'error' if is_error else 'general'

    def _expand_query(self, query_text):
        """
        Расширяет запрос, добавляя варианты с аббревиатурами и полными формами
        """
        expanded_queries = [query_text]
        
        # Проверяем на аббревиатуры в запросе
        for abbr, full_form in self.text_processor.abbreviations.items():
            if abbr in query_text.upper():
                # Создаем вариант, где аббревиатура заменена полной формой
                expanded_queries.append(query_text.upper().replace(abbr, full_form))
        
        # Проверяем на полные формы в запросе
        for full_form, abbr in self.text_processor.full_forms.items():
            if full_form in query_text.lower():
                # Создаем вариант, где полная форма заменена аббревиатурой
                expanded_queries.append(query_text.lower().replace(full_form, abbr))
        
        return expanded_queries

    def predict(self, text):
        """
        Метод для расчета сходства между запросом и всеми документами в датасете
        """
        intent = self._extract_intent(text)
        
        # Расширяем запрос вариантами с аббревиатурами и полными формами
        expanded_queries = self._expand_query(text)
        
        # Обрабатываем каждый вариант запроса
        all_similarities = []
        for query in expanded_queries:
            processed_text = self.text_processor.preprocess_text(query)
            
            # TF-IDF векторизация запроса
            text_vector_tfidf = self.vectorizer.transform([processed_text])
            
            # Косинусное сходство для TF-IDF
            similarity_tfidf = cosine_similarity(text_vector_tfidf, self.model_tfidf)[0]
            
            # Если используем BERT, вычисляем и комбинируем с TF-IDF
            if self.use_bert and self.bert_embeddings is not None:
                try:
                    # Получаем BERT эмбеддинг для запроса
                    query_embedding = self.bert_model.encode([query])[0]
                    
                    # Косинусное сходство для BERT эмбеддингов
                    similarity_bert = cosine_similarity(
                        [query_embedding], 
                        self.bert_embeddings
                    )[0]
                    
                    # Комбинируем результаты: 0.6 * BERT + 0.4 * TF-IDF
                    similarity = 0.6 * similarity_bert + 0.4 * similarity_tfidf
                    
                    # Повышаем вес документов, соответствующих намерению запроса
                    if intent == 'error':
                        # Если запрос об ошибке, повышаем вес документов с ошибками
                        similarity = similarity + 0.2 * self.dataset['is_error'].values
                except Exception as e:
                    print(f"Ошибка при использовании BERT: {e}, используем только TF-IDF")
                    similarity = similarity_tfidf
            else:
                similarity = similarity_tfidf
                
                # Применяем весовые коэффициенты на основе намерения запроса
                if intent == 'error':
                    similarity = similarity + 0.2 * self.dataset['is_error'].values
            
            all_similarities.append(similarity)
            
        # Берем максимальную вероятность для каждого документа из всех вариантов запроса
        max_similarity = np.max(all_similarities, axis=0)
            
        return max_similarity
    
    def get_recommendations(self, text, top_n=5):
        """
        Метод для получения top_n наиболее похожих документов
        """
        similarity = self.predict(text)
        indices = np.argsort(similarity)[::-1][:top_n]
        
        result = self.dataset.iloc[indices][['Заголовок статьи', 'Описание']].copy()
        result['вероятность'] = similarity[indices]
        
        return result
    
    def save_model(self, model_path):
        """
        Метод для сохранения модели в файл
        """
        # Если используем BERT, временно отключаем модель перед сохранением
        bert_model_tmp = None
        if self.use_bert:
            bert_model_tmp = self.bert_model
            self.bert_model = None
        
        with open(model_path, 'wb') as f:
            pickle.dump(self, f)
        
        # Восстанавливаем модель BERT
        if bert_model_tmp is not None:
            self.bert_model = bert_model_tmp
            
    @staticmethod
    def load_model(model_path):
        """
        Статический метод для загрузки модели из файла
        """
        with open(model_path, 'rb') as f:
            model = pickle.load(f)
            
        # Если используем BERT, загружаем модель после десериализации
        if model.use_bert:
            try:
                model.bert_model = SentenceTransformer('DeepPavlov/rubert-base-cased-sentence')
            except Exception as e:
                print(f"Не удалось загрузить BERT модель: {e}")
                model.use_bert = False
                
        return model
        

if __name__ == "__main__":
    import time
    import os
    import argparse
    
    retrain = False
    
    model_path = 'model.pkl'
    
    try:
        start_time = time.time()
        
        # Проверяем, нужно ли заново обучить модель или загрузить существующую
        if retrain or not os.path.exists(model_path):
            print("Создание и обучение новой модели...")
            # Создание модели с указанием пути к датасету
            model = Model('docs/dataset.parquet', use_bert=True)
            print(f"Время загрузки данных: {time.time() - start_time:.2f} секунд")

            start_time = time.time()
            # Обучение модели
            model.train()
            print(f"Время обучения модели: {time.time() - start_time:.2f} секунд")
            
            # Сохраняем обученную модель
            model.save_model(model_path)
            print(f"Модель сохранена в файл: {model_path}")
        else:
            print(f"Загрузка существующей модели из файла: {model_path}")
            model = Model.load_model(model_path)
            print(f"Время загрузки модели: {time.time() - start_time:.2f} секунд")

        start_time = time.time()

        # Получение рекомендаций для основного запроса
        print("\nОсновной результат поиска:")
        recommendations = model.get_recommendations(
            "Разблокировать участника компании",
            top_n=10
        )
        print("Найденные статьи:")
        # Вывод найденных статей
        for i, (title, desc, prob) in enumerate(zip(recommendations['Заголовок статьи'], recommendations['Описание'], recommendations['вероятность'])):
            print(f"{i+1}. {title} (вероятность: {prob:.4f})")
            if not pd.isna(desc):
                print(f"   {desc[:100]}..." if len(str(desc)) > 100 else f"   {desc}")
            print()
        print(f"Время получения рекомендаций: {time.time() - start_time:.2f} секунд")
    except Exception as e:
        print(f"Произошла ошибка: {e}")  # Обработка возможных исключений

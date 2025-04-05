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
from transformers import pipeline
from nltk.tokenize import sent_tokenize, word_tokenize

# Импортируем TextProcessor из utils
import utils

class Model:
    """
    Модель для семантического поиска релевантных статей в базе знаний
    Портала поставщиков на основе запросов пользователей.
    
    Использует комбинацию TF-IDF и BERT для достижения наилучших результатов.
    """
    def __init__(self, dataset_path: str, use_bert: bool = True, use_llm: bool = True):
        """
        Инициализация модели поиска
        
        
        dataset_path (str): Путь к файлу с базой знаний (parquet)
        use_bert (bool): Использовать ли BERT для семантического поиска
        use_llm (bool): Использовать ли LLM для генерации ответов
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
        
        # Инициализация LLM для генерации ответов
        self.use_llm = use_llm
        self.llm = None
        if self.use_llm:
            try:
                self.llm = pipeline("text-generation", model="microsoft/Phi-3-mini-4k-instruct", trust_remote_code=True)
                print("LLM модель успешно загружена")
            except Exception as e:
                print(f"Не удалось загрузить LLM модель: {e}")
                self.use_llm = False

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
            
            # Комбинированное сходство с весами (увеличиваем вес TF-IDF и LSA)
            combined_similarity = 0.5 * tfidf_similarity + 0.2 * lsa_similarity
            if self.use_bert:
                combined_similarity += 0.3 * bert_similarity
            
            
            # Применение контекстных весов на основе классификации
            similarity = self._apply_context_weights(
                combined_similarity, 
                query_type, 
                user_role, 
                component,
                text
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
        component: Optional[str],
        text: str = None
    ) -> np.ndarray:
        """
        Применение весовых коэффициентов на основе контекста запроса
        
        
        similarity (np.ndarray): Исходная релевантность
        query_type (str): Тип запроса (error/instruction/info)
        user_role (Optional[str]): Роль пользователя
        component (Optional[str]): Компонент системы
        text (str, optional): Текст запроса для дополнительной обработки
            
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
        
        # Дополнительная обработка ключевых слов запроса
        if text:
            text_lower = text.lower()
            keywords = []
            
            
            # Если найдены ключевые слова, повышаем релевантность документов, содержащих их
            if keywords:
                for i in range(len(self.dataset)):
                    title = self.dataset.iloc[i]['Заголовок статьи'].lower()
                    desc = str(self.dataset.iloc[i]['Описание']).lower() if not pd.isna(self.dataset.iloc[i]['Описание']) else ""
                    combined_text = f"{title} {desc}"
                    
                    for keyword in keywords:
                        if keyword in combined_text:
                            # Увеличиваем вес в зависимости от того, сколько раз ключевое слово 
                            # встречается в тексте и насколько текст информативен
                            count = combined_text.count(keyword)
                            boost = min(0.4, 0.1 * count)  # Максимум +0.4 к релевантности
                            
                            # Штраф за слишком короткие описания
                            content_length = len(desc.split())
                            
                            weighted_similarity[i] += boost
        
        return weighted_similarity

    def get_recommendations(self, text: str, top_n: int = 5) -> pd.DataFrame:
        """
        Получение top_n наиболее релевантных документов
        
        
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
    
    def _split_text_into_segments(self, text: str, segment_size: int = 150, overlap: int = 50) -> List[str]:
        """
        Разбиение текста на перекрывающиеся сегменты
        
        text (str): Текст для разбиения
        segment_size (int): Размер сегмента в словах
        overlap (int): Размер перекрытия между сегментами в словах
        
        Returns:
            List[str]: Список сегментов текста
        """
        if not text or pd.isna(text):
            return []
            
        # Разбиваем текст на предложения
        sentences = sent_tokenize(text)
        segments = []
        
        # Если текст короткий, возвращаем его целиком
        if len(sentences) <= 3:
            return [text]
            
        # Разбиваем текст на сегменты с перекрытием
        current_segment = []
        current_word_count = 0
        
        for sentence in sentences:
            words = word_tokenize(sentence)
            current_segment.append(sentence)
            current_word_count += len(words)
            
            # Если достигнут размер сегмента, сохраняем его
            if current_word_count >= segment_size:
                segments.append(' '.join(current_segment))
                
                # Оставляем последние слова для перекрытия
                overlap_sentences = []
                overlap_word_count = 0
                
                # Идем с конца и собираем предложения до достижения нужного перекрытия
                for sent in reversed(current_segment):
                    sent_words = word_tokenize(sent)
                    if overlap_word_count + len(sent_words) <= overlap:
                        overlap_sentences.insert(0, sent)
                        overlap_word_count += len(sent_words)
                    else:
                        break
                
                # Начинаем новый сегмент с предложений перекрытия
                current_segment = overlap_sentences
                current_word_count = overlap_word_count
        
        # Добавляем последний сегмент, если он не пустой
        if current_segment:
            segments.append(' '.join(current_segment))
            
        return segments
    
    def extract_relevant_fragments(self, text: str, top_n: int = 5, top_k_fragments: int = 10) -> List[Dict[str, Any]]:
        """
        Извлечение наиболее релевантных фрагментов из статей для заданного запроса
        
        text (str): Текст запроса
        top_n (int): Количество статей для анализа
        top_k_fragments (int): Количество фрагментов для извлечения
        
        Returns:
            List[Dict[str, Any]]: Список словарей с информацией о релевантных фрагментах
        """
        # Получаем наиболее релевантные статьи
        recommendations = self.get_recommendations(text, top_n=top_n)
        
        # Классифицируем запрос
        query_classification = self.text_processor.classify_query(text)
        
        # Создаем вектор запроса
        if self.use_bert:
            query_embedding = self.bert_model.encode(text)
        
        all_fragments = []
        
        # Проверяем, есть ли ключевые слова в запросе
        text_lower = text.lower()
        
        # Для каждой статьи извлекаем релевантные фрагменты
        for i, row in recommendations.iterrows():
            title = row['Заголовок статьи']
            description = row['Описание'] if not pd.isna(row['Описание']) else ""
            full_text = f"{title}. {description}"
            article_relevance = row['релевантность']
            
            
            # Разбиваем статью на сегменты
            segments = self._split_text_into_segments(full_text)
            
            # Вычисляем релевантность каждого сегмента
            for segment in segments:
                # Пропускаем слишком короткие фрагменты (менее 20 слов)
                word_count = len(segment.split())
                if word_count < 20:
                    continue
                
                # Вычисляем штраф за короткие тексты
                length_penalty = min(1.0, word_count / 50)  # Полный вес только для текстов от 50 слов
                
                if self.use_bert:
                    # BERT-эмбединг для сегмента
                    try:
                        segment_embedding = self.bert_model.encode(segment)
                        bert_similarity = cosine_similarity([query_embedding], [segment_embedding])[0][0]
                        
                        # Добавляем лексический поиск с TF-IDF
                        processed_segment = self.text_processor.preprocess_text(segment)
                        segment_vector = self.vectorizer.transform([processed_segment])
                        tfidf_similarity = cosine_similarity(segment_vector, self.vectorizer.transform([self.text_processor.preprocess_text(text)]))[0][0]
                        
                        # Комбинируем с большим весом для TF-IDF
                        segment_relevance = 0.5 * tfidf_similarity + 0.5 * bert_similarity
                    except:
                        # Если возникла ошибка, используем только TF-IDF
                        processed_segment = self.text_processor.preprocess_text(segment)
                        segment_vector = self.vectorizer.transform([processed_segment])
                        segment_relevance = cosine_similarity(segment_vector, self.vectorizer.transform([self.text_processor.preprocess_text(text)]))[0][0]
                else:
                    # TF-IDF для сегмента
                    processed_segment = self.text_processor.preprocess_text(segment)
                    segment_vector = self.vectorizer.transform([processed_segment])
                    segment_relevance = cosine_similarity(segment_vector, self.vectorizer.transform([self.text_processor.preprocess_text(text)]))[0][0]
                
                # Применяем штраф за длину текста
                segment_relevance = segment_relevance * length_penalty
                
                # Учитываем релевантность статьи при оценке сегмента
                combined_relevance = 0.7 * segment_relevance + 0.3 * article_relevance
                
                # Проверяем присутствие ключевых слов запроса в сегменте
                segment_lower = segment.lower()
                
                all_fragments.append({
                    'fragment': segment,
                    'relevance': combined_relevance,
                    'title': title,
                    'article_type': row['тип'],
                    'user_role': row['роль'],
                    'component': row['компонент']
                })
        
        # Сортируем фрагменты по релевантности
        all_fragments.sort(key=lambda x: x['relevance'], reverse=True)
        
        # Возвращаем top_k наиболее релевантных фрагментов
        return all_fragments[:top_k_fragments]
    
    def create_prompt_for_llm(self, text: str, fragments: List[Dict[str, Any]]) -> str:
        """
        Создание промпта для LLM на основе запроса и релевантных фрагментов
        
        text (str): Текст запроса
        fragments (List[Dict[str, Any]]): Список релевантных фрагментов
        
        Returns:
            str: Промпт для LLM
        """
        # Классифицируем запрос
        query_classification = self.text_processor.classify_query(text)
        
        # Формируем промпт
        prompt = f"""Пользователь задал вопрос, я тебе даю его вопрос(он может быть с орфографическими ошибками, неточностями и т.д.) и даю фрагменты из нашей базы знаний. тебе нужно соеденить все фрагменты в один ответ на вопрос пользователя, ответ должен ссылаться на источник ифнормации. Информацию можно использовать только из фрагментов, не используй другие источники.
Вопрос пользователя: {text}
Тип запроса: {query_classification['query_type']}
Роль пользователя: {query_classification['user_role'] or 'Не определена'}
Компонент: {query_classification['component'] or 'Не определен'}

Релевантные фрагменты из базы знаний:
"""
        
        # Добавляем фрагменты
        for i, fragment in enumerate(fragments, 1):
            prompt += f"\n--- Фрагмент {i} (из статьи '{fragment['title']}') ---\n{fragment['fragment']}\n"
        
        return prompt
    
    def generate_answer(self, text: str, top_n: int = 5, top_k_fragments: int = 7) -> Dict[str, Any]:
        """
        Генерация ответа на запрос пользователя
        
        text (str): Текст запроса
        top_n (int): Количество статей для анализа
        top_k_fragments (int): Количество фрагментов для извлечения
        
        Returns:
            Dict[str, Any]: Словарь с ответом и дополнительной информацией
        """
        # Отключаем LLM из-за проблем совместимости
        self.use_llm = False
        
        # Классификация запроса
        query_classification = self.text_processor.classify_query(text)
        
        # Проверяем, нужно ли перенаправить пользователя к оператору
        if query_classification.get('needs_operator', False):
            return {
                "answer": "Для решения вашей проблемы требуется помощь оператора. Мы переводим вас на специалиста технической поддержки.",
                "fragments": [],
                "sources": [],
                "needs_operator": True
            }
        
        # Извлекаем релевантные фрагменты
        fragments = self.extract_relevant_fragments(text, top_n=top_n, top_k_fragments=top_k_fragments)
        
        # Если фрагментов нет, возвращаем сообщение об ошибке
        if not fragments:
            return {
                "answer": "К сожалению, не удалось найти релевантную информацию по вашему запросу.",
                "fragments": [],
                "sources": []
            }
        
        # Генерируем ответ на основе релевантных фрагментов без использования LLM
        try:
            # Составляем ответ из наиболее релевантных фрагментов
            if fragments:
                # Берем самый релевантный фрагмент как основу ответа
                top_fragment = fragments[0]['fragment']
                title = fragments[0]['title']
                
                # Формируем вступление в зависимости от типа запроса
                intro = ""
                if query_classification['query_type'] == 'error':
                    intro = "Для решения вашей проблемы рекомендуется: "
                elif query_classification['query_type'] == 'instruction':
                    intro = "Инструкция по вашему запросу: "
                else:
                    intro = "По вашему запросу найдена следующая информация: "
                
                # Формируем основную часть ответа
                answer = f"{intro}\n\n{top_fragment}\n\nИсточник: {title}"
                
                # Если есть дополнительные фрагменты, добавляем их
                if len(fragments) > 1:
                    answer += "\n\nДополнительная информация:"
                    
                    for i in range(1, min(3, len(fragments))):
                        fragment = fragments[i]
                        answer += f"\n\n{fragment['fragment']}\nИсточник: {fragment['title']}"
            else:
                answer = "К сожалению, не удалось сформировать ответ на ваш запрос."
            
            # Получаем источники (уникальные заголовки статей)
            sources = list(set([fragment['title'] for fragment in fragments]))
            
            return {
                "answer": answer,
                "fragments": [f['fragment'] for f in fragments],
                "sources": sources
            }
        except Exception as e:
            print(f"Ошибка при генерации ответа: {e}")
            # В случае ошибки возвращаем первый фрагмент как ответ
            if fragments:
                answer = f"По вашему запросу: \n\n{fragments[0]['fragment']}\n\nИсточник: {fragments[0]['title']}"
            else:
                answer = "Произошла ошибка при обработке вашего запроса."
                
            return {
                "answer": answer,
                "fragments": [f['fragment'] for f in fragments],
                "sources": list(set([fragment['title'] for fragment in fragments]))
            }

    def save_model(self, model_path: str) -> None:
        """
        Сохранение модели в файл
        
        
        model_path (str): Путь для сохранения модели
        """
        # Временно отключаем BERT модель и LLM для сериализации
        bert_model_tmp = None
        llm_tmp = None
        
        if self.use_bert:
            bert_model_tmp = self.bert_model
            self.bert_model = None
        
        if self.use_llm:
            llm_tmp = self.llm
            self.llm = None
        
        # Сохранение модели
        with open(model_path, 'wb') as f:
            pickle.dump(self, f)
        
        # Восстановление BERT модели и LLM
        if bert_model_tmp is not None:
            self.bert_model = bert_model_tmp
            
        if llm_tmp is not None:
            self.llm = llm_tmp
        
        print(f"Модель сохранена в {model_path}")

    @staticmethod
    def load_model(model_path: str) -> 'Model':
        """
        Загрузка модели из файла
        
        
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
        
        # Если нужно, восстанавливаем LLM
        if model.use_llm:
            try:
                model.llm = pipeline("text-generation", model="microsoft/Phi-3-mini-4k-instruct", trust_remote_code=True)
                print("LLM модель успешно загружена")
            except Exception as e:
                print(f"Не удалось загрузить LLM модель: {e}")
                model.use_llm = False
                
        return model


if __name__ == "__main__":
    retrain = False
    query = """ "ОрТИКуЛь" """
    model_path = "model.pkl"
    dataset_path = "docs/dataset.parquet"
    top_n = 10
    
    try:
        start_time = time.time()
        
        # Проверка необходимости переобучения модели
        if retrain or not os.path.exists(model_path):
            print(f"Создание и обучение новой модели...")
            # Создание модели
            model = Model(dataset_path, use_bert=True, use_llm=True)
            print(f"Время загрузки данных: {time.time() - start_time:.2f} с")
            
            # Обучение модели
            start_time = time.time()
            model.train()
            print(f"Время обучения модели: {time.time() - start_time:.2f} с")
            
            # Сохранение модели
            model.save_model(model_path)
        else:
            print(f"Загрузка существующей модели из {model_path}")
            model = Model.load_model(model_path)
            print(f"Время загрузки модели: {time.time() - start_time:.2f} с")
        
        # Выполнение поиска
        start_time = time.time()
        print(f"\nЗапрос: '{query}'")
        
        # Анализ запроса
        query_analysis = model.text_processor.classify_query(query)
        print(f"Анализ запроса:")
        print(f"  Тип запроса: {query_analysis['query_type']}")
        print(f"  Роль пользователя: {query_analysis['user_role']}")
        print(f"  Компонент: {query_analysis['component']}")
        
        # Получение релевантных фрагментов
        print("\nИзвлечение релевантных фрагментов...")
        fragments = model.extract_relevant_fragments(query, top_n=top_n, top_k_fragments=7)
        
        # Генерация ответа с использованием LLM
        print("\nГенерация ответа на основе релевантных фрагментов...")
        answer_data = model.generate_answer(query, top_n=top_n, top_k_fragments=7)
        
        # Вывод ответа
        print("\nОтвет:")
        print(answer_data["answer"])
        
        print("\nИсточники:")
        for source in answer_data["sources"]:
            print(f"- {source}")
        
        # Получение результатов для сравнения
        recommendations = model.get_recommendations(query, top_n=top_n)
        
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
        
        print(f"Время выполнения: {time.time() - start_time:.2f} с")
    
    except Exception as e:
        print(f"Произошла ошибка: {e}")
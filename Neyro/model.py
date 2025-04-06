"""
Модуль для поиска релевантных статей в базе знаний Портала поставщиков
"""

# Импорт библиотек для работы с данными и математических операций
import numpy as np  # Библиотека для научных вычислений и работы с массивами
import pandas as pd  # Библиотека для обработки и анализа структурированных данных

# Импорт компонентов для векторизации текста и вычисления схожести
from sklearn.feature_extraction.text import TfidfVectorizer  # Для преобразования текста в TF-IDF векторы
from sklearn.metrics.pairwise import cosine_similarity  # Для расчета косинусного сходства между векторами
from sklearn.decomposition import TruncatedSVD  # Для снижения размерности векторов (LSA)

# Импорт библиотек для сохранения/загрузки моделей и работы с файлами


import pickle  # Для сериализации объектов Python
import os  # Для работы с файловой системой
import time  # Для измерения времени выполнения

# Импорт библиотек для работы с нейронными сетями
import torch  # Фреймворк для глубокого обучения
from sentence_transformers import SentenceTransformer, CrossEncoder  # Для создания эмбеддингов предложений
from transformers import pipeline  # Для работы с предобученными моделями трансформеров

# Импорт инструментов для обработки текста
import re  # Для работы с регулярными выражениями
from nltk.tokenize import sent_tokenize, word_tokenize  # Для разбиения текста на предложения и слова
from rank_bm25 import BM25Okapi # Для ранжирования с использованием BM25

# Импорт типов для аннотаций
from typing import List, Dict, Tuple, Optional, Any, Union  # Для типизации кода

# Импортируем TextProcessor из utils
import utils

class Model:
    """
    Модель для семантического поиска релевантных статей в базе знаний
    Портала поставщиков на основе запросов пользователей.
    
    Использует комбинацию TF-IDF и BERT для достижения наилучших результатов.
    """
    CANDIDATES_K = 100 # Количество кандидатов для этапа переранжирования

    def __init__(self, dataset_path: str, use_bert: bool = True, use_llm: bool = True, use_cross_encoder: bool = True):
        """
        Инициализация модели поиска
        
        
        dataset_path (str): Путь к файлу с базой знаний (parquet)
        use_bert (bool): Использовать ли BERT для семантического поиска
        use_llm (bool): Использовать ли LLM для генерации ответов
        use_cross_encoder (bool): Использовать ли Cross-Encoder для переранжирования
        """
        # Сохраняем путь к датасету
        self.dataset_path = dataset_path
        
        # Загрузка датасета
        self.dataset = pd.read_parquet(dataset_path)
        
        # Обработчик текста
        self.text_processor = utils.TextProcessor()
        
        # Инициализация BM25
        self.bm25 = None
        
        # Параметры модели
        self.use_bert = use_bert
        self.bert_model = None
        self.bert_embeddings = None
        self.use_cross_encoder = use_cross_encoder
        self.cross_encoder = None
        self.tfidf_matrix = None
        self.lsa_matrix = None
        
        # Инициализация BERT модели для семантического поиска
        if self.use_bert:
            try:
                self.bert_model = SentenceTransformer('ai-forever/sbert_large_nlu_ru')
                print("SentenceTransformer (bert_model) загружен.")
            except Exception as e:
                print(f"Не удалось загрузить BERT модель: {e}")
                self.use_bert = False
        
        # Инициализация Cross-Encoder для переранжирования
        if self.use_cross_encoder:
            try:
                self.cross_encoder = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
                print("CrossEncoder модель загружена.")
            except Exception as e:
                print(f"Не удалось загрузить CrossEncoder модель: {e}. Переранжирование с CrossEncoder отключено.")
                self.use_cross_encoder = False
        
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
        # Сначала полная предобработка для BERT и возможных будущих нужд
        self.dataset['processed_text_full'] = self.dataset['combined_text'].apply(
            self.text_processor.preprocess_text
        )
        # Затем упрощенная предобработка ТОЛЬКО для BM25
        print("Упрощенная предобработка текстов для BM25...")
        # Мы будем использовать результат _preprocess_for_bm25 напрямую (список токенов)
        tokenized_corpus_for_bm25 = self.dataset['combined_text'].apply(
            self.text_processor._preprocess_for_bm25
        ).tolist()

        # --- Используем уже готовый список списков токенов --- 
        # Отфильтруем пустые списки, которые могли появиться после упрощенной обработки
        self.bm25_indices = [idx for idx, tokens in enumerate(tokenized_corpus_for_bm25) if tokens] 
        filtered_tokenized_corpus = [tokens for tokens in tokenized_corpus_for_bm25 if tokens]

        # Обучение BM25
        print("Обучение BM25...")
        # Проверка, что корпус не пуст
        if filtered_tokenized_corpus:
            print(f"Пример токенизированного документа для BM25 (первые 20 токенов): {filtered_tokenized_corpus[0][:20]}")
            self.bm25 = BM25Okapi(filtered_tokenized_corpus)
            print("Модель BM25 обучена.")
        else:
            print("Ошибка: Корпус для обучения BM25 пуст после фильтрации.")

        # Если используем BERT, создаем семантические эмбеддинги
        if self.use_bert:
            try:
                print("Создание эмбеддингов с помощью SentenceTransformer (bert_model)...")
                self.bert_embeddings = self.bert_model.encode(
                    self.dataset['combined_text'].tolist(),
                    show_progress_bar=True,
                    batch_size=16
                )
                print(f"Эмбеддинги (bert_embeddings) созданы, размер: {self.bert_embeddings.shape}")
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

    def predict(self, text: str) -> Tuple[np.ndarray, Dict[str, np.ndarray]]:
        """
        Вычисление релевантности между запросом и документами
        
        
        text (str): Текст запроса
            
        Returns:
            Tuple[np.ndarray, Dict[str, np.ndarray]]: Массив значений релевантности для каждого документа и словарь промежуточных оценок
        """
        # Классификация запроса
        classification = self.text_processor.classify_query(text)
        query_type = classification['query_type']
        user_role = classification['user_role']
        component = classification['component']
        
        # Расширение запроса вариантами (для улучшения поиска)
        query_variants = self._generate_query_variants(text, classification)
        
        # Вычисление релевантности для всех вариантов запроса
        all_scores = []
        num_docs = len(self.dataset) # Количество документов
        # Структура для хранения промежуточных оценок кандидатов для каждого варианта
        all_candidate_data_variants = [] 
        
        # Вычисляем эмбеддинг запроса один раз, если используем BERT
        query_embedding = None
        if self.use_bert and self.bert_model:
            try:
                # Используем исходный текст для BERT / CrossEncoder
                query_embedding = self.bert_model.encode(text) 
            except Exception as e:
                print(f"Ошибка при кодировании запроса BERT: {e}")
                self.use_bert = False # Отключаем BERT для этого запроса, если кодирование не удалось

        # Предобрабатываем исходный запрос ОДИН РАЗ
        processed_base_query = self.text_processor.preprocess_text(text)
        # print(f"\n--- [DEBUG] Предобработанный базовый запрос: ---\n{processed_base_query}\n---") # Убираем отладку

        for query, weight in query_variants:
            # Токенизация предобработанного запроса
            # Сначала получаем УПРОЩЕННУЮ предобработку для варианта запроса `query`
            # (query все еще содержит полную предобработку из _generate_query_variants)
            # Лучше передавать исходный текст варианта в _preprocess_for_bm25, 
            # но _generate_query_variants сейчас возвращает уже обработанный.
            # Пока используем `text` - базовый исходный текст, но это НЕ ИДЕАЛЬНО.
            # TODO: Переделать _generate_query_variants, чтобы возвращал исходные тексты вариантов.
            tokenized_query_for_bm25 = self.text_processor._preprocess_for_bm25(text) # Используем базовый текст
            if not tokenized_query_for_bm25:
                print(f"Предупреждение: Пустой токенизированный запрос для BM25 после упрощенной обработки. Пропускаем вариант.")
                all_scores.append(np.zeros(num_docs))
                all_candidate_data_variants.append(None)
                continue
            
            # ===== Этап 1: Retrieval (BM25) =====
            bm25_scores = np.zeros(num_docs)
            if self.bm25:
                try:
                    # Используем УПРОЩЕННУЮ токенизацию запроса
                    bm25_raw_scores = self.bm25.get_scores(tokenized_query_for_bm25)
                    # Проверка совпадения размеров: bm25_indices теперь содержит индексы оригинального датасета
                    # для которых был создан корпус filtered_tokenized_corpus
                    if hasattr(self, 'bm25_indices') and len(bm25_raw_scores) == len(self.bm25_indices): # <<<--- ИСПРАВЛЕНО: Сравниваем с количеством индексов
                        # Создаем временный массив оценок, индексированный так же, как bm25_indices
                        scores_for_indices = np.zeros(len(self.bm25_indices))
                        # Заполняем оценки, полученные от BM25
                        scores_for_indices = bm25_raw_scores
                        # Распределяем оценки по оригинальным индексам датасета
                        for i, original_idx in enumerate(self.bm25_indices):
                            if i < len(scores_for_indices): # Защита от ошибок несоответствия длины
                                bm25_scores[original_idx] = scores_for_indices[i]
                            else:
                                print(f"Предупреждение: Индекс {i} вне диапазона scores_for_indices ({len(scores_for_indices)}) при сопоставлении bm25_indices.")
                                
                    elif hasattr(self, 'bm25_indices'):
                        print(f"Предупреждение: Несоответствие размеров BM25 scores ({len(bm25_raw_scores)}) и bm25_indices ({len(self.bm25_indices)}). Оценки BM25 не будут применены.")
                    else:
                        print("Предупреждение: Отсутствуют индексы bm25_indices. Оценки BM25 не будут применены.")
                except Exception as e:
                    print(f"Ошибка при расчете BM25 для запроса '{query[:50]}...': {e}")
            else:
                print("Предупреждение: Модель BM25 недоступна.")

            # --- [DEBUG] Вывод кандидатов BM25 --- 
            print(f"--- [DEBUG] Топ-10 кандидатов BM25 для варианта запроса '{query[:50]}...' ---")
            top_bm25_indices_debug = np.argsort(bm25_scores)[::-1][:10] 
            for bm25_idx in top_bm25_indices_debug:
                score = bm25_scores[bm25_idx]
                if score > 0: # Показываем только с ненулевой оценкой
                    title = self.dataset.loc[bm25_idx, 'Заголовок статьи']
                    print(f"  - Индекс: {bm25_idx}, Оценка BM25: {score:.4f}, Заголовок: {title}")
            print("---")
            # --- [DEBUG] Конец вывода BM25 ---

            # --- Отбор кандидатов ---
            candidate_indices_unsorted = np.argsort(bm25_scores)
            candidate_indices = candidate_indices_unsorted[-self.CANDIDATES_K:][::-1]
            # Отбрасываем кандидатов с нулевой BM25 оценкой (если такие есть)
            non_zero_bm25_mask = bm25_scores[candidate_indices] > 0
            candidate_indices = candidate_indices[non_zero_bm25_mask]
            if len(candidate_indices) == 0:
                print(f"Предупреждение: Не найдено кандидатов с BM25 > 0 для варианта запроса: '{query[:50]}...'")
                all_scores.append(np.zeros(num_docs))
                all_candidate_data_variants.append(None) # Добавляем placeholder
                continue # Переходим к следующему варианту
                
            candidate_bm25_scores = bm25_scores[candidate_indices]

            # ===== Этап 2: Reranking (только для кандидатов) =====
            # ======================================

            cross_encoder_scores = None # Инициализируем для хранения оценок CrossEncoder
            combined_scores_candidates = None # Инициализируем комбинированные оценки

            # --- Переранжирование с CrossEncoder (если включено) ---
            # <<< ЗАКОММЕНТИРОВАНО, ЧТОБЫ ВЕРНУТЬСЯ К BERT (Bi-Encoder) >>>
            # if self.use_cross_encoder and self.cross_encoder:
            #     try:
            #         print(f"\n--- [DEBUG] Запуск CrossEncoder для {len(candidate_indices)} кандидатов ---")
            #         # Формируем пары (запрос, текст кандидата) для CrossEncoder
            #         cross_inp = [(text, self.dataset.loc[idx, 'combined_text']) for idx in candidate_indices]
            #         # Получаем оценки от CrossEncoder
            #         cross_encoder_scores = self.cross_encoder.predict(cross_inp, show_progress_bar=False)
            #        
            #         # --- [DEBUG] Вывод сырых оценок CrossEncoder ---
            #         # print("Сырые оценки CrossEncoder (Топ 10): ...") # Убираем отладку
            #         # --- [DEBUG] Конец вывода ---
            #       
            #         # Используем оценки CrossEncoder как основную меру релевантности ДО контекста
            #         combined_scores_candidates = cross_encoder_scores 
            #     except Exception as e:
            #         print(f"Ошибка при переранжировании CrossEncoder: {e}. Используется Bi-Encoder/BM25.")
            #         # Если CrossEncoder не сработал, откатываемся к Bi-Encoder/BM25
            #         # self.use_cross_encoder = False # Отключаем для этого запроса
            #         cross_encoder_scores = np.zeros(len(candidate_indices)) # Ставим нули, чтобы не мешать отладке

            # --- Переранжирование с Bi-Encoder (SentenceTransformer) + BM25 (если CrossEncoder не используется) ---
            if combined_scores_candidates is None: # Если CrossEncoder не использовался или не сработал
                 # --- BERT семантическое сходство (только для кандидатов) ---
                 bert_similarity_candidates = np.zeros(len(candidate_indices)) 
                 if self.use_bert and self.bert_embeddings is not None and query_embedding is not None: 
                     try: 
                         candidate_bert_embeddings = self.bert_embeddings[candidate_indices] 
                         bert_similarity = cosine_similarity( 
                             [query_embedding], 
                             candidate_bert_embeddings 
                         )[0] 
                         if bert_similarity.shape == (len(candidate_indices),): 
                             bert_similarity_candidates = bert_similarity 
                         else: 
                             print(f"Предупреждение: Неожиданная форма BERT similarity: {bert_similarity.shape}") 
                     except Exception as e: 
                         print(f"Ошибка при вычислении BERT сходства для кандидатов: {e}")
 
                 # --- Нормализация BM25 (только для кандидатов) ---
                 # Инициализируем переменную перед if/else на всякий случай
                 norm_bm25_scores_candidates = np.zeros_like(candidate_bm25_scores) 
                 min_bm25_cand = np.min(candidate_bm25_scores)
                 max_bm25_cand = np.max(candidate_bm25_scores)
                 if max_bm25_cand > min_bm25_cand:
                     norm_bm25_scores_candidates = (candidate_bm25_scores - min_bm25_cand) / (max_bm25_cand - min_bm25_cand)
                 else:
                     norm_bm25_scores_candidates = np.full_like(candidate_bm25_scores, 0.5 if max_bm25_cand > 0 else 0)

                 # --- Комбинированное сходство (только для кандидатов) ---
                 bert_weight = 0.5 # <<<--- Возвращаем к 0.5, чтобы дать больше веса бонусу за ключевое слово
                 if self.use_bert:
                     combined_scores_candidates = (1 - bert_weight) * norm_bm25_scores_candidates + bert_weight * bert_similarity_candidates
                 else:
                     combined_scores_candidates = norm_bm25_scores_candidates

            # --- [DEBUG] Вывод сырых оценок кандидатов ПЕРЕД контекстом ---
            print(f"--- [DEBUG] Топ-{min(10, len(candidate_indices))} кандидатов ПЕРЕД контекстом (Вариант: '{query[:30]}...') ---")
            # Сортируем индексы кандидатов по их 'сырой' комбинированной оценке
            sorted_candidate_indices_before_context = candidate_indices[np.argsort(combined_scores_candidates)[::-1]]
            sorted_combined_scores_before_context = np.sort(combined_scores_candidates)[::-1]
            # Берем BM25 и BERT/CE оценки для отсортированных кандидатов
            sorted_bm25_scores_before_context = bm25_scores[sorted_candidate_indices_before_context]
            if self.use_cross_encoder and cross_encoder_scores is not None:
                # Если есть CE, берем его оценки (они и есть combined_scores_candidates)
                sorted_ce_scores_before_context = sorted_combined_scores_before_context
                sorted_bert_scores_before_context = np.zeros_like(sorted_ce_scores_before_context) # BERT не используется напрямую
            elif self.use_bert and 'bert_similarity_candidates' in locals() and bert_similarity_candidates is not None:
                # Если есть BERT, берем его оценки
                # Нужен пересчет индексов, так как bert_similarity_candidates имеет порядок candidate_indices
                original_indices_map = {idx: i for i, idx in enumerate(candidate_indices)}
                # Проверка на случай, если sorted_candidate_indices_before_context пуст
                if len(sorted_candidate_indices_before_context) > 0:
                    bert_indices_to_fetch = [original_indices_map[idx] for idx in sorted_candidate_indices_before_context]
                    # Проверка валидности индексов
                    if all(i < len(bert_similarity_candidates) for i in bert_indices_to_fetch):
                       sorted_bert_scores_before_context = bert_similarity_candidates[bert_indices_to_fetch]
                    else:
                       print("Предупреждение: Невалидные индексы для bert_similarity_candidates.")
                       sorted_bert_scores_before_context = np.zeros_like(sorted_combined_scores_before_context)
                else:
                    sorted_bert_scores_before_context = np.zeros_like(sorted_combined_scores_before_context)

                sorted_ce_scores_before_context = np.zeros_like(sorted_bert_scores_before_context) # CE не используется
            else: # Если ни BERT ни CE не используются (только BM25)
                sorted_bert_scores_before_context = np.zeros_like(sorted_combined_scores_before_context)
                sorted_ce_scores_before_context = np.zeros_like(sorted_combined_scores_before_context)

            for i in range(min(10, len(sorted_candidate_indices_before_context))):
                idx = sorted_candidate_indices_before_context[i]
                raw_score = sorted_combined_scores_before_context[i]
                # Обеспечиваем наличие переменных перед использованием
                bm25_s = sorted_bm25_scores_before_context[i] if i < len(sorted_bm25_scores_before_context) else 0
                bert_s = sorted_bert_scores_before_context[i] if i < len(sorted_bert_scores_before_context) else 0
                ce_s = sorted_ce_scores_before_context[i] if i < len(sorted_ce_scores_before_context) else 0
                title = self.dataset.loc[idx, 'Заголовок статьи']
                print(f"  - Индекс: {idx}, Сырой Score: {raw_score:.4f} (BM25: {bm25_s:.4f}, BERT: {bert_s:.4f}, CE: {ce_s:.4f}), Заголовок: {title}")
            print("---")
            # --- [DEBUG] Конец вывода сырых оценок ---

            # --- Применение контекстных весов (только для кандидатов) ---
            # Применяется к combined_scores_candidates, полученным либо от CrossEncoder, либо от BiEncoder/BM25
            scores_with_context_candidates = self._apply_context_weights(
                combined_scores_candidates, # Оценки только кандидатов
                query_type,
                user_role,
                component,
                text,
                indices=candidate_indices # Передаем индексы кандидатов
            ) # Теперь применяем контекст ВСЕГДА, даже для CrossEncoder

            # Применение веса варианта запроса и отбор кандидатов
            final_scores_variant = np.zeros(num_docs) # Начинаем с нулей
            candidate_final_scores = scores_with_context_candidates * weight # Применяем вес варианта
            final_scores_variant[candidate_indices] = candidate_final_scores # Ставим оценки только для кандидатов
            
            all_scores.append(final_scores_variant)
            
            # Сохраняем промежуточные данные кандидатов для этого варианта (для отладки)
            variant_candidate_data = {
                'indices': candidate_indices.copy(),
                'bm25': candidate_bm25_scores.copy(),
                'bert': bert_similarity_candidates.copy() if not (self.use_cross_encoder and cross_encoder_scores is not None) else np.zeros(len(candidate_indices)), # Сохраняем BERT только если НЕ CrossEncoder
                'cross_encoder': cross_encoder_scores.copy() if (self.use_cross_encoder and cross_encoder_scores is not None) else np.zeros(len(candidate_indices)), # Сохраняем CrossEncoder если использовался
                'combined': combined_scores_candidates.copy(), # Это будет либо CrossEncoder score, либо BiEncoder+BM25
                'context': scores_with_context_candidates.copy(),
                'final_cand_score': candidate_final_scores.copy()
            }
            all_candidate_data_variants.append(variant_candidate_data)

        # Выбираем максимальное значение релевантности для каждого документа
        if all_scores:
            max_scores = np.max(all_scores, axis=0)
            # Находим, какой вариант дал максимальную оценку для каждого документа
            best_variant_indices = np.argmax(all_scores, axis=0)
            
            # Собираем промежуточные оценки для отладки (только для документов с ненулевой итоговой оценкой)
            final_debug_scores = { 
                'bm25': np.zeros(num_docs),
                'bert': np.zeros(num_docs),
                'cross_encoder': np.zeros(num_docs),
                'combined_initial': np.zeros(num_docs),
                'context_weighted': np.zeros(num_docs)
            }
            active_doc_indices = np.where(max_scores > 0)[0]
            for doc_idx in active_doc_indices:
                variant_idx = best_variant_indices[doc_idx]
                candidate_data = all_candidate_data_variants[variant_idx]
                if candidate_data is not None: # Проверка на случай пропуска варианта
                    try:
                        # Находим локальный индекс документа среди кандидатов этого варианта
                        local_idx = np.where(candidate_data['indices'] == doc_idx)[0][0]
                        # Заполняем debug оценки
                        final_debug_scores['bm25'][doc_idx] = candidate_data['bm25'][local_idx]
                        final_debug_scores['bert'][doc_idx] = candidate_data['bert'][local_idx]
                        final_debug_scores['cross_encoder'][doc_idx] = candidate_data['cross_encoder'][local_idx]
                        final_debug_scores['combined_initial'][doc_idx] = candidate_data['combined'][local_idx] # Это будет оценка CE если он использовался
                        # Если контекст не применялся для CE, то context_weighted будет равен combined_initial
                        final_debug_scores['context_weighted'][doc_idx] = candidate_data['context'][local_idx] 
                    except IndexError: # Если документ не найден среди кандидатов (не должно происходить, но для безопасности)
                        print(f"Предупреждение: Документ {doc_idx} не найден среди кандидатов варианта {variant_idx}, хотя имеет max_score > 0.")
        else:
            # Возвращаем нули если не было вариантов запроса или произошла ошибка
            max_scores = np.zeros(num_docs)
            final_debug_scores = {
                'bm25': np.zeros(num_docs),
                'bert': np.zeros(num_docs),
                'cross_encoder': np.zeros(num_docs),
                'combined_initial': np.zeros(num_docs),
                'context_weighted': np.zeros(num_docs)
            }
        
        # Возвращаем итоговые очки и промежуточные для отладки
        return max_scores, final_debug_scores

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
        text: str = None,
        indices: Optional[np.ndarray] = None
    ) -> np.ndarray:
        """
        Применение весовых коэффициентов на основе контекста запроса (МУЛЬТИПЛИКАТИВНО)
        
        
        similarity (np.ndarray): Исходная релевантность
        query_type (str): Тип запроса (error/instruction/info)
        user_role (Optional[str]): Роль пользователя
        component (Optional[str]): Компонент системы
        text (str, optional): Текст запроса для дополнительной обработки
        indices (Optional[np.ndarray], optional): Индексы документов, для которых применяются веса. 
                                                Если None, применяются ко всем.
            
        Returns:
            np.ndarray: Модифицированная релевантность с учетом контекста
        """
        # Если индексы не переданы, работаем со всеми документами
        if indices is None:
            indices_to_process = np.arange(len(self.dataset))
            weighted_similarity = similarity.copy()
        else:
            # Работаем только с переданными индексами
            indices_to_process = indices
            # similarity здесь уже содержит оценки только для кандидатов
            weighted_similarity = similarity.copy() 

        # --- Мультипликативные факторы для контекста ---
        type_boost_factor = 0.03 # Уменьшаем общие бонусы
        role_boost_factor = 0.04
        component_boost_factor = 0.03
        # -------------------------------------------

        # Применение весов (итерируемся по индексам из similarity/indices_to_process)
        for k, doc_idx in enumerate(indices_to_process):
            # Применение весов по типу запроса
            doc_type = self.document_categories.get(doc_idx)
            if doc_type == query_type:
                weighted_similarity[k] *= (1 + type_boost_factor)
            
            # Применение весов по роли пользователя
            if user_role:
                doc_role = self.document_roles.get(doc_idx)
                if doc_role == user_role:
                    weighted_similarity[k] *= (1 + role_boost_factor)
            
            # Применение весов по компоненту системы
            if component:
                doc_topic = self.document_topics.get(doc_idx)
                if doc_topic == component:
                    weighted_similarity[k] *= (1 + component_boost_factor)

        # Дополнительная обработка ключевых слов запроса (Бонус за заголовок)
        if text:
            text_lower = text.lower()
            # Получаем лемматизированные ключевые слова из запроса (без стоп-слов)
            try:
                query_tokens = word_tokenize(re.sub(r'[^\w\s]', ' ', text_lower))
                query_keywords = { # Используем set для быстрой проверки
                    self.text_processor.lemmatize(token) 
                    for token in query_tokens 
                    if token not in self.text_processor.stop_words and len(token) > 1
                }
            except Exception as e:
                print(f"Ошибка токенизации/лемматизации запроса для бонуса: {e}")
                query_keywords = set()
            
            # Если найдены ключевые слова, повышаем релевантность документов,
            # заголовок которых содержит эти слова
            if query_keywords:
                # --- Скорректированные и новые бонусы ---
                # Бонусы за "прайслист" (остаются уменьшенными)
                pricelist_lemma = self.text_processor.lemmatize("прайслист")
                title_boost_pricelist = 0.2
                body_boost_pricelist = 0.05

                # Бонусы за "обновление" (ЕЩЕ УВЕЛИЧЕНЫ)
                update_lemma = self.text_processor.lemmatize("обновление")
                update_synonyms_lemmas = {
                    update_lemma,
                    self.text_processor.lemmatize("изменение"),
                    self.text_processor.lemmatize("загрузка"), # Часто используется в контексте прайсов
                    self.text_processor.lemmatize("замена"),
                    self.text_processor.lemmatize("редактирование")
                }
                title_boost_update = 0.6  # Увеличено с 0.4
                body_boost_update = 0.25 # Увеличено с 0.15

                # !!! НОВЫЙ КОМБИНИРОВАННЫЙ БОНУС !!!
                combined_boost_title = 0.8 # Сильный бонус, если ОБА слова в ЗАГОЛОВКЕ
                combined_boost_body = 0.4  # Бонус, если ОБА слова в ТЕЛЕ (и не в заголовке)

                # Бонус за общие ключевые слова (остается маленьким)
                general_keyword_boost = 0.05


                # Снова итерируемся по индексам
                for k, doc_idx in enumerate(indices_to_process):
                    # Используем исходную similarity[k] для проверки > 0, чтобы избежать умножения нуля
                    # и проверяем валидность индекса k
                    if k >= len(similarity) or similarity[k] <= 0:
                        continue # Пропускаем, если нет оценки или она нулевая

                    title = self.dataset.iloc[doc_idx]['Заголовок статьи'].lower()
                    body_text = self.dataset.loc[doc_idx, 'combined_text'].lower()

                    # Лемматизируем заголовок один раз
                    try:
                        title_tokens = word_tokenize(re.sub(r'[^a-zA-Zа-яА-Я0-9\\s]', ' ', title, flags=re.UNICODE))
                        title_lemmas = {self.text_processor.lemmatize(token) for token in title_tokens}
                    except Exception as e:
                        print(f"Ошибка лемматизации заголовка {doc_idx} для бонуса: {e}")
                        title_lemmas = set()

                    # --- Проверка наличия ключевых лемм ---
                    has_pricelist_in_title = pricelist_lemma in title_lemmas
                    has_update_in_title = any(lemma in title_lemmas for lemma in update_synonyms_lemmas)

                    # Проверка в теле (простая, без полной лемматизации тела для скорости)
                    try:
                        has_pricelist_in_body = pricelist_lemma in body_text
                    except TypeError:
                        has_pricelist_in_body = False
                    try:
                        has_update_in_body = any(lemma in body_text for lemma in update_synonyms_lemmas)
                    except TypeError:
                        has_update_in_body = False

                    has_general_keywords_in_title = any(keyword in title_lemmas for keyword in query_keywords)

                    # --- Применение мультипликативных бонусов ---
                    current_boost = 1.0 # Начинаем с нейтрального множителя

                    # 1. Самый сильный бонус: ОБА слова в ЗАГОЛОВКЕ
                    if has_pricelist_in_title and has_update_in_title:
                        current_boost *= (1 + combined_boost_title)
                    # 2. Сильные бонусы: одно из ТОЧНЫХ слов в ЗАГОЛОВКЕ (если не было комбинации выше)
                    elif has_pricelist_in_title:
                         current_boost *= (1 + title_boost_pricelist)
                    elif has_update_in_title:
                         current_boost *= (1 + title_boost_update)

                    # 3. Средний бонус: ОБА слова в ТЕЛЕ (и не было комбинации или точных слов в заголовке)
                    elif not has_pricelist_in_title and not has_update_in_title and \
                         has_pricelist_in_body and has_update_in_body:
                         current_boost *= (1 + combined_boost_body)

                    # 4. Слабые бонусы: одно из ТОЧНЫХ слов в ТЕЛЕ (и не было его в заголовке, и не было комбинации в теле)
                    elif not has_pricelist_in_title and not (has_pricelist_in_body and has_update_in_body) and \
                         has_pricelist_in_body:
                         current_boost *= (1 + body_boost_pricelist)
                    elif not has_update_in_title and not (has_pricelist_in_body and has_update_in_body) and \
                         has_update_in_body:
                        current_boost *= (1 + body_boost_update)

                    # 5. Самый слабый бонус: ОБЩИЕ слова в ЗАГОЛОВКЕ (если не было никаких точных совпадений в заголовке/теле)
                    elif not has_pricelist_in_title and not has_update_in_title and \
                         not has_pricelist_in_body and not has_update_in_body and \
                         has_general_keywords_in_title:
                        current_boost *= (1 + general_keyword_boost)

                    # Применяем итоговый буст к оценке
                    weighted_similarity[k] *= current_boost

        # Убедимся, что оценки не превышают 1.0 (из-за возможных неточностей float)
        # np.clip(weighted_similarity, 0, 1.0, out=weighted_similarity) # <-- Закомментировано для отладки

        return weighted_similarity

    def get_recommendations(self, text: str, top_n: int = 5) -> pd.DataFrame:
        """
        Получение top_n наиболее релевантных документов
        
        
        text (str): Текст запроса
        top_n (int): Количество документов для вывода
            
        Returns:
            pd.DataFrame: Датафрейм с найденными документами, их итоговой релевантностью 
                          и промежуточными оценками для отладки.
        """
        # Вычисление релевантности и получение промежуточных оценок
        similarity, debug_scores = self.predict(text)
        
        # Получение индексов наиболее релевантных документов
        indices = np.argsort(similarity)[::-1][:top_n]
        
        # Формирование результата
        result = self.dataset.iloc[indices][['Заголовок статьи', 'Описание']].copy()
        result['релевантность'] = similarity[indices]
        
        # Добавление промежуточных оценок для отладки
        result['score_bm25'] = debug_scores['bm25'][indices]
        result['score_bert'] = debug_scores['bert'][indices]
        result['score_combined'] = debug_scores['combined_initial'][indices]
        result['score_context'] = debug_scores['context_weighted'][indices]

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
    
    def extract_relevant_fragments(self, text: str, top_n: int = 5, top_k_fragments: int = 10) -> Tuple[List[Dict[str, Any]], pd.DataFrame]: # <<< ИЗМЕНЕНО: возвращаемый тип
        """
        Извлечение наиболее релевантных фрагментов из статей для заданного запроса
        
        text (str): Текст запроса
        top_n (int): Количество статей для анализа
        top_k_fragments (int): Количество фрагментов для извлечения
        
        Returns:
            Tuple[List[Dict[str, Any]], pd.DataFrame]: 
                Список словарей с информацией о релевантных фрагментах и 
                DataFrame с рекомендациями, использованными для их поиска.
        """
        print(f"--- [DEBUG extract_relevant_fragments] Начало для запроса: '{text[:50]}...', top_n={top_n}, top_k_fragments={top_k_fragments}") # Отладка
        # Получаем наиболее релевантные статьи
        recommendations = self.get_recommendations(text, top_n=top_n)
        print(f"--- [DEBUG extract_relevant_fragments] Получено {len(recommendations)} рекомендаций.") # Отладка
        # print(recommendations.head()) # Можно раскомментировать для просмотра рекомендаций
        
        # Классифицируем запрос
        query_classification = self.text_processor.classify_query(text)
        
        # Извлекаем именованные сущности из запроса
        query_spacy_entities = self.text_processor.extract_entities_spacy(text)
        
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
                
                # Извлекаем именованные сущности из сегмента для сравнения с запросом
                segment_spacy_entities = self.text_processor.extract_entities_spacy(segment)
                
                # Считаем совпадения сущностей
                entity_matches = 0
                for q_ent_text, q_ent_type in query_spacy_entities:
                    for s_ent_text, s_ent_type in segment_spacy_entities:
                        if q_ent_type == s_ent_type and (
                            q_ent_text.lower() in s_ent_text.lower() or 
                            s_ent_text.lower() in q_ent_text.lower()
                        ):
                            entity_matches += 1
                
                # Бонус за совпадение сущностей
                entity_bonus = min(0.3, 0.1 * entity_matches)

                segment_relevance = 0.0 # Инициализируем релевантность сегмента
                if self.use_bert and query_embedding is not None:
                    # BERT-эмбединг для сегмента
                    try:
                        segment_embedding = self.bert_model.encode(segment)
                        bert_similarity = cosine_similarity([query_embedding], [segment_embedding])[0][0]

                        # Релевантность сегмента на основе BERT и бонуса за сущности
                        segment_relevance = 0.8 * bert_similarity + 0.2 * entity_bonus
                    except Exception as e:
                        print(f"Ошибка при обработке сегмента BERT: {e}")
                        # Если BERT не сработал, используем только бонус за сущности
                        segment_relevance = entity_bonus
                else:
                    # Если BERT не используется, релевантность = бонус за сущности
                    segment_relevance = entity_bonus

                # Применяем штраф за длину текста
                segment_relevance = segment_relevance * length_penalty

                # Учитываем релевантность статьи при оценке сегмента
                # article_relevance теперь основана на BM25 (+BERT), полученном из get_recommendations
                combined_relevance = 0.6 * segment_relevance + 0.4 * article_relevance
                
                # Проверяем присутствие ключевых слов запроса в сегменте
                segment_lower = segment.lower()
                
                # Дополнительная информация о сущностях
                entity_info = {
                    'organizations': [ent_text for ent_text, ent_type in segment_spacy_entities if ent_type == 'ORG'],
                    'persons': [ent_text for ent_text, ent_type in segment_spacy_entities if ent_type == 'PER'],
                    'locations': [ent_text for ent_text, ent_type in segment_spacy_entities if ent_type == 'LOC']
                }
                
                all_fragments.append({
                    'fragment': segment,
                    'relevance': combined_relevance,
                    'title': title,
                    'article_type': row['тип'],
                    'user_role': row['роль'],
                    'component': row['компонент'],
                    'entity_matches': entity_matches,
                    'entities': entity_info
                })
        
        # Сортируем фрагменты по релевантности
        all_fragments.sort(key=lambda x: x['relevance'], reverse=True)
        
        result_fragments = all_fragments[:top_k_fragments]
        print(f"--- [DEBUG extract_relevant_fragments] Возвращается {len(result_fragments)} фрагментов.") # Отладка
        # Возвращаем top_k наиболее релевантных фрагментов и DataFrame с рекомендациями
        return result_fragments, recommendations # <<< ИЗМЕНЕНО: возвращаем кортеж
    
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
        
        # Извлекаем именованные сущности из запроса
        spacy_entities = self.text_processor.extract_entities_spacy(text)
        
        # Формируем информацию о сущностях
        orgs = query_classification.get('organizations', [])
        persons = query_classification.get('persons', [])
        locations = query_classification.get('locations', [])
        
        # Формируем промпт
        prompt = f"""Пользователь задал вопрос, я тебе даю его вопрос(он может быть с орфографическими ошибками, неточностями и т.д.) и даю фрагменты из нашей базы знаний. тебе нужно соеденить все фрагменты в один ответ на вопрос пользователя, ответ должен ссылаться на источник ифнормации и можно немного выдумывать информацию, чтобы пользователь получил информацию, которая ему нужна
Вопрос пользователя: {text}
Тип запроса: {query_classification['query_type']}
Роль пользователя: {query_classification['user_role'] or 'Не определена'}
Компонент: {query_classification['component'] or 'Не определен'}
"""

        # Добавляем информацию о сущностях, если они есть
        if orgs or persons or locations:
            prompt += "\nВыявленные сущности в запросе:\n"
            
            if orgs:
                prompt += f"- Организации: {', '.join(orgs)}\n"
            if persons:
                prompt += f"- Персоны: {', '.join(persons)}\n"
            if locations:
                prompt += f"- Местоположения: {', '.join(locations)}\n"

        prompt += "\nРелевантные фрагменты из базы знаний:\n"
        
        # Добавляем фрагменты
        for i, fragment in enumerate(fragments, 1):
            prompt += f"\n--- Фрагмент {i} (из статьи '{fragment['title']}') ---\n{fragment['fragment']}\n"
            
            # Добавляем информацию о сущностях, найденных во фрагменте
            if 'entities' in fragment and any(fragment['entities'].values()):
                prompt += "Сущности в этом фрагменте: "
                
                entity_parts = []
                if fragment['entities'].get('organizations'):
                    entity_parts.append(f"Организации: {', '.join(fragment['entities']['organizations'])}")
                if fragment['entities'].get('persons'):
                    entity_parts.append(f"Персоны: {', '.join(fragment['entities']['persons'])}")
                if fragment['entities'].get('locations'):
                    entity_parts.append(f"Местоположения: {', '.join(fragment['entities']['locations'])}")
                
                prompt += "; ".join(entity_parts) + "\n"
        
        return prompt
    
    def _create_reasoning_prompt(self, query: str, query_classification: Dict[str, Any], recommendations: pd.DataFrame, fragments: List[Dict[str, Any]]) -> str:
        """
        Создание промпта для LLM для генерации объяснения выбора статей и фрагментов.
        
        Args:
            query (str): Текст запроса пользователя.
            query_classification (Dict[str, Any]): Результат классификации запроса.
            recommendations (pd.DataFrame): DataFrame с рекомендованными статьями (топ-N).
            fragments (List[Dict[str, Any]]): Список извлеченных релевантных фрагментов (топ-K).
            
        Returns:
            str: Промпт для LLM.
        """
        print(f"--- [DEBUG _create_reasoning_prompt] Начало создания промпта.") # Отладка
        prompt = f"""Объясни от первого лица, как ты пришел к ответу на следующий запрос пользователя. Опиши свой ход мыслей по шагам: 
1. Анализ запроса: кратко опиши, как ты понял запрос (тип, ключевые темы/сущности).
2. Поиск статей: какие статьи из базы знаний показались наиболее релевантными и почему (например, упомяни совпадение ключевых слов, тематики, контекста). Упомяни 1-3 самые важные статьи.
3. Выбор фрагментов: почему ты выбрал именно эти фрагменты из найденных статей для формирования ответа? Что в них было важного?

Запрос пользователя: "{query}"

Твой анализ запроса:
- Тип: {query_classification.get('query_type', 'не определен')}
- Роль пользователя: {query_classification.get('user_role', 'не определена')}
- Компонент/Тема: {query_classification.get('component', 'не определена')}
- Ключевые действия: {query_classification.get('actions', [])}
- Проблемы: {query_classification.get('problems', [])}
- Сущности (Организации): {query_classification.get('organizations', [])}
- Сущности (Персоны): {query_classification.get('persons', [])}

Найденные релевантные статьи (Топ-{len(recommendations)}):
"""
        # Добавляем информацию о статьях
        for i, (_, row) in enumerate(recommendations.iterrows()):
            prompt += f"- Статья {i+1}: \"{row['Заголовок статьи']}\" (Релевантность: {row['релевантность']:.3f}, Тип: {row['тип']}, Роль: {row['роль']}, Компонент: {row['компонент']})\n"
            # Можно добавить больше деталей о score_bm25, score_bert и т.д., если нужно
            
        prompt += f"\nВыбранные ключевые фрагменты (Топ-{len(fragments)}):\n"
        
        # Добавляем информацию о фрагментах
        for i, fragment_info in enumerate(fragments):
            prompt += f"- Фрагмент {i+1} из статьи \"{fragment_info['title']}\":\n"
            prompt += f"  \"{fragment_info['fragment'][:150]}...\"\n" # Показываем начало фрагмента
            prompt += f"  (Релевантность фрагмента: {fragment_info['relevance']:.3f}, Совпадений сущностей: {fragment_info.get('entity_matches', 0)})\n"
            
        prompt += "\nТеперь, опиши свой ход мыслей:"
        print(f"--- [DEBUG _create_reasoning_prompt] Промпт успешно создан (длина: {len(prompt)}).") # Отладка
        return prompt
    
    def generate_answer(self, text: str, top_n: int = 5, top_k_fragments: int = 7) -> Dict[str, Any]:
        """
        Генерация ответа на запрос пользователя с использованием гибридного подхода

        Args:
            text (str): Текст запроса пользователя
            top_n (int): Количество релевантных документов для поиска
            top_k_fragments (int): Количество фрагментов для анализа

        Returns:
            Dict[str, Any]: Словарь с ответом, фрагментами, источниками и объяснением
        """
        start_time = time.time()
        
        if not text.strip():
            return {
                "answer": "Пустой запрос.", 
                "fragments": [], 
                "sources": [],
                "reasoning": "Запрос не содержит текста.", # Добавляем причину для пустого запроса
                "llm_answer_raw": "",
                "recommendations_df_json": pd.DataFrame().to_json(orient="records", force_ascii=False),
                "execution_time": time.time() - start_time
            }

        print(f"\\nПолучен запрос: '{text}'")
        print(f"Параметры: top_n={top_n}, top_k_fragments={top_k_fragments}")

        try:
            # 1. Классификация запроса (чтобы передать в _create_reasoning_prompt)
            print("Анализ запроса...")
            query_classification = self.text_processor.classify_query(text)
            print(f"Результаты классификации: {query_classification}")
            
            # 2. Извлечение релевантных фрагментов и получение DataFrame с рекомендациями
            print(f"Извлечение релевантных фрагментов (top_n={top_n}, top_k_fragments={top_k_fragments})...")
            # Вызываем extract_relevant_fragments, он вернет и фрагменты, и DataFrame
            fragments, recommendations_df = self.extract_relevant_fragments(
                text, 
                top_n=top_n, 
                top_k_fragments=top_k_fragments
            )
            print(f"Найдено {len(fragments)} релевантных фрагментов.")
            # print(f"DataFrame рекомендаций (первые 5):\\n{recommendations_df.head().to_string()}") # Отладка

            # Добавляем обработку случая, когда фрагменты не найдены
            if not fragments:
                print("Релевантные фрагменты не найдены.")
                # Можно вернуть стандартный ответ или попробовать сгенерировать ответ без фрагментов
                return {
                    "answer": "К сожалению, не удалось найти точную информацию по вашему запросу в базе знаний.",
                    "fragments": [],
                    "sources": [],
                    "reasoning": "Не найдено релевантных фрагментов текста в статьях базы знаний, соответствующих запросу.",
                    "llm_answer_raw": "",
                    "recommendations_df_json": recommendations_df.to_json(orient="records", force_ascii=False),
                    "execution_time": time.time() - start_time
                }

            # 3. Генерация ответа с помощью LLM (если включено)
            llm_answer = "Генерация ответа LLM отключена."
            llm_answer_raw = "" # Сохраняем 'сырой' ответ LLM для отладки
            if self.use_llm and self.llm:
                print("Генерация ответа с помощью LLM...")
                prompt = self.create_prompt_for_llm(text, fragments)
                # print(f"--- LLM Prompt для ответа: ---\\n{prompt}\\n---") # Отладка
                
                # Убедимся, что llm - это pipeline
                if isinstance(self.llm, pipeline):
                    try:
                        # Устанавливаем параметры генерации
                        generation_args = {
                            "max_new_tokens": 350, # Увеличим немного лимит
                            "temperature": 0.7, # Можно немного повысить для разнообразия
                            "top_p": 0.9,
                            "do_sample": True,
                            "eos_token_id": self.llm.tokenizer.eos_token_id,
                            "pad_token_id": self.llm.tokenizer.pad_token_id if self.llm.tokenizer.pad_token_id else self.llm.tokenizer.eos_token_id # Используем eos если pad не задан
                        }
                        
                        outputs = self.llm(prompt, **generation_args)
                        generated_text = outputs[0]['generated_text']
                        
                        # Извлекаем только сгенерированный ответ (после промпта)
                        # Ищем конец промпта, чтобы отсечь его. Phi-3 обычно добавляет <|end|> или <|assistant|>
                        prompt_end_markers = ["<|end|>", "<|assistant|>"]
                        answer_start_index = -1
                        # Ищем последнее вхождение маркера конца промпта
                        for marker in prompt_end_markers:
                           idx = generated_text.rfind(marker)
                           if idx != -1:
                               answer_start_index = max(answer_start_index, idx + len(marker))

                        if answer_start_index != -1:
                             llm_answer_raw = generated_text[answer_start_index:].strip()
                        else:
                            # Если маркеры не найдены, пытаемся отрезать исходный промпт
                            if generated_text.startswith(prompt):
                                llm_answer_raw = generated_text[len(prompt):].strip()
                            else:
                                # Если и это не сработало, берем все как есть (менее надежно)
                                llm_answer_raw = generated_text.strip()
                                print("Предупреждение: Не удалось точно отделить ответ LLM от промпта.")

                        # Пост-обработка ответа (убираем возможные артефакты)
                        llm_answer = llm_answer_raw.replace("<|endoftext|>", "").replace("<|im_end|>", "").strip()
                        
                        print(f"Ответ LLM получен (сырой): {llm_answer_raw[:200]}...") # Показываем начало сырого ответа
                        print(f"Ответ LLM получен (обработанный): {llm_answer[:200]}...") # Показываем начало обработанного ответа

                    except Exception as e:
                        print(f"Ошибка при генерации ответа LLM: {e}")
                        # traceback.print_exc() # Для детальной отладки
                        llm_answer = "Произошла ошибка при генерации ответа."
                        llm_answer_raw = f"Error: {e}"
                else:
                    print("Ошибка: self.llm не является объектом pipeline.")
                    llm_answer = "Ошибка конфигурации LLM."
                    llm_answer_raw = "LLM is not a Hugging Face pipeline object."
            else:
                 # Если LLM отключен, формируем ответ из лучших фрагментов
                 print("LLM отключен. Формируем ответ из лучших фрагментов.")
                 # Сортируем фрагменты по убыванию score_final, если он есть, иначе по score_cross_encoder
                 sort_key = 'score_final' if 'score_final' in fragments[0] else 'score_cross_encoder'
                 fragments.sort(key=lambda x: x.get(sort_key, 0), reverse=True)
                 # Берем текст первого (лучшего) фрагмента
                 llm_answer = fragments[0]['text']
                 llm_answer_raw = "LLM disabled. Used best fragment."


            # 4. Генерация объяснения ("размышления") с помощью LLM (если включено)
            reasoning_text = "Генерация объяснения отключена или произошла ошибка."
            if self.use_llm and self.llm and isinstance(self.llm, pipeline):
                print("Генерация объяснения выбора (reasoning)...")
                reasoning_prompt = self._create_reasoning_prompt(text, query_classification, recommendations_df, fragments)
                # print(f"--- LLM Prompt для объяснения: ---\\n{reasoning_prompt}\\n---") # Отладка
                try:
                    # Используем немного другие параметры для краткости
                    reasoning_args = {
                        "max_new_tokens": 150, # Короче ответ для объяснения
                        "temperature": 0.5, # Менее креативный
                        "top_p": 0.9,
                        "do_sample": True,
                        "eos_token_id": self.llm.tokenizer.eos_token_id,
                        "pad_token_id": self.llm.tokenizer.pad_token_id if self.llm.tokenizer.pad_token_id else self.llm.tokenizer.eos_token_id
                    }
                    
                    reasoning_outputs = self.llm(reasoning_prompt, **reasoning_args)
                    generated_reasoning = reasoning_outputs[0]['generated_text']

                    # Извлекаем только сгенерированное объяснение
                    prompt_end_markers = ["<|end|>", "<|assistant|>"]
                    reasoning_start_index = -1
                    for marker in prompt_end_markers:
                       idx = generated_reasoning.rfind(marker)
                       if idx != -1:
                           reasoning_start_index = max(reasoning_start_index, idx + len(marker))
                    
                    if reasoning_start_index != -1:
                         reasoning_text_raw = generated_reasoning[reasoning_start_index:].strip()
                    else:
                        if generated_reasoning.startswith(reasoning_prompt):
                            reasoning_text_raw = generated_reasoning[len(reasoning_prompt):].strip()
                        else:
                            reasoning_text_raw = generated_reasoning.strip()
                            print("Предупреждение: Не удалось точно отделить объяснение LLM от промпта.")

                    # Пост-обработка
                    reasoning_text = reasoning_text_raw.replace("<|endoftext|>", "").replace("<|im_end|>", "").strip()
                    print(f"Объяснение LLM получено: {reasoning_text[:200]}...")

                except Exception as e:
                    print(f"Ошибка при генерации объяснения LLM: {e}")
                    # traceback.print_exc() # Для детальной отладки
                    reasoning_text = f"Произошла ошибка при генерации объяснения: {e}"
            elif not (self.use_llm and self.llm and isinstance(self.llm, pipeline)):
                 reasoning_text = "Генерация объяснения невозможна: LLM отключена или не является pipeline."
                 if not fragments: # Если фрагментов нет, даем другую причину
                      reasoning_text = "Не найдено релевантных фрагментов текста в статьях базы знаний, соответствующих запросу."
                 elif fragments: # Если фрагменты есть, но LLM нет
                      reasoning_text = "Объяснение не сгенерировано, так как LLM отключена. Ответ сформирован на основе наиболее релевантного фрагмента."


            # 5. Формирование источников
            print("Формирование источников...")
            source_ids = set(frag['doc_id'] for frag in fragments)
            sources = self.dataset.loc[list(source_ids), ['id', 'Заголовок статьи', 'Ссылка на статью']].rename(
                 columns={'Заголовок статьи': 'title', 'Ссылка на статью': 'url', 'id': 'doc_id'}
            ).to_dict('records')
            print(f"Сформировано {len(sources)} источников.")

            # 6. Формирование итогового ответа
            end_time = time.time()
            result = {
                "answer": llm_answer,
                "fragments": fragments, # Оставляем фрагменты для возможного использования на фронтенде
                "sources": sources,
                "reasoning": reasoning_text, # Добавляем сгенерированное объяснение
                "llm_answer_raw": llm_answer_raw, # Добавляем сырой ответ для отладки
                "recommendations_df_json": recommendations_df.to_json(orient="records", force_ascii=False), # Добавляем DF для анализа
                "execution_time": end_time - start_time
            }
            print(f"Генерация ответа завершена за {result['execution_time']:.2f} сек.")
            return result

        except Exception as e:
            # Логируем ошибку
            print(f"Критическая ошибка в generate_answer: {e}")
            # import traceback # Раскомментируйте для полного стека вызовов
            # traceback.print_exc()
            
            # Возвращаем сообщение об ошибке
            return {
                "answer": f"Произошла внутренняя ошибка при обработке запроса: {e}",
                "fragments": [],
                "sources": [],
                "reasoning": f"Ошибка обработки: {e}", # Указываем ошибку в причине
                "llm_answer_raw": "",
                "recommendations_df_json": pd.DataFrame().to_json(orient="records", force_ascii=False),
                "execution_time": time.time() - start_time
            }

    def save_model(self, model_path: str) -> None:
        """
        Сохранение модели в файл
        
        
        model_path (str): Путь для сохранения модели
        """
        # Временно отключаем BERT модель и LLM для сериализации
        bert_model_tmp = None
        llm_tmp = None
        cross_encoder_tmp = None
        
        if self.use_bert:
            bert_model_tmp = self.bert_model
            self.bert_model = None
        
        if self.use_llm:
            llm_tmp = self.llm
            self.llm = None
        
        if self.use_cross_encoder:
            cross_encoder_tmp = self.cross_encoder
            self.cross_encoder = None
        
        # Сохранение модели
        with open(model_path, 'wb') as f:
            pickle.dump(self, f)
        
        # Восстановление BERT модели и LLM
        if bert_model_tmp is not None:
            self.bert_model = bert_model_tmp
            
        if llm_tmp is not None:
            self.llm = llm_tmp
        
        if cross_encoder_tmp is not None:
            self.cross_encoder = cross_encoder_tmp
        
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
                model.bert_model = SentenceTransformer('ai-forever/sbert_large_nlu_ru')
            except Exception as e:
                print(f"Не удалось загрузить BERT модель: {e}")
                model.use_bert = False
        
        # Если нужно, восстанавливаем LLM
        # Убираем проверку флага из файла, пытаемся загрузить всегда, 
        # если LLM в принципе предполагается использовать (это определяется логикой приложения).
        # Флаг use_llm будет выставлен в False только если загрузка не удастся.
        # if model.use_llm:  <--- УДАЛЯЕМ ЭТУ ПРОВЕРКУ
        try:
            # Сначала убедимся, что атрибут llm существует (на всякий случай)
            if not hasattr(model, 'llm'):
                 model.llm = None
            
            # Пытаемся загрузить pipeline
            model.llm = pipeline("text-generation", model="microsoft/Phi-3-mini-4k-instruct", trust_remote_code=True)
            print("LLM модель успешно загружена (принудительная попытка в load_model)")
            # Устанавливаем флаг в True, так как загрузка удалась
            model.use_llm = True 
        except Exception as e:
            print(f"!!!!!!!! НЕ УДАЛОСЬ ЗАГРУЗИТЬ LLM МОДЕЛЬ в load_model !!!!!!!!")
            print(f"Ошибка: {e}")
            import traceback
            traceback.print_exc() # Печатаем полный traceback для диагностики
            model.use_llm = False # Устанавливаем False, так как загрузка не удалась
            model.llm = None # Убедимся, что llm это None
        
        # Если нужно, восстанавливаем CrossEncoder модель
        if model.use_cross_encoder:
            try:
                model.cross_encoder = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
                print("CrossEncoder модель успешно загружена.")
            except Exception as e:
                print(f"Не удалось загрузить CrossEncoder модель: {e}. Переранжирование с CrossEncoder отключено.")
                model.use_cross_encoder = False
                
        return model


if __name__ == "__main__":
    retrain = False
    query = """  Какие шаги необходимо выполнить для создания коммерческого предложения через портал поставщиков? """
    model_path = "model.pkl"
    dataset_path = "docs/dataset.parquet"
    top_n = 10
    
    try:
        start_time = time.time()
        
        # Проверка необходимости переобучения модели
        if retrain or not os.path.exists(model_path):
            print(f"Создание и обучение новой модели...")
            # Создание модели
            model = Model(dataset_path, use_bert=True, use_llm=True, use_cross_encoder=True)
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
        
        # --- УДАЛЕНО: Не нужно пересоздавать модель после загрузки --- 
        # Загруженная модель уже содержит обученные компоненты (включая BM25)
        # Если нужно изменить флаг для теста, можно сделать это напрямую:
        # model.use_cross_encoder = True # или False
        # И при необходимости дозагрузить саму модель CrossEncoder:
        # if model.use_cross_encoder and model.cross_encoder is None:
        #    try:
        #        model.cross_encoder = CrossEncoder(...) 
        #    except: ... 
 
        # Выполнение поиска 
        start_time = time.time()
        print(f"\nЗапрос: '{query}'")
        print(f"Режим переранжирования: {'CrossEncoder' if model.use_cross_encoder else 'BiEncoder + BM25'}")
        
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
        # Расширяем список столбцов для zip
        cols_to_zip = [
            recommendations['Заголовок статьи'], 
            recommendations['Описание'], 
            recommendations['релевантность'],
            recommendations['тип'],
            recommendations['роль'],
            recommendations['компонент'],
            recommendations['score_bm25'],
            recommendations['score_bert'],
            recommendations['score_combined'],
            recommendations['score_context']
        ]
        # Расширяем переменные в цикле
        for i, (title, desc, rel, q_type, role, comp, bm25, bert, combined, context) in enumerate(zip(*cols_to_zip)):
            # Выводим основную информацию и итоговую релевантность
            print(f"{i+1}. {title} (релевантность: {rel:.4f})")
            # Выводим промежуточные оценки
            print(f"   Scores: BM25={bm25:.4f}, BERT={bert:.4f}, Combined={combined:.4f}, Context={context:.4f}")
            # Выводим контекст
            print(f"   Контекст: Тип={q_type}, Роль={role}, Компонент={comp}")
            if not pd.isna(desc):
                print(f"   Описание: {desc[:100]}..." if len(str(desc)) > 100 else f"   Описание: {desc}")
            print()
        
        print(f"Время выполнения: {time.time() - start_time:.2f} с")
    
    except Exception as e:
        print(f"Произошла ошибка: {e}")
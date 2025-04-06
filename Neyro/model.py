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
        # if query_classification.get('needs_operator', False):
        #     return {
        #         "answer": "Для решения вашей проблемы требуется помощь оператора. Мы переводим вас на специалиста технической поддержки.",
        #         "fragments": [],
        #         "sources": [],
        #         "needs_operator": True
        #     }
        
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
        if model.use_llm:
            try:
                model.llm = pipeline("text-generation", model="microsoft/Phi-3-mini-4k-instruct", trust_remote_code=True)
                print("LLM модель успешно загружена")
            except Exception as e:
                print(f"Не удалось загрузить LLM модель: {e}")
                model.use_llm = False
        
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
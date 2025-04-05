"""
Модуль для обработки текста и анализа запросов пользователей Портала поставщиков
"""

import pandas as pd
import nltk
import re
from difflib import get_close_matches
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer
from nltk.util import ngrams
import pymorphy2
from collections import Counter
import numpy as np

# Скачиваем необходимые ресурсы NLTK
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

class TextProcessor:
    """
    Класс для предварительной обработки текста запросов пользователей Портала поставщиков
    """
    def __init__(self):
        # Инициализация стеммера для русского языка
        self.stemmer = SnowballStemmer('russian')
        
        # Получение списка русских стоп-слов
        try:
            self.stop_words = set(stopwords.words('russian'))
            # Исключаем важные негативные частицы и слова, определяющие контекст
            self.stop_words -= {'не', 'нет', 'без', 'ошибка', 'проблема'}
        except LookupError:
            print("Не удалось загрузить стоп-слова NLTK")
            self.stop_words = set()
            
        # Инициализация морфологического анализатора
        try:
            self.morph = pymorphy2.MorphAnalyzer()
        except:
            print("Не удалось инициализировать PyMorphy2")
            self.morph = None
            
        # Словари для хранения словаря и n-грамм
        self.vocabulary = set()
        self.ngram_vocabulary = {}
        
        # Словари для обработки аббревиатур
        self.abbreviations = {}  # аббревиатура -> полная форма
        self.full_forms = {}     # полная форма -> аббревиатура
        
        # Определение предметных областей и ключевых сущностей Портала поставщиков
        self.domain_entities = {
            'документы': {'упд', 'универсальный передаточный документ', 'накладная', 'счет', 'счет-фактура', 
                         'акт', 'договор', 'контракт', 'оферта', 'заявка'},
            'роли': {'заказчик', 'поставщик', 'исполнитель', 'закупщик', 'покупатель', 'продавец', 'получатель', 'отправитель'},
            'действия': {'разблокировать', 'заблокировать', 'зарегистрировать', 'подписать', 'отправить', 'получить', 
                         'создать', 'удалить', 'изменить', 'отклонить', 'согласовать'},
            'проблемы': {'ошибка', 'проблема', 'не работает', 'не удается', 'не получается', 'отсутствует', 
                         'недоступен', 'отказ', 'сбой', 'неисправность'},
            'компоненты': {'портал', 'сайт', 'система', 'личный кабинет', 'реестр', 'каталог', 'профиль'}
        }
        
        # Общий набор сущностей для быстрого поиска
        self.all_entities = set()
        for entity_set in self.domain_entities.values():
            self.all_entities.update(entity_set)

    def build_vocabulary(self, texts):
        """
        Создание словаря слов и n-грамм для предобработки текста
        
        Args:
            texts (List[str]): Список текстов для анализа
        """
        all_words = []
        bigrams_list = []
        trigrams_list = []
        
        for text in texts:
            if pd.isna(text):
                continue
                
            # Предварительная нормализация текста
            text = str(text).lower()
            
            # Поиск и извлечение аббревиатур
            self._extract_abbreviations(text)
            
            # Очистка текста от пунктуации
            clean_text = re.sub(r'[^\w\s]', ' ', text)
            
            # Токенизация текста
            words = word_tokenize(clean_text)
            all_words.extend(words)
            
            # Создаем n-граммы для улучшения качества поиска
            if len(words) > 1:
                bigrams_list.extend([' '.join(bg) for bg in list(ngrams(words, 2))])
            if len(words) > 2:
                trigrams_list.extend([' '.join(tg) for tg in list(ngrams(words, 3))])
        
        # Сохраняем уникальные слова в словарь
        self.vocabulary = set(all_words)
        
        # Подсчитываем частоту n-грамм
        bigram_counter = Counter(bigrams_list)
        trigram_counter = Counter(trigrams_list)
        
        # Сохраняем только часто встречающиеся n-граммы
        self.ngram_vocabulary = {
            'bigrams': {bg for bg, count in bigram_counter.items() if count >= 2},
            'trigrams': {tg for tg, count in trigram_counter.items() if count >= 2}
        }
        
        # Добавляем предметные сущности и термины в словарь n-грамм
        for entity in self.all_entities:
            words = entity.split()
            if len(words) == 2:
                self.ngram_vocabulary['bigrams'].add(entity)
            elif len(words) == 3:
                self.ngram_vocabulary['trigrams'].add(entity)

    def _extract_abbreviations(self, text):
        """
        Извлечение аббревиатур и их полных форм из текста
        
        Args:
            text (str): Текст для анализа
        """
        # Паттерн 1: "полная форма (АББР)"
        pattern1 = r'([а-яА-Яa-zA-Z\s]+)\s+\(([А-ЯA-Z]{2,})\)'
        matches1 = re.findall(pattern1, text)
        for full_form, abbr in matches1:
            full_form = full_form.strip().lower()
            abbr = abbr.strip().upper()
            self.abbreviations[abbr] = full_form
            self.full_forms[full_form] = abbr
            
        # Паттерн 2: "АББР (полная форма)"
        pattern2 = r'([А-ЯA-Z]{2,})\s+\(([а-яА-Яa-zA-Z\s]+)\)'
        matches2 = re.findall(pattern2, text)
        for abbr, full_form in matches2:
            full_form = full_form.strip().lower()
            abbr = abbr.strip().upper()
            self.abbreviations[abbr] = full_form
            self.full_forms[full_form] = abbr
        
        # Поиск потенциальных аббревиатур в тексте
        sentences = sent_tokenize(text)
        for sentence in sentences:
            words = word_tokenize(sentence)
            
            # Ищем последовательности из заглавных букв
            for i in range(len(words) - 2):
                if all(word and word[0].isupper() for word in words[i:i+3] if word):
                    # Формируем потенциальную аббревиатуру
                    potential_abbr = ''.join(word[0].upper() for word in words[i:i+3] if word)
                    if len(potential_abbr) >= 2 and potential_abbr.isupper():
                        full_form = ' '.join(words[i:i+3]).lower()
                        # Проверяем, есть ли аббревиатура в тексте
                        if potential_abbr in sentence.upper():
                            self.abbreviations[potential_abbr] = full_form
                            self.full_forms[full_form] = potential_abbr

    def correct_spelling(self, word, cutoff=0.8):
        """
        Исправление опечаток с использованием словаря
        
        Args:
            word (str): Слово для проверки
            cutoff (float): Порог сходства (от 0 до 1)
            
        Returns:
            str: Исправленное слово или исходное, если подходящего варианта не найдено
        """
        if not self.vocabulary or word in self.vocabulary:
            return word

        # Поиск ближайших по написанию слов
        matches = get_close_matches(word, self.vocabulary, n=1, cutoff=cutoff)
        return matches[0] if matches else word

    def lemmatize(self, token):
        """
        Лемматизация слова (приведение к нормальной форме)
        
        Args:
            token (str): Слово для лемматизации
            
        Returns:
            str: Лемматизированное слово
        """
        if self.morph:
            # Использование морфологического анализатора
            return self.morph.parse(token)[0].normal_form
        else:
            # Если морфологический анализатор недоступен, используем стемминг
            return self.stemmer.stem(token)

    def extract_entities(self, text):
        """
        Извлечение предметных сущностей из текста
        
        Args:
            text (str): Текст для анализа
            
        Returns:
            dict: Словарь с найденными сущностями по категориям
        """
        text_lower = text.lower()
        found_entities = {category: set() for category in self.domain_entities}
        
        # Поиск сущностей из каждой категории
        for category, entities in self.domain_entities.items():
            for entity in entities:
                if entity in text_lower:
                    found_entities[category].add(entity)
        
        # Поиск аббревиатур
        for abbr, full_form in self.abbreviations.items():
            if abbr.lower() in text_lower:
                # Определяем категорию по полной форме
                for category, entities in self.domain_entities.items():
                    if any(term in full_form for term in entities):
                        found_entities[category].add(abbr.lower())
                        found_entities[category].add(full_form)
        
        return found_entities

    def extract_ngrams(self, tokens):
        """
        Извлечение n-грамм из токенов текста
        
        Args:
            tokens (List[str]): Список токенов
            
        Returns:
            List[str]: Список найденных n-грамм
        """
        ngrams_found = []
        
        if len(tokens) < 2:
            return ngrams_found
            
        # Проверка биграмм
        bigrams_list = [' '.join(bg) for bg in list(ngrams(tokens, 2))]
        for bg in bigrams_list:
            if bg in self.ngram_vocabulary.get('bigrams', set()):
                ngrams_found.append(bg)
                
        # Проверка триграмм
        if len(tokens) >= 3:
            trigrams_list = [' '.join(tg) for tg in list(ngrams(tokens, 3))]
            for tg in trigrams_list:
                if tg in self.ngram_vocabulary.get('trigrams', set()):
                    ngrams_found.append(tg)
                    
        return ngrams_found

    def expand_query(self, text):
        """
        Расширение запроса с добавлением аббревиатур и полных форм
        
        Args:
            text (str): Исходный запрос
            
        Returns:
            List[str]: Список вариантов запроса
        """
        expanded_terms = []
        
        # Обработка аббревиатур и их полных форм
        for abbr, full_form in self.abbreviations.items():
            if abbr.lower() in text.lower():
                expanded_terms.append(full_form)
            elif full_form in text.lower():
                expanded_terms.append(abbr.lower())
        
        # Поиск терминов из предметной области
        for entity_list in self.domain_entities.values():
            for entity in entity_list:
                if entity in text.lower():
                    # Добавляем синонимы и связанные термины
                    for category, terms in self.domain_entities.items():
                        for term in terms:
                            if entity in term and entity != term:
                                expanded_terms.append(term)
        
        return expanded_terms

    def preprocess_text(self, text):
        """
        Комплексная предобработка текста для поиска
        
        Args:
            text (str): Исходный текст
            
        Returns:
            str: Обработанный текст, готовый для векторизации
        """
        if pd.isna(text):
            return ""
            
        # Извлечение предметных сущностей
        found_entities = self.extract_entities(str(text))
        
        # Расширение запроса дополнительными терминами
        expanded_terms = self.expand_query(str(text))
        
        # Нормализация текста
        text = str(text).lower()
        text = re.sub(r'[^\w\s]', ' ', text)
        
        # Токенизация
        try:
            tokens = word_tokenize(text)
        except:
            print("Ошибка токенизации")
            return ""

        # Исправление опечаток
        if self.vocabulary:
            tokens = [self.correct_spelling(token) for token in tokens if token.isalpha()]
        else:
            tokens = [token for token in tokens if token.isalpha()]

        # Извлечение n-грамм
        ngrams_found = self.extract_ngrams(tokens)
        
        # Удаление стоп-слов и лемматизация
        processed_tokens = []
        for token in tokens:
            if token not in self.stop_words:
                processed_tokens.append(self.lemmatize(token))
                
        # Формирование результата
        result = ' '.join(processed_tokens)
        
        # Добавление n-грамм и предметных сущностей
        if ngrams_found:
            result += ' ' + ' '.join([ng.replace(' ', '_') for ng in ngrams_found])
        
        # Добавление найденных сущностей
        for category, entities in found_entities.items():
            if entities:
                for entity in entities:
                    result += ' ' + entity.replace(' ', '_')
        
        # Добавление расширенных терминов
        if expanded_terms:
            result += ' ' + ' '.join([term.replace(' ', '_') for term in expanded_terms])
            
        return result
        
    def classify_query(self, text):
        """
        Классификация запроса пользователя
        
        Args:
            text (str): Текст запроса
            
        Returns:
            dict: Словарь с классификацией запроса
        """
        # Классификация по типу запроса
        text_lower = text.lower()
        
        # Извлекаем сущности
        entities = self.extract_entities(text)
        
        # Определяем тип запроса (проблема/инструкция/справка)
        query_type = 'info'  # По умолчанию информационный запрос
        if any(term in text_lower for term in ['ошибка', 'проблема', 'не работает', 'не удается']):
            query_type = 'error'
        elif any(term in text_lower for term in ['как', 'инструкция', 'подробно', 'объясните']):
            query_type = 'instruction'
            
        # Определяем роль пользователя
        user_role = None
        for role in entities.get('роли', []):
            user_role = role
            break
            
        # Определяем компонент системы
        component = None
        for doc in entities.get('документы', []):
            component = doc
            break
        
        if not component:
            for comp in entities.get('компоненты', []):
                component = comp
                break
                
        # Формируем результат классификации
        classification = {
            'query_type': query_type,
            'user_role': user_role,
            'component': component,
            'actions': list(entities.get('действия', [])),
            'problems': list(entities.get('проблемы', []))
        }
        
        return classification

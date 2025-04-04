"""
Модуль для утилитных функций
"""

import pandas as pd  # Для работы с табличными данными
import nltk  # Библиотека для обработки естественного языка
import re  # Для работы с регулярными выражениями
from difflib import get_close_matches  # Для нечеткого поиска слов
from nltk.tokenize import word_tokenize, sent_tokenize  # Для разбиения текста на токены и предложения
from nltk.corpus import stopwords  # Для получения списка стоп-слов
from nltk.stem import SnowballStemmer  # Для стемминга слов
from nltk.util import ngrams  # Для генерации n-грамм
import string  # Для работы со строками
import pymorphy2  # Для морфологического анализа
from collections import Counter  # Для подсчета частот

# Скачиваем необходимые ресурсы NLTK при необходимости
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    print("Загружаем 'stopwords' для NLTK...")
    nltk.download('stopwords')


try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    print("Загружаем 'punkt' для NLTK...")
    nltk.download('punkt')


try:
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    print("Загружаем 'punkt_tab' для NLTK...")
    nltk.download('punkt_tab')


class TextProcessor:
    """
    Класс для предварительной обработки текста с расширенными возможностями
    """
    def __init__(self):
        self.stemmer = SnowballStemmer('russian')  # Инициализация стеммера для русского языка
        try:
            self.stop_words = set(stopwords.words('russian'))  # Получение списка русских стоп-слов
            # Исключаем из стоп-слов негативные частицы и важные слова для определения контекста
            self.stop_words -= {'не', 'нет', 'никак', 'ошибка', 'проблема'}
        except LookupError:
            print("Критическая ошибка: не удалось загрузить стоп-слова NLTK.")
            self.stop_words = set()
            
        self.vocabulary = set()  # Словарь для исправления опечаток
        self.ngram_vocabulary = {}  # Словарь для хранения n-грамм
        
        # Инициализация морфологического анализатора
        try:
            self.morph = pymorphy2.MorphAnalyzer()
        except:
            print("Не удалось инициализировать PyMorphy2. Будет использован только стемминг.")
            self.morph = None
            
        # Словарь технических терминов, которые нужно сохранять целиком
        self.tech_terms = {
            'контрактная система', 'счет', 'ошибка', 'проблема', 'не удается', 
            'не работает', 'баг', 'интерфейс', 'документация', 'установка', 
            'настройка', 'руководство', 'инструкция'
        }
        
        # Автоматически найденные аббревиатуры и их полные формы
        self.abbreviations = {}  # Словарь для хранения пар аббревиатура -> полная форма
        self.full_forms = {}     # Словарь для хранения пар полная форма -> аббревиатура

    def build_vocabulary(self, texts):
        """
        Создание словаря слов и n-грамм для предобработки текста
        """
        all_words = []
        bigrams_list = []
        trigrams_list = []
        
        # Для автоматического обнаружения аббревиатур
        potential_abbr_patterns = []
        
        for text in texts:
            if pd.isna(text):
                continue
                
            # Предварительная нормализация текста
            text = str(text).lower()
            
            # Поиск аббревиатур и их полных форм
            self._extract_abbreviations(text)
            
            text = re.sub(r'[^\w\s]', ' ', text)  # Удаляем знаки пунктуации
            
            # Токенизация для отдельных слов
            words = word_tokenize(text)
            all_words.extend(words)
            
            # Создаем биграммы и триграммы
            if len(words) > 1:
                bigrams_list.extend([' '.join(bg) for bg in list(ngrams(words, 2))])
            if len(words) > 2:
                trigrams_list.extend([' '.join(tg) for tg in list(ngrams(words, 3))])
        
        # Формируем словарь уникальных слов
        self.vocabulary = set(all_words)
        
        # Формируем словарь часто встречающихся n-грамм (биграммы и триграммы)
        bigram_counter = Counter(bigrams_list)
        trigram_counter = Counter(trigrams_list)
        
        # Сохраняем только n-граммы, которые встречаются хотя бы 2 раза
        self.ngram_vocabulary = {
            'bigrams': {bg for bg, count in bigram_counter.items() if count >= 2},
            'trigrams': {tg for tg, count in trigram_counter.items() if count >= 2}
        }
        
        # Добавляем технические термины в словарь n-грамм
        for term in self.tech_terms:
            words = term.split()
            if len(words) == 2:
                self.ngram_vocabulary['bigrams'].add(term)
            elif len(words) == 3:
                self.ngram_vocabulary['trigrams'].add(term)
        
        # Добавляем найденные полные формы аббревиатур в словарь n-грамм
        for full_form in self.full_forms:
            words = full_form.split()
            if len(words) == 2:
                self.ngram_vocabulary['bigrams'].add(full_form)
            elif len(words) == 3:
                self.ngram_vocabulary['trigrams'].add(full_form)
            elif len(words) > 3:
                # Добавляем многословные выражения как отдельные термины
                self.tech_terms.add(full_form)

    def _extract_abbreviations(self, text):
        """
        Извлекает аббревиатуры и их полные формы из текста
        """
        # Паттерны для поиска аббревиатур
        # 1. Аббревиатура в скобках: "универсальный передаточный документ (УПД)"
        pattern1 = r'([а-яА-Яa-zA-Z\s]+)\s+\(([А-ЯA-Z]{2,})\)'
        matches1 = re.findall(pattern1, text)
        for full_form, abbr in matches1:
            full_form = full_form.strip().lower()
            abbr = abbr.strip().upper()
            self.abbreviations[abbr] = full_form
            self.full_forms[full_form] = abbr
            
        # 2. Полная форма в скобках: "УПД (универсальный передаточный документ)"
        pattern2 = r'([А-ЯA-Z]{2,})\s+\(([а-яА-Яa-zA-Z\s]+)\)'
        matches2 = re.findall(pattern2, text)
        for abbr, full_form in matches2:
            full_form = full_form.strip().lower()
            abbr = abbr.strip().upper()
            self.abbreviations[abbr] = full_form
            self.full_forms[full_form] = abbr
        
        # 3. Автоматическое формирование аббревиатур из последовательностей слов
        # Разбиваем текст на предложения
        sentences = sent_tokenize(text)
        for sentence in sentences:
            words = word_tokenize(sentence)
            for i in range(len(words) - 2):  # Минимум 3 слова для аббревиатуры
                # Проверяем, что слова начинаются с заглавной буквы
                if all(word and word[0].isupper() for word in words[i:i+3] if word):
                    # Формируем потенциальную аббревиатуру из первых букв
                    potential_abbr = ''.join(word[0].upper() for word in words[i:i+3] if word)
                    if len(potential_abbr) >= 2 and potential_abbr.isupper():
                        full_form = ' '.join(words[i:i+3]).lower()
                        # Проверяем, что аббревиатура находится где-то рядом в тексте
                        if potential_abbr in sentence.upper():
                            self.abbreviations[potential_abbr] = full_form
                            self.full_forms[full_form] = potential_abbr

    def _get_abbreviation(self, text):
        """
        Получает аббревиатуру для текста, если это полная форма
        """
        text_lower = text.lower()
        if text_lower in self.full_forms:
            return self.full_forms[text_lower]
        
        # Генерируем потенциальную аббревиатуру из первых букв слов
        words = text_lower.split()
        if len(words) >= 2:
            potential_abbr = ''.join(word[0].upper() for word in words if word)
            if len(potential_abbr) >= 2:
                return potential_abbr
        return None

    def _get_full_form(self, text):
        """
        Получает полную форму для аббревиатуры
        """
        text_upper = text.upper()
        if text_upper in self.abbreviations:
            return self.abbreviations[text_upper]
        return None

    def _expand_query_with_abbreviations(self, text):
        """
        Расширяет запрос, добавляя аббревиатуры и полные формы
        """
        expanded_terms = []
        words = word_tokenize(text.lower())
        
        # Проверяем каждое слово на аббревиатуру
        for word in words:
            if word.isupper() and len(word) >= 2:
                # Это может быть аббревиатура
                full_form = self._get_full_form(word)
                if full_form:
                    expanded_terms.append(full_form.replace(' ', '_'))
            
        # Проверяем n-граммы на полные формы
        for n in range(2, 5):  # Проверяем от биграмм до 4-грамм
            if len(words) >= n:
                for i in range(len(words) - n + 1):
                    phrase = ' '.join(words[i:i+n])
                    abbr = self._get_abbreviation(phrase)
                    if abbr:
                        expanded_terms.append(abbr)
        
        return expanded_terms

    def correct_spelling(self, word, cutoff=0.8):
        """
        Исправление опечаток с помощью алгоритма Левенштейна (difflib)
        """
        if not self.vocabulary or word in self.vocabulary:
            return word

        # Используем get_close_matches для нахождения похожих слов
        matches = get_close_matches(word, self.vocabulary, n=1, cutoff=cutoff)
        return matches[0] if matches else word

    def extract_entities(self, text):
        """
        Выделение технических сущностей из текста
        """
        entities = []
        
        # Проверяем на наличие технических терминов
        for term in self.tech_terms:
            if term in text.lower():
                entities.append(term)
                
        # Ищем паттерны ошибок (например, коды ошибок)
        error_codes = re.findall(r'(ошибка|error)[:\s]+[A-Za-z0-9]+', text.lower())
        if error_codes:
            entities.extend(error_codes)
            
        return entities

    def lemmatize(self, token):
        """
        Лемматизация с помощью PyMorphy2
        """
        if not self.morph:
            return self.stemmer.stem(token)
        
        # Получаем нормальную форму слова
        return self.morph.parse(token)[0].normal_form

    def extract_ngrams(self, tokens):
        """
        Извлекает n-граммы из токенов
        """
        ngrams_found = []
        
        # Если список токенов слишком короткий, возвращаем пустой список
        if len(tokens) < 2:
            return ngrams_found
            
        # Проверяем биграммы
        bigrams_list = [' '.join(bg) for bg in list(ngrams(tokens, 2))]
        for bg in bigrams_list:
            if bg in self.ngram_vocabulary['bigrams']:
                ngrams_found.append(bg)
                
        # Проверяем триграммы
        if len(tokens) >= 3:
            trigrams_list = [' '.join(tg) for tg in list(ngrams(tokens, 3))]
            for tg in trigrams_list:
                if tg in self.ngram_vocabulary['trigrams']:
                    ngrams_found.append(tg)
                    
        return ngrams_found

    def preprocess_text(self, text):
        """
        Улучшенный метод для предобработки текста: 
        - токенизация
        - удаление стоп-слов
        - лемматизация/стемминг
        - исправление опечаток
        - сохранение n-грамм и сущностей
        - обработка аббревиатур
        """
        if pd.isna(text):  # Проверка на NaN значения
            return ""
            
        # Извлекаем сущности до предобработки
        entities = self.extract_entities(str(text))
        
        # Расширяем запрос аббревиатурами и полными формами
        expanded_terms = self._expand_query_with_abbreviations(str(text))
        
        # Приводим к нижнему регистру и удаляем лишние символы
        text = str(text).lower()
        text = re.sub(r'[^\w\s]', ' ', text)  # Удаляем знаки пунктуации
        
        try:
            # Токенизация
            tokens = word_tokenize(text)
        except LookupError:
            print("Критическая ошибка: не удалось загрузить токенизатор NLTK.")
            return ""

        # Исправление опечаток, если словарь не пустой
        if self.vocabulary:
            tokens = [self.correct_spelling(token) for token in tokens if token.isalpha()]
        else:
            tokens = [token for token in tokens if token.isalpha()]

        # Извлечение n-грамм до удаления стоп-слов
        ngrams_found = self.extract_ngrams(tokens) if self.ngram_vocabulary else []
        
        # Удаление стоп-слов и лемматизация/стемминг
        processed_tokens = []
        for token in tokens:
            if token not in self.stop_words:
                processed_tokens.append(self.lemmatize(token))
                
        # Объединяем обработанные токены в строку
        result = ' '.join(processed_tokens)
        
        # Добавляем найденные n-граммы и сущности
        if ngrams_found:
            result += ' ' + ' '.join([ng.replace(' ', '_') for ng in ngrams_found])
            
        if entities:
            result += ' ' + ' '.join([entity.replace(' ', '_') for entity in entities])
            
        # Добавляем расширенные термины (аббревиатуры и полные формы)
        if expanded_terms:
            result += ' ' + ' '.join(expanded_terms)
            
        return result

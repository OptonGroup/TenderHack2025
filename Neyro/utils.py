"""
Модуль для утилитных функций
"""

import pandas as pd  # Для работы с табличными данными
import nltk  # Библиотека для обработки естественного языка
import re  # Для работы с регулярными выражениями
from difflib import get_close_matches  # Для нечеткого поиска слов
from nltk.tokenize import word_tokenize  # Для разбиения текста на токены
from nltk.corpus import stopwords  # Для получения списка стоп-слов
from nltk.stem import SnowballStemmer  # Для стемминга слов

# Скачиваем необходимые ресурсы NLTK при необходимости
try:
    nltk.data.find('corpora/stopwords')
except nltk.downloader.DownloadError:
    print("Загружаем 'stopwords' для NLTK...")
    nltk.download('stopwords')
except LookupError:
     print("Ресурс 'stopwords' не найден, но уже скачан. Пропускаем.")


try:
    nltk.data.find('tokenizers/punkt')
except nltk.downloader.DownloadError:
    print("Загружаем 'punkt' для NLTK...")
    nltk.download('punkt')
except LookupError:
     print("Ресурс 'punkt' не найден, но уже скачан. Пропускаем.")

try:
    nltk.data.find('tokenizers/punkt_tab')
except nltk.downloader.DownloadError:
    print("Загружаем 'punkt_tab' для NLTK...")
    nltk.download('punkt_tab')
except LookupError:
    print("Ресурс 'punkt_tab' не найден, но уже скачан. Пропускаем.")


class TextProcessor:
    """
    Класс для предварительной обработки текста
    """
    def __init__(self):
        self.stemmer = SnowballStemmer('russian')  # Инициализация стеммера для русского языка
        try:
            self.stop_words = set(stopwords.words('russian'))  # Получение списка русских стоп-слов
        except LookupError:
            # Эта ситуация не должна возникать из-за проверок выше, но на всякий случай
            print("Критическая ошибка: не удалось загрузить стоп-слова NLTK.")
            self.stop_words = set()
        self.vocabulary = set()  # Словарь для исправления опечаток

    def build_vocabulary(self, texts):
        """
        Создание словаря слов для исправления опечаток
        """
        all_words = []
        for text in texts:
            if pd.isna(text):
                continue
            # Используем re.findall для извлечения слов, обрабатываем как строку
            words = re.findall(r'\b\w+\b', str(text).lower())
            all_words.extend(words)
        self.vocabulary = set(all_words)

    def correct_spelling(self, word, cutoff=0.8):
        """
        Исправление опечаток с помощью алгоритма Левенштейна (difflib)
        """
        if not self.vocabulary or word in self.vocabulary:
            return word

        # Используем get_close_matches для нахождения похожих слов
        matches = get_close_matches(word, self.vocabulary, n=1, cutoff=cutoff)
        return matches[0] if matches else word

    def preprocess_text(self, text):
        """
        Метод для предобработки текста: токенизация, удаление стоп-слов, стемминг и исправление опечаток
        """
        if pd.isna(text):  # Проверка на NaN значения
            return ""
        try:
            # Обрабатываем текст как строку
            tokens = word_tokenize(str(text).lower())  # Токенизация и приведение к нижнему регистру
        except LookupError:
             # Эта ситуация не должна возникать из-за проверок выше
            print("Критическая ошибка: не удалось загрузить токенизатор NLTK.")
            return ""

        # Исправление опечаток, если словарь не пустой
        if self.vocabulary:
            tokens = [self.correct_spelling(token) for token in tokens if token.isalpha()] # Исправляем только слова
        else:
             tokens = [token for token in tokens if token.isalpha()] # Отфильтровываем не-слова

        tokens = [token for token in tokens if token not in self.stop_words]  # Удаление стоп-слов
        tokens = [self.stemmer.stem(token) for token in tokens]  # Стемминг токенов
        return ' '.join(tokens)  # Объединение токенов в строку

"""
Модуль для обработки текста и анализа запросов пользователей Портала поставщиков
"""

# Импортируем необходимые библиотеки
import pandas as pd  # Для работы с табличными данными
import nltk  # Библиотека для обработки естественного языка
import re  # Библиотека для работы с регулярными выражениями
from difflib import get_close_matches  # Для поиска похожих слов
from nltk.tokenize import word_tokenize, sent_tokenize  # Функции для разбиения текста на слова и предложения
from nltk.corpus import stopwords  # Коллекция стоп-слов
from nltk.stem import SnowballStemmer  # Стеммер для приведения слов к основе
from nltk.util import ngrams  # Функция для создания n-грамм
import pymorphy2  # Морфологический анализатор для русского языка
from collections import Counter  # Для подсчета частоты элементов
import numpy as np  # Библиотека для научных вычислений

# Автоматическая загрузка необходимых ресурсов NLTK
try:
    nltk.data.find('corpora/stopwords')  # Проверяем, загружены ли стоп-слова
except LookupError:
    nltk.download('stopwords')  # Если нет, загружаем их

try:
    nltk.data.find('tokenizers/punkt')  # Проверяем, загружен ли токенизатор
except LookupError:
    nltk.download('punkt')  # Если нет, загружаем его

class TextProcessor:
    """
    Класс для предварительной обработки текста запросов пользователей Портала поставщиков
    """
    def __init__(self):
        # Инициализация стеммера для русского языка
        self.stemmer = SnowballStemmer('russian')  # Создаем стеммер для русского языка
        
        # Получение списка русских стоп-слов
        try:
            self.stop_words = set(stopwords.words('russian'))  # Загружаем стоп-слова для русского языка
            # Исключаем важные негативные частицы и слова, определяющие контекст
            self.stop_words -= {'не', 'нет', 'без', 'ошибка', 'проблема'}  # Удаляем из стоп-слов важные для контекста слова
        except LookupError:
            print("Не удалось загрузить стоп-слова NLTK")  # Выводим сообщение об ошибке
            self.stop_words = set()  # Создаем пустое множество стоп-слов
            
        # Инициализация морфологического анализатора
        try:
            self.morph = pymorphy2.MorphAnalyzer()  # Создаем морфологический анализатор
        except:
            print("Не удалось инициализировать PyMorphy2")  # Выводим сообщение об ошибке
            self.morph = None  # Устанавливаем значение None
            
        # Словари для хранения словаря и n-грамм
        self.vocabulary = set()  # Создаем пустое множество для словаря
        self.ngram_vocabulary = {}  # Создаем пустой словарь для n-грамм
        
        # Словари для обработки аббревиатур
        self.abbreviations = {}  # Словарь: аббревиатура -> полная форма
        self.full_forms = {}     # Словарь: полная форма -> аббревиатура
        
        # Определение предметных областей и ключевых сущностей Портала поставщиков
        self.domain_entities = {
            'документы': {'упд', 'универсальный передаточный документ', 'накладная', 'счет', 'счет-фактура', 
                         'акт', 'договор', 'контракт', 'оферта', 'заявка'},  # Типы документов
            'роли': {'заказчик', 'поставщик', 'исполнитель', 'закупщик', 'покупатель', 'продавец', 'получатель', 'отправитель'},  # Роли пользователей
            'действия': {'разблокировать', 'заблокировать', 'зарегистрировать', 'подписать', 'отправить', 'получить', 
                         'создать', 'удалить', 'изменить', 'отклонить', 'согласовать'},  # Возможные действия
            'проблемы': {'ошибка', 'проблема', 'не работает', 'не удается', 'не получается', 'отсутствует', 
                         'недоступен', 'отказ', 'сбой', 'неисправность'},  # Типы проблем
            'компоненты': {'портал', 'сайт', 'система', 'личный кабинет', 'реестр', 'каталог', 'профиль'}  # Компоненты системы
        }
        
        # Общий набор сущностей для быстрого поиска
        self.all_entities = set()  # Создаем пустое множество для всех сущностей
        for entity_set in self.domain_entities.values():  # Перебираем все категории сущностей
            self.all_entities.update(entity_set)  # Добавляем сущности в общее множество

    def build_vocabulary(self, texts):
        """
        Создание словаря слов и n-грамм для предобработки текста
        
        Args:
            texts (List[str]): Список текстов для анализа
        """
        all_words = []  # Создаем пустой список для всех слов
        bigrams_list = []  # Создаем пустой список для биграмм
        trigrams_list = []  # Создаем пустой список для триграмм
        
        for text in texts:  # Перебираем все тексты
            if pd.isna(text):  # Проверяем, не является ли текст пустым (NaN)
                continue  # Если да, переходим к следующему тексту
                
            # Предварительная нормализация текста
            text = str(text).lower()  # Приводим текст к нижнему регистру
            
            # Поиск и извлечение аббревиатур
            self._extract_abbreviations(text)  # Извлекаем аббревиатуры из текста
            
            # Очистка текста от пунктуации
            clean_text = re.sub(r'[^\w\s]', ' ', text)  # Заменяем все символы, кроме букв, цифр и пробелов, на пробелы
            
            # Токенизация текста
            words = word_tokenize(clean_text)  # Разбиваем текст на отдельные слова
            all_words.extend(words)  # Добавляем слова в общий список
            
            # Создаем n-граммы для улучшения качества поиска
            if len(words) > 1:  # Если в тексте больше одного слова
                bigrams_list.extend([' '.join(bg) for bg in list(ngrams(words, 2))])  # Создаем биграммы
            if len(words) > 2:  # Если в тексте больше двух слов
                trigrams_list.extend([' '.join(tg) for tg in list(ngrams(words, 3))])  # Создаем триграммы
        
        # Сохраняем уникальные слова в словарь
        self.vocabulary = set(all_words)  # Преобразуем список слов в множество (уникальные значения)
        
        # Подсчитываем частоту n-грамм
        bigram_counter = Counter(bigrams_list)  # Считаем частоту биграмм
        trigram_counter = Counter(trigrams_list)  # Считаем частоту триграмм
        
        # Сохраняем только часто встречающиеся n-граммы
        self.ngram_vocabulary = {
            'bigrams': {bg for bg, count in bigram_counter.items() if count >= 2},  # Биграммы, встречающиеся не менее 2 раз
            'trigrams': {tg for tg, count in trigram_counter.items() if count >= 2}  # Триграммы, встречающиеся не менее 2 раз
        }
        
        # Добавляем предметные сущности и термины в словарь n-грамм
        for entity in self.all_entities:  # Перебираем все предметные сущности
            words = entity.split()  # Разбиваем сущность на слова
            if len(words) == 2:  # Если сущность состоит из 2 слов
                self.ngram_vocabulary['bigrams'].add(entity)  # Добавляем в словарь биграмм
            elif len(words) == 3:  # Если сущность состоит из 3 слов
                self.ngram_vocabulary['trigrams'].add(entity)  # Добавляем в словарь триграмм

    def _extract_abbreviations(self, text):
        """
        Извлечение аббревиатур и их полных форм из текста
        
        Args:
            text (str): Текст для анализа
        """
        # Паттерн 1: "полная форма (АББР)"
        pattern1 = r'([а-яА-Яa-zA-Z\s]+)\s+\(([А-ЯA-Z]{2,})\)'  # Регулярное выражение для поиска полной формы и аббревиатуры
        matches1 = re.findall(pattern1, text)  # Находим все совпадения
        for full_form, abbr in matches1:  # Перебираем найденные пары
            full_form = full_form.strip().lower()  # Очищаем и приводим к нижнему регистру полную форму
            abbr = abbr.strip().upper()  # Очищаем и приводим к верхнему регистру аббревиатуру
            self.abbreviations[abbr] = full_form  # Сохраняем в словарь аббревиатур
            self.full_forms[full_form] = abbr  # Сохраняем в словарь полных форм
            
        # Паттерн 2: "АББР (полная форма)"
        pattern2 = r'([А-ЯA-Z]{2,})\s+\(([а-яА-Яa-zA-Z\s]+)\)'  # Регулярное выражение для поиска аббревиатуры и полной формы
        matches2 = re.findall(pattern2, text)  # Находим все совпадения
        for abbr, full_form in matches2:  # Перебираем найденные пары
            full_form = full_form.strip().lower()  # Очищаем и приводим к нижнему регистру полную форму
            abbr = abbr.strip().upper()  # Очищаем и приводим к верхнему регистру аббревиатуру
            self.abbreviations[abbr] = full_form  # Сохраняем в словарь аббревиатур
            self.full_forms[full_form] = abbr  # Сохраняем в словарь полных форм
        
        # Поиск потенциальных аббревиатур в тексте
        sentences = sent_tokenize(text)  # Разбиваем текст на предложения
        for sentence in sentences:  # Перебираем предложения
            words = word_tokenize(sentence)  # Разбиваем предложение на слова
            
            # Ищем последовательности из заглавных букв
            for i in range(len(words) - 2):  # Перебираем слова с запасом для триграмм
                if all(word and word[0].isupper() for word in words[i:i+3] if word):  # Проверяем, начинаются ли 3 слова подряд с заглавной буквы
                    # Формируем потенциальную аббревиатуру
                    potential_abbr = ''.join(word[0].upper() for word in words[i:i+3] if word)  # Создаем аббревиатуру из первых букв
                    if len(potential_abbr) >= 2 and potential_abbr.isupper():  # Если аббревиатура содержит не менее 2 букв и все в верхнем регистре
                        full_form = ' '.join(words[i:i+3]).lower()  # Создаем полную форму
                        # Проверяем, есть ли аббревиатура в тексте
                        if potential_abbr in sentence.upper():  # Если аббревиатура встречается в предложении
                            self.abbreviations[potential_abbr] = full_form  # Сохраняем в словарь аббревиатур
                            self.full_forms[full_form] = potential_abbr  # Сохраняем в словарь полных форм

    def correct_spelling(self, word, cutoff=0.8):
        """
        Исправление опечаток с использованием словаря
        
        Args:
            word (str): Слово для проверки
            cutoff (float): Порог сходства (от 0 до 1)
            
        Returns:
            str: Исправленное слово или исходное, если подходящего варианта не найдено
        """
        if not self.vocabulary or word in self.vocabulary:  # Если словарь пуст или слово уже есть в словаре
            return word  # Возвращаем исходное слово

        # Поиск ближайших по написанию слов
        matches = get_close_matches(word, self.vocabulary, n=1, cutoff=cutoff)  # Ищем похожие слова
        return matches[0] if matches else word  # Возвращаем первое похожее слово или исходное, если ничего не найдено

    def lemmatize(self, token):
        """
        Лемматизация слова (приведение к нормальной форме)
        
        Args:
            token (str): Слово для лемматизации
            
        Returns:
            str: Лемматизированное слово
        """
        if self.morph:  # Если морфологический анализатор доступен
            # Использование морфологического анализатора
            return self.morph.parse(token)[0].normal_form  # Возвращаем нормальную форму слова
        else:
            # Если морфологический анализатор недоступен, используем стемминг
            return self.stemmer.stem(token)  # Возвращаем основу слова

    def extract_entities(self, text):
        """
        Извлечение предметных сущностей из текста
        
        Args:
            text (str): Текст для анализа
            
        Returns:
            dict: Словарь с найденными сущностями по категориям
        """
        text_lower = text.lower()  # Приводим текст к нижнему регистру
        found_entities = {category: set() for category in self.domain_entities}  # Создаем словарь для найденных сущностей
        
        # Поиск сущностей из каждой категории
        for category, entities in self.domain_entities.items():  # Перебираем категории и их сущности
            for entity in entities:  # Перебираем сущности
                if entity in text_lower:  # Если сущность найдена в тексте
                    found_entities[category].add(entity)  # Добавляем в список найденных
        
        # Поиск аббревиатур
        for abbr, full_form in self.abbreviations.items():  # Перебираем аббревиатуры и их полные формы
            if abbr.lower() in text_lower:  # Если аббревиатура найдена в тексте
                # Определяем категорию по полной форме
                for category, entities in self.domain_entities.items():  # Перебираем категории
                    if any(term in full_form for term in entities):  # Если полная форма содержит термин из категории
                        found_entities[category].add(abbr.lower())  # Добавляем аббревиатуру
                        found_entities[category].add(full_form)  # Добавляем полную форму
        
        return found_entities  # Возвращаем найденные сущности

    def extract_ngrams(self, tokens):
        """
        Извлечение n-грамм из токенов текста
        
        Args:
            tokens (List[str]): Список токенов
            
        Returns:
            List[str]: Список найденных n-грамм
        """
        ngrams_found = []  # Создаем пустой список для найденных n-грамм
        
        if len(tokens) < 2:  # Если токенов меньше 2
            return ngrams_found  # Возвращаем пустой список
            
        # Проверка биграмм
        bigrams_list = [' '.join(bg) for bg in list(ngrams(tokens, 2))]  # Создаем список биграмм
        for bg in bigrams_list:  # Перебираем биграммы
            if bg in self.ngram_vocabulary.get('bigrams', set()):  # Если биграмма есть в словаре
                ngrams_found.append(bg)  # Добавляем в список найденных
                
        # Проверка триграмм
        if len(tokens) >= 3:  # Если токенов не менее 3
            trigrams_list = [' '.join(tg) for tg in list(ngrams(tokens, 3))]  # Создаем список триграмм
            for tg in trigrams_list:  # Перебираем триграммы
                if tg in self.ngram_vocabulary.get('trigrams', set()):  # Если триграмма есть в словаре
                    ngrams_found.append(tg)  # Добавляем в список найденных
                    
        return ngrams_found  # Возвращаем найденные n-граммы

    def expand_query(self, text):
        """
        Расширение запроса с добавлением аббревиатур и полных форм
        
        Args:
            text (str): Исходный запрос
            
        Returns:
            List[str]: Список вариантов запроса
        """
        expanded_terms = []  # Создаем пустой список для расширенных терминов
        
        # Обработка аббревиатур и их полных форм
        for abbr, full_form in self.abbreviations.items():  # Перебираем аббревиатуры и их полные формы
            if abbr.lower() in text.lower():  # Если аббревиатура найдена в тексте
                expanded_terms.append(full_form)  # Добавляем полную форму
            elif full_form in text.lower():  # Если полная форма найдена в тексте
                expanded_terms.append(abbr.lower())  # Добавляем аббревиатуру
        
        # Поиск терминов из предметной области
        for entity_list in self.domain_entities.values():  # Перебираем списки сущностей
            for entity in entity_list:  # Перебираем сущности
                if entity in text.lower():  # Если сущность найдена в тексте
                    # Добавляем синонимы и связанные термины
                    for category, terms in self.domain_entities.items():  # Перебираем категории
                        for term in terms:  # Перебираем термины
                            if entity in term and entity != term:  # Если термин содержит сущность, но не равен ей
                                expanded_terms.append(term)  # Добавляем термин
        
        return expanded_terms  # Возвращаем расширенные термины

    def preprocess_text(self, text):
        """
        Комплексная предобработка текста для поиска
        
        Args:
            text (str): Исходный текст
            
        Returns:
            str: Обработанный текст, готовый для векторизации
        """
        if pd.isna(text):  # Если текст пустой (NaN)
            return ""  # Возвращаем пустую строку
            
        # Извлечение предметных сущностей
        found_entities = self.extract_entities(str(text))  # Извлекаем сущности из текста
        
        # Расширение запроса дополнительными терминами
        expanded_terms = self.expand_query(str(text))  # Расширяем запрос
        
        # Нормализация текста
        text = str(text).lower()  # Приводим текст к нижнему регистру
        text = re.sub(r'[^\w\s]', ' ', text)  # Заменяем все символы, кроме букв, цифр и пробелов, на пробелы
        
        # Токенизация
        try:
            tokens = word_tokenize(text)  # Разбиваем текст на слова
        except:
            print("Ошибка токенизации")  # Выводим сообщение об ошибке
            return ""  # Возвращаем пустую строку

        # Исправление опечаток
        if self.vocabulary:  # Если словарь не пуст
            tokens = [self.correct_spelling(token) for token in tokens if token.isalpha()]  # Исправляем опечатки в словах
        else:
            tokens = [token for token in tokens if token.isalpha()]  # Оставляем только слова

        # Извлечение n-грамм
        ngrams_found = self.extract_ngrams(tokens)  # Извлекаем n-граммы
        
        # Удаление стоп-слов и лемматизация
        processed_tokens = []  # Создаем пустой список для обработанных токенов
        for token in tokens:  # Перебираем токены
            if token not in self.stop_words:  # Если токен не является стоп-словом
                processed_tokens.append(self.lemmatize(token))  # Лемматизируем и добавляем в список
                
        # Формирование результата
        result = ' '.join(processed_tokens)  # Объединяем обработанные токены в строку
        
        # Добавление n-грамм и предметных сущностей
        if ngrams_found:  # Если найдены n-граммы
            result += ' ' + ' '.join([ng.replace(' ', '_') for ng in ngrams_found])  # Добавляем n-граммы, заменяя пробелы на подчеркивания
        
        # Добавление найденных сущностей
        for category, entities in found_entities.items():  # Перебираем категории и их сущности
            if entities:  # Если найдены сущности
                for entity in entities:  # Перебираем сущности
                    result += ' ' + entity.replace(' ', '_')  # Добавляем сущность, заменяя пробелы на подчеркивания
        
        # Добавление расширенных терминов
        if expanded_terms:  # Если есть расширенные термины
            result += ' ' + ' '.join([term.replace(' ', '_') for term in expanded_terms])  # Добавляем термины, заменяя пробелы на подчеркивания
            
        return result  # Возвращаем обработанный текст
        
    def classify_query(self, text):
        """
        Классификация запроса пользователя
        
        Args:
            text (str): Текст запроса
            
        Returns:
            dict: Словарь с классификацией запроса
        """
        # Классификация по типу запроса
        text_lower = text.lower()  # Приводим текст к нижнему регистру
        
        # Извлекаем сущности
        entities = self.extract_entities(text)  # Извлекаем сущности из текста
        
        # Определяем тип запроса (проблема/инструкция/справка)
        query_type = 'info'  # По умолчанию информационный запрос
        if any(term in text_lower for term in ['ошибка', 'проблема', 'не работает', 'не удается']):  # Если текст содержит слова, указывающие на проблему
            query_type = 'error'  # Устанавливаем тип запроса "ошибка"
        elif any(term in text_lower for term in ['как', 'инструкция', 'подробно', 'объясните']):  # Если текст содержит слова, указывающие на инструкцию
            query_type = 'instruction'  # Устанавливаем тип запроса "инструкция"
            
        # Определяем роль пользователя
        user_role = None  # По умолчанию роль не определена
        for role in entities.get('роли', []):  # Перебираем найденные роли
            user_role = role  # Устанавливаем роль пользователя
            break  # Берем первую найденную роль
            
        # Определяем компонент системы
        component = None  # По умолчанию компонент не определен
        for doc in entities.get('документы', []):  # Перебираем найденные документы
            component = doc  # Устанавливаем компонент
            break  # Берем первый найденный документ
        
        if not component:  # Если компонент не определен по документам
            for comp in entities.get('компоненты', []):  # Перебираем найденные компоненты
                component = comp  # Устанавливаем компонент
                break  # Берем первый найденный компонент
        
        # Определяем необходимость перевода на оператора
        needs_operator = False
        
        # Ключевые слова, указывающие на необходимость оператора
        operator_keywords = [
            'оператор', 'специалист', 'поддержка', 'помогите', 'срочно', 'критично',
            'соединить', 'человек', 'перевести на', 'переключить', 'живой человек'
        ]
        
        # Критичные проблемы, требующие вмешательства оператора
        critical_issues = [
            'блокировка', 'взлом', 'утечка', 'недоступен', 'потеря данных', 
            'деньги', 'оплата', 'счет', 'платеж', 'финансы', 'контракт разорван',
            'угроза', 'штраф', 'санкции', 'срыв сроков', 'юрист'
        ]
        
        # Проверяем наличие ключевых слов для оператора
        if any(keyword in text_lower for keyword in operator_keywords):
            needs_operator = True
            
        # Проверяем наличие критичных проблем
        if query_type == 'error' and any(issue in text_lower for issue in critical_issues):
            needs_operator = True
            
        # Проверяем сложность запроса (длинные запросы с множеством деталей)
        if len(text.split()) > 20 and query_type == 'error':
            needs_operator = True
                
        # Формируем результат классификации
        classification = {
            'query_type': query_type,  # Тип запроса
            'user_role': user_role,  # Роль пользователя
            'component': component,  # Компонент системы
            'actions': list(entities.get('действия', [])),  # Список действий
            'problems': list(entities.get('проблемы', [])),  # Список проблем
            'needs_operator': needs_operator  # Флаг необходимости перевода на оператора
        }
        
        return classification  # Возвращаем результат классификации

import numpy as np  # Для работы с числовыми массивами
import pandas as pd  # Для работы с табличными данными
from sklearn.feature_extraction.text import TfidfVectorizer  # Для векторизации текста с помощью TF-IDF
from sklearn.metrics.pairwise import cosine_similarity  # Для расчета косинусного сходства между векторами
import pickle  # Для сериализации и десериализации объектов Python

# Импортируем TextProcessor из utils
import utils  # Используем абсолютный импорт вместо относительного

class TenderModel:
    """
    Класс для создания и использования модели поиска похожих тендеров
    """
    def __init__(self, dataset_path):
        self.dataset = pd.read_parquet(dataset_path)  # Загрузка датасета из файла parquet
        self.vectorizer = TfidfVectorizer()  # Инициализация TF-IDF векторизатора
        self.text_processor = utils.TextProcessor()  # Создание экземпляра обработчика текста
        self.model = None  # Переменная для хранения обученной модели

    def train(self):   
        """
        Метод для обучения модели
        """
        # Объединяем заголовок и описание для лучшего поиска
        self.dataset['combined_text'] = self.dataset['Заголовок статьи'] + ' ' + self.dataset['Описание'].fillna('')
        
        # Создаем словарь для исправления опечаток
        self.text_processor.build_vocabulary(self.dataset['combined_text'])
        
        # Предобработка объединенного текста
        self.dataset['processed_text'] = self.dataset['combined_text'].apply(self.text_processor.preprocess_text)
        # Обучение векторизатора на предобработанных текстах
        self.vectorizer.fit(self.dataset['processed_text'])
        # Преобразование текстов в TF-IDF векторы
        self.model = self.vectorizer.transform(self.dataset['processed_text'])

    def predict(self, text):
        """
        Метод для расчета сходства между запросом и всеми документами в датасете
        """
        processed_text = self.text_processor.preprocess_text(text)  # Предобработка запроса
        text_vector = self.vectorizer.transform([processed_text])  # Преобразование запроса в TF-IDF вектор
        similarity = cosine_similarity(text_vector, self.model)  # Расчет косинусного сходства
        return similarity
    
    def get_recommendations(self, text, top_n=5):
        """
        Метод для получения top_n наиболее похожих документов
        """
        similarity = self.predict(text)  # Получение значений сходства
        indices = np.argsort(similarity[0])[::-1][:top_n]  # Сортировка индексов по убыванию сходства
        return self.dataset.iloc[indices][['Заголовок статьи', 'Описание']]  # Возврат найденных документов
    
    def save_model(self, model_path):
        """
        Метод для сохранения модели в файл
        """
        with open(model_path, 'wb') as f:
            pickle.dump(self, f)  # Сериализация объекта модели
            
    @staticmethod
    def load_model(model_path):
        """
        Статический метод для загрузки модели из файла
        """
        with open(model_path, 'rb') as f:
            return pickle.load(f)  # Десериализация объекта модели
        

if __name__ == "__main__":
    try:
        # Получение запроса от пользователя
        input_text = input("Введите текст запроса: ")
        # Создание модели с указанием пути к датасету
        model = TenderModel('docs/dataset.parquet')
        # Обучение модели
        model.train()
        # Получение рекомендаций
        recommendations = model.get_recommendations(input_text)
        print("Найденные статьи:")
        # Вывод найденных статей
        for i, (title, desc) in enumerate(zip(recommendations['Заголовок статьи'], recommendations['Описание'])):
            print(f"{i+1}. {title}")
            if not pd.isna(desc):
                print(f"   {desc[:100]}..." if len(str(desc)) > 100 else f"   {desc}")
            print()
    except Exception as e:
        print(f"Произошла ошибка: {e}")  # Обработка возможных исключений

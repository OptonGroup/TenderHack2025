# TenderHack2025 - ИИ-ассистент для портала закупок Москвы

🚀 TenderHack 2025

## 📋 Описание

TenderHack2025 - это интеллектуальный помощник для работы с порталом [zakupki.mos.ru](https://zakupki.mos.ru). Ассистент помогает пользователям эффективно взаимодействовать с порталом, автоматизирует рутинные задачи и предоставляет поддержку в режиме реального времени, включая возможность быстрого соединения с живым оператором.

## 🔧 Интересные технические решения

- ✨ **Двухфакторная аутентификация** с использованием access и refresh токенов, хранящихся в [HTTP-only cookies](https://developer.mozilla.org/ru/docs/Web/HTTP/Cookies)
- 🔐 **CSRF-защита**
- 🤖 **AI-интеграция** с локальной моделью [Microsoft Phi-3-mini-4k-instruct](https://huggingface.co/microsoft/phi-3-mini-4k-instruct)
- 📈 **Асинхронное API** с использованием [FastAPI](https://fastapi.tiangolo.com/)
- 📄 **Валидация данных** через [Pydantic](https://docs.pydantic.dev/)
- 📱 **Адаптивный интерфейс**

## 📚 Используемые технологии и библиотеки

- [FastAPI](https://fastapi.tiangolo.com/) - современный высокопроизводительный веб-фреймворк
- [SQLAlchemy](https://www.sqlalchemy.org/) - SQL тулкит и ORM
- [JWT](https://jwt.io/) - безопасный механизм передачи данных в формате JSON
- [Pydantic](https://docs.pydantic.dev/) - библиотека для валидации данных
- [Jinja2](https://jinja.palletsprojects.com/) - шаблонизатор для Python
- [pandas](https://pandas.pydata.org/) - библиотека для анализа данных
- [uvicorn](https://www.uvicorn.org/) - ASGI сервер для Python
- [Passlib](https://passlib.readthedocs.io/) - библиотека для хэширования паролей
- [Microsoft Phi-3-mini-4k-instruct](https://huggingface.co/microsoft/phi-3-mini-4k-instruct) - языковая модель для локального развертывания

## Архитектура Модели ИИ-Ассистента

```mermaid
graph LR
    A[01. Запрос информации] --> B(spaCy);
    A --> C(NLTK);
    A --> D(SymSpell);
    subgraph "Этап 1: Обработка запроса"
        direction LR
        A
        B
        C
        D
        T1("- Классификация типа запроса <br/> (ошибка/инструкция/справка)<br/>- Предобработка запроса <br/> (нормализация, токенизация, <br/> исправление опечаток)<br/>- Генерация вариантов <br/> запроса для улучшения поиска") -.-> A;
    end

    A --> E[02. Поиск информации среди статей];
    E --> F(BM25);
    E --> G(BERT);
    E --> H(ensemble);
    subgraph "Этап 2: Поиск релевантных статей"
        direction LR
        E
        F
        G
        H
        T2("- Взвешенное комбинирование <br/> BM25, BERT<br/>- Применение контекстных весов <br/> на основе классификации запроса<br/>- Возможность отключения <br/> отдельных моделей") -.-> E;
    end

    E --> I[03. Обработка статей];
    I --> J(sber_nlu);
    I --> K(NLTK);
    I --> L(Cross-Encoders);
    subgraph "Этап 3: Анализ и ранжирование статей"
        direction LR
        I
        J
        K
        L
        T3("- Объединение заголовков и описаний <br/> для улучшения поиска<br/>- Классификация документов <br/> по типам<br/>- 2х этапный поиск информации: <br/>   - быстрый с BM25 <br/>   - долгий с Cross-Encoders") -.-> I;
    end

    I --> M[04. Формирование ответа];
    M --> N(torch);
    M --> O(transformers);
    subgraph "Этап 4: Генерация ответа"
        direction LR
        M
        N
        O
        T4("- Сортировка и выбор top-n <br/> релевантных документов<br/>- Выделение необходимой информации<br/>- Передача в LLM для генерации <br/> ответа и добавление ссылок <br/> на источники") -.-> M;
    end

    style A fill:#0a1931,stroke:#333,stroke-width:2px,color:#fff
    style E fill:#0a1931,stroke:#333,stroke-width:2px,color:#fff
    style I fill:#0a1931,stroke:#333,stroke-width:2px,color:#fff
    style M fill:#0a1931,stroke:#333,stroke-width:2px,color:#fff

    style B fill:#182c4a,stroke:#555,stroke-width:1px,color:#eee
    style C fill:#182c4a,stroke:#555,stroke-width:1px,color:#eee
    style D fill:#182c4a,stroke:#555,stroke-width:1px,color:#eee
    style F fill:#182c4a,stroke:#555,stroke-width:1px,color:#eee
    style G fill:#182c4a,stroke:#555,stroke-width:1px,color:#eee
    style H fill:#182c4a,stroke:#555,stroke-width:1px,color:#eee
    style J fill:#182c4a,stroke:#555,stroke-width:1px,color:#eee
    style K fill:#182c4a,stroke:#555,stroke-width:1px,color:#eee
    style L fill:#182c4a,stroke:#555,stroke-width:1px,color:#eee
    style N fill:#182c4a,stroke:#555,stroke-width:1px,color:#eee
    style O fill:#182c4a,stroke:#555,stroke-width:1px,color:#eee

    style T1 fill:#0a1931,stroke:#0a1931,color:#ccc
    style T2 fill:#0a1931,stroke:#0a1931,color:#ccc
    style T3 fill:#0a1931,stroke:#0a1931,color:#ccc
    style T4 fill:#0a1931,stroke:#0a1931,color:#ccc

```

Я добавил этот график в ваш `README.md` файл.



## 📂 Структура проекта

```
TenderHack2025/
├── Backend/
│   ├── static/
│   │   ├── js/
│   │   ├── css/
│   │   └── img/
│   ├── templates/
│   ├── uploads/
│   │   └── tenders/
│   ├── auth.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   └── server.py
├── Neyro/
│   ├── tests/
│   ├── analyze/
│   ├── app.py
│   ├── model.py
│   ├── utils.py
│   ├── requirements.txt
│   └── dictionary_ru.txt
├── docs/
│   └── dataset.parquet
└── README.md
```

- **Backend/** - основная директория с кодом приложения
  - **static/** - статические файлы (JavaScript, CSS, изображения)
  - **templates/** - шаблоны Jinja2 для рендеринга HTML
  - **uploads/** - директория для загружаемых пользователями файлов
- **Neyro/** - модуль для работы с моделью Microsoft Phi-3
  - **tests/** - юнит-тесты для моделей и утилит
  - **analyze/** - скрипты для анализа производительности моделей
  - **model.py** - основная реализация работы с LLM-моделью
  - **utils.py** - вспомогательные функции для обработки и нормализации текста
  - **dictionary_ru.txt** - словарь русских слов для проверки правописания

## 💡 Особенности реализации

- 🛡️ Защита от CSRF-атак
- 📝 Хэширование паролей с использованием алгоритма bcrypt
- 🗄️ Использование ORM SQLAlchemy для работы с базой данных
- 🤖 AI-чат с возможностью эскалации к оператору поддержки
- 📊 Административная панель для управления пользователями и мониторинга системы

## 🔌 API Эндпоинты для работы с пользователями и чатами

### Пользователи (Users)

- 🔐 **POST /api/login** - Аутентификация пользователя с выдачей JWT токенов
- 📝 **POST /api/register** - Регистрация нового пользователя
- 🔑 **POST /api/refresh-token** - Обновление access токена с помощью refresh токена
- 🚪 **POST /api/logout** - Выход из системы, инвалидация токенов
- 👤 **GET /api/users/me** - Получение информации о текущем пользователе
- 📋 **GET /api/users** - Получение списка всех пользователей (admin)
- 🔍 **GET /api/users/{user_id}** - Получение информации о пользователе по ID

### Чаты (Chat)

- 💬 **POST /api/chat-history** - Создание нового сообщения в чате
- 📚 **GET /api/chat-history** - Получение истории чатов пользователя
- 📖 **GET /api/chat-history/{chat_id}** - Получение конкретного чата по ID
- ✏️ **PATCH /api/chat-history/{message_id}** - Обновление сообщения
- 🗑️ **DELETE /api/chat-history/{chat_id}** - Удаление чата
- ⭐ **POST /api/chat-history/{chat_id}/finish** - Завершение чата с рейтингом
- 👨‍💼 **POST /api/call-operator** - Запрос на подключение оператора поддержки
- 📊 **GET /api/support-requests** - Получение запросов в поддержку (для операторов)
- ✅ **POST /api/support-requests/{chat_id}/resolve** - Разрешение запроса поддержки

## 🚀 Запуск проекта

### Локальная установка

```bash
# Клонирование репозитория
git clone https://github.com/your-username/TenderHack2025.git
cd TenderHack2025

# Установка зависимостей Backend
pip install -r requirements.txt

# Установка зависимостей Neyro
cd Neyro
pip install -r requirements.txt
cd ..

# Запуск сервера
cd Backend
uvicorn server:app --reload
```

### Запуск через Docker

```bash
# Сборка образа
docker build -t tenderhack2025 .

# Запуск контейнера
docker run -d -p 8000:8000 --name tenderhack tenderhack2025
```

Или с помощью Docker Compose:

```bash
# Запуск с помощью docker-compose
docker-compose up -d
```

## 🧠 Модуль Neyro

Модуль `Neyro` представляет собой серверную часть AI-ассистента, основанного на модели **Microsoft Phi-3-mini-4k-instruct**. Особенности:

- 🌐 Локальное развертывание нейросети без зависимости от внешних API
- ⚡ Оптимизация для работы на CPU с минимальными требованиями к ресурсам
- 🇷🇺 Полноценная поддержка русского языка с использованием словаря
- 📏 Контекстная обработка и анализ текстов до 4000 токенов
- 🔄 Автоматическое определение необходимости эскалации к оператору
- 📊 Встроенные механизмы анализа и стресс-тестирования модели

Файл [`model.py`](./Neyro/model.py) содержит основные классы для работы с моделью, а [`utils.py`](./Neyro/utils.py) предоставляет набор утилит для предобработки текста и оптимизации скорости работы.

Запуск модуля Neyro отдельно:

```bash
cd Neyro
python app.py
```

## 🏗️ Сборка проекта

```bash
# Создание виртуального окружения
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate  # Windows

# Установка зависимостей
pip install -r requirements.txt
pip install -r Neyro/requirements.txt

# Инициализация базы данных
python -c "from Backend.database import init_db; init_db()"

# Сборка фронтенда (если используется npm)
cd Frontend
npm install
npm run build
cd ..

# Упаковка в Docker (опционально)
docker build -t tenderhack2025 
```

# Скриншоты продукта
![pupupu](https://github.com/user-attachments/assets/8a70b2d2-0b2f-4635-8f5a-24c5a7b5e127)



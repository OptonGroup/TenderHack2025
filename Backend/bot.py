import os
import logging
import asyncio
from datetime import datetime
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import BotCommand, BotCommandScopeDefault
from uuid import uuid4
import json
import requests

from database import SessionLocal, engine, Base
import models
from models import User
from auth import get_password_hash, authenticate_user, create_access_token
from dotenv import load_dotenv
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
load_dotenv()
BOT_TOKEN = os.getenv("TG_BOT_TOKEN")
if not BOT_TOKEN:
    logger.error("Ошибка: TG_BOT_TOKEN не задан в переменных окружения")
    exit(1)

# URL для взаимодействия с чат-API
API_URL = os.getenv("API_URL", "http://localhost:8000")

bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Список команд для меню бота
commands = [
    BotCommand(command="start", description="Начать работу с ботом"),
    BotCommand(command="help", description="Показать справку"),
    BotCommand(command="register", description="Зарегистрироваться в системе"),
    BotCommand(command="login", description="Войти в систему"),
    BotCommand(command="chat", description="Начать новый чат"),
    BotCommand(command="chats", description="Получить список ваших чатов"),
    BotCommand(command="clear", description="Очистить текущий чат")
]

# Класс для хранения состояний пользователя при регистрации
class RegisterStates(StatesGroup):
    waiting_for_username = State()
    waiting_for_email = State()
    waiting_for_password = State()

# Класс для хранения состояний пользователя при входе
class LoginStates(StatesGroup):
    waiting_for_username = State()
    waiting_for_password = State()

# Класс для хранения состояний при общении в чате
class ChatStates(StatesGroup):
    waiting_for_message = State()

# Обработчик команды /start
@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    """
    Обработчик команды /start - приветствие и предложение зарегистрироваться
    """
    await message.answer(
        "Привет! Я бот для TenderHack.\n"
        "Вы можете зарегистрироваться или войти в систему.\n\n"
        "Доступные команды:\n"
        "/register - Зарегистрироваться\n"
        "/login - Войти в систему\n"
        "/help - Показать справку"
    )

# Обработчик команды /help
@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    """
    Обработчик команды /help - показывает доступные команды
    """
    await message.answer(
        "Доступные команды:\n"
        "/register - Зарегистрироваться\n"
        "/login - Войти в систему"
    )


@dp.message(Command("register"))
async def cmd_register(message: types.Message, state: FSMContext):
    """
    Обработчик команды /register - начало процесса регистрации
    """
    await message.answer("Давайте начнем регистрацию. Введите ваше имя пользователя:")
    await state.set_state(RegisterStates.waiting_for_username)


@dp.message(StateFilter(RegisterStates.waiting_for_username))
async def process_username(message: types.Message, state: FSMContext):
    """
    Обработчик ввода имени пользователя
    """
    username = message.text.strip()
    
    # Проверяем, что имя не пустое
    if not username:
        await message.answer("Имя пользователя не может быть пустым. Попробуйте еще раз:")
        return
    
    # Проверяем уникальность имени пользователя
    db = SessionLocal()
    existing_user = db.query(User).filter(User.username == username).first()
    db.close()
    
    if existing_user:
        await message.answer("Пользователь с таким именем уже существует. Введите другое имя:")
        return
    
    # Сохраняем имя пользователя
    await state.update_data(username=username)
    await message.answer("Теперь введите ваш email:")
    await state.set_state(RegisterStates.waiting_for_email)


@dp.message(StateFilter(RegisterStates.waiting_for_email))
async def process_email(message: types.Message, state: FSMContext):
    """
    Обработчик ввода email
    """
    email = message.text.strip()
    
    # Простая проверка формата email
    if "@" not in email or "." not in email:
        await message.answer("Пожалуйста, введите корректный email:")
        return
    
    # Проверяем уникальность email
    db = SessionLocal()
    existing_user = db.query(User).filter(User.email == email).first()
    db.close()
    
    if existing_user:
        await message.answer("Пользователь с таким email уже существует. Введите другой email:")
        return
    
    # Сохраняем email
    await state.update_data(email=email)
    await message.answer("Теперь введите пароль (минимум 8 символов):")
    await state.set_state(RegisterStates.waiting_for_password)

# Обработчик ввода пароля
@dp.message(StateFilter(RegisterStates.waiting_for_password))
async def process_password(message: types.Message, state: FSMContext):
    """
    Обработчик ввода пароля и завершение регистрации
    """
    password = message.text.strip()
    
    if len(password) < 8:
        await message.answer("Пароль должен содержать не менее 8 символов. Попробуйте еще раз:")
        return
    
    data = await state.get_data()
    username = data["username"]
    email = data["email"]
    hashed_password = get_password_hash(password)
    
    try:
        db = SessionLocal()
        new_user = User(
            username=username,
            email=email,
            hashed_password=hashed_password,
            is_active=True
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        db.close()
        
        await message.answer(
            f"Регистрация успешно завершена!\n"
            f"Ваше имя пользователя: {username}\n"
            f"Ваш email: {email}\n\n"
            f"Теперь вы можете войти в систему с помощью команды /login"
        )
    except Exception as e:
        logger.error(f"Ошибка при регистрации пользователя: {e}")
        await message.answer("Произошла ошибка при регистрации. Пожалуйста, попробуйте позже.")
    await state.clear()

@dp.message(Command("login"))
async def cmd_login(message: types.Message, state: FSMContext):
    """
    Обработчик команды /login - начало процесса входа
    """
    await message.answer("Введите ваше имя пользователя:")
    await state.set_state(LoginStates.waiting_for_username)

@dp.message(StateFilter(LoginStates.waiting_for_username))
async def process_login_username(message: types.Message, state: FSMContext):
    username = message.text.strip()
    
    db = SessionLocal()
    user = db.query(User).filter(User.username == username).first()
    db.close()
    
    if not user:
        await message.answer("Пользователь с таким именем не найден. Попробуйте еще раз или зарегистрируйтесь с помощью /register")
        await state.clear()
        return
    
    await state.update_data(username=username)
    await message.answer("Введите ваш пароль:")
    await state.set_state(LoginStates.waiting_for_password)


@dp.message(StateFilter(LoginStates.waiting_for_password))
async def process_login_password(message: types.Message, state: FSMContext):
    """
    Обработчик ввода пароля при входе
    """
    password = message.text.strip()
    
    data = await state.get_data()
    username = data["username"]
    
    db = SessionLocal()
    user = authenticate_user(db, username, password)
    db.close()
    
    if not user:
        await message.answer("Неверный пароль. Попробуйте еще раз:")
        return
    
    access_token = create_access_token(data={"sub": user.username})
    
    await state.update_data(user_id=user.id, access_token=access_token)
    
    await message.answer(
        f"Вход выполнен успешно! Добро пожаловать, {username}!\n"
        f"Теперь вы можете использовать функции бота."
    )
    
    # Очищаем только состояние, но не данные пользователя
    await state.set_state(None)

# Функция для проверки авторизации пользователя
async def check_auth(state: FSMContext) -> bool:
    """
    Проверяет, авторизован ли пользователь
    """
    data = await state.get_data()
    return bool(data.get("access_token"))

# Обработчик команды /chat
@dp.message(Command("chat"))
async def cmd_chat(message: types.Message, state: FSMContext):
    """
    Начинает новый чат или продолжает существующий
    """
    # Проверяем авторизацию
    if not await check_auth(state):
        await message.answer("Для начала чата необходимо войти в систему с помощью команды /login")
        return
    
    # Создаем новый идентификатор чата
    chat_id = str(uuid4())
    
    # Сохраняем ID чата в состоянии пользователя
    await state.update_data(current_chat_id=chat_id)
    
    # Устанавливаем состояние ожидания сообщения
    await state.set_state(ChatStates.waiting_for_message)
    
    await message.answer(
        "Новый чат начат. Просто отправьте ваш вопрос, и я попытаюсь на него ответить.\n"
        "Для выхода из чата введите /clear или начните новый чат с помощью /chat"
    )

# Обработчик команды /chats
@dp.message(Command("chats"))
async def cmd_chats(message: types.Message, state: FSMContext):
    """
    Показывает список доступных чатов пользователя
    """
    # Проверяем авторизацию
    if not await check_auth(state):
        await message.answer("Для просмотра чатов необходимо войти в систему с помощью команды /login")
        return
    
    data = await state.get_data()
    access_token = data.get("access_token")
    
    # Запрос к API для получения списка чатов
    try:
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(f"{API_URL}/api/chat-history", headers=headers)
        
        if response.status_code == 200:
            chats = response.json()
            
            if not chats:
                await message.answer("У вас пока нет активных чатов. Начните новый с помощью команды /chat")
            else:
                chat_list = "\n".join([f"• {chat}" for chat in chats])
                await message.answer(
                    f"Ваши активные чаты:\n{chat_list}\n\n"
                    f"Для продолжения чата используйте команду /chat"
                )
        else:
            await message.answer(f"Ошибка при получении списка чатов: {response.status_code}")
    
    except Exception as e:
        logger.error(f"Ошибка при получении списка чатов: {e}")
        await message.answer("Произошла ошибка при получении списка чатов")

# Обработчик команды /clear - очистка текущего чата
@dp.message(Command("clear"))
async def cmd_clear(message: types.Message, state: FSMContext):
    """
    Очищает текущий чат и выходит из режима чата
    """
    await state.clear_state()
    await message.answer("Чат завершен. Вы можете начать новый чат с помощью команды /chat")

# Обработчик сообщений в чате
@dp.message(StateFilter(ChatStates.waiting_for_message))
async def process_chat_message(message: types.Message, state: FSMContext):
    """
    Обрабатывает сообщения пользователя в режиме чата
    """
    # Получаем данные сеанса
    data = await state.get_data()
    user_id = data.get("user_id")
    access_token = data.get("access_token")
    chat_id = data.get("current_chat_id")
    
    # Получаем сообщение пользователя
    user_message = message.text.strip()
    
    # Если пользователь хочет выйти из чата
    if user_message.lower() in ["выход", "exit", "quit", "стоп", "stop"]:
        await state.clear_state()
        await message.answer("Чат завершен. Вы можете начать новый чат с помощью команды /chat")
        return
    
    try:
        # 1. Сохраняем сообщение пользователя в истории чата
        chat_message_data = {
            "user_id": user_id,
            "chat_id": chat_id,
            "message": user_message,
            "is_bot": False
        }
        
        headers = {"Authorization": f"Bearer {access_token}"}
        
        # Отправляем запрос на сохранение сообщения пользователя
        response = requests.post(
            f"{API_URL}/api/chat-history",
            json=chat_message_data,
            headers=headers
        )
        
        if response.status_code != 200:
            logger.error(f"Ошибка при сохранении сообщения пользователя: {response.status_code}, {response.text}")
            await message.answer("Ошибка при обработке сообщения. Пожалуйста, попробуйте позже.")
            return
        
        # 2. Отправляем запрос к AI для получения ответа
        ai_response = requests.get(
            f"http://localhost:7777/query?query={requests.utils.quote(user_message)}",
            headers=headers
        )
        
        if ai_response.status_code != 200:
            logger.error(f"Ошибка при запросе к AI: {ai_response.status_code}, {ai_response.text}")
            await message.answer("Не удалось получить ответ от AI. Пожалуйста, попробуйте позже.")
            return
        
        # Извлекаем ответ от AI
        ai_data = ai_response.json()
        ai_answer = ai_data.get("answer", "Не удалось получить ответ")
        needs_operator = ai_data.get("needs_operator", False)
        
        # 3. Сохраняем ответ бота в истории чата
        bot_message_data = {
            "user_id": user_id,
            "chat_id": chat_id,
            "message": ai_answer,
            "is_bot": True
        }
        
        bot_response = requests.post(
            f"{API_URL}/api/chat-history",
            json=bot_message_data,
            headers=headers
        )
        
        if bot_response.status_code != 200:
            logger.error(f"Ошибка при сохранении ответа бота: {bot_response.status_code}, {bot_response.text}")
        
        # 4. Отправляем ответ пользователю
        await message.answer(ai_answer)
        
        # 5. Если нужна помощь оператора, отправляем запрос на соединение
        if needs_operator:
            try:
                operator_request = requests.post(
                    f"{API_URL}/api/call-operator",
                    json={"chat_id": chat_id},
                    headers=headers
                )
                
                if operator_request.status_code == 200:
                    await message.answer("Я вижу, что ваш вопрос требует помощи оператора. Запрос оператору уже отправлен, вам ответят в ближайшее время.")
                else:
                    logger.error(f"Ошибка при вызове оператора: {operator_request.status_code}, {operator_request.text}")
            except Exception as e:
                logger.error(f"Ошибка при вызове оператора: {e}")
    
    except Exception as e:
        logger.error(f"Ошибка при обработке сообщения в чате: {e}")
        await message.answer("Произошла ошибка при обработке вашего сообщения. Пожалуйста, попробуйте позже.")

# Обработчик для отмены текущего состояния
@dp.message(F.text.lower().in_(["отмена", "отменить"]), StateFilter(None, RegisterStates, LoginStates, ChatStates))
async def cancel_handler(message: types.Message, state: FSMContext):
    """
    Обработчик для отмены текущего состояния по команде "отмена"
    """
    current_state = await state.get_state()
    if current_state is None:
        return
    
    await state.clear()
    await message.answer("Действие отменено.")

async def set_commands(bot: Bot):
    """
    Устанавливает команды бота в меню
    """
    await bot.set_my_commands(commands, scope=BotCommandScopeDefault())
    logger.info("Команды бота установлены")

async def main():
    """
    Основная функция для запуска бота
    """
    try:
        # Инициализация базы данных
        Base.metadata.create_all(bind=engine)
        logger.info("База данных инициализирована")
        
        # Установка команд бота
        await set_commands(bot)
        
        # Запуск бота
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Возникла ошибка при запуске бота: {e}")
    finally:
        await bot.session.close()
        await storage.close()

if __name__ == "__main__":
    print('Запуск бота...')
    asyncio.run(main()) 
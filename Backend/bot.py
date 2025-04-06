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

bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Список команд для меню бота
commands = [
    BotCommand(command="start", description="Начать работу с ботом"),
    BotCommand(command="help", description="Показать справку"),
    BotCommand(command="register", description="Зарегистрироваться в системе"),
    BotCommand(command="login", description="Войти в систему")
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
    
    await state.clear()

@dp.message(F.text.lower().in_(["отмена", "отменить"]), StateFilter(None, RegisterStates, LoginStates))
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
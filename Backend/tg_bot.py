import telebot
from dotenv import load_dotenv
import os

load_dotenv()


token = os.environ.get('TOKEN')

bot=telebot.TeleBot(token)

def start_message(message):
  bot.send_message(message.chat.id,"Привет, я бота созданный командой «MISIS x OptonGroup» для TenderHAck✌️ ")
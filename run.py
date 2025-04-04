import telebot
from Handlers import register_all_handlers
from Database import Database
import logging



db = Database()
bot = telebot.TeleBot("")
register_all_handlers(bot)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, filename="bot_logs.log", filemode="a", encoding="utf-8")
    bot.polling()

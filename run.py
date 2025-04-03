import telebot
from Handlers import register_all_handlers
from Database import Database


db = Database()
bot = telebot.TeleBot("6811215765:AAGri2LdNJ2LTH1uyLcaRm_F1Z1HukHnATo")
register_all_handlers(bot)

if __name__ == '__main__':
    bot.polling()

from Markups import Markup


def tenant_menu(bot, message):
    # check existing in db


    markup = Markup.tenant_markup()
    bot.send_message(message.chat.id, "tmp", reply_markup=markup)


def register_tenant_handlers(bot):
    (bot.message_handler(commands=['tenant_menu'], bot=bot)
     (lambda message: tenant_menu(bot, message)))



from Database import Database
from Entities import Ad
from Handlers.tenant import tenant_menu
from Markups import Markup


db = Database()
user_data = {}


def landlord_menu(bot, message):
    ad = db.get_ad(message.chat.id)

    text = 'У вас пока нет объявлений.'
    if ad is not None:
        text = (f'У вас уже есть одно объявление:\n\n'
                f'|{ad.district} | {ad.price} р. | {ad.address} |\n\n'
                f'Чтобы создать больше объявлений оформите платную подписку.')

    markup = Markup.landlord_markup()
    bot.send_message(message.chat.id, text, reply_markup=markup)


def district_choice(bot, callback):
    ad = db.get_ad(callback.message.chat.id)

    if ad is not None:
        markup = Markup.go_home_markup()
        bot.send_message(callback.message.chat.id,
                         "У вас уже есть одно объявление.\n"
                         "Удалите старое или оформите платную подписку.",
                         reply_markup=markup)
    else:
        markup = Markup.district_markup()
        bot.send_message(callback.message.chat.id,
                         'Выберите район в котором хотите сдавать квартиру:',
                         reply_markup=markup)

def price_choice(bot, callback):
    def save_price(message):
        try:
            price = int(message.text)  # Пытаемся преобразовать в число
            user_data[message.chat.id]['price'] = price  # Сохраняем в словарь
            address_choice(bot, message)
        except ValueError:  # Если введено не число
            bot.send_message(message.chat.id, "Это не число! Попробуйте снова.")
            price_choice(bot, callback)  # Запрашиваем повторный ввод

    user_data[callback.message.chat.id] = {'district': callback.data}
    bot.send_message(callback.message.chat.id, "Введите цену аренды (только цифры):")
    bot.register_next_step_handler(callback.message, save_price)


def address_choice(bot, message):
    def save_address(message):
        user_id = message.chat.id

        ad = Ad(user_id,
                user_data[user_id]['district'],
                user_data[user_id]['price'],
                message.text)

        db.add_ad(ad)
        bot.send_message(message.chat.id, "Вы успешно создали объявление!")
        landlord_menu(bot, message)

    bot.send_message(message.chat.id, 'Укажите точный адрес жилья:')
    bot.register_next_step_handler(message, save_address)

def go_home(bot, callback):
    landlord_menu(bot, callback.message)


def delete_ad(bot, callback):
    db.delete_ad(callback.message.chat.id)

    bot.send_message(callback.message.chat.id, 'Объявление удалено.')
    landlord_menu(bot, callback.message)


def go_tenant(bot, callback):
    tenant_menu(bot, callback.message)


def register_landlord_handlers(bot):
    (bot.message_handler(commands=['landlord_menu'], bot=bot)
     (lambda message: landlord_menu(bot, message)))

    (bot.callback_query_handler(lambda clb: clb.data == 'ad_create')
     (lambda message: district_choice(bot, message)))

    (bot.callback_query_handler(lambda clb: clb.data in Ad.ALL_DISTRICTS)
     (lambda message: price_choice(bot, message)))

    (bot.callback_query_handler(lambda clb: clb.data == 'go_home')
     (lambda message: go_home(bot, message)))

    (bot.callback_query_handler(lambda clb: clb.data == 'delete_ad')
     (lambda message: delete_ad(bot, message)))

    (bot.callback_query_handler(lambda clb: clb.data == 'change_role')
     (lambda message: go_tenant(bot, message)))

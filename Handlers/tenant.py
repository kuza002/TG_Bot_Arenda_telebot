import Entities
from Database import Database
import Handlers
from Markups import Markup


users_data = {}
db = Database()

def tenant_menu(bot, message):
    user_id = message.chat.id
    filter = db.get_filter(user_id)

    text = "У вас пока что не настроен фильтр для поиска жилья."
    if filter is not None:
        text = (f"У Вас есть настроенный фильтр\n"
                f"| {", ".join(filter.districts)} | от. {filter.min_price}р. |  до. {filter.max_price}р. |")

    markup = Markup.tenant_markup()
    bot.send_message(user_id, text, reply_markup=markup)


def create_filter(bot, callback):
    user_id = callback.message.chat.id

    db.delete_filter(user_id)

    if user_id not in users_data:
        users_data[user_id] = {'selected_districts': []}

    bot.send_message(
        user_id,
        "🔹 Выберите районы (можно несколько):",
        reply_markup=Markup.district_checkbox_markup(users_data[user_id], user_id)
    )


def checkbox_district_process(bot, callback):
    user_id = callback.message.chat.id
    callback_data = callback.data.split('_')[1]
    if callback_data == "done":
        selected = users_data[user_id]['selected_districts']
        if not selected:
            bot.answer_callback_query(callback.id, "❌ Вы не выбрали ни одного района!")
        else:
            bot.edit_message_text(
                f"✔️ Выбрано: {', '.join(selected)}",
                user_id,
                callback.message.message_id
            )
            ask_min_price(bot, callback.message)
        return

    # Обработка выбора района
    district = callback.data.split('_')[1]

    if user_id not in users_data:
        users_data[user_id] = []

    if district in users_data[user_id]['selected_districts']:
        users_data[user_id]['selected_districts'].remove(district)
    else:
        users_data[user_id]['selected_districts'].append(district)

    # Обновляем сообщение с новыми отметками
    bot.edit_message_text(
        "🔹 Выберите районы (можно несколько):",
        user_id,
        callback.message.message_id,
        reply_markup=Markup.district_checkbox_markup(users_data[user_id], user_id)
    )


def ask_min_price(bot, message):
    def save_min_price(message):
        users_data[message.chat.id]['min_price'] = message.text
        ask_max_price(bot, message)

    bot.send_message(message.chat.id, 'Введите минимальную сумму для арендной платы:')
    bot.register_next_step_handler(message, save_min_price)


def ask_max_price(bot, message):
    def save_min_price(message):
        users_data[message.chat.id]['max_price'] = message.text
        filter = Entities.Filter(message.chat.id,
                                 users_data[message.chat.id]['selected_districts'],
                                 users_data[message.chat.id]['min_price'],
                                 users_data[message.chat.id]['max_price'])

        db.add_filter(filter)
        bot.send_message(message.chat.id, "Фильтр успешно сохранен")
        tenant_menu(bot, message)

    bot.send_message(message.chat.id, 'Введите максимальную сумму для арендной платы:')
    bot.register_next_step_handler(message, save_min_price)


def find_by_filter(bot, callback):
    bot.send_message(callback.message.chat.id, "tmp")
    filter = db.get_filter(callback.message.chat.id)
    ads = db.find_ads_by_filter(filter)

    if filter is None:
        bot.send_message("Не найдено жилья соответствующего вашим настройкам")

    text = '|             Район            |   Цена   |             Адрес             |'
    for ad in ads:
        text += f'\n| {ad.district} | {ad.price} | {ad.address}'

    bot.send_message(callback.message.chat.id, text)


def go_landlord(bot, callback):
    user = db.get_user(callback.message.chat.id)
    db.delete_user(user.id)

    user.role = 'landlord'
    db.add_user(user)

    Handlers.landlord.landlord_menu(bot, callback.message)


def register_tenant_handlers(bot):
    (bot.message_handler(commands=['tenant_menu'], bot=bot)
     (lambda message: tenant_menu(bot, message)))
    (bot.callback_query_handler(lambda clb: clb.data == 'create_filter')
     (lambda message: create_filter(bot, message)))

    (bot.callback_query_handler(lambda clb: clb.data.startswith("checkbox_"))
     (lambda message: checkbox_district_process(bot, message)))

    (bot.callback_query_handler(lambda clb: clb.data == 'go_landlord')
     (lambda message: go_landlord(bot, message)))

    (bot.callback_query_handler(lambda clb: clb.data == "find_by_filter")
     (lambda message: find_by_filter(bot, message)))

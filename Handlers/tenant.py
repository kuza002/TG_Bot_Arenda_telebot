import logging

import Entities
from Database import Database
import Handlers
from Entities import Ad
from Markups import Markup
from utils import edit_or_send_message, log_event

users_data = {}
db = Database()


def tenant_menu(bot, message):
    log_event('Entered to tenant_menu', message)

    user_id = message.chat.id
    filter = db.get_filter(user_id)

    if filter is None:
        text = """
🔍 *Фильтр не настроен*

У вас пока нет сохраненных параметров поиска.
Нажмите "⚙️ Настроить фильтр поиска" чтобы начать поиск идеального жилья!
"""
    else:
        text = f"""
⚙️ *Ваши текущие настройки поиска*

🏙 *Районы:* {", ".join(filter.districts)}
💰 *Диапазон цен:* {filter.min_price} - {filter.max_price} ₽/мес

Используйте кнопку "🔍 Найти жильё" для поиска по вашим критериям.
"""

    markup = Markup.tenant_markup()
    edit_or_send_message(bot, message, text, markup, parse_mode='Markdown')


def create_filter(bot, callback):
    log_event('Entered to create_filter', callback)
    user_id = callback.message.chat.id
    db.delete_filter(user_id)

    if user_id not in users_data:
        users_data[user_id] = {'selected_districts': []}

    text = """
📍 *Выбор районов*

Отметьте нужные районы (можно несколько):
✅ - выбранный район
🔘 - доступный для выбора

Нажмите "🚀 Готово" для продолжения.
"""
    edit_or_send_message(
        bot,
        callback.message,
        text,
        Markup.district_checkbox_markup(users_data[user_id], user_id),
        parse_mode='Markdown'
    )


def checkbox_district_process(bot, callback):
    log_event('Entered to tenant_menu', callback)
    user_id = callback.message.chat.id
    callback_data = callback.data.split('_')[1]

    if callback_data == "done":
        selected = users_data[user_id]['selected_districts']
        if not selected:
            bot.answer_callback_query(callback.id, "⚠️ Пожалуйста, выберите хотя бы один район!")
        else:
            text = f"""
✅ *Выбранные районы:*
{", ".join(selected)}

Теперь укажите желаемый ценовой диапазон.
"""
            edit_or_send_message(bot, callback.message, text, parse_mode='Markdown')
            ask_min_price(bot, callback.message)
        return

    district = callback.data.split('_')[1]

    if district in users_data[user_id]['selected_districts']:
        users_data[user_id]['selected_districts'].remove(district)
    else:
        users_data[user_id]['selected_districts'].append(district)

    edit_or_send_message(
        bot,
        callback.message,
        "📍 Выберите районы (можно несколько):",
        Markup.district_checkbox_markup(users_data[user_id], user_id),
        parse_mode='Markdown'
    )


def ask_min_price(bot, message):
    log_event('Entered to tenant_menu', message)
    def save_min_price(msg):
        try:
            price = int(msg.text)
            if price <= 0:
                raise ValueError
            users_data[msg.chat.id]['min_price'] = price
            ask_max_price(bot, msg)
        except ValueError:
            error_text = """
❌ *Некорректная сумма*

Пожалуйста, введите минимальную цену:
• Только цифры
• Больше 0
Пример: *30000*
"""
            edit_or_send_message(bot, msg, error_text, parse_mode='Markdown')
            bot.register_next_step_handler(msg, save_min_price)

    text = """
💰 *Минимальная цена*

Введите минимальную сумму аренды в рублях:
Пример: *30000*
"""
    edit_or_send_message(bot, message, text, parse_mode='Markdown')
    bot.register_next_step_handler(message, save_min_price)


def ask_max_price(bot, message):
    log_event('Entered to ask_max_price', message)
    def save_max_price(msg):
        try:
            max_price = int(msg.text)
            min_price = users_data[msg.chat.id]['min_price']

            if max_price <= min_price:
                error_text = f"""
⚠️ *Максимальная цена должна быть больше {min_price}₽*

Попробуйте ввести сумму больше минимальной:
"""
                edit_or_send_message(bot, msg, error_text, parse_mode='Markdown')
                bot.register_next_step_handler(msg, save_max_price)
                return

            users_data[msg.chat.id]['max_price'] = max_price
            save_filter(bot, msg)
        except ValueError:
            error_text = """
❌ *Некорректная сумма*
Пожалуйста, введите максимальную цену:
• Только цифры
• Больше минимальной
Пример: 60000
"""
            edit_or_send_message(bot, msg, error_text, parse_mode='Markdown')
            bot.register_next_step_handler(msg, save_max_price)

    text = f"""
💰 * Максимальная цена *

Текущая минимальная цена: *{users_data[message.chat.id]['min_price']}₽ *
Введите максимальную сумму аренды.
Пример: *60000*
"""
    edit_or_send_message(bot, message, text, parse_mode='Markdown')
    bot.register_next_step_handler(message, save_max_price)

def save_filter(bot, message):
    log_event('Entered to save_filter', message)
    user_id = message.chat.id
    filter_data = users_data[user_id]

    filter = Entities.Filter(
        user_id,
        filter_data['selected_districts'],
        filter_data['min_price'],
        filter_data['max_price']
    )

    db.add_filter(filter)

    success_text = f"""
🎉 * Фильтр успешно сохранен! *

Теперь вы можете искать жильё по параметрам:
🏙 *Районы: *{", ".join(filter.districts)}
💰 *Цена: *{filter.min_price} - {filter.max_price} ₽ / мес

Нажмите
"🔍 Найти жильё по фильтру" для просмотра вариантов.
"""
    edit_or_send_message(bot, message, success_text, parse_mode='Markdown')
    tenant_menu(bot, message)

def find_by_filter(bot, callback):
    log_event('Entered to find_by_filter', callback)
    filter = db.get_filter(callback.message.chat.id)
    if filter is None:
        filter = Entities.Filter(callback.message.chat.id, Ad.ALL_DISTRICTS, 0, 1000000000)
    ads = db.find_ads_by_filter(filter)

    if not ads:
        text = """
🔎 *Подходящих вариантов не найдено *

Попробуйте:
• Расширить ценовой диапазон
• Добавить больше районов
• Изменить параметры поиска
"""
    else:
        text = """
🏠 Найденные варианты жилья:
"""
        for i, ad in enumerate(ads, 1):
            text += f"""
{i}. * {ad.district}
район *
💵 *Цена: *{ad.price} ₽ / мес
📍 *Адрес: *{ad.address}
——————————————
"""

    markup = Markup.go_home_markup()
    edit_or_send_message(bot, callback.message, text, markup, parse_mode='Markdown')

def go_landlord(bot, callback):
    log_event('Entered to go_landlord', callback)
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
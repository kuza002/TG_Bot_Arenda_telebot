from Database import Database
from Entities import Ad
import Handlers
from Markups import Markup
from utils import edit_or_send_message, log_event

db = Database()
user_data = {}


def landlord_menu(bot, message):
    log_event('Entered to landlord_menu', message)
    user_id = message.chat.id
    ad = db.get_ad(user_id)

    if ad is None:
        text = """
📭 *У вас пока нет объявлений*

Создайте первое объявление и начните получать предложения от арендаторов!
"""
    else:
        text = f"""
🏠 *Ваше текущее объявление:*

📍 Район: *{ad.district}*
💵 Цена: *{ad.price} ₽/мес*
🏡 Адрес: *{ad.address}*

✨ Для создания дополнительных объявлений оформите *Премиум подписку*
"""

    markup = Markup.landlord_markup()
    edit_or_send_message(bot, message, text, markup, parse_mode='Markdown')


def district_choice(bot, callback):
    log_event('Entered to district_choice', callback)
    ad = db.get_ad(callback.message.chat.id)

    if ad is not None:
        text = """
⚠️ *Лимит объявлений исчерпан*

У вас уже есть активное объявление:
1. Удалите текущее объявление
2. Оформите *Премиум подписку* для добавления новых
"""
        markup = Markup.go_home_markup()
        edit_or_send_message(bot, callback.message, text, markup, parse_mode='Markdown')
    else:
        text = """
🏙 *Выберите район*

Укажите район, где находится ваша квартира:
"""
        markup = Markup.district_markup()
        edit_or_send_message(bot, callback.message, text, markup, parse_mode='Markdown')


def price_choice(bot, callback):
    log_event('Entered to price_choice', callback)
    def save_price(message):
        try:
            price = int(message.text)
            if price <= 0:
                raise ValueError

            user_data[message.chat.id] = {
                'district': callback.data,
                'price': price
            }
            address_choice(bot, message)
        except ValueError:
            error_text = """
❌ *Некорректная сумма*

Пожалуйста, введите корректную цену аренды (только цифры):
Пример: *35000*
"""
            edit_or_send_message(bot, message, error_text, parse_mode='Markdown')
            bot.register_next_step_handler(message, save_price)

    text = """
💵 *Укажите стоимость аренды*

Введите месячную стоимость аренды (только цифры):
Пример: *35000*
"""
    user_data[callback.message.chat.id] = {'district': callback.data}
    edit_or_send_message(bot, callback.message, text, parse_mode='Markdown')
    bot.register_next_step_handler(callback.message, save_price)


def address_choice(bot, message):
    log_event('Entered to address_choice', message)
    def save_address(message):
        user_id = message.chat.id
        ad_data = user_data[user_id]

        ad = Ad(
            user_id,
            ad_data['district'],
            ad_data['price'],
            message.text
        )

        db.add_ad(ad)

        success_text = f"""
🎉 *Объявление создано!*

Теперь ваша квартира в районе *{ad.district}* 
по цене *{ad.price} ₽/мес* будет видна арендаторам.
"""
        edit_or_send_message(bot, message, success_text, parse_mode='Markdown')
        landlord_menu(bot, message)

    text = """
🏡 *Укажите точный адрес*

Напишите полный адрес квартиры (улица, дом, квартира):
Пример: *ул. Примерная, д. 10, кв. 25*
"""
    edit_or_send_message(bot, message, text, parse_mode='Markdown')
    bot.register_next_step_handler(message, save_address)


def delete_ad(bot, callback):
    log_event('Entered to delete_ad', callback)
    db.delete_ad(callback.message.chat.id)

    text = """
🗑 *Объявление удалено*

Вы можете создать новое объявление когда захотите.
"""
    edit_or_send_message(bot, callback.message, text, parse_mode='Markdown')
    landlord_menu(bot, callback.message)


def go_tenant(bot, callback):
    log_event('Entered to go_tenant', callback)
    user = db.get_user(callback.message.chat.id)
    db.delete_user(user.id)

    user.role = 'tenant'
    db.add_user(user)

    Handlers.tenant.tenant_menu(bot, callback.message)


def register_landlord_handlers(bot):
    (bot.message_handler(commands=['landlord_menu'], bot=bot)
     (lambda message: landlord_menu(bot, message)))

    (bot.callback_query_handler(lambda clb: clb.data == 'ad_create')
     (lambda message: district_choice(bot, message)))

    (bot.callback_query_handler(lambda clb: clb.data in Ad.ALL_DISTRICTS)
     (lambda message: price_choice(bot, message)))

    (bot.callback_query_handler(lambda clb: clb.data == 'delete_ad')
     (lambda message: delete_ad(bot, message)))

    (bot.callback_query_handler(lambda clb: clb.data == 'go_tenant')
     (lambda message: go_tenant(bot, message)))
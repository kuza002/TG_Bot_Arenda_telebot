from telebot import types
from Database import Database
import Entities
from Handlers.landlord import landlord_menu
from Handlers.tenant import tenant_menu
from Markups import Markup
from utils import edit_or_send_message

db = Database()

def handle_start(bot, message):
    user = db.get_user(message.chat.id)

    if user is None:
        markup = Markup.role_markup()
        welcome_text = """
🌟 *Добро пожаловать в RentMaster!* 🌟

Я помогу вам:
• 🏠 *Сдать* квартиру быстро и безопасно
• 🔍 *Найти* идеальное жильё по вашим критериям

Вы у нас впервые? Выберите свою роль:
        """
        bot.send_message(message.chat.id,
                         welcome_text,
                         parse_mode='Markdown',
                         reply_markup=markup)
    else:
        if user.role == 'landlord':
            landlord_menu(bot, message)
        elif user.role == 'tenant':
            tenant_menu(bot, message)

def register_user(bot, callback):
    role = callback.data.split('_')[1]
    user = Entities.User.from_callback(callback, role)
    db.add_user(user)


    handle_start(bot, callback.message)

def sub(bot, callback):
    sub_step = callback.data.split('_')[1]
    back = 'go_home'
    markup = None

    if sub_step == 'price':
        text = """
💎 *Премиум подписка* 💎

Преимущества подписки:
• 🔥 Горячие предложения на 24 часа раньше
• 👑 Выделенные объявления в поиске
• 🛡️ Гарантия безопасности сделки

*Условия:*
Нажимая кнопку "Далее ▶️", вы соглашаетесь с условиями оплаты в размере одного миллиона рублей.
        """
        next = "sub_organs"

    elif sub_step == 'organs':
        text = """

Премиум подписка включает:
• 📅 30 дней premium-доступа
• 🔔 Персональные уведомления
• 💬 Приоритетная поддержка

🫀 *Дополнительные условия*
Все парные органы будут переданы в исследовательский центр "И так сойдёт".

Нажмите "Далее ▶️" чтобы продолжить
        """
        next = "sub_work"

    elif sub_step == 'work':
        text = """
👨‍💻 *Последний шаг!*

Специальные условия для:
• 🏢 Компаний
• 🤝 Партнеров
• 👥 Риелторов

** Дополнительные условия **

Помимо всего вышеперечисленного Вы так же обязуетесь взять автора данного бота в свою команду.

Нажмите "Далее ▶️" для деталей
        """
        next = "sub_job"
        back = 'sub_rely'

    elif sub_step == 'job':
        text = """
✨ *Спасибо за интерес!* ✨

Наш менеджер свяжется с вами для:
• 🎁 Персонального предложения
• ❓ Ответов на вопросы
• 💼 Обсуждения сотрудничества

Ждем вас среди премиум-пользователей!
        """
        markup = Markup.go_home_markup()
    elif sub_step == 'rely':
        text = """
Согласны, с последнее было уже чересчур, нужно было подсекать раньше 😔
        """
        markup = Markup.go_home_markup()

    if markup is None:
        markup = Markup.next_or_back(next, back)

    edit_or_send_message(bot, callback.message, text, markup)

def go_home(bot, callback):
    handle_start(bot, callback.message)

def register_common_handlers(bot):
    bot.message_handler(commands=['start'])(lambda msg: handle_start(bot, msg))
    (bot.callback_query_handler(func=lambda callback: callback.data.startswith('role'))
     (lambda call: register_user(bot, call)))
    (bot.callback_query_handler(func=lambda callback: callback.data.startswith('sub'))
     (lambda call: sub(bot, call)))
    (bot.callback_query_handler(lambda clb: clb.data == 'go_home')
     (lambda message: go_home(bot, message)))

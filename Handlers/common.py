from telebot import types

from Database import Database
import Entities
from Handlers.landlord import landlord_menu
from Handlers.tenant import tenant_menu
from Markups import Markup

db = Database()


def handle_start(bot, message):
    # Приветственное сообщение

    user = db.get_user(message.chat.id)

    if user is None:
        markup = Markup.role_markup()

        bot.send_message(message.chat.id,
                     "Привет! Кажется, Вы у нас впервые? "
                     "Хотите сдать или найти квартиру?",
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

    bot.send_message(callback.message.chat.id, f"Вы успешно зарегистрированы!")

    handle_start(bot, callback.message)

### Долгая подписка ###

def sub(bot, callback):
    print(callback.data)
    sub_step = callback.data.split('_')[1]
    back = 'go_home'
    markup = None

    if sub_step == 'price':
        text = ('Нажимая кнопку "Далее" вы соглашаетесь на перевод на счет '
                'разработчика суммы в размере 3 миллиардов рублей')
        next = "sub_organs"

    elif sub_step == 'organs':
        text = ('Нажимая кнопку "Далее" вы также соглашаетесь на передачу части '
                'органов в научно исследовательский центр "И так сойдёт!"')
        next = "sub_work"

    elif sub_step == 'work':
        text = ('Помимо всего вышеперечисленного, при нажатии на кнопку '
                '"Далее", Вы так же обязуетесь взять разработчика данного бота'
                'в свою команду.')
        next = "sub_job"
        back = 'sub_rely'

    elif sub_step == 'job' or sub_step == 'rely':
        markup = Markup.go_home_markup()
        if sub_step == 'job':
            text = ("Мы провели перерасчет и поняли что последнего пункта будет "
                     "вполне достаточно. Свяжитесь с разработчиком для получения "
                     "подписки.")
        else:
            text = ("Согласны, с последним перебор, пожалуй.")

    if markup is None:
        markup = Markup.next_or_back(next, back)

    bot.send_message(callback.message.chat.id, text, reply_markup=markup)


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

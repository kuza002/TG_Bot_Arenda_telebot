from telebot import types

import Entities


class Markup:

    @staticmethod
    def role_markup():
        markup = types.InlineKeyboardMarkup()
        landlord_btn = types.InlineKeyboardButton('Сдать квартиру 😈', callback_data='role_landlord')
        tenant_btn = types.InlineKeyboardButton('Снять квартиру 😢', callback_data='role_tenant')
        markup.row(landlord_btn)
        markup.row(tenant_btn)

        return markup

    @staticmethod
    def landlord_markup():
        markup = types.InlineKeyboardMarkup()
        create_btn = types.InlineKeyboardButton("Создать объявление",
                                                callback_data='ad_create')
        del_btn = types.InlineKeyboardButton("Удалить объявление",
                                             callback_data='delete_ad')
        change_role_btn = types.InlineKeyboardButton("Сменить роль",
                                                 callback_data='go_tenant')
        sub_btn = types.InlineKeyboardButton('Подписка', callback_data='sub_price')

        markup.row(create_btn)
        markup.row(del_btn)
        markup.row(change_role_btn, sub_btn)

        return markup

    @staticmethod
    def district_markup():
        markup = types.InlineKeyboardMarkup()

        districts = Entities.Ad.ALL_DISTRICTS
        btn_row = []
        for district in districts:
            btn_district = types.InlineKeyboardButton(district, callback_data=district)
            btn_row.append(btn_district)
            if len(btn_row) == 2:
                markup.row(*btn_row)
                btn_row = []

        return markup


    @staticmethod
    def go_home_markup(callback='go_home'):
        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton('Назад', callback_data=callback))

        return markup

    @staticmethod
    def next_or_back(next_callback, back_callback):
        markup = Markup.go_home_markup(back_callback)
        markup.add(
            types.InlineKeyboardButton('Далее', callback_data=next_callback))

        return markup

    @staticmethod
    def tenant_markup():
        markup = types.InlineKeyboardMarkup()
        find_btn = types.InlineKeyboardButton('Найти жильё',
                                              callback_data='find_by_filter')
        filter_btn = types.InlineKeyboardButton("Изменить фильтр",
                                                callback_data='create_filter')
        change_role_btn = types.InlineKeyboardButton("Сменить роль",
                                                     callback_data='go_landlord')
        sub_btn = types.InlineKeyboardButton('Подписка',
                                             callback_data='sub_price')

        markup.row(find_btn)
        markup.row(filter_btn)
        markup.row(change_role_btn, sub_btn)

        return markup

    @staticmethod
    def district_checkbox_markup(user_data, user_id):
        keyboard = types.InlineKeyboardMarkup()
        button_row = []
        for district in Entities.Ad.ALL_DISTRICTS:
            # Если район уже выбран, добавляем галочку
            if district in user_data['selected_districts']:
                button_text = f"✅ {district}"
            else:
                button_text = district

            btn = types.InlineKeyboardButton(button_text,
                                             callback_data=f"checkbox_{district}")
            button_row.append(btn)

            if len(button_row) == 2:
                keyboard.row(*button_row)
                button_row = []

        # Кнопка "Готово" для завершения выбора
        keyboard.add(types.InlineKeyboardButton("🚀 Готово", callback_data="checkbox_done"))

        return keyboard

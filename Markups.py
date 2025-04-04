from telebot import types
import Entities


class Markup:

    @staticmethod
    def role_markup():
        markup = types.InlineKeyboardMarkup()
        landlord_btn = types.InlineKeyboardButton('🏠 Сдать квартиру (Арендодатель)',
                                                  callback_data='role_landlord')
        tenant_btn = types.InlineKeyboardButton('🔍 Снять квартиру (Арендатор)',
                                                callback_data='role_tenant')
        markup.row(landlord_btn)
        markup.row(tenant_btn)
        return markup

    @staticmethod
    def landlord_markup():
        markup = types.InlineKeyboardMarkup()
        create_btn = types.InlineKeyboardButton("📝 Создать объявление",
                                                callback_data='ad_create')
        del_btn = types.InlineKeyboardButton("🗑️ Удалить объявление",
                                             callback_data='delete_ad')
        change_role_btn = types.InlineKeyboardButton("🔄 Сменить на арендатора",
                                                     callback_data='go_tenant')
        sub_btn = types.InlineKeyboardButton('💎 Премиум подписка',
                                             callback_data='sub_price')

        markup.row(create_btn)
        markup.row(del_btn)
        markup.row(change_role_btn, sub_btn)
        return markup

    @staticmethod
    def district_markup():
        markup = types.InlineKeyboardMarkup()
        districts = Entities.Ad.ALL_DISTRICTS

        for i in range(0, len(districts), 2):
            row = []
            for district in districts[i:i + 2]:
                emoji = '🏙️' if 'центр' in district.lower() else '🌆'
                btn = types.InlineKeyboardButton(
                    f"{emoji} {district}",
                    callback_data=district
                )
                row.append(btn)
            markup.row(*row)

        return markup

    @staticmethod
    def go_home_markup(callback='go_home'):
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('↩️ Назад', callback_data=callback))
        return markup

    @staticmethod
    def next_or_back(next_callback, back_callback):
        markup = types.InlineKeyboardMarkup()
        markup.row(
            types.InlineKeyboardButton('◀️ Назад', callback_data=back_callback),
            types.InlineKeyboardButton('Далее ▶️', callback_data=next_callback)
        )
        return markup

    @staticmethod
    def tenant_markup():
        markup = types.InlineKeyboardMarkup()
        markup.row(
            types.InlineKeyboardButton('🔍 Найти жильё по фильтру',
                                       callback_data='find_by_filter')
        )
        markup.row(
            types.InlineKeyboardButton('⚙️ Настроить фильтр поиска',
                                       callback_data='create_filter')
        )
        markup.row(
            types.InlineKeyboardButton('🔄 Стать арендодателем',
                                       callback_data='go_landlord'),
            types.InlineKeyboardButton('💎 Премиум',
                                       callback_data='sub_price')
        )
        return markup

    @staticmethod
    def district_checkbox_markup(user_data, user_id):
        keyboard = types.InlineKeyboardMarkup()
        districts = Entities.Ad.ALL_DISTRICTS

        for i in range(0, len(districts), 2):
            row = []
            for district in districts[i:i + 2]:
                emoji = '✅' if district in user_data['selected_districts'] else '🔘'
                btn = types.InlineKeyboardButton(
                    f"{emoji} {district}",
                    callback_data=f"checkbox_{district}"
                )
                row.append(btn)
            keyboard.row(*row)

        keyboard.row(
            types.InlineKeyboardButton('🚀 Готово', callback_data="checkbox_done")
        )
        return keyboard
def edit_or_send_message(bot, message, text, markup=None, parse_mode=None):
    user_id = message.chat.id
    try:
        # Пытаемся изменить существующее сообщение
        bot.edit_message_text(
            chat_id=user_id,
            message_id=message.message_id,
            text=text,
            reply_markup=markup
        )
    except Exception as e:
        # Если не получится изменить (например, сообщение слишком старое)
        bot.send_message(user_id, text, reply_markup=markup, parse_mode=parse_mode)
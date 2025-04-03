import telebot
from telebot.types import Message


class User:
    def __init__(self,user_id, name, role):
        user_id = str(user_id)
        self.name = name
        self.id = user_id
        self.role = role

    @staticmethod
    def from_callback(callback, role):

        user_id = callback.from_user.id
        name = f'{callback.from_user.first_name} {callback.from_user.last_name}'
        user = User(user_id, name, role)
        return user

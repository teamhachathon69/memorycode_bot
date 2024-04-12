import telebot
from telebot import types
from dotenv import load_dotenv
from typing import List, Dict
from os import environ

load_dotenv()

YANDEX_API_TOKEN = environ.get("yandex_api_token")
YANDEX_FOLDER_ID = environ.get("yandex_folder_id")
BOT_TOKEN = environ.get("bot_token")

bot = telebot.TeleBot(BOT_TOKEN)
questions = [('Каким человеком был этот человек?', None), ('Чему он посвятил свою жизнь?', None), ('Какие качества были ему присущи?', None), ('За что его будут помнить?', None), ('Что он оставил после себя?', None),
             ('В чём он видел смысл жизни?', None), ('Как он относился к людям?', None), ('Чем он дорожил больше всего?', None), ('Что было для него самым важным?', None), ('Какие достижения этого человека вы бы отметили?', None)]
answers: Dict[int, List[str]] = {}
pagination: Dict[int, int] = {}


def get_keyboard() -> types.InlineKeyboardMarkup:
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(
        types.InlineKeyboardButton("◀️", callback_data="issues:back"),
        types.InlineKeyboardButton("🔁", callback_data="issues:regenerate"),
        types.InlineKeyboardButton("▶️", callback_data="issues:next")
    )
    keyboard.add(types.InlineKeyboardButton("⏹️", callback_data="issues:stop"))
    return keyboard


def handle_que(message: types.Message, only_edited: bool = False) -> None:
    if pagination[message.chat.id] >= len(questions):
        handle_general_answer(message)
        return
    text = answers[message.chat.id][pagination[message.chat.id]][0]
    if current_answer := answers[message.chat.id][pagination[message.chat.id]][1]:
        text += f"\nТекущий ответ: {current_answer}"
    bot.edit_message_text(text,
                          message.chat.id, message.id, reply_markup=get_keyboard())
    if not only_edited:
        bot.register_next_step_handler_by_chat_id(
            message.chat.id, answer_question(message))


def handle_general_answer(message: types.Message):
    bot.edit_message_text("Спасибо за участие!",
                          message.chat.id, message.id)


@bot.message_handler(commands=['start'])
def command_start(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.KeyboardButton(text="Приступем"))
    bot.reply_to(
        message, "Привет! Я помогу вам создать эпитафию о человеке.", reply_markup=keyboard)


@bot.message_handler(func=lambda message: message.text == 'Приступем')
def handle_attack(message: types.Message):
    answers[message.chat.id] = questions.copy()
    pagination[message.chat.id] = 0
    message = bot.send_message(
        message.chat.id, answers[message.chat.id][pagination[message.chat.id]][0], reply_markup=get_keyboard())
    bot.register_next_step_handler_by_chat_id(
        message.chat.id, answer_question(message))


def answer_question(que_message: types.Message):
    def wrapped(message: types.Message):
        if message.text.startswith("/"):
            return
        answers[message.chat.id][pagination[message.chat.id]] = (questions[pagination[message.chat.id]][0], message.text)
        pagination[message.chat.id] += 1
        try:
            bot.delete_message(message.chat.id, message.id)
        except telebot.apihelper.ApiTelegramException:
            pass
        handle_que(que_message)
    return wrapped


@bot.callback_query_handler(lambda cb: cb.data == 'issues:back')
def handle_query_back(callback: types.CallbackQuery):
    pagination[callback.message.chat.id] -= 1
    handle_que(callback.message, only_edited=True)


@bot.callback_query_handler(lambda cb: cb.data == 'issues:next')
def handle_query_next(callback: types.CallbackQuery):
    pagination[callback.message.chat.id] += 1
    handle_que(callback.message, only_edited=True)


@bot.callback_query_handler(lambda cb: cb.data == 'issues:stop')
def handle_query_stop(callback: types.CallbackQuery):
    handle_general_answer(callback.message)


def start_bot():
    bot.polling()

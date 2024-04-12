import telebot
import requests
from telebot import types

# API от YandexGPT
API_KEY = "API"
# токен бота
TOKEN = "TOKEN"

bot = telebot.TeleBot(TOKEN)
questions = []
answers = {}

def generate_question():
    url = "https://api.ai-jobs.tech/generate_yandexgpt"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    data = {
        "prompt": "Сформулируйте вопрос, ответ на который поможет создать эпитафию о человеке.",
        "length": 150
    }

    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        return response.json()['text']
    else:
        return "Ошибка при генерации вопроса"

def generate_unique_question():
    global questions
    question = generate_question()
    while question in questions:
        question = generate_question()
    questions.append(question)
    return question

def generate_epitaph():
    epitaph = "\n".join([f"- {answers[q]}" for q in questions])
    return epitaph

@bot.message_handler(commands=['start'])
def start(message):
    global questions, answers
    questions = []
    answers = {}
    bot.reply_to(message, "Привет! Я помогу вам создать эпитафию о человеке. Давайте начнем с генерации первого вопроса.")
    ask_question(message)

def ask_question(message):
    global questions
    if len(questions) < 5:
        question = generate_unique_question()
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.add(types.KeyboardButton('Перегенерировать вопрос'))
        bot.send_message(message.chat.id, f"Вопрос: {question}", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "Уже задано максимальное количество вопросов.")

@bot.message_handler(func=lambda message: message.text == 'Перегенерировать вопрос')
def handle_regenerate(message):
    ask_question(message)

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    global questions, answers
    current_question = questions[-1]
    answers[current_question] = message.text

    if len(answers) < len(questions):
        bot.reply_to(message, "Спасибо за ответ! Отправляю следующий вопрос.")
        ask_question(message)
    else:
        epitaph = generate_epitaph()
        bot.send_message(message.chat.id, f"Эпитафия:\n{epitaph}")

bot.polling()

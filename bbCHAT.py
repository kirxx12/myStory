import requests
from bs4 import BeautifulSoup as BS
import telebot
from telebot import types
import random

SETTINGS = {
            'TOKEN': '5045841524:AAEPe3fQ7qOebErRgQlvayImGsYpkRpYNHc'
           }

URL: str = 'https://anekdotov.net/anekdot/month/'
n: list = [1, 2, 3, 4, 5, 6]


def pars_anek(URL):
    req = requests.get(URL)
    soup = BS(req.text, 'html.parser')
    anekdots = soup.find_all('div', class_='anekdot')
    clear_anekdots = [c.text for c in anekdots]
    random.shuffle(clear_anekdots)
    return clear_anekdots


list_of_jokes = pars_anek(URL)
bot = telebot.TeleBot(SETTINGS['TOKEN'])


@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Хочу анекдот")
    btn2 = types.KeyboardButton("Хочу фото!")
    markup.add(btn1, btn2)
    bot.send_message(message.chat.id,
                     'Привет, чтобы начать просто выбери опцию!',
                     reply_markup=markup)


@bot.message_handler(content_types=['text'])
def func(message):
    if message.text == 'Хочу анекдот':
        bot.send_message(message.chat.id, list_of_jokes[0])
        del list_of_jokes[0]
    elif message.text == 'Хочу фото!':
        global n
        if len(n) > 1:
            i = n[random.randint(0, len(n)) - 1]
            n.remove(i)
            img = open(f'bot-tg\photos\{i}.jpg', 'rb')
            bot.send_photo(message.chat.id, img)
        else:
            bot.send_message(message.chat.id,
                             'К сожалению, фотографии кончились(')


bot.polling()

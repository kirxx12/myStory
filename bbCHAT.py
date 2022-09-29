import requests
from bs4 import BeautifulSoup as BS
import telebot
from telebot import types
import random
from SETTINGS import SETTINGS

URL: str = 'https://anekdotov.net/anekdot/month/'
n: list = [1, 2, 3, 4, 5, 6]


def pars_anek(URL: str) -> list:
    """Функция для парсинга по ссылке, принимает
        ссылку, возвращает список результатов"""
    req = requests.get(URL)
    soup = BS(req.text, 'html.parser')
    anekdots = soup.find_all('div', class_='anekdot')
    clear_anekdots = [c.text for c in anekdots]
    random.shuffle(clear_anekdots)
    return clear_anekdots


def markup_maker(command_list: list) -> types.ReplyKeyboardMarkup:
    """Создает необходимое количество кнопок,
        Чтобы пользователь взаимодействовал с ботом"""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button_list = []
    for command in command_list:
        button_list.append(types.KeyboardButton(command))
    markup.add(*button_list)
    return markup


list_of_jokes: list = pars_anek(URL)
bot = telebot.TeleBot(SETTINGS['TOKEN'])


@bot.message_handler(commands=['start'])
def start(message) -> None:
    command_list = ['Хочу анекдот!', 'Хочу фото!']
    markup = markup_maker(command_list)
    bot.send_message(message.chat.id,
                     'Привет, чтобы начать просто выбери опцию!',
                     reply_markup=markup)


@bot.message_handler(content_types=['text'])
def func(message) -> None:
    message_text = {'Лучшее за месяц': 'month/',
                    'Лучшее за неделю': 'week/',
                    'Лучшее за этот день': 'day/'
                    }
    if message.text == 'Хочу анекдот!':
        command_list = ['Лучшее за неделю',
                        'Лучшее за месяц',
                        'Лучшее за этот день',
                        'Вернутся']
        markup = markup_maker(command_list)
        bot.send_message(message.chat.id,
                         "Выбери раздел на этом сайте!", reply_markup=markup)
    elif message.text == 'Хочу фото!':
        global n
        if len(n) > 1:
            i = n[random.randint(0, len(n)) - 1]
            n.remove(i)
            img = open(f'photos/{i}.jpg', 'rb')
            bot.send_photo(message.chat.id, img)
        else:
            bot.send_message(message.chat.id,
                             'К сожалению, фотографии кончились(')
    elif message.text in message_text.keys():
        url = 'http://anekdotov.net/anekdot/' + message_text[message.text]
        list_of_jokes = pars_anek(url)
        bot.send_message(message.chat.id, list_of_jokes[0])
        del list_of_jokes[0]
        start(message)
    elif message.text == 'Вернутся':
        start(message)


bot.polling()

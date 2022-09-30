import requests
from bs4 import BeautifulSoup as BS
import telebot
from telebot import types
import random
from SETTINGS import SETTINGS

URL: str = 'https://anekdotov.net/anekdot/month/'
n: list = [1, 2, 3, 4, 5, 6]
var_category = 0
finder_muztorg = False


def pars_muztorg(zapros: list) -> list:
    """Парс в музторге"""
    url = 'https://www.muztorg.ru/search/' + '%20'.join(zapros)
    response = requests.get(url)
    soup = BS(response.text, 'lxml')
    name = [str(i) for i in soup.find_all('div', class_='title')]
    most_popular_name = name[0][name[0].find('a href'):name[0].find('/a>')]
    print(most_popular_name)
    most_popular_name = (most_popular_name[most_popular_name.find('>')
                         + 1: most_popular_name.find('<')])
    print(most_popular_name)
    price = [str(i) for i in soup.find_all('p', class_='price')]
    most_popular_price = price[0][price[0].rfind('meta content="')+14:]
    most_popular_price = most_popular_price[:most_popular_price.find('"')]
    return f'{most_popular_name} - {most_popular_price}'


def pars_anek(URL: str) -> list:
    """Функция для парсинга по ссылке, принимает
        ссылку, возвращает список результатов"""
    req = requests.get(URL)
    soup = BS(req.text, 'lxml')
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
    command_list = ['Хочу анекдот!',
                    'Хочу фото!',
                    'Хочу найти цену в Музторге']
    markup = markup_maker(command_list)
    bot.send_message(message.chat.id,
                     'Привет, чтобы начать просто выбери опцию!',
                     reply_markup=markup)


@bot.message_handler(content_types=['text'])
def func(message=None,
         chat_id_from_prev_message=None,
         text_from_prev_message=None) -> None:
    if message is None:
        chat_id = chat_id_from_prev_message
        text_mess = text_from_prev_message
    else:
        chat_id = message.chat.id
        text_mess = message.text
    global var_category, finder_muztorg
    if finder_muztorg:
        bot.send_message(chat_id, pars_muztorg(text_mess.split()))
        finder_muztorg = False
    categoryes_list = [{'Лучшее за месяц': 'anekdot/month/',
                        'Лучшее за неделю': 'anekdot/week/',
                        'Лучшее за этот день': 'anekdot/day/'},
                       {'Пошлые': 'intim/',
                        'Злободневные': 'anekdot/today/',
                        'Еврейские': 'anekdot/jew/'},
                       {'Про армию': 'anwar/',
                        'Про врачей': 'anekdot/med/',
                        'Вовочка': 'vovochka/'}]
    message_text = categoryes_list[var_category]
    if text_mess == 'Хочу анекдот!':
        command_list = list(categoryes_list[var_category].keys())
        command_list.append('Другие')
        command_list.append('Вернутся')
        markup = markup_maker(command_list)
        bot.send_message(chat_id,
                         "Выбери раздел на этом сайте!", reply_markup=markup)
    elif text_mess == 'Хочу фото!':
        global n
        if len(n) > 1:
            i = n[random.randint(0, len(n)) - 1]
            n.remove(i)
            img = open(f'photos/{i}.jpg', 'rb')
            bot.send_photo(chat_id, img)
        else:
            bot.send_message(chat_id,
                             'К сожалению, фотографии кончились(')
    elif text_mess in message_text.keys():
        url = 'http://anekdotov.net/' + message_text[text_mess]
        list_of_jokes = pars_anek(url)
        print(list_of_jokes, url)
        bot.send_message(chat_id, list_of_jokes[0])
        del list_of_jokes[0]
        start(message)
    elif text_mess == 'Вернутся':
        start(message)
    elif text_mess == 'Другие':
        if var_category > 1:
            var_category = 0
            func(None, chat_id, 'Хочу анекдот!')
        else:
            var_category += 1
            func(None, chat_id, 'Хочу анекдот!')
    elif text_mess == 'Хочу найти цену в Музторге':
        bot.send_message(chat_id, 'ВВедите название товара:)')
        finder_muztorg = True


bot.polling()

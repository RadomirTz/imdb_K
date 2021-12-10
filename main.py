import PIL
from imageio.core import request
from imdb.parser import sql
import telebot
from imdb import IMDb
import random
from googletrans import Translator
from bs4 import BeautifulSoup
from io import BytesIO
from PIL import Image, ImageDraw
import requests
from imageio import *
import sqlite3

from telebot.types import ReplyKeyboardMarkup


test = int()
ab = False
trigger = False
trigger_2 = True

sqlite_connect = sqlite3.connect('database.db', check_same_thread=False)
cursor = sqlite_connect.cursor()


API_KEY = '2050624983:AAF8MEVibBbDrQTLMUV2Q_i5Y9EAM29C3Ng'
bot = telebot.TeleBot(API_KEY)

ip_movie = IMDb()
translator = Translator()

cursor.execute('CREATE TABLE IF NOT EXISTS user_info (id_user INT, language INT)')
for i in cursor.execute("SELECT * FROM user_info"):
    print(i)
sqlite_connect.commit()
# title, year, directors, synopsis, full-size cover url

@bot.message_handler(commands=['start'])
def add_id(message):
    global trigger
    global test

    keyboard_random = ReplyKeyboardMarkup()
    keyboard_random.row('Боевик', 'Ужасы', 'Триллер', 'Комедия', 'Драма', 'Детектив', 'Фантастика', 'Адвенчюра')
    test = 0
    trigger = True
    list_ids = []
    for i in cursor.execute(f'SELECT * FROM user_info WHERE id_user == {int(message.chat.id)}'):
        list_ids.append(i)
        bot.send_message(message.chat.id, 'Вас приветствует бот IMDb 👋' + '\n' + 'Что хотите посмотреть? Может быть, фантастику?🧐', reply_markup=keyboard_random)
        test = 1
        break
    if test != 1:
        cursor.execute('INSERT INTO user_info VALUES (?, ?)', (int(message.chat.id),1,))
        sqlite_connect.commit()
        bot.send_message(message.chat.id, 'Вас приветсвует бот IMDb 👋' + '\n' + 'Что хотите посмотреть? Может быть, фантастику?🧐', reply_markup=keyboard_random)
        

@bot.message_handler(commands=['my_info'])
def my_info_dev(message):
    bot.send_message(message.chat.id, cursor.execute(f'SELECT * FROM user_info WHERE id_user == {message.chat.id}'))


@bot.message_handler(commands=['alls'])
def all_info(message):
    for i in cursor.execute("SELECT * FROM user_info"):
        bot.send_message(message.chat.id, i)


def random_int(a):
    b = str(a)
    zero_int = '0'*(8-len(b)) + b
    print(zero_int)
    return zero_int


def result_(id, keys, movie_id_, status):
    str_genres = ''
    str_directors = ''
    str_rating = ''
    str_year = ''
    str_description = ''
    
    translator = Translator()
    if status == 'random':
        if 'plot outline' in keys.keys():
            if len(str(keys['plot outline'])) <= 1024:
                for i in cursor.execute(f'SELECT language FROM user_info WHERE id_user=={id}'):
                    
                    if str(i) == '(1,)':
                        str_description = translator.translate(str(keys['plot outline']), dest='ru').text
                    if str(i) == '(2,)':
                        str_description = str(keys['plot']).text
            else:
                str_description = 'Too long...'
        else:
            str_description = 'No'
    else:
        if 'plot' in keys.keys():
            if len(str(keys['plot'])) <= 1024:
                for i in cursor.execute(f'SELECT language FROM user_info WHERE id_user=={id}'):
                    
                    if str(i) == '(1,)':
                        str_description = translator.translate(str(keys['plot']), dest='ru').text
                    if str(i) == '(2,)':
                        str_description = str(keys['plot'])
            else:
                str_description = 'Too long...'
        else:
            str_description = 'No'
    if 'year' in keys.keys():
        str_year = str(keys['year'])
    else:
        str_year = '?'
    if 'directors' in keys.keys():
        for director in keys['directors']:
            if str_directors == '':
                str_directors += director['name']
            else:
                str_directors += ', ' + director['name']
    else:
        str_directors = 'No'

    if 'genres' in keys.keys():
        for i in keys['genres']:
            if str_genres == '':
                str_genres +=   i
            else:
                str_genres += ', ' + i
    else:
        str_genres = 'No'
    
    if 'rating' in keys.keys():
        str_rating = str(keys['rating'])
    else:
        str_rating = 'No'
    
    for i in cursor.execute(f'SELECT language FROM user_info WHERE id_user=={id}'): 
        if str(i) == '(2,)':
            result = '🚧' + keys['title'] + '' + '(' + str_year + ')' + '\n' +'⚡️Genres: ' + str_genres + '\n' +'👨‍🎓Directors: ' + str_directors + '\n' + '⭐️Rating: '  + str_rating + '\n' + '📋Description: ' + str_description + '\n' + '🔎URL: ' + 'imdb.com/title/tt' + keys.movieID
            
        elif str(i) == '(1,)':
            result = '🚧' + keys['title'] + '' + '(' + str_year + ')' + '\n' +'⚡️Жанры: ' + str_genres + '\n' +'👨‍🎓Режиссеры: ' + str_directors + '\n' + '⭐️Рейтинг: '  + str_rating + '\n' + '📋Описание: ' + str_description + '\n' + '🔎URL: ' + 'imdb.com/title/tt' + keys.movieID
            
    if 'full-size cover url' in keys.keys():
        img = keys['full-size cover url']
        
    else:
        img = 'https://www.thefamouspeople.com/profiles/images/kai-lawrence-1.jpg'
        
    return result, img


@bot.message_handler(commands=['language'])
def language_change(message):
    language_select = telebot.types.ReplyKeyboardMarkup(row_width=5)
    button1 = telebot.types.KeyboardButton('/Russian')
    button2 = telebot.types.KeyboardButton('/English')
    language_select.add(button1, button2)
    for i in cursor.execute(f'SELECT language FROM user_info WHERE id_user=={message.chat.id}'):
        if str(i) == '(2,)':
            bot.send_message(message.chat.id, 'Select a language: ', reply_markup=language_select)
        if str(i) == '(1,)':
            bot.send_message(message.chat.id, 'Выберите язык: ', reply_markup=language_select)


@bot.message_handler(commands=['Russian', 'English'])
def language_change_2(message):
    if message.text == '/Russian':
        cursor.execute(f'UPDATE user_info SET language== {1} WHERE id_user=={message.chat.id}')
        sqlite_connect.commit()
        bot.send_message(message.chat.id, 'Язык был успешно изменён на русский', reply_markup=telebot.types.ReplyKeyboardRemove())

    elif message.text == '/English':
        cursor.execute(f'UPDATE user_info SET language== {2} WHERE id_user=={message.chat.id}')
        sqlite_connect.commit()
        bot.send_message(message.chat.id, 'The language has been successfully changed to English', reply_markup=telebot.types.ReplyKeyboardRemove())




@bot.message_handler(commands=['random'])
def send_text(message):
    global ab
    b = ''
    bot.send_message(message.chat.id, 'Please wait...')
    ab = False
    while True:
        try:
            a = random.randint(1,9999999)
            d = random_int(a)
            
            keys = ip_movie.get_movie(d)
            b = str(keys['title'])
            break
        except:
            ab = False
            print('Не существует')
            print(a)
    
    result, img = result_(message.chat.id, keys, d, 'random')
    print(d) 
    bot.send_photo(message.chat.id, img, caption=result, reply_markup=telebot.types.ReplyKeyboardRemove())


@bot.message_handler(commands=['all'])
def unknown_command(message):
    try:
        keys = ip_movie.search_movie_advanced(translator.translate(message.text.replace('/all', ''), dest='en').text)
    except:
        bot.send_message(message.chat.id, 'Use "/random" for random movie', reply_markup=telebot.types.ReplyKeyboardRemove())
        exit()
    print(keys)
    if keys != []:
        id_movie = keys[0]
        #result, img = result_(id_movie, 'unknown', 'text')
        #bot.send_photo(message.chat.id, img, caption=result)
        result__ = ''
        number = 0
        for i in keys:
            if number == 10:
                break
            else:
                number += 1
                result__ += str(number) + '. ' + str(i) + '\n'
        mm = telebot.types.ReplyKeyboardMarkup(row_width=5)
        button1 = telebot.types.KeyboardButton('/film ' + str(keys[0]))
        button2 = telebot.types.KeyboardButton('/film ' + str(keys[1]))
        button3 = telebot.types.KeyboardButton('/film ' + str(keys[2]))
        button4 = telebot.types.KeyboardButton('/film ' + str(keys[3]))
        button5 = telebot.types.KeyboardButton('/film ' + str(keys[4]))
        mm.add(button1, button2, button3, button4, button5)
        bot.send_photo(message.chat.id,keys[0]['full-size cover url'], caption=result__, reply_markup=mm)
        print(keys[0].keys())
    else:
        bot.send_message(message.chat.id, 'Ничего не найдено...', reply_markup=telebot.types.ReplyKeyboardRemove())


@bot.message_handler(commands=['film'])
def concret_command(message):
    try:
        keys = ip_movie.search_movie_advanced(translator.translate(message.text.replace('/film ', ''), dest='en').text)
        print(message.text.replace('/film ', ''))
    except:
        bot.send_message(message.chat.id, 'Use "/random" for random movie', reply_markup=telebot.types.ReplyKeyboardRemove())
        exit()
    print(keys)
    if keys != []:
        for i in keys:
            if str(i) == str(message.text).replace('/film ', ''):
                print(str(i) + '  ' + str(message.text).replace('/film ', ''))
                id_movie = keys[0]
                result, img = result_(message.chat.id, i, 'unknown', 'text')
                bot.send_photo(message.chat.id, img, caption=result, reply_markup=telebot.types.ReplyKeyboardRemove())
                print(keys[0].keys())
                break
            else:
                print('не то')
                print(str(i) + '  ' + str(message.text).replace('/film ', ''))
    else:
        bot.send_message(message.chat.id, 'Ничего не найдено...', reply_markup=telebot.types.ReplyKeyboardRemove())

def genres_random(genre, idr, message):
    if genre == 'Драма' or genre == 'Комедия' or genre == 'Боевик' or genre == 'Адвенчюра' or genre == 'Ужасы' or genre == 'Детектив' or genre == 'Фантастика':
        if genre == 'Драма':
            b = requests.get('https://www.imdb.com/list/ls009668711/')
        elif genre == 'Комедия':
            b = requests.get('https://www.imdb.com/list/ls009668747/')
        elif genre == 'Боевик':
            b = requests.get('https://www.imdb.com/list/ls009668579/')
        elif genre == 'Адвенчюра':
            b = requests.get('https://www.imdb.com/list/ls009609925/')
        elif genre == 'Ужасы':
            b = requests.get('https://www.imdb.com/list/ls000007562/')
        elif genre == 'Детектив':
            b = requests.get('https://www.imdb.com/list/ls054080500/')
        elif genre == 'Фантастика':
            b = requests.get('https://www.imdb.com/list/ls009668082/')
        soup = BeautifulSoup(b.content, 'html.parser')
        titles = soup.find_all('h3', class_='lister-item-header')
        id = int()
        a = random.randint(0,100)
        film = titles[a]
        votro = BeautifulSoup(str(film), 'html.parser')
        urll = votro.find('a')
        uu = urll['href'].replace('/title/tt', '').replace('/', '')
        keys = ip_movie.get_movie(int(uu))
        
        result, img = result_(idr, keys, 'afa', 'пвп')
        return result, img
    else:
        strafff = 0
@bot.message_handler(content_types=['text'])
def unknown_command(message):
    try:
        id = message.chat.id
        print(id)
        result, img = genres_random(message.text, id, message.text)
        bot.send_photo(message.chat.id, img, caption=result, reply_markup=telebot.types.ReplyKeyboardRemove())
    except:
        try:
            keys = ip_movie.search_movie_advanced(translator.translate(message.text, dest='en').text)
        except:
            bot.send_message(message.chat.id, 'Use "/random" for random movie', reply_markup=telebot.types.ReplyKeyboardRemove())
            exit()
        print(keys)
        if keys != []:
            id_movie = keys[0]
            result, img = result_(message.chat.id, id_movie, 'unknown', 'text')
            bot.send_photo(message.chat.id, img, caption=result, reply_markup=telebot.types.ReplyKeyboardRemove())
            print(keys[0].keys())
        else:
            bot.send_message(message.chat.id, 'Ничего не найдено...', reply_markup=telebot.types.ReplyKeyboardRemove())
    

bot.polling(none_stop=True)
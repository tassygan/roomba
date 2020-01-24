import telebot
from telebot import types
import random
from database import SQL

token = "1012837410:AAFY0lxwBFgWPIbRO-lO_MumXnlYJl-1ReQ"
bot = telebot.TeleBot(token)
db = SQL()
name = ""
age = 0

@bot.message_handler(commands = ['start'])
def start(message):
	bot.send_message(message.chat.id, 'roomba - Hайди того самого соседа!\n\n'
	'@rroomba это:\n\n'
	'- поиск соседей по интересам\n'
	'- аренда комнат/квартир\n'
	'- взять на подселение\n'
	'- поиск компаньона для совместной аренды\n\n'
	'Соседство в стиле "Румба"!\n\n'
	'Для подачи объявления пишите на: @rroomba_info\n'
	'Правила размещения по ссылке: @rroomba_rules\n\n'
	'Навигация:\n'
	'- по объявлениям #ищужилье #возьмуксебе #сдамкв\n'
	'- по полу #девушка #парень #семья\n'
	'- по геолокации #есильский #cарыаркинский #алматинский #байконурский\n')

	keyboard = types.InlineKeyboardMarkup()
	button1 = types.InlineKeyboardButton('#ищужилье', callback_data = 'search')
	button2 = types.InlineKeyboardButton('#возьмуксебе', callback_data = 'take')
	button3 = types.InlineKeyboardButton('#сдамкв', callback_data = 'rent')
	keyboard.add(button1)
	keyboard.add(button2)
	keyboard.add(button3)
	bot.send_message(message.chat.id, 'Выбери категорию:', reply_markup = keyboard)

@bot.callback_query_handler(func=lambda call:True)
def callback(call):
	if call.message:
		if call.data == 'search':
			bot.send_message(call.message.chat.id, 'Введите ваше Имя:')
			#@bot.message_handler(content_types = ['text'])
			def name_insert_data(message):
				name = message.text
			bot.send_message(call.message.chat.id, 'Введите ваш Возраст:')
			@bot.message_handler(content_types = ['text'])
			def age_insert_data(message):
				age = int(message.text)
				db.insert_data(name, age)	

"""
def age_insert_data(message):
	age = int(message.text)
	db.insert_data(name, age)
	db.close()

@bot.message_handler(content_types = ['text'])
def name_insert_data(message):
	name = message.text
	db.insert_data(name)

@bot.message_handler(content_types = ['text'])
def game(message):
	global num
	mynum = int(message.text)
	if num == mynum:
		photo = open('12.png', 'rb')
		bot.send_photo(message.chat.id, photo)
	elif mynum > num:
		bot.send_message(message.chat.id, 'Less...')
	else:
		bot.send_message(message.chat.id, 'More...')
"""

bot.polling(none_stop = True)
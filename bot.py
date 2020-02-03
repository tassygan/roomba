import telebot
import random
import time
from telebot import types
from database import SQL
from search import Search, Tenant

token = "1012837410:AAFY0lxwBFgWPIbRO-lO_MumXnlYJl-1ReQ"
bot = telebot.TeleBot(token)
db = SQL()
mode = 0
flat_id = 1
search = Search()
tenant = Tenant()

search_st = False
take_st = False
tenant_st = False

@bot.message_handler(commands = ['start'])
def start(message):
	keyboard = types.ReplyKeyboardMarkup(True, True)
	keyboard.row('Показать квартиры', 'Добавить новое объявление')
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
	'- по геолокации #есильский #cарыаркинский #алматинский #байконурский\n', reply_markup=keyboard)

	#bot.send_message(message.chat.id, 'Выбери категорию:', reply_markup = keyboard)

@bot.callback_query_handler(func=lambda call:True)
def callback(call):
	global mode, search_st, tenant_st, take_st, flat_id
	if call.message:
		if call.data == 'flat_out':
			if flat_id > db.flat_num():
				bot.send_message(call.message.chat.id, 'Квартиры закончились')
				flat_id = 1
				return
			flat = db.flat_out(flat_id)
			flat_id += 1
			keyboard = types.InlineKeyboardMarkup()
			button = types.InlineKeyboardButton('Следующая квартира', callback_data = 'flat_out')
			keyboard.add(button)
			bot.send_message(call.message.chat.id, 'Расположение квартиры: '+ flat[1] + '\n' + 'Цена аренды: '+ flat[2] + '\n' +'Описание: ' +flat[3] + '\n' + 'Номер телефона: ' + flat[4], reply_markup = keyboard)
			for photo_id in flat[5]:
				photo_id += '.jpg'
				img = open(photo_id, 'rb')
				bot.send_photo(call.message.chat.id, img)
		elif call.data == 'search_delete_true':
			db.search_delete(str(call.message.chat.id))
			bot.send_message(call.message.chat.id, 'Ваша анкета удалена')


@bot.message_handler(content_types = ['text'])
def name_insert_data(message):
	global search, mode, search_st, tenant_st, take_st
	if message.text == 'Добавить новое объявление':
		keyboard = types.ReplyKeyboardMarkup(True, True)
		keyboard.row('Жилье','Людей для заселения')
		keyboard.row('Назад в меню')
		bot.send_message(message.chat.id, 'Что вы ищете?', reply_markup = keyboard)
	elif message.text == 'Назад в меню':
		search_st = tenant_st = mode = 0
		keyboard = types.ReplyKeyboardMarkup(True, True)
		keyboard.row('Показать квартиры', 'Добавить новое объявление' )
		bot.send_message(message.chat.id, 'Главное меню', reply_markup=keyboard)
	elif message.text == 'Жилье':
		keyboard = types.ReplyKeyboardMarkup(True, True)
		keyboard.row('Я ищу комнату', 'Я ищу жилье целиком')
		keyboard.row('Назад в меню')
		bot.send_message(message.chat.id, 'Выберите что-то одно:', reply_markup=keyboard)
	elif message.text == 'Людей для заселения':
		keyboard = types.ReplyKeyboardMarkup(True, True)
		keyboard.row('Я предлагаю комнату', 'Я предлагаю жилье целиком')
		keyboard.row('Назад в меню')
		bot.send_message(message.chat.id, 'Выберите что-то одно:', reply_markup=keyboard)
	elif message.text == 'Я ищу комнату':
		chat_id = str(message.chat.id)
		'''
		if db.search_check_chat_id(chat_id) == True:
			bot.send_message(message.chat.id, 'Вы уже заполняли анкету')
			keyboard = types.InlineKeyboardMarkup()
			button1 = types.InlineKeyboardButton('Да', callback_data = 'search_delete_true') 
			button2 = types.InlineKeyboardButton('Нет', callback_data = 'search_delete_false')
			keyboard.add(button1)
			keyboard.add(button2)
			bot.send_message(message.chat.id, 'Хотите удалить вашу анкету?', reply_markup = keyboard)
			return
		'''
		keyboard = types.ReplyKeyboardMarkup(True, False)
		keyboard.row('Назад в меню')
		bot.send_message(message.chat.id, 'Прошу вас заполнить анкету', reply_markup=keyboard)
		time.sleep(1)
		bot.send_message(message.chat.id, 'Ваши ФИО:')
		search_st = True
		mode = 1
	elif message.text == 'Я ищу жилье целиком':
		keyboard = types.ReplyKeyboardMarkup(True, False)
		keyboard.row('Поиск по цене')
		keyboard.row('Поиск по расположению')
		keyboard.row('Назад в меню')
		search_st = False
		flat_num = db.flat_num()
		bot.send_message(message.chat.id, 'Количество квартир: ' + str(flat_num), reply_markup = keyboard)
		keyboard = types.InlineKeyboardMarkup()
		button = types.InlineKeyboardButton('Да', callback_data = 'flat_out')
		keyboard.add(button)
		bot.send_message(message.chat.id, 'Показать квартиру?', reply_markup = keyboard)
	elif message.text == 'Я предлагаю жилье целиком' or message.text == 'Я предлагаю комнату':
		keyboard = types.ReplyKeyboardMarkup(True, False)
		keyboard.row('Назад в меню')
		bot.send_message(message.chat.id, 'Расположение вашей квартиры:', reply_markup = keyboard)
		tenant_st = True
		mode = 1
	elif message.text == 'Показать квартиры':
		keyboard = types.ReplyKeyboardMarkup(True, False)
		keyboard.row('Поиск по цене')
		keyboard.row('Поиск по расположению')
		keyboard.row('Назад в меню')
		search_st = False
		flat_num = db.flat_num()
		bot.send_message(message.chat.id, 'Количество квартир: ' + str(flat_num), reply_markup = keyboard)
		keyboard = types.InlineKeyboardMarkup()
		button = types.InlineKeyboardButton('Да', callback_data = 'flat_out')
		keyboard.add(button)
		bot.send_message(message.chat.id, 'Показать квартиру?', reply_markup = keyboard)

	elif search_st == True:	
		if mode == 1:
			search.chat_id = message.chat.id
			search.name = message.text
			mode = 2
			bot.send_message(message.chat.id, 'Введите ваш возраст:')
		elif mode == 2: 
			search.age = int(message.text)
			mode = 3
			bot.send_message(message.chat.id, 'Укажите вашу сферу деятельности:')
		elif mode == 3: 
			search.sphere = message.text
			mode = 4
			bot.send_message(message.chat.id, 'Укажите языки, на которых вы говорите:')
		elif mode == 4: 
			search.langs = message.text
			mode = 5
			bot.send_message(message.chat.id, 'Ваши интересы, хобби, любимые книги и фильмы')
		elif mode == 5: 
			search.interest = message.text
			mode = 6
			bot.send_message(message.chat.id, 'Желаемый район города(рядом с..)')
		elif mode == 6: 
			search.distr = message.text
			mode = 7
			bot.send_message(message.chat.id, 'Желательная цена')
		elif mode == 7: 
			search.price = message.text
			mode = 8
			bot.send_message(message.chat.id, 'Требования к квартире')
		elif mode == 8:
			search.require = message.text
			mode = 9
			bot.send_message(message.chat.id, 'Ваш номер телефона:')
		elif mode == 9:
			search.phone_num = message.text
			db.search_insert(search)
			bot.send_message(message.chat.id, 'Подбираем вам подходящую квартиру...')
			bot.send_chat_action(message.chat.id, 'typing')
			time.sleep(3)
			keyboard = types.InlineKeyboardMarkup();
			search_st = False
			button = types.InlineKeyboardButton('Показать квартиру', callback_data = 'flat_out')
			keyboard.add(button)
			bot.send_message(message.chat.id, 'Подходящие запросы найдены:', reply_markup = keyboard)
	elif tenant_st == True:
		if mode == 1:
			tenant.location = message.text
			mode = 2
			bot.send_message(message.chat.id, 'Цена аренды:')
		elif mode == 2:
			tenant.price = message.text
			mode = 3
			bot.send_message(message.chat.id, 'Описание вашей квартиры/комнаты (этаж, площадь, \
			интернет, мебель, бытовая техника)')
		elif mode == 3:
			tenant.description = message.text
			mode = 4
			bot.send_message(message.chat.id, 'Ваш номер телефона:')
		elif mode == 4:
			tenant.phone_num = message.text
			db.tenant_insert(tenant)
			bot.send_message(message.chat.id, 'Ваша квартира добавлена!')
			tenant_st = False

			
	
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
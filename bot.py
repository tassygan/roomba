import telebot
import random
import time
import functions
from telebot import types
from database import SQL
from search import Search, Tenant

token = "1012837410:AAFY0lxwBFgWPIbRO-lO_MumXnlYJl-1ReQ"
bot = telebot.TeleBot(token)
db = SQL()
mode = 0
flat_id = 1
cur_flat = 0
search = Search()
tenant = Tenant()
flat_matches = ""

search_st = False
sleep_places_st = False
tenant_st = False

@bot.message_handler(commands = ['start'])
def start(message):
	keyboard = types.ReplyKeyboardMarkup(True, True)
	keyboard.row('🏡Показать квартиры', '📋Добавить новое объявление')
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
	global mode, search_st, tenant_st, flat_id, flat_matches, cur_flat, sleep_places_st
	if call.message:
		if call.data == 'flat_out' or call.data == 'flat_prev':
			bot.delete_message(call.message.chat.id, call.message.message_id)
			if call.data == 'flat_prev':
				flat_id -= 2
			flat = db.flat_out(flat_id)
			flat_id += 1
			keyboard = types.InlineKeyboardMarkup()
			if flat_id <= db.flat_num():
				button = types.InlineKeyboardButton('Следующая квартира >>', callback_data = 'flat_out')
				keyboard.add(button)
			if flat_id > 2:
				button = types.InlineKeyboardButton('<< Предыдущая квартира', callback_data = 'flat_prev')
				keyboard.add(button)
			bot.send_message(call.message.chat.id, '*Расположение квартиры:* '+ flat[1] + ' район, ' + flat[2] + '\n' + \
			 '*Цена аренды:* '+ str(flat[3]) + '\n' + '*Количество комнат:* ' + str(flat[4]) + '\n' + \
			 '*Количество спальных мест:* ' + str(flat[5]) + '\n' + '*Описание:* '+ flat[6] + '\n' + \
			 '*Номер телефона:* ' + flat[7], reply_markup = keyboard, parse_mode = 'Markdown')
			'''
			for photo_id in flat[5]:
				photo_id += '.jpg'
				img = open(photo_id, 'rb')
				bot.send_photo(call.message.chat.id, img)
			'''
		elif call.data == 'matches_out' or call.data == 'matches_out_prev':
			bot.delete_message(call.message.chat.id, call.message.message_id)
			if call.data == 'matches_out_prev':
				cur_flat -= 2
			flat = flat_matches[cur_flat]
			cur_flat += 1
			keyboard = types.InlineKeyboardMarkup()
			if cur_flat + 1 <= len(flat_matches):
				button = types.InlineKeyboardButton('Следующая квартира >>', callback_data = 'matches_out')
				keyboard.add(button)
			if cur_flat > 1:
				button = types.InlineKeyboardButton('<< Предыдущая квартира', callback_data = 'matches_out_prev')
				keyboard.add(button)
			book_st = db.check_book(call.message.chat.id, flat_matches[cur_flat-1][0])
			if book_st == False:
				button = types.InlineKeyboardButton('Забронировать квартиру', callback_data = 'book_flat')
				keyboard.add(button)
			bot.send_message(call.message.chat.id, '*Расположение квартиры:* '+ flat[1] + ' район, ' + flat[2] + '\n' + \
			 '*Цена аренды:* '+ str(flat[3]) + '\n' + '*Количество комнат:* ' + str(flat[4]) + '\n' + \
			 '*Количество спальных мест:* ' + str(flat[5]) + '\n' + '*Стоимость аренды на одного человека:*' + str(int(flat[3]/flat[5])) + \
			 '\n' + '*Описание:* '+ flat[6] + '\n' + '*Номер телефона:* ' + flat[7] + '\n' + '*Забронировано человеком: *' + str(flat[8]), \
			 reply_markup = keyboard, parse_mode = 'Markdown')
		elif call.data == 'book_flat':
			db.book_flat(call.message.chat.id, flat_matches[cur_flat-1][0])
			if flat_matches[cur_flat-1][8] == 0:
				bot.send_message(flat_matches[cur_flat-1][10], 'Ваша квартира была забронирована одним человеком!')
			else:
				bot.send_message(flat_matches[cur_flat-1][10], 'Ваша квартира была забронирована еще одним человеком!')
			bot.edit_message_text(chat_id = call.message.chat.id,message_id = call.message.message_id, text = 'Квартира успешно забронирована!')
		elif call.data == 'search_delete_true':
			db.search_delete(str(call.message.chat.id))
			bot.send_message(call.message.chat.id, 'Ваша анкета удалена')
		elif call.data == '100' or '150' or '200' or '250' or '300':
			filter_price = int(call.data)*1000;



@bot.message_handler(content_types = ['text'])
def name_insert_data(message):
	global search, mode, search_st, tenant_st, flat_matches, cur_flat, sleep_places_st
	if message.text == '📋Добавить новое объявление':
		keyboard = types.ReplyKeyboardMarkup(True, True)
		keyboard.row('🏠Жилье','👤Людей для заселения')
		keyboard.row('🔙Назад в меню')
		bot.send_message(message.chat.id, 'Что вы ищете?', reply_markup = keyboard)
	elif message.text == '🔙Назад в меню':
		search_st = tenant_st = sleep_places_st = mode = 0
		keyboard = types.ReplyKeyboardMarkup(True, True)
		keyboard.row('🏡Показать квартиры', '📋Добавить новое объявление' )
		bot.send_message(message.chat.id, 'Главное меню', reply_markup=keyboard)
	elif message.text == '🏠Жилье':
		keyboard = types.ReplyKeyboardMarkup(True, True)
		keyboard.row('🛋Я ищу спальное место', '🏘Я ищу жилье целиком')
		keyboard.row('🔙Назад в меню')
		bot.send_message(message.chat.id, 'Выберите что-то одно:', reply_markup=keyboard)
	elif message.text == '👤Людей для заселения':
		keyboard = types.ReplyKeyboardMarkup(True, True)
		keyboard.row('🛋Я предлагаю комнату', '🏡Я предлагаю жилье целиком')
		keyboard.row('🔙Назад в меню')
		bot.send_message(message.chat.id, 'Выберите что-то одно:', reply_markup=keyboard)
	elif message.text == 'Я ищу комнату' or message.text == '🛋Я ищу спальное место':
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
		keyboard.row('🔙Назад в меню')
		bot.send_message(message.chat.id, 'Прошу вас заполнить анкету', reply_markup=keyboard)
		time.sleep(1)
		bot.send_message(message.chat.id, 'Ваши ФИО:')
		if message.text == 'Я ищу комнату':
			search_st = True
		else:
			sleep_places_st = True
		mode = 1
	elif message.text == '🏘Я ищу жилье целиком':
		keyboard = types.ReplyKeyboardMarkup(True, False)
		keyboard.row('Поиск по цене')
		keyboard.row('Поиск по расположению')
		keyboard.row('🔙Назад в меню')
		search_st = False
		flat_num = db.flat_num()
		bot.send_message(message.chat.id, 'Количество квартир: ' + str(flat_num), reply_markup = keyboard)
		keyboard = types.InlineKeyboardMarkup()
		button = types.InlineKeyboardButton('Да', callback_data = 'flat_out')
		keyboard.add(button)
		bot.send_message(message.chat.id, 'Показать квартиру?', reply_markup = keyboard)
	elif message.text == '🏡Я предлагаю жилье целиком' or message.text == '🛋Я предлагаю комнату':
		keyboard = types.ReplyKeyboardMarkup(True, False)
		keyboard.row('Алматинский', 'Байконурский')
		keyboard.row('Есильский', 'Сарыаркинский')
		keyboard.row('🔙Назад в меню')
		bot.send_message(message.chat.id, 'В каком районе находится ваша квартира?', reply_markup = keyboard)
		tenant_st = True
		mode = 1
	elif message.text == '🏡Показать квартиры' or message.text == 'Назад':
		keyboard = types.ReplyKeyboardMarkup(True, False)
		keyboard.row('Поиск по цене')
		keyboard.row('Поиск по расположению')
		keyboard.row('🔙Назад в меню')
		search_st = False
		sleep_places_st = False
		flat_num = db.flat_num()
		bot.send_message(message.chat.id, 'Количество квартир: ' + str(flat_num), reply_markup = keyboard)
		keyboard = types.InlineKeyboardMarkup()
		button = types.InlineKeyboardButton('Да', callback_data = 'flat_out')
		keyboard.add(button)
		bot.send_message(message.chat.id, 'Показать квартиру?', reply_markup = keyboard)
	elif message.text == 'Поиск по цене':
		keyboard = types.InlineKeyboardMarkup()
		button = types.InlineKeyboardButton('до 100.000 тенге', callback_data = '100')
		keyboard.add(button)
		button = types.InlineKeyboardButton('до 150.000 тенге', callback_data = '150')
		keyboard.add(button)
		button = types.InlineKeyboardButton('до 200.000 тенге', callback_data = '200')
		keyboard.add(button)
		button = types.InlineKeyboardButton('до 250.000 тенге', callback_data = '250')
		keyboard.add(button)
		button = types.InlineKeyboardButton('до 300.000 тенге', callback_data = '300')
		keyboard.add(button)
		bot.send_message(message.chat.id, 'Выберите цену:', reply_markup=keyboard)
	elif search_st == True or sleep_places_st == True:	
		if mode == 1:
			search.chat_id = message.chat.id
			search.name = message.text
			mode = 2
			bot.send_message(message.chat.id, 'Введите ваш возраст:')
		elif mode == 2: 
			age = message.text
			if age.isdigit() == True:
				search.age = int(message.text)
				mode = 3
				bot.send_message(message.chat.id, 'Укажите вашу сферу деятельности:')
			else:
				bot.send_message(message.chat.id, 'Неправильный ввод! Введите целое число.')
		elif mode == 3: 
			search.sphere = message.text
			mode = 4
			keyboard = types.ReplyKeyboardMarkup(True, False)
			keyboard.row('Казахский', 'Русский', 'Оба языка')
			keyboard.row('Назад в меню')
			bot.send_message(message.chat.id, 'Укажите языки, на которых вы говорите:', reply_markup=keyboard)
		elif mode == 4:
			lang = message.text
			if lang == 'Казахский' or lang == 'Русский' or lang == 'Оба языка': 
				search.langs = message.text
				mode = 5
				keyboard = types.ReplyKeyboardMarkup(True, True)
				keyboard.row('🔙Назад в меню')
				bot.send_message(message.chat.id, 'Ваши интересы, хобби, любимые книги и фильмы', reply_markup=keyboard)
			else:
				bot.send_message(message.chat.id, 'Неправильный ввод!')
		elif mode == 5: 
			search.interest = message.text
			mode = 6
			keyboard = types.ReplyKeyboardMarkup(True, False)
			keyboard.row('Алматинский', 'Байконурский')
			keyboard.row('Есильский', 'Сарыаркинский')
			keyboard.row('🔙Назад в меню')
			bot.send_message(message.chat.id, 'Желаемый район города', reply_markup = keyboard)
		elif mode == 6: 
			distr = message.text
			if distr == 'Алматинский' or distr == 'Байконурский' or distr == 'Есильский' or distr == 'Сарыаркинский':
				search.distr = message.text
				mode = 7
				keyboard = types.ReplyKeyboardMarkup(True, True)
				keyboard.row('🔙Назад в меню')
				bot.send_message(message.chat.id, 'Желательная цена (тенге)', reply_markup=keyboard)
			else:
				bot.send_message(message.chat.id, 'Неправильный ввод!')
		elif mode == 7:
			price = message.text
			if price.isdigit() == True: 
				search.price = int(message.text)
				mode = 8
				bot.send_message(message.chat.id, 'Требования к квартире')
			else:
				bot.send_message(message.chat.id, 'Неправильный ввод! Введите целое число.')
		elif mode == 8:
			search.require = message.text
			mode = 9
			bot.send_message(message.chat.id, 'Ваш номер телефона:')
		elif mode == 9:
			search.phone_num = message.text
			if search_st == True:
				db.search_insert(search)
			else:
				db.sleep_insert(search)
			bot.send_message(message.chat.id, '*Подбираем вам подходящие квартиры...*', parse_mode = "Markdown")
			bot.send_chat_action(message.chat.id, 'typing')
			time.sleep(3)
			search_st = sleep_places_st = False
			flat_matches = db.get_matches(search)
			keyboard = types.InlineKeyboardMarkup();
			button = types.InlineKeyboardButton('Показать квартиры', callback_data = 'matches_out')
			keyboard.add(button)
			bot.send_message(message.chat.id, 'Квартиры найдены', reply_markup = keyboard)
	elif tenant_st == True:
		if mode == 1:
			distr = message.text
			if distr == 'Алматинский' or distr == 'Байконурский' or distr == 'Есильский' or distr == 'Сарыаркинский':
				tenant.distr = message.text
				mode = 2
				keyboard = types.ReplyKeyboardMarkup(True, True)
				keyboard.row('🔙Назад в меню')
				bot.send_message(message.chat.id, 'Укажите ваш точный адрес', reply_markup=keyboard)
			else:
				bot.send_message(message.chat.id, 'Неправильный ввод!')
		elif mode == 2:
			tenant.chat_id = message.chat.id
			tenant.address = message.text
			mode = 3
			bot.send_message(message.chat.id, 'Цена аренды в тенге:')
		elif mode == 3:
			price = message.text
			if price.isdigit() == True:
				tenant.price = int(message.text)
				mode = 4
				bot.send_message(message.chat.id, 'Количество комнат в вашей квартире')
			else:
				bot.send_message(message.chat.id, 'Неправильный ввод! Введите целое число')
		elif mode == 4:
			room_num = message.text
			if room_num.isdigit() == True:
				tenant.room_num = int(message.text)
				mode = 5
				bot.send_message(message.chat.id, 'Количество людей для заселения')
			else:
				bot.send_message(message.chat.id, 'Неправильный ввод! Введите целое число')
		elif mode == 5:
			sleep_places = message.text
			if sleep_places.isdigit() == True:
				tenant.sleep_places = int(message.text)
				mode = 6
				bot.send_message(message.chat.id, 'Описание вашей квартиры/комнаты (этаж, площадь, \
				интернет, мебель, бытовая техника)')
			else:
				bot.send_message(message.chat.id, 'Неправильный ввод! Введите целое число')
		elif mode == 6:
			tenant.description = message.text
			mode = 7
			bot.send_message(message.chat.id, 'Ваш номер телефона:')
		elif mode == 7:
			tenant.phone_num = message.text
			db.tenant_insert(tenant)
			bot.send_message(message.chat.id, 'Ваша квартира добавлена!')
			tenant_st = False
			mode = 0

bot.polling(none_stop = True)
import telebot
import time
import urllib
from telebot import types
from database import SQL
from users import Seeker, Offerer
import photos

token = "1012837410:AAFY0lxwBFgWPIbRO-lO_MumXnlYJl-1ReQ"
bot = telebot.TeleBot(token)
db = SQL()
mode = 0
flat_id = 1
cur_flat = 0
cur_profile = 0
change_st = 0
last_mess_id = 0
seeker = Seeker()
offerer = Offerer()
flat_matches = ""
flat_profiles = ""
flats = ""
profiles = ""

flat_profile_st = False
seeker_st = False
seeker_search_st = False
offerer_st = False
search_profile = False
search_flat = False

def default_vars():
	global mode, flat_id, cur_flat, cur_profile, change_st, last_mess_id, seeker, offerer, flat_matches, flat_profiles,\
	flats, profiles, flat_profile_st, seeker_st, offerer_st, search_profile, search_flat, seeker_search_st
	mode = 0
	flat_id = 1
	cur_flat = 0
	cur_profile = 0
	change_st = 0
	last_mess_id = 0
	seeker = Seeker()
	offerer = Offerer()
	flat_matches = ""
	flat_profiles = ""
	flats = ""
	profiles = ""

	flat_profile_st = False
	seeker_st = False
	seeker_search_st = False
	offerer_st = False
	search_profile = False
	search_flat = False

@bot.message_handler(commands = ['start'])
def start(message):
	default_vars()
	keyboard = types.ReplyKeyboardMarkup(True, False)
	keyboard.row('📋Добавить новое объявление', 'Просмотреть объявления')
	keyboard.row('Мои объявления', 'Обратная связь')
	bot.send_message(message.chat.id, 'roomba - Hайди того самого соседа!\n\n'
	'@rroomba это:\n\n'
	'- поиск соседей по интересам\n'
	'- аренда комнат/квартир\n'
	'- взять на подселение\n'
	'- поиск компаньона для совместной аренды\n\n'
	'Соседство в стиле "Румба"!\n\n'
	'Для подачи объявления пишите на: @rroomba_info\n'
	'Правила размещения по ссылке: @rroomba_rules\n\n', reply_markup=keyboard)

@bot.message_handler(commands = ['menu'])
def main_menu(message):
	default_vars()
	keyboard = types.ReplyKeyboardMarkup(True, False)
	keyboard.row('📋Добавить новое объявление', 'Просмотреть объявления')
	keyboard.row('Мои объявления', 'Обратная связь')
	bot.send_message(message.chat.id, 'Главное меню', reply_markup=keyboard)

@bot.message_handler(func=lambda message:message.text is not None and len(message.text) > 6 and message.text[:7] == '/advert')
def adverts(message):
	if message.text[7] == '1':
		profile_id = message.text[8:]
		profile = db.get_profile_by_id(profile_id)
		if profile[2] > 1000:
			age = str(int(profile[2]/100)) + '-' + str(profile[2]%100)
		else:
			age = profile[2]
		if profile[5] == 'student':
			work = 'студент'
		else:
			work = 'работник'
		cap = '*Имя:* '+ profile[1] + '\n' + '*Возраст:* ' + str(age) + '\n' + \
		 '*Откуда родом:* '+ profile[3] + '\n' + '*Пол:* ' + profile[4] + '\n' + \
		 '*Работник или студент:* ' + work + '\n' + '*Место:* ' + profile[6] + \
		 '\n' + '*Режим сна:* '+ profile[7] + '\n' + '*Языки:* ' + profile[8] + '\n' + '*О себе:* ' + profile[13]
		photo_id = db.get_profile_photo(profile[0])
		keyboard = types.InlineKeyboardMarkup()
		button = types.InlineKeyboardButton('Изменить объявление', callback_data = 'change_profile')
		keyboard.add(button)
		button = types.InlineKeyboardButton('Удалить объявление', callback_data = 'delete_profile')
		keyboard.add(button)
		if photo_id == '0':
			bot.send_message(message.chat.id, cap, reply_markup = keyboard, parse_mode = 'Markdown')
		else: 
			photo = photos.download_photo(photo_id)
			bot.send_photo(message.chat.id, photo, caption = cap, reply_markup=keyboard, parse_mode = 'Markdown')
	elif message.text[7] == '2':
		flat_id = message.text[8:]
		flat = db.get_flat_by_id(flat_id)
		keyboard = types.InlineKeyboardMarkup()
		cap = '*Расположение квартиры:* '+ flat[1] + ' район, ' + flat[2] + '\n' + \
		 '*Цена аренды:* '+ str(flat[3]) + '\n' + '*Количество комнат:* ' + str(flat[4]) + '\n' + \
		 '*Количество спальных мест:* ' + str(flat[5]) + '\n' + '*Стоимость аренды на одного человека:*' + str(flat[6]) + \
		 '\n' + '*Описание:* '+ flat[7] + '\n' + '*Номер телефона:* ' + flat[8]
		photo_id = db.get_flat_photo_file_id(flat[0])
		if photo_id == '0':
			bot.send_message(message.chat.id, cap, parse_mode = 'Markdown')
		else: 
			photo = photos.download_photo(photo_id)
			bot.send_photo(message.chat.id, photo, caption = cap, parse_mode = 'Markdown')

@bot.message_handler(func=lambda message:message.text is not None and len(message.text) > 6 and message.text[:7] == '/delete')
def adverts(message):
	if message.text[7] == '2':
		flat_id = message.text[8:]
		db.offerer_delete(flat_id)
		bot.send_message(message.chat.id, 'Ваше объявление удалено.')

@bot.callback_query_handler(func=lambda call:True)
def callback(call):
	global mode, seeker_st, offerer_st, search_flat, flat_id, flat_profile_st, change_st, last_mess_id, flat_matches, cur_flat, sleep_places_st, cur_profile, flat_profiles, profiles, flats
	if call.message:
		if call.data == 'flat_next' or call.data == 'flat_prev':
			flat_profile_st = False
			bot.delete_message(call.message.chat.id, call.message.message_id)
			if call.data == 'flat_prev':
				cur_flat -= 2
			if flat_matches is None or cur_flat >= len(flat_matches) or cur_flat < 0:
				bot.send_message(call.message.chat.id, 'Ошибка. Попробуйте еще раз.')
				return	
			flat = flat_matches[cur_flat]
			cur_flat += 1
			keyboard = types.InlineKeyboardMarkup()
			if flat[9] > 0:
				button = types.InlineKeyboardButton('Просмотреть профили соседей', callback_data = 'book_profiles')
				keyboard.add(button)
			if cur_flat + 1 <= len(flat_matches) and cur_flat > 1:
				button1 = types.InlineKeyboardButton('Следующая >>', callback_data = 'flat_next')
				button2 = types.InlineKeyboardButton('<< Предыдущая', callback_data = 'flat_prev')
				keyboard.row(button2, button1)
			elif cur_flat > 1:
				button = types.InlineKeyboardButton('<< Предыдущая квартира', callback_data = 'flat_prev')
				keyboard.add(button)
			elif cur_flat + 1 <= len(flat_matches):
				button = types.InlineKeyboardButton('Следующая квартира >>', callback_data = 'flat_next')
				keyboard.add(button)
			cap = '*Расположение квартиры:* '+ flat[1] + ' район, ' + flat[2] + '\n' + \
			 '*Цена аренды:* '+ str(flat[3]) + '\n' + '*Количество комнат:* ' + str(flat[4]) + '\n' + \
			 '*Количество спальных мест:* ' + str(flat[5]) + '\n' + '*Стоимость аренды на одного человека:*' + str(flat[6]) + \
			 '\n' + '*Описание:* '+ flat[7] + '\n' + '*Номер телефона:* ' + flat[8] + '\n' + '*Забронировали* ' + str(flat[9]) + ' *человек*'
			photo_id = db.get_flat_photo_file_id(flat[0])
			if photo_id == '0':
				bot.send_message(call.message.chat.id, cap, reply_markup = keyboard, parse_mode = 'Markdown')
			else: 
				photo = photos.download_photo(photo_id)
				bot.send_photo(call.message.chat.id, photo, caption = cap, reply_markup = keyboard, parse_mode = 'Markdown')
		elif call.data == 'matches_out' or call.data == 'matches_out_prev' or call.data == 'rematch':
			flat_profile_st = False
			bot.delete_message(call.message.chat.id, call.message.message_id)
			if call.data == 'rematch':
				seeker = Seeker()
				seeker = db.get_rematches(call.message.chat.id)
				flat_matches = db.get_matches(seeker)
			if call.data == 'matches_out_prev':
				cur_flat -= 2
			if flat_matches is None or cur_flat >= len(flat_matches) or cur_flat < 0:
				bot.send_message(call.message.chat.id, 'Ошибка. Попробуйте еще раз.')
				return
			flat = flat_matches[cur_flat]
			cur_flat += 1
			keyboard = types.InlineKeyboardMarkup()
			if flat[9] > 0:
				button = types.InlineKeyboardButton('Просмотреть профили соседей', callback_data = 'book_profiles')
				keyboard.add(button)
			book_st = db.check_book(call.message.chat.id, flat_matches[cur_flat-1][0])
			if book_st == False:
				button = types.InlineKeyboardButton('Забронировать квартиру', callback_data = 'book_flat')
				keyboard.add(button)
			if cur_flat + 1 <= len(flat_matches) and cur_flat > 1:
				button1 = types.InlineKeyboardButton('Следующая >>', callback_data = 'matches_out')
				button2 = types.InlineKeyboardButton('<< Предыдущая', callback_data = 'matches_out_prev')
				keyboard.row(button2, button1)
			elif cur_flat > 1:
				button = types.InlineKeyboardButton('<< Предыдущая квартира', callback_data = 'matches_out_prev')
				keyboard.add(button)
			else:
				button = types.InlineKeyboardButton('Следующая квартира >>', callback_data = 'matches_out')
				keyboard.add(button)
			cap = '*Расположение квартиры:* '+ flat[1] + ' район, ' + flat[2] + '\n' + \
			 '*Цена аренды:* '+ str(flat[3]) + '\n' + '*Количество комнат:* ' + str(flat[4]) + '\n' + \
			 '*Количество спальных мест:* ' + str(flat[5]) + '\n' + '*Стоимость аренды на одного человека:*' + str(flat[6]) + \
			 '\n' + '*Описание:* '+ flat[7] + '\n' + '*Номер телефона:* ' + flat[8] + '\n' + '*Забронировали* ' + str(flat[9]) + ' *человек*'
			photo_id = db.get_flat_photo_file_id(flat_matches[cur_flat-1][0])
			if photo_id == '0':
				bot.send_message(call.message.chat.id, cap, reply_markup = keyboard, parse_mode = 'Markdown')
			else: 
				photo = photos.download_photo(photo_id)
				bot.send_photo(call.message.chat.id, photo, caption = cap, reply_markup = keyboard, parse_mode = 'Markdown')
		elif call.data == 'book_flat':
			db.book_flat(call.message.chat.id, flat_matches[cur_flat-1][0])
			if flat_matches[cur_flat-1][9] == 0:
				bot.send_message(flat_matches[cur_flat-1][11], 'Ваша квартира была забронирована одним человеком!')
			else:
				bot.send_message(flat_matches[cur_flat-1][11], 'Ваша квартира была забронирована еще одним человеком!')
			bot.send_message(call.message.chat.id, 'Квартира успешно забронирована!')
		elif call.data == 'profile_next' or call.data == 'profile_prev' or call.data == 'rematch_profiles':
			bot.delete_message(call.message.chat.id, call.message.message_id)
			if call.data == 'rematch_profiles':
				profile = db.get_profile(call.message.chat.id)
				profiles = db.get_profiles_by_filters(profile[9], profile[11])
			if call.data == 'profile_prev':
				cur_profile -= 2
			if profiles is None or cur_profile >= len(profiles) or cur_profile < 0:
				bot.send_message(call.message.chat.id, 'Ошибка. Попробуйте еще раз.')
				return
			profile = profiles[cur_profile]
			cur_profile += 1
			keyboard = types.InlineKeyboardMarkup()
			if cur_profile + 1 <= len(profiles) and cur_profile > 1:
				button1 = types.InlineKeyboardButton('Следующий >>', callback_data = 'profile_next')
				button2 = types.InlineKeyboardButton('<< Предыдущий', callback_data = 'profile_prev')
				keyboard.row(button2, button1)
			elif cur_profile > 1:
				button = types.InlineKeyboardButton('<< Предыдущий профиль', callback_data = 'profile_prev')
				keyboard.add(button)
			elif cur_profile + 1 <= len(profiles):
				button = types.InlineKeyboardButton('Следующий профиль >>', callback_data = 'profile_next')
				keyboard.add(button)
			if profile[2] > 1000:
				age = str(int(profile[2]/100)) + '-' + str(profile[2]%100)
			else:
				age = profile[2]
			if profile[5] == 'student':
				work = 'студент'
			else:
				work = 'работник'
			cap = '*Имя:* '+ profile[1] + '\n' + '*Возраст:* ' + str(age) + '\n' + \
			 '*Откуда родом:* '+ profile[3] + '\n' + '*Пол:* ' + profile[4] + '\n' + \
			 '*Работник или студент:* ' + work + '\n' + '*Место:*' + profile[6] + \
			 '\n' + '*Режим сна:* '+ profile[7] + '\n' + '*Языки:* ' + profile[8] + '\n' + '*О себе:* ' + profile[13]
			photo_id = db.get_profile_photo(profile[0])
			if photo_id == '0':
				bot.send_message(call.message.chat.id, cap, reply_markup = keyboard, parse_mode = 'Markdown')
			else: 
				photo = photos.download_photo(photo_id)
				bot.send_photo(call.message.chat.id, photo, caption = cap, reply_markup = keyboard, parse_mode = 'Markdown')
		elif call.data == 'book_profiles' or call.data == 'book_profiles_prev':
			if not flat_profile_st: 
				flat_profiles = db.get_flat_profiles(flat_matches[cur_flat-1][0])
				cur_flat -= 1
				cur_profile = 0
				flat_profile_st = True
			bot.delete_message(call.message.chat.id, call.message.message_id)
			if call.data == 'book_profiles_prev':
				cur_profile -= 2
			if flat_profiles is None or cur_profile >= len(flat_profiles) or cur_profile < 0:
				bot.send_message(call.message.chat.id, 'Ошибка. Попробуйте еще раз.')
				return
			profile = db.get_profile_by_id(flat_profiles[cur_profile])
			cur_profile += 1
			keyboard = types.InlineKeyboardMarkup()
			if search_flat == False:
				button = types.InlineKeyboardButton('Назад к объявлению', callback_data = 'matches_out')
			else:
				button = types.InlineKeyboardButton('Назад к объявлению', callback_data = 'flat_next')
			keyboard.add(button)
			if cur_profile + 1 <= len(flat_profiles) - 1 and cur_profile > 1:
				button1 = types.InlineKeyboardButton('Следующий >>', callback_data = 'book_profiles')
				button2 = types.InlineKeyboardButton('<< Предыдущий', callback_data = 'book_profiles_prev')
				keyboard.row(button2, button1)
			elif cur_profile > 1:
				button = types.InlineKeyboardButton('<< Предыдущий профиль', callback_data = 'book_profiles_prev')
				keyboard.add(button)
			elif cur_profile + 1 <= len(flat_profiles) - 1:
				button = types.InlineKeyboardButton('Следующий профиль >>', callback_data = 'book_profiles')
				keyboard.add(button)
			if profile[2] > 1000:
				age = str(int(profile[2]/100)) + '-' + str(profile[2]%100)
			else:
				age = profile[2]
			if profile[5] == 'student':
				work = 'студент'
			else:
				work = 'работник'
			cap = '*Имя:* '+ profile[1] + '\n' + '*Возраст:* ' + str(age) + '\n' + \
			 '*Откуда родом:* '+ profile[3] + '\n' + '*Пол:* ' + profile[4] + '\n' + \
			 '*Работник или студент:* ' + work + '\n' + '*Место:*' + profile[6] + \
			 '\n' + '*Режим сна:* '+ profile[7] + '\n' + '*Языки:* ' + profile[8] + '\n' + '*О себе:* ' + profile[13]
			photo_id = db.get_profile_photo(profile[0])
			if photo_id == '0':
				bot.send_message(call.message.chat.id, cap, reply_markup = keyboard, parse_mode = 'Markdown')
			else: 
				photo = photos.download_photo(photo_id)
				bot.send_photo(call.message.chat.id, photo, caption = cap, reply_markup = keyboard, parse_mode = 'Markdown')
		elif call.data == 'delete_profile':
			db.seeker_delete(str(call.message.chat.id))
			bot.delete_message(call.message.chat.id, call.message.message_id)
			bot.send_message(call.message.chat.id, '*Объявление удалено.*', parse_mode = 'Markdown')
		elif call.data == 'delete_flat':
			db.offerer_delete(str(call.message.chat.id))
			bot.delete_message(call.message.chat.id, call.message.message_id)
			bot.send_message(call.message.chat.id, '*Объявление удалено.*', parse_mode = 'Markdown')
		elif call.data == 'change_profile':
			keyboard = types.InlineKeyboardMarkup()
			button1 = types.InlineKeyboardButton('Изменить Имя', callback_data = 'change_name')
			button2 = types.InlineKeyboardButton('Изменить Возраст', callback_data = 'change_age')
			button3 = types.InlineKeyboardButton('Изменить\nОткуда Родом', callback_data = 'change_homeland')
			button4 = types.InlineKeyboardButton('Изменить О себе', callback_data = 'change_desc')
			keyboard.row(button1, button2)
			keyboard.row(button3, button4)
			bot.edit_message_reply_markup(chat_id = call.message.chat.id, message_id = call.message.message_id, reply_markup = keyboard)
		elif call.data == 'change_name':
			bot.send_message(call.message.chat.id, 'Введите новое Имя')
			change_st = 1
			last_mess_id = call.message.message_id
		elif call.data == 'change_age':
			bot.send_message(call.message.chat.id, 'Введите новый возраст\n(целое число)')
			change_st = 2
			last_mess_id = call.message.message_id
		elif call.data == 'change_homeland':
			bot.send_message(call.message.chat.id, 'Введите новое место откуда Вы родом\n(регион, город)')
			change_st = 3
			last_mess_id = call.message.message_id
		elif call.data == 'change_desc':
			bot.send_message(call.message.chat.id, 'Напишите новое описание о себе')
			change_st = 4
			last_mess_id = call.message.message_id


@bot.message_handler(content_types = ['text'])
def name_insert_data(message):
	global seeker, offerer, mode, seeker_st, offerer_st, flat_matches, seeker_search_st, search_profile, search_flat, profiles, flats, cur_flat, sleep_places_st, cur_profile, last_mess_id, change_st
	if message.text == '📋Добавить новое объявление':
		keyboard = types.ReplyKeyboardMarkup(True, False)
		keyboard.row('👤Ищу людей для сожительства')
		keyboard.row('Ищу жилье')
		keyboard.row('🏠Предлагаю жилье')
		keyboard.row('🔙Назад в меню')
		bot.send_message(message.chat.id, 'Выберите что-то одно:\n1.👤Ищу соседей\n2.🏠Предлагаю жилье', reply_markup = keyboard)
	elif message.text == 'Просмотреть объявления':
		keyboard = types.ReplyKeyboardMarkup(True, True)
		keyboard.row('👤Просмотреть профили', '🏠Просмотреть квартиры')
		bot.send_message(message.chat.id, 'Какие объявления вы хотите просмотреть?\n1.👤Профили\n2.🏠Квартиры', reply_markup = keyboard)
	elif message.text == '👤Просмотреть профили':
		search_profile = True
		mode = 1
		seeker = Seeker()
		bot.send_message(message.chat.id, 'Для более удобного показа профилей прошу вас указать район города и желаемую стоимость аренды')
		time.sleep(1)
		keyboard = types.ReplyKeyboardMarkup(True, True)
		keyboard.row('Алматинский', 'Байконурский')
		keyboard.row('Есильский', 'Сарыаркинский')
		keyboard.row('🔙Назад в меню')
		bot.send_message(message.chat.id, 'Для начала укажите желаемый район', reply_markup = keyboard)
	elif message.text == '🏠Просмотреть квартиры':
		search_flat = True
		mode = 1
		offerer = Offerer()
		bot.send_message(message.chat.id, 'Для более удобного просмотра квартир прошу Вас ответить на пару вопросов')
		keyboard = types.ReplyKeyboardMarkup(True, True)
		keyboard.row('Алматинский', 'Байконурский')
		keyboard.row('Есильский', 'Сарыаркинский')
		keyboard.row('🔙Назад в меню')
		time.sleep(2)
		bot.send_message(message.chat.id, 'В каком районе города Вы ищете квартиру?', reply_markup=keyboard)
	elif message.text == 'Мои объявления':
		profile = db.get_profile(message.chat.id)
		flats = db.get_flat(message.chat.id)
		if profile is None and len(flats) == 0:
			bot.send_message(message.chat.id, 'У вас нет активных объявлений.')
			return
		text = '*Ваши объявления*\n\n'
		if profile is not None:
			text += '*Поиск квартиры*\n'
			text += 'Подробнее: /advert1' + str(profile[0]) + '\n\n'
		if flats is not None:
			for flat in flats:
				text += '*Сдача квартиры в аренду*\n'
				text += 'Подробнее: ' + '/advert2' + str(flat[0]) + '\n' + 'Удалить: ' + '/delete2' + str(flat[0]) + '\n\n'
		bot.send_message(message.chat.id, text, parse_mode = 'Markdown')
	elif message.text == '🔙Назад в меню':
		default_vars()
		keyboard = types.ReplyKeyboardMarkup(True, False)
		keyboard.row('📋Добавить новое объявление', 'Просмотреть объявления')
		keyboard.row('Мои объявления', 'Обратная связь')
		bot.send_message(message.chat.id, 'Главное меню', reply_markup=keyboard)
	elif message.text == '👤Ищу людей для сожительства':
		chat_id = str(message.chat.id)
		if db.seeker_check_chat_id(chat_id) == True:
			keyboard = types.InlineKeyboardMarkup()
			button = types.InlineKeyboardButton('Просмотреть профили людей', callback_data = 'rematch_profiles')
			keyboard.add(button)
			bot.send_message(message.chat.id, 'У вас уже есть активное объявление. '
			'Чтобы изменить или удалить объявление перейдите в раздел *\'Мои объявления\'*'
			' в главном меню (/menu).', reply_markup = keyboard, parse_mode = 'Markdown')
			return
		keyboard = types.ReplyKeyboardMarkup(True, False)
		keyboard.row('🔙Назад в меню')
		bot.send_message(message.chat.id, 'Прошу вас заполнить анкету', reply_markup=keyboard)
		time.sleep(1)
		bot.send_message(message.chat.id, 'Введите Ваше имя.')
		seeker_search_st = True
		mode = 1
	elif message.text == 'Ищу жилье':
		chat_id = str(message.chat.id)
		if db.seeker_check_chat_id(chat_id) == True:
			keyboard = types.InlineKeyboardMarkup()
			button = types.InlineKeyboardButton('Просмотреть квартиры', callback_data = 'rematch')
			keyboard.add(button)
			bot.send_message(message.chat.id, 'У вас уже есть активное объявление. '
			'Чтобы изменить или удалить объявление перейдите в раздел *\'Мои объявления\'*'
			' в главном меню (/menu).', reply_markup = keyboard, parse_mode = 'Markdown')
			return

		keyboard = types.ReplyKeyboardMarkup(True, False)
		keyboard.row('🔙Назад в меню')
		bot.send_message(message.chat.id, 'Прошу вас заполнить анкету', reply_markup=keyboard)
		time.sleep(1)
		bot.send_message(message.chat.id, 'Введите Ваше имя.')
		seeker_st = True
		mode = 1
	elif message.text == '🏠Предлагаю жилье':
		keyboard = types.ReplyKeyboardMarkup(True, True)
		keyboard.row('🛋Я предлагаю комнату', '🏡Я предлагаю жилье целиком')
		keyboard.row('🔙Назад в меню')
		bot.send_message(message.chat.id, 'Выберите что-то одно:', reply_markup=keyboard)
	elif message.text == '🏘Я ищу жилье целиком':
		keyboard = types.ReplyKeyboardMarkup(True, False)
		keyboard.row('Поиск по цене')
		keyboard.row('Поиск по расположению')
		keyboard.row('🔙Назад в меню')
		seeker_st = False
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
		offerer_st = True
		mode = 1
	elif message.text == '🏡Показать квартиры' or message.text == 'Назад':
		keyboard = types.ReplyKeyboardMarkup(True, False)
		keyboard.row('Поиск по цене')
		keyboard.row('Поиск по расположению')
		keyboard.row('🔙Назад в меню')
		seeker_st = False
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
	elif seeker_st == True or seeker_search_st == True:	
		if mode == 1:
			seeker.chat_id = message.chat.id
			seeker.name = message.text
			mode = 2
			keyboard = types.ReplyKeyboardMarkup(True, True)
			keyboard.row('от 16 до 18', 'от 18 до 23')
			keyboard.row('от 23 до 29', 'от 29 до 35')
			keyboard.row('Другое', '🔙Назад в меню')
			bot.send_message(message.chat.id, 'Укажите Ваш возраст.', reply_markup = keyboard)
		elif mode == 2:
			if message.text == 'Другое':
				bot.send_message(message.chat.id, 'Введите Ваш возраст. Прошу ввести целое число')
				return
			if message.text == 'от 16 до 18':
				age = '1618'
			elif message.text == 'от 18 до 23':
				age = '1823'
			elif message.text == 'от 23 до 29':
				age = '2329'
			elif message.text == 'от 29 до 35':
				age = '2935'
			else:
				age = message.text
				if not age.isdigit() or int(age) > 110:
					bot.send_message(message.chat.id, 'Неправильный ввод! Введите целое число.')
					return
			seeker.age = int(age)
			mode += 1
			bot.send_message(message.chat.id, 'Откуда Вы?\n(регион, город)')
		elif mode == 3:
			seeker.homeland = message.text
			mode += 1
			keyboard = types.ReplyKeyboardMarkup(True, False)
			keyboard.row('👱Мужчина', '👩Женщина')
			keyboard.row('🔙Назад в меню')
			bot.send_message(message.chat.id, 'Укажите Ваш пол', reply_markup = keyboard)
		elif mode == 4:
			if message.text == '👱Мужчина':
				seeker.gender = 'Муж'
			elif message.text == '👩Женщина':
				seeker.gender = 'Жен'
			else:
				keyboard = types.ReplyKeyboardMarkup(True, False)
				keyboard.row('👱Мужчина', '👩Женщина')
				keyboard.row('🔙Назад в меню')
				bot.send_message(message.chat.id, 'Неправильный ввод! Прошу Вас воспользоваться клавиатурой', reply_markup = keyboard)
				return
			mode += 1
			keyboard = types.ReplyKeyboardMarkup(True, False)
			keyboard.row('учусь', 'работаю', 'не учусь и не работаю')
			keyboard.row('🔙Назад в меню')
			bot.send_message(message.chat.id, 'Вы учитесь или работаете', reply_markup = keyboard)
		elif mode == 5:
			keyboard = types.ReplyKeyboardMarkup(True, False)
			if message.text == 'учусь':
				seeker.worker_or_student = 'student'
				keyboard.row('🔙Назад в меню')
				keyboard.row('Astana IT University', 'КазГЮА')
				keyboard.row('Аграрка', 'Назарбаев Университет')
				keyboard.row('Евразийский НУ', 'Университет Астаны')
				keyboard.row('Медунивер', 'Коледж')
				keyboard.row('Другое...')
				bot.send_message(message.chat.id, 'Где Вы учитесь?', reply_markup=keyboard)
			elif message.text == 'работаю':
				seeker.worker_or_student = 'worker'
				keyboard.row('🔙Назад в меню')
				keyboard.row('Строительство', 'Торговля')
				keyboard.row('IT', 'Образование')
				keyboard.row('Госслужба', 'Работаю на себя')
				keyboard.row('Частная комания', 'Рестораны/кафе')
				keyboard.row('Другое...')
				bot.send_message(message.chat.id, 'Какая у Вас сфера деятельности?', reply_markup=keyboard)
			elif message.text == 'не учусь и не работаю':
				seeker.worker_or_student = 'neither'
				mode += 2
				keyboard = types.ReplyKeyboardMarkup(True, False)
				keyboard.row('Казахский', 'Русский', 'Оба языка')
				keyboard.row('Назад в меню')
				bot.send_message(message.chat.id, 'Укажите языки, на которых Вы говорите', reply_markup=keyboard)
			else:
				bot.send_message(message.chat.id, 'Неправильный ввод!')
				return
			mode += 1
		elif mode == 6:
			status = seeker.worker_or_student
			if message.text == 'Другое...':
				if status == 'student':
					bot.send_message(message.chat.id, 'Напишите название места где Вы учитесь')
				elif status == 'worker':
					bot.send_message(message.chat.id, 'Напишите сферу деятельности, в которой Вы работаете')
			else:
				seeker.study_or_work_place = message.text
				mode += 1
				keyboard = types.ReplyKeyboardMarkup(True, False)
				if status == 'student':
					keyboard.row('Жаворонок', 'Сова')
					keyboard.row('🔙Назад в меню')
					bot.send_message(message.chat.id, 'Какой у Вас режим?', reply_markup=keyboard)
				elif status == 'worker':
					keyboard.row('С утра до вечера', 'С утра')
					keyboard.row('Ночью', 'Вахтовые смены')
					keyboard.row('День-Ночь', '🔙Назад в меню')
					bot.send_message(message.chat.id, 'В какое время Вы работаете?', reply_markup=keyboard)
		elif mode == 7:
			seeker.sleeping_mode = message.text
			mode += 1
			keyboard = types.ReplyKeyboardMarkup(True, False)
			keyboard.row('Казахский', 'Русский', 'Оба языка')
			keyboard.row('Назад в меню')
			bot.send_message(message.chat.id, 'Укажите языки, на которых Вы говорите:', reply_markup=keyboard)
		elif mode == 8:
			lang = message.text
			if lang == 'Казахский' or lang == 'Русский' or lang == 'Оба языка': 
				seeker.langs = message.text
				mode += 1
				keyboard = types.ReplyKeyboardMarkup(True, False)
				keyboard.row('Курю/Не пью', 'Не курю/Пью')
				keyboard.row('Не курю/Не пью', 'Курю/Пью')
				keyboard.row('🔙Назад в меню')
				bot.send_message(message.chat.id, 'Вредные привычки', reply_markup=keyboard)
			else:
				bot.send_message(message.chat.id, 'Неправильный ввод!')
		elif mode == 9:
			seeker.bad_habits = message.text
			mode += 1
			keyboard = types.ReplyKeyboardMarkup(True, True)
			keyboard.row('Алматинский', 'Байконурский')
			keyboard.row('Есильский', 'Сарыаркинский')
			keyboard.row('🔙Назад в меню')
			bot.send_message(message.chat.id, 'Желаемый район города', reply_markup = keyboard)
		elif mode == 10:
			distr = message.text
			if distr == 'Алматинский' or distr == 'Байконурский' or distr == 'Есильский' or distr == 'Сарыаркинский':
				seeker.distr = message.text
				mode += 1
				bot.send_message(message.chat.id, 'Уточните возле чего вам удобно жить(название \
				микрорайона, магазин, бизнес-центр, пересечение улиц, достопримечательность)')
			else:
				bot.send_message(message.chat.id, 'Неправильный ввод!')
		elif mode == 11:
			seeker.near_what = message.text
			mode += 1
			keyboard = types.ReplyKeyboardMarkup(True, True)
			keyboard.row('до 20.000 тенге', 'от 20.000 до 30.000 тенге')
			keyboard.row('от 30.000 до 40.000 тенге', 'от 40.000 до 50.000 тенге')
			keyboard.row('выше 50.000 тенге', '🔙Назад в меню')
			bot.send_message(message.chat.id, 'Желательная цена', reply_markup=keyboard)
		elif mode == 12:
			seeker.price = message.text
			keyboard = types.ReplyKeyboardMarkup(True, True)
			keyboard.row('Отдельную комнату', 'Можно с кем-нибудь в комнате')
			keyboard.row('Оба варианта')
			keyboard.row('🔙Назад в меню')
			bot.send_message(message.chat.id, 'Я ищу...', reply_markup=keyboard)
			mode += 1
		elif mode == 13:
			seeker.seeking_for = message.text
			mode += 1
			bot.send_message(message.chat.id, 'Расскажите о себе (интересы, хобби, путешествия, книги, фильмы)')
		elif mode == 14:
			seeker.interest = message.text
			mode += 1
			bot.send_message(message.chat.id, 'Введите ваш номер телефона\n(пример: 8-ххх-ххх-хх-хх)')
		elif mode == 15:
			num = message.text
			digits = 0
			correct = True
			for a in num:
				if a.isdigit():
					digits += 1
				elif a != '-':
					correct = False
			if digits != 11:
				correct = False
			if not correct:
				bot.send_message(message.chat.id, 'Неправильный ввод!')
				return
			seeker.phone_num = message.text
			bot.send_message(message.chat.id, 'Отправьте своё селфи')
			mode += 1
		elif mode == 16:
			bot.send_message(message.chat.id, 'Загрузите фотографию')
	elif offerer_st == True:
		if mode == 1:
			distr = message.text
			if distr == 'Алматинский' or distr == 'Байконурский' or distr == 'Есильский' or distr == 'Сарыаркинский':
				offerer.distr = message.text
				mode = 2
				keyboard = types.ReplyKeyboardMarkup(True, True)
				keyboard.row('🔙Назад в меню')
				bot.send_message(message.chat.id, 'Укажите ваш точный адрес', reply_markup=keyboard)
			else:
				bot.send_message(message.chat.id, 'Неправильный ввод!')
		elif mode == 2:
			offerer.chat_id = message.chat.id
			offerer.address = message.text
			mode = 3
			bot.send_message(message.chat.id, 'Цена аренды в тенге:')
		elif mode == 3:
			price = message.text
			if price.isdigit() == True:
				offerer.price = int(message.text)
				mode = 4
				bot.send_message(message.chat.id, 'Количество комнат в вашей квартире')
			else:
				bot.send_message(message.chat.id, 'Неправильный ввод! Введите целое число')
		elif mode == 4:
			room_num = message.text
			if room_num.isdigit() == True:
				offerer.room_num = int(message.text)
				mode = 5
				bot.send_message(message.chat.id, 'Количество людей для заселения')
			else:
				bot.send_message(message.chat.id, 'Неправильный ввод! Введите целое число')
		elif mode == 5:
			sleep_places = message.text
			if sleep_places.isdigit() == True:
				offerer.sleep_places = int(message.text)
				mode = 6
				bot.send_message(message.chat.id, 'Описание вашей квартиры/комнаты (этаж, площадь, \
				интернет, мебель, бытовая техника)')
			else:
				bot.send_message(message.chat.id, 'Неправильный ввод! Введите целое число')
		elif mode == 6:
			offerer.description = message.text
			mode = 7
			bot.send_message(message.chat.id, 'Ваш номер телефона:')
		elif mode == 7:
			offerer.phone_num = message.text
			mode += 1
			bot.send_message(message.chat.id, 'Загрузите фото вашей квартиры')
		elif mode == 8:
			bot.send_message(message.chat.id, 'Загрузите фото!')
	elif search_profile == True:
		if mode == 1:
			distr = message.text
			if distr == 'Алматинский' or distr == 'Байконурский' or distr == 'Есильский' or distr == 'Сарыаркинский':
				seeker.distr = message.text
				mode += 1
				keyboard = types.ReplyKeyboardMarkup(True, True)
				keyboard.row('до 20.000 тенге', 'от 20.000 до 30.000 тенге')
				keyboard.row('от 30.000 до 40.000 тенге', 'от 40.000 до 50.000 тенге')
				keyboard.row('выше 50.000 тенге', '🔙Назад в меню')
				bot.send_message(message.chat.id, 'Теперь укажите желаемую стоимость аренды.', reply_markup=keyboard)
			else:
				bot.send_message(message.chat.id, 'Неправильный ввод!')
		elif mode == 2:
			seeker.price = message.text
			profiles = db.get_profiles_by_filters(seeker.distr, seeker.price)
			seeker = Seeker()
			search_profile = False
			mode = 0
			profile = profiles[cur_profile]
			cur_profile += 1
			keyboard = types.InlineKeyboardMarkup()
			if cur_profile + 1 <= len(profiles) and cur_profile > 1:
				button1 = types.InlineKeyboardButton('Следующий >>', callback_data = 'profile_next')
				button2 = types.InlineKeyboardButton('<< Предыдущий', callback_data = 'profile_prev')
				keyboard.row(button2, button1)
			elif cur_profile > 1:
				button = types.InlineKeyboardButton('<< Предыдущий профиль', callback_data = 'profile_prev')
				keyboard.add(button)
			else:
				button = types.InlineKeyboardButton('Следующий профиль >>', callback_data = 'profile_next')
				keyboard.add(button)
			if profile[2] > 1000:
				age = str(int(profile[2]/100)) + '-' + str(profile[2]%100)
			else:
				age = profile[2]
			if profile[5] == 'student':
				work = 'студент'
			else:
				work = 'работник'
			cap = '*Имя:* '+ profile[1] + '\n' + '*Возраст:* ' + str(age) + '\n' + \
			 '*Откуда родом:* '+ profile[3] + '\n' + '*Пол:* ' + profile[4] + '\n' + \
			 '*Работник или студент:* ' + work + '\n' + '*Место:*' + profile[6] + \
			 '\n' + '*Режим сна:* '+ profile[7] + '\n' + '*Языки:* ' + profile[8] + '\n' + '*О себе:* ' + profile[13]
			photo_id = db.get_profile_photo(profile[0])
			if photo_id == '0':
				bot.send_message(message.chat.id, cap, reply_markup = keyboard, parse_mode = 'Markdown')
			else: 
				photo = photos.download_photo(photo_id)
				bot.send_photo(message.chat.id, photo, caption = cap, reply_markup = keyboard, parse_mode = 'Markdown')
	elif search_flat == True:
		if mode == 1:
			distr = message.text
			if distr == 'Алматинский' or distr == 'Байконурский' or distr == 'Есильский' or distr == 'Сарыаркинский':
				offerer.distr = message.text
				mode += 1
				bot.send_message(message.chat.id, 'В какую стоимость вы ищете квартиру?\n(в тенге)')
			else:
				bot.send_message(message.chat.id, 'Неправильный ввод!')
		elif mode == 2:
			price = message.text
			if price.isdigit() == True:
				offerer.price = int(message.text)
			else:
				bot.send_message(message.chat.id, 'Неправильный ввод! Введите целое число')
			flat_matches = db.get_flats_by_filters(offerer.distr, offerer.price)
			mode = 0
			offerer = Offerer()
			flat = flat_matches[cur_flat]
			cur_flat += 1
			keyboard = types.InlineKeyboardMarkup()
			if flat[9] > 0:
				button = types.InlineKeyboardButton('Просмотреть профили соседей', callback_data = 'book_profiles')
				keyboard.add(button)
			if cur_flat + 1 <= len(flat_matches) and cur_flat > 1:
				button1 = types.InlineKeyboardButton('Следующая >>', callback_data = 'flat_next')
				button2 = types.InlineKeyboardButton('<< Предыдущая', callback_data = 'flat_prev')
				keyboard.row(button2, button1)
			elif cur_flat > 1:
				button = types.InlineKeyboardButton('<< Предыдущая квартира', callback_data = 'flat_prev')
				keyboard.add(button)
			else:
				button = types.InlineKeyboardButton('Следующая квартира >>', callback_data = 'flat_next')
				keyboard.add(button)
			cap = '*Расположение квартиры:* '+ flat[1] + ' район, ' + flat[2] + '\n' + \
			 '*Цена аренды:* '+ str(flat[3]) + '\n' + '*Количество комнат:* ' + str(flat[4]) + '\n' + \
			 '*Количество спальных мест:* ' + str(flat[5]) + '\n' + '*Стоимость аренды на одного человека:*' + str(flat[6]) + \
			 '\n' + '*Описание:* '+ flat[7] + '\n' + '*Номер телефона:* ' + flat[8] + '\n' + '*Забронировали* ' + str(flat[9]) + ' *человек*'
			photo_id = db.get_flat_photo_file_id(flat[0])
			if photo_id == '0':
				bot.send_message(message.chat.id, cap, reply_markup = keyboard, parse_mode = 'Markdown')
			else: 
				photo = photos.download_photo(photo_id)
				bot.send_photo(message.chat.id, photo, caption = cap, reply_markup = keyboard, parse_mode = 'Markdown')
	elif change_st > 0:
		if change_st == 1:
			name = message.text
			db.change_name(message.chat.id, name)
			bot.send_message(message.chat.id, 'Ваше Имя успешно изменено!')
			profile = db.get_profile(message.chat.id)
			if profile[2] > 1000:
				age = str(int(profile[2]/100)) + '-' + str(profile[2]%100)
			else:
				age = profile[2]
			if profile[5] == 'student':
				work = 'студент'
			else:
				work = 'работник'
			keyboard = types.InlineKeyboardMarkup()
			button1 = types.InlineKeyboardButton('Изменить Имя', callback_data = 'change_name')
			button2 = types.InlineKeyboardButton('Изменить Возраст', callback_data = 'change_age')
			button3 = types.InlineKeyboardButton('Изменить\nОткуда Родом', callback_data = 'change_homeland')
			button4 = types.InlineKeyboardButton('Изменить О себе', callback_data = 'change_desc')
			keyboard.row(button1, button2)
			keyboard.row(button3, button4)
			cap = '*Имя:* '+ profile[1] + '\n' + '*Возраст:* ' + str(age) + '\n' + \
			 '*Откуда родом:* '+ profile[3] + '\n' + '*Пол:* ' + profile[4] + '\n' + \
			 '*Работник или студент:* ' + work + '\n' + '*Место:* ' + profile[6] + \
			 '\n' + '*Режим сна:* '+ profile[7] + '\n' + '*Языки:* ' + profile[8] + '\n' + '*О себе:* ' + profile[13]
			photo_id = db.get_profile_photo(profile[0])
			if photo_id == '0':
				bot.edit_message_text(chat_id = message.chat.id, message_id = last_mess_id, text = cap, reply_markup = keyboard, parse_mode = 'Markdown')
			else: 
				bot.edit_message_caption(chat_id = message.chat.id, message_id = last_mess_id, caption = cap, reply_markup=keyboard, parse_mode = 'Markdown')
			change_st = 0
		elif change_st == 2:
			age = message.text
			if not age.isdigit():
				bot.send_message(message.chat.id, 'Введите целое число!')
				return
			db.change_age(message.chat.id, age)
			bot.send_message(message.chat.id, 'Ваш возраст успешно изменен!')
			profile = db.get_profile(message.chat.id)
			if profile[2] > 1000:
				age = str(int(profile[2]/100)) + '-' + str(profile[2]%100)
			else:
				age = profile[2]
			if profile[5] == 'student':
				work = 'студент'
			else:
				work = 'работник'
			keyboard = types.InlineKeyboardMarkup()
			button1 = types.InlineKeyboardButton('Изменить Имя', callback_data = 'change_name')
			button2 = types.InlineKeyboardButton('Изменить Возраст', callback_data = 'change_age')
			button3 = types.InlineKeyboardButton('Изменить\nОткуда Родом', callback_data = 'change_homeland')
			button4 = types.InlineKeyboardButton('Изменить О себе', callback_data = 'change_desc')
			keyboard.row(button1, button2)
			keyboard.row(button3, button4)
			cap = '*Имя:* '+ profile[1] + '\n' + '*Возраст:* ' + str(age) + '\n' + \
			 '*Откуда родом:* '+ profile[3] + '\n' + '*Пол:* ' + profile[4] + '\n' + \
			 '*Работник или студент:* ' + work + '\n' + '*Место:* ' + profile[6] + \
			 '\n' + '*Режим сна:* '+ profile[7] + '\n' + '*Языки:* ' + profile[8] + '\n' + '*О себе:* ' + profile[13]
			photo_id = db.get_profile_photo(profile[0])
			if photo_id == '0':
				bot.edit_message_text(chat_id = message.chat.id, message_id = last_mess_id, text = cap, reply_markup = keyboard, parse_mode = 'Markdown')
			else: 
				bot.edit_message_caption(chat_id = message.chat.id, message_id = last_mess_id, caption = cap, reply_markup=keyboard, parse_mode = 'Markdown')
			change_st = 0
		elif change_st == 3:
			homeland = message.text
			db.change_homeland(message.chat.id, homeland)
			bot.send_message(message.chat.id, 'Ваше место откуда Вы родом успешно изменено!')
			profile = db.get_profile(message.chat.id)
			if profile[2] > 1000:
				age = str(int(profile[2]/100)) + '-' + str(profile[2]%100)
			else:
				age = profile[2]
			if profile[5] == 'student':
				work = 'студент'
			else:
				work = 'работник'
			keyboard = types.InlineKeyboardMarkup()
			button1 = types.InlineKeyboardButton('Изменить Имя', callback_data = 'change_name')
			button2 = types.InlineKeyboardButton('Изменить Возраст', callback_data = 'change_age')
			button3 = types.InlineKeyboardButton('Изменить\nОткуда Родом', callback_data = 'change_homeland')
			button4 = types.InlineKeyboardButton('Изменить О себе', callback_data = 'change_desc')
			keyboard.row(button1, button2)
			keyboard.row(button3, button4)
			cap = '*Имя:* '+ profile[1] + '\n' + '*Возраст:* ' + str(age) + '\n' + \
			 '*Откуда родом:* '+ profile[3] + '\n' + '*Пол:* ' + profile[4] + '\n' + \
			 '*Работник или студент:* ' + work + '\n' + '*Место:* ' + profile[6] + \
			 '\n' + '*Режим сна:* '+ profile[7] + '\n' + '*Языки:* ' + profile[8] + '\n' + '*О себе:* ' + profile[13]
			photo_id = db.get_profile_photo(profile[0])
			if photo_id == '0':
				bot.edit_message_text(chat_id = message.chat.id, message_id = last_mess_id, text = cap, reply_markup = keyboard, parse_mode = 'Markdown')
			else: 
				bot.edit_message_caption(chat_id = message.chat.id, message_id = last_mess_id, caption = cap, reply_markup=keyboard, parse_mode = 'Markdown')
			change_st = 0
		elif change_st == 4:
			desc = message.text
			db.change_desc(message.chat.id, desc)
			bot.send_message(message.chat.id, 'Ваше описание о себе успешно изменено!')
			profile = db.get_profile(message.chat.id)
			if profile[2] > 1000:
				age = str(int(profile[2]/100)) + '-' + str(profile[2]%100)
			else:
				age = profile[2]
			if profile[5] == 'student':
				work = 'студент'
			else:
				work = 'работник'
			keyboard = types.InlineKeyboardMarkup()
			button1 = types.InlineKeyboardButton('Изменить Имя', callback_data = 'change_name')
			button2 = types.InlineKeyboardButton('Изменить Возраст', callback_data = 'change_age')
			button3 = types.InlineKeyboardButton('Изменить\nОткуда Родом', callback_data = 'change_homeland')
			button4 = types.InlineKeyboardButton('Изменить О себе', callback_data = 'change_desc')
			keyboard.row(button1, button2)
			keyboard.row(button3, button4)
			cap = '*Имя:* '+ profile[1] + '\n' + '*Возраст:* ' + str(age) + '\n' + \
			 '*Откуда родом:* '+ profile[3] + '\n' + '*Пол:* ' + profile[4] + '\n' + \
			 '*Работник или студент:* ' + work + '\n' + '*Место:* ' + profile[6] + \
			 '\n' + '*Режим сна:* '+ profile[7] + '\n' + '*Языки:* ' + profile[8] + '\n' + '*О себе:* ' + profile[13]
			photo_id = db.get_profile_photo(profile[0])
			if photo_id == '0':
				bot.edit_message_text(chat_id = message.chat.id, message_id = last_mess_id, text = cap, reply_markup = keyboard, parse_mode = 'Markdown')
			else: 
				bot.edit_message_caption(chat_id = message.chat.id, message_id = last_mess_id, caption = cap, reply_markup=keyboard, parse_mode = 'Markdown')
			change_st = 0

@bot.message_handler(content_types = ['photo'])
def upload_photo(message):
	global mode, offerer_st, offerer, seeker, seeker_st, flat_matches, profiles, seeker_search_st
	if offerer_st == True and mode == 8:
		offerer.photo_id.append(photos.document_handler(message, bot))
		db.offerer_insert(offerer)
		bot.send_message(message.chat.id, 'Ваша квартира добавлена!')
		offerer_st = False
		offerer = Offerer()
		mode = 0
	elif (seeker_st == True or seeker_search_st == True) and mode == 16:
		seeker.photo_id.append(photos.document_handler(message, bot))
		db.seeker_insert(seeker)
		bot.send_message(message.chat.id, 'Ваша анкета сформирована!')
		bot.send_chat_action(message.chat.id, 'typing')
		time.sleep(2)
		profile = db.get_profile(message.chat.id)
		if profile[2] > 1000:
			age = str(int(profile[2]/100)) + '-' + str(profile[2]%100)
		else:
			age = profile[2]
		if profile[5] == 'student':
			work = 'студент'
		else:
			work = 'работник'
		cap = '*Имя:* '+ profile[1] + '\n' + '*Возраст:* ' + str(age) + '\n' + \
		 '*Откуда родом:* '+ profile[3] + '\n' + '*Пол:* ' + profile[4] + '\n' + \
		 '*Работник или студент:* ' + work + '\n' + '*Место:* ' + profile[6] + \
		 '\n' + '*Режим сна:* '+ profile[7] + '\n' + '*Языки:* ' + profile[8] + '\n' + '*О себе:* ' + profile[13]
		photo_id = db.get_profile_photo(profile[0])
		if photo_id == '0':
			bot.send_message(message.chat.id, cap, parse_mode = 'Markdown')
		else: 
			photo = photos.download_photo(photo_id)
			bot.send_photo(message.chat.id, photo, caption = cap, parse_mode = 'Markdown')
		bot.send_chat_action(message.chat.id, 'typing')
		time.sleep(2)
		bot.send_message(message.chat.id, 'Если Вы желаете изменить анкету, Вы можете сделать это в разделе \'Мои объявления\' в главном меню /menu')
		time.sleep(2)
		if seeker_st == True:
			bot.send_message(message.chat.id, '*Мы подбираем для Вас квартиры с идеальными соседями...*', parse_mode = "Markdown")
			bot.send_chat_action(message.chat.id, 'typing')
			time.sleep(5)
			seeker_st = False
			flat_matches = db.get_matches(seeker)
			seeker = Seeker()
			keyboard = types.InlineKeyboardMarkup();
			button = types.InlineKeyboardButton('Показать', callback_data = 'matches_out')
			keyboard.add(button)
			bot.send_message(message.chat.id, 'Квартиры найдены!', reply_markup = keyboard)
		elif seeker_search_st == True:
			bot.send_message(message.chat.id, '*Мы подбираем для Вас идеальных людей для сожительства...*', parse_mode = 'Markdown')
			bot.send_chat_action(message.chat.id, 'typing')
			time.sleep(5)
			seeker_search_st = False
			profiles = db.get_profiles_by_filters(seeker.distr, seeker.price)
			seeker = Seeker()
			keyboard = types.InlineKeyboardMarkup();
			button = types.InlineKeyboardButton('Показать', callback_data = 'profile_next')
			keyboard.add(button)
			bot.send_message(message.chat.id, 'Люди найдены!', reply_markup = keyboard)
bot.polling(none_stop=True)
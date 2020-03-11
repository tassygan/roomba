import telebot
import time
import urllib
from telebot import types
from database import SQL
from users import Seeker
import photos

token = "1149025408:AAHPU-RBBk_DPdIxl5dmC53U3EjJeu708To" #mainbot
#token = "1012837410:AAFY0lxwBFgWPIbRO-lO_MumXnlYJl-1ReQ" #testbot
bot = telebot.TeleBot(token)
db = SQL()
allvars = {}

class Settings:
	def __init__(self):
		self.mode = 0
		self.cur_profile = 0
		self.change_st = 0
		self.last_mess_id = 0
		self.seeker = Seeker()
		self.profiles = ""
		self.seeker_st = False
		self.seeker_search_st = False
		self.search_profile = False
		self.feedback_st = False		
def add_new_user(chat_id):
	global allvars
	if chat_id in allvars.keys():
		return 
	a = Settings()
	allvars[chat_id] = a;
def default_vars(chat_id):
	global allvars
	allvars[chat_id] = Settings()

@bot.message_handler(commands = ['start'])
def start(message):
	add_new_user(message.chat.id)
	default_vars(message.chat.id)
	keyboard = types.ReplyKeyboardMarkup(True, False)
	keyboard.row('Добавить новое объявление', 'Просмотреть объявления')
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
	default_vars(message.chat.id)
	keyboard = types.ReplyKeyboardMarkup(True, False)
	keyboard.row('Добавить новое объявление', 'Просмотреть объявления')
	keyboard.row('Мои объявления', 'Обратная связь')
	bot.send_message(message.chat.id, 'Главное меню', reply_markup=keyboard)

def profile_info(profile):
	if profile[20] == True:
		text = '*Ищет людей для подселения в свою квартиру*\n*Расположение квартиры:* ' + profile[9] + ' район\n\n'
	else:
		text = ''
	if profile[2] > 1000:
		age = str(int(profile[2]/100)) + '-' + str(profile[2]%100)
	else:
		age = str(profile[2])
	age += ' лет'
	if profile[5] == 'student':
		work = '*Студент.* Учусь в '
	else:
		work = 'Работаю в сфере'
	place = ""
	if profile[8] == 'Казахский':
		place = 'Говорю на казахском'
	elif profile[8] == 'Русский':
		place = 'Говорю на русском'
	else:
		place = 'Говорю и на казахском, и на русском'
	food = ''

	if len(profile) > 20 and profile[21] is not None:
		if profile[21] is True:
			food = '*Умеею готовить: *' + 'Да\n'
		else:
			food = '*Умеею готовить: *' + 'Нет\n'

	text += '*Имя:* '+ profile[1] + '\n' + '*Возраст:* ' + str(age) + '\n' + \
			'*Родом с* '+ profile[3] + '\n' + '*Пол:* ' + profile[4] + '\n' + work + \
			profile[6] + '\n' + '*Режим сна:* '+ profile[7] + '\n' + place + '\n' + food + \
			'*Вредные привычки: *' + profile[18] + '\n' + '*О себе:* ' + profile[13]
	if profile[19] is not None:
		text += '\n@'+profile[19]
	return text

@bot.message_handler(func=lambda message:message.text is not None and len(message.text) > 6 and message.text[:7] == '/advert')
def adverts(message):
	if message.text[7] == '1':
		profile_id = message.text[8:]
		profile = db.get_profile_by_id(profile_id)
		cap = profile_info(profile)
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
def delete_ads(message):
	if message.text[7] == '2':
		flat_id = message.text[8:]
		db.offerer_delete(flat_id)
		bot.send_message(message.chat.id, 'Ваше объявление удалено.')

@bot.callback_query_handler(func=lambda call:True)
def callback(call):
	global allvars
	add_new_user(call.message.chat.id)
	u = allvars[call.message.chat.id]
	if call.message:
		if call.data == 'profile_next' or call.data == 'profile_prev' or call.data == 'rematch_profiles':
			bot.delete_message(call.message.chat.id, call.message.message_id)
			if call.data == 'rematch_profiles':
				profile = db.get_profile(call.message.chat.id)
				seeker = Seeker(profile)
				u.profiles = db.get_profiles_by_filters(seeker)
			if call.data == 'profile_prev':
				u.cur_profile -= 2
			if u.profiles is None or u.cur_profile >= len(u.profiles) or u.cur_profile < 0:
				bot.send_message(call.message.chat.id, 'Ошибка. Попробуйте еще раз.')
				return
			profile = u.profiles[u.cur_profile]
			u.cur_profile += 1
			keyboard = types.InlineKeyboardMarkup()
			if u.cur_profile + 1 <= len(u.profiles) and u.cur_profile > 1:
				button1 = types.InlineKeyboardButton('Следующий >>', callback_data = 'profile_next')
				button2 = types.InlineKeyboardButton('<< Предыдущий', callback_data = 'profile_prev')
				keyboard.row(button2, button1)
			elif u.cur_profile > 1:
				button = types.InlineKeyboardButton('<< Предыдущий профиль', callback_data = 'profile_prev')
				keyboard.add(button)
			elif u.cur_profile + 1 <= len(u.profiles):
				button = types.InlineKeyboardButton('Следующий профиль >>', callback_data = 'profile_next')
				keyboard.add(button)
			cap = profile_info(profile)
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
			U.change_st = 1
			U.last_mess_id = call.message.message_id
		elif call.data == 'change_age':
			bot.send_message(call.message.chat.id, 'Введите новый возраст\n(целое число)')
			U.change_st = 2
			U.last_mess_id = call.message.message_id
		elif call.data == 'change_homeland':
			bot.send_message(call.message.chat.id, 'Введите новое место откуда Вы родом\n(регион, город)')
			u.change_st = 3
			u.last_mess_id = call.message.message_id
		elif call.data == 'change_desc':
			bot.send_message(call.message.chat.id, 'Напишите новое описание о себе')
			u.change_st = 4
			u.last_mess_id = call.message.message_id

@bot.message_handler(content_types = ['text'])
def name_insert_data(message):
	global allvars
	add_new_user(message.chat.id)
	u = allvars[message.chat.id]
	if message.text == 'Добавить новое объявление':
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
		u.seeker_search_st = True
		u.mode = 1
	elif message.text == '🔙Назад в меню':
		default_vars(message.chat.id)
		keyboard = types.ReplyKeyboardMarkup(True, True)
		keyboard.row('Добавить новое объявление', 'Просмотреть объявления')
		keyboard.row('Мои объявления', 'Обратная связь')
		bot.send_message(message.chat.id, 'Главное меню', reply_markup=keyboard)
	elif message.text == 'Просмотреть объявления':
		u.search_profile = True
		u.mode = 1
		u.seeker = Seeker()
		bot.send_message(message.chat.id, 'Для более удобного показа профилей прошу вас указать район города и желаемую стоимость аренды')
		time.sleep(1)
		keyboard = types.ReplyKeyboardMarkup(True, True)
		keyboard.row('Алматинский', 'Байконурский')
		keyboard.row('Есильский', 'Сарыаркинский')
		keyboard.row('🔙Назад в меню')
		bot.send_message(message.chat.id, 'Для начала укажите желаемый район', reply_markup = keyboard)
	elif message.text == 'Мои объявления':
		profile = db.get_profile(message.chat.id)
		if profile is None:
			bot.send_message(message.chat.id, 'У вас нет активных объявлений.')
			return
		text = '*Ваши объявления*\n\n'
		if profile is not None:
			text += '*Поиск квартиры*\n'
			text += '📄Подробнее: /advert1' + str(profile[0]) + '\n\n'
		bot.send_message(message.chat.id, text, parse_mode = 'Markdown')
	elif message.text == 'Обратная связь' or u.feedback_st == True:
		if u.feedback_st == False:
			u.feedback_st = True
			keyboard = types.ReplyKeyboardMarkup(True, True)
			keyboard.row('🔙Назад в меню')
			bot.send_message(message.chat.id, 'Оставьте свой отзыв или предложение, отправив нам сообщение!', reply_markup=keyboard)
		else:
			bot.send_message(365391038, str(message.text) + '\nот ' + str(message.from_user.last_name) + ' ' + str(message.from_user.first_name) + ' @' + str(message.from_user.username) )
			default_vars()
			keyboard = types.ReplyKeyboardMarkup(True, True)
			keyboard.row('Добавить новое объявление', 'Просмотреть объявления')
			keyboard.row('Мои объявления', 'Обратная связь')
			bot.send_message(message.chat.id, 'Спасибо за оставленный отзыв!', reply_markup=keyboard)
	elif u.seeker_st == True or u.seeker_search_st == True:	
		if u.mode == 1:
			u.seeker.chat_id = message.chat.id
			u.seeker.name = message.text
			u.mode = 2
			keyboard = types.ReplyKeyboardMarkup(True, True)
			keyboard.row('🔙Назад в меню')
			bot.send_message(message.chat.id, 'Введите свой возраст.', reply_markup = keyboard)
		elif u.mode == 2:
			age = message.text
			if not age.isdigit() or int(age) > 110 or int(age) < 14:
				bot.send_message(message.chat.id, 'Неправильный ввод! Введите целое число.')
				return
			u.seeker.age = int(age)
			u.mode += 1
			keyboard = types.ReplyKeyboardMarkup(True, True)
			keyboard.row('🔙Назад в меню')
			bot.send_message(message.chat.id, 'Откуда Вы?\n(регион, город)', reply_markup=keyboard)
		elif u.mode == 3:
			u.seeker.homeland = message.text
			u.mode += 1
			keyboard = types.ReplyKeyboardMarkup(True, True)
			keyboard.row('Мужчина', 'Женщина')
			keyboard.row('🔙Назад в меню')
			bot.send_message(message.chat.id, 'Укажите Ваш пол', reply_markup = keyboard)
		elif u.mode == 4:
			if message.text == 'Мужчина':
				u.seeker.gender = 'Мужчина'
			elif message.text == 'Женщина':
				u.seeker.gender = 'Женщина'
			else:
				keyboard = types.ReplyKeyboardMarkup(True, True)
				keyboard.row('Мужчина', 'Женщина')
				keyboard.row('🔙Назад в меню')
				bot.send_message(message.chat.id, 'Неправильный ввод! Прошу Вас воспользоваться клавиатурой', reply_markup = keyboard)
				return
			u.mode += 1
			keyboard = types.ReplyKeyboardMarkup(True, True)
			keyboard.row('учусь', 'работаю', 'не учусь и не работаю')
			keyboard.row('🔙Назад в меню')
			bot.send_message(message.chat.id, 'Вы учитесь или работаете', reply_markup = keyboard)
		elif u.mode == 5:
			keyboard = types.ReplyKeyboardMarkup(True, True)
			if message.text == 'учусь':
				u.seeker.worker_or_student = 'student'
				keyboard.row('🔙Назад в меню')
				keyboard.row('Astana IT University', 'КазГЮА')
				keyboard.row('Аграрка', 'Назарбаев Университет')
				keyboard.row('Евразийский НУ', 'Университет Астаны')
				keyboard.row('Медунивер', 'Коледж')
				keyboard.row('Другое...')
				bot.send_message(message.chat.id, 'Где Вы учитесь?', reply_markup=keyboard)
			elif message.text == 'работаю':
				u.seeker.worker_or_student = 'worker'
				keyboard.row('🔙Назад в меню')
				keyboard.row('Строительство', 'Торговля')
				keyboard.row('IT', 'Образование')
				keyboard.row('Госслужба', 'Работаю на себя')
				keyboard.row('Частная комания', 'Рестораны/кафе')
				keyboard.row('Другое...')
				bot.send_message(message.chat.id, 'Какая у Вас сфера деятельности?', reply_markup=keyboard)
			elif message.text == 'не учусь и не работаю':
				u.seeker.worker_or_student = 'neither'
				u.mode += 2
				keyboard = types.ReplyKeyboardMarkup(True, True)
				keyboard.row('Казахский', 'Русский', 'Оба языка')
				keyboard.row('Назад в меню')
				bot.send_message(message.chat.id, 'Укажите языки, на которых Вы говорите', reply_markup=keyboard)
			else:
				bot.send_message(message.chat.id, 'Неправильный ввод!')
				return
			u.mode += 1
		elif u.mode == 6:
			status = u.seeker.worker_or_student
			if message.text == 'Другое...':
				if status == 'student':
					bot.send_message(message.chat.id, 'Напишите название места где Вы учитесь')
				elif status == 'worker':
					bot.send_message(message.chat.id, 'Напишите сферу деятельности, в которой Вы работаете')
			else:
				u.seeker.study_or_work_place = message.text
				u.mode += 1
				keyboard = types.ReplyKeyboardMarkup(True, True)
				if status == 'student':
					keyboard.row('Жаворонок', 'Сова')
					keyboard.row('🔙Назад в меню')
					bot.send_message(message.chat.id, 'Какой у Вас режим?', reply_markup=keyboard)
				elif status == 'worker':
					keyboard.row('С утра до вечера', 'С утра')
					keyboard.row('Ночью', 'Вахтовые смены')
					keyboard.row('День-Ночь', '🔙Назад в меню')
					bot.send_message(message.chat.id, 'В какое время Вы работаете?', reply_markup=keyboard)
		elif u.mode == 7:
			u.seeker.sleeping_mode = message.text
			u.mode += 1
			keyboard = types.ReplyKeyboardMarkup(True, True)
			keyboard.row('Казахский', 'Русский', 'Оба языка')
			keyboard.row('🔙Назад в меню')
			bot.send_message(message.chat.id, 'Укажите языки, на которых Вы говорите:', reply_markup=keyboard)
		elif u.mode == 8:
			lang = message.text
			if lang == 'Казахский' or lang == 'Русский' or lang == 'Оба языка': 
				u.seeker.langs = message.text
				u.mode += 1
				keyboard = types.ReplyKeyboardMarkup(True, True)
				keyboard.row('Курю/Не пью', 'Не курю/Пью')
				keyboard.row('Не курю/Не пью', 'Курю/Пью')
				keyboard.row('🔙Назад в меню')
				bot.send_message(message.chat.id, 'Вредные привычки', reply_markup=keyboard)
			else:
				bot.send_message(message.chat.id, 'Неправильный ввод!')
				return
		elif u.mode == 9:
			u.seeker.bad_habits = message.text
			u.mode += 1
			keyboard = types.ReplyKeyboardMarkup(True, True)
			keyboard.row('Да', 'Нет')
			keyboard.row('🔙Назад в меню')
			bot.send_message(message.chat.id, 'Умеете ли Вы готовить?', reply_markup=keyboard)
		elif u.mode == 10:
			if message.text == 'Да':
				u.seeker.food = True
			elif message.text == 'Нет':
				u.seeker.food = False
			else:
				bot.send_message(message.chat.id, 'Неправильный ввод!\n(Да/Нет)')
				return
			u.mode += 1
			keyboard = types.ReplyKeyboardMarkup(True, True)
			keyboard.row('Да', 'Нет')
			keyboard.row('🔙Назад в меню')
			bot.send_message(message.chat.id, 'Вы ищете людей на подселение в свою квартиру?', reply_markup=keyboard)
		elif u.mode == 11:
			if message.text == 'Да':
				u.seeker.hata = True
				keyboard = types.ReplyKeyboardMarkup(True, True)
				keyboard.row('Алматинский', 'Байконурский')
				keyboard.row('Есильский', 'Сарыаркинский')
				keyboard.row('🔙Назад в меню')
				bot.send_message(message.chat.id, 'В каком районе находится ваша квартира?', reply_markup = keyboard)
			elif message.text == 'Нет':
				u.seeker.hata = False
				keyboard = types.ReplyKeyboardMarkup(True, True)
				keyboard.row('Алматинский', 'Байконурский')
				keyboard.row('Есильский', 'Сарыаркинский')
				keyboard.row('🔙Назад в меню')
				bot.send_message(message.chat.id, 'Желаемый район города', reply_markup = keyboard)
			else:
				bot.send_message(message.chat.id, 'Неправильный ввод.\n(Да/Нет)')
				return
			u.mode += 1
		elif u.mode == 12:
			distr = message.text
			if distr == 'Алматинский' or distr == 'Байконурский' or distr == 'Есильский' or distr == 'Сарыаркинский':
				u.seeker.distr = message.text
				u.mode += 1
				if u.seeker.hata == True:
					u.mode += 2
					keyboard = types.ReplyKeyboardMarkup(True, True)
					keyboard.row('до 20.000 тенге', 'от 20.000 до 30.000 тенге')
					keyboard.row('от 30.000 до 40.000 тенге', 'от 40.000 до 50.000 тенге')
					keyboard.row('выше 50.000 тенге', '🔙Назад в меню')
					bot.send_message(message.chat.id, 'Стоимость аренды квартиры с одного человека', reply_markup=keyboard)
				else:	
					bot.send_message(message.chat.id, 'Уточните возле чего вам удобно жить(название \
					микрорайона, магазин, бизнес-центр, пересечение улиц, достопримечательность)')
			else:
				bot.send_message(message.chat.id, 'Неправильный ввод!')
		elif u.mode == 13:
			u.seeker.near_what = message.text
			u.mode += 1
			keyboard = types.ReplyKeyboardMarkup(True, True)
			keyboard.row('до 20.000 тенге', 'от 20.000 до 30.000 тенге')
			keyboard.row('от 30.000 до 40.000 тенге', 'от 40.000 до 50.000 тенге')
			keyboard.row('выше 50.000 тенге', '🔙Назад в меню')
			bot.send_message(message.chat.id, 'Желательная цена', reply_markup=keyboard)
		elif u.mode == 14:
			u.seeker.price = message.text
			keyboard = types.ReplyKeyboardMarkup(True, True)
			keyboard.row('Отдельную комнату', 'Можно с кем-нибудь в комнате')
			keyboard.row('Оба варианта')
			keyboard.row('🔙Назад в меню')
			bot.send_message(message.chat.id, 'Я ищу...', reply_markup=keyboard)
			u.mode += 1
		elif u.mode == 15:
			if u.seeker.hata == True:
				u.seeker.price = message.text
			else:
				u.seeker.seeking_for = message.text
			u.mode += 1
			keyboard = types.ReplyKeyboardMarkup(True, True)
			keyboard.row('🔙Назад в меню')
			bot.send_message(message.chat.id, 'Расскажите о себе (интересы, хобби, путешествия, книги, фильмы)',reply_markup=keyboard)
		elif u.mode == 16:
			u.seeker.interest = message.text
			u.mode += 1
			keyboard = types.ReplyKeyboardMarkup(True, True)
			keyboard.row('🔙Назад в меню')
			bot.send_message(message.chat.id, 'Введите ваш номер телефона\n(пример: 8-ххх-ххх-хх-хх)', reply_markup=keyboard)
		elif u.mode == 17:
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
			u.seeker.phone_num = message.text
			keyboard = types.ReplyKeyboardMarkup(True, True)
			keyboard.row('🔙Назад в меню')
			bot.send_message(message.chat.id, 'Отправьте своё селфи', reply_markup=keyboard)
			u.mode += 1
		elif u.mode == 18:
			bot.send_message(message.chat.id, 'Загрузите фотографию')
	elif u.search_profile == True:
		if u.mode == 1:
			distr = message.text
			if distr == 'Алматинский' or distr == 'Байконурский' or distr == 'Есильский' or distr == 'Сарыаркинский':
				u.seeker.distr = message.text
				u.mode += 1
				keyboard = types.ReplyKeyboardMarkup(True, True)
				keyboard.row('до 20.000 тенге', 'от 20.000 до 30.000 тенге')
				keyboard.row('от 30.000 до 40.000 тенге', 'от 40.000 до 50.000 тенге')
				keyboard.row('выше 50.000 тенге', '🔙Назад в меню')
				bot.send_message(message.chat.id, 'Теперь укажите желаемую стоимость аренды.', reply_markup=keyboard)
			else:
				bot.send_message(message.chat.id, 'Неправильный ввод!')
		elif u.mode == 2:
			u.seeker.price = message.text
			u.seeker.chat_id = message.chat.id
			u.seeker.hata = None
			u.profiles = db.get_profiles_by_filters(u.seeker)
			u.seeker = Seeker()
			u.search_profile = False
			u.mode = 0
			if u.profiles is None or u.cur_profile >= len(u.profiles) or u.cur_profile < 0:
				bot.send_message(message.chat.id, 'Ошибка. Попробуйте еще раз.')
				return
			profile = u.profiles[u.cur_profile]
			u.cur_profile += 1
			keyboard = types.InlineKeyboardMarkup()
			if u.cur_profile + 1 <= len(u.profiles) and u.cur_profile > 1:
				button1 = types.InlineKeyboardButton('Следующий >>', callback_data = 'profile_next')
				button2 = types.InlineKeyboardButton('<< Предыдущий', callback_data = 'profile_prev')
				keyboard.row(button2, button1)
			elif u.cur_profile > 1:
				button = types.InlineKeyboardButton('<< Предыдущий профиль', callback_data = 'profile_prev')
				keyboard.add(button)
			elif u.cur_profile + 1 <= len(u.profiles):
				button = types.InlineKeyboardButton('Следующий профиль >>', callback_data = 'profile_next')
				keyboard.add(button)
			cap = profile_info(profile)
			photo_id = db.get_profile_photo(profile[0])
			if photo_id == '0':
				bot.send_message(message.chat.id, cap, reply_markup = keyboard, parse_mode = 'Markdown')
			else: 
				photo = photos.download_photo(photo_id)
				bot.send_photo(message.chat.id, photo, caption = cap, reply_markup = keyboard, parse_mode = 'Markdown')
	elif u.change_st > 0:
		if change_st == 1:
			name = message.text
			db.change_name(message.chat.id, name)
			bot.send_message(message.chat.id, 'Ваше Имя успешно изменено!')
			profile = db.get_profile(message.chat.id)
			keyboard = types.InlineKeyboardMarkup()
			button1 = types.InlineKeyboardButton('Изменить Имя', callback_data = 'change_name')
			button2 = types.InlineKeyboardButton('Изменить Возраст', callback_data = 'change_age')
			button3 = types.InlineKeyboardButton('Изменить\nОткуда Родом', callback_data = 'change_homeland')
			button4 = types.InlineKeyboardButton('Изменить О себе', callback_data = 'change_desc')
			keyboard.row(button1, button2)
			keyboard.row(button3, button4)
			cap = profile_info(profile)
			photo_id = db.get_profile_photo(profile[0])
			if photo_id == '0':
				bot.edit_message_text(chat_id = message.chat.id, message_id = last_mess_id, text = cap, reply_markup = keyboard, parse_mode = 'Markdown')
			else: 
				bot.edit_message_caption(chat_id = message.chat.id, message_id = last_mess_id, caption = cap, reply_markup = keyboard, parse_mode = 'Markdown')
			change_st = 0
		elif change_st == 2:
			age = message.text
			if not age.isdigit():
				bot.send_message(message.chat.id, 'Введите целое число!')
				return
			db.change_age(message.chat.id, age)
			bot.send_message(message.chat.id, 'Ваш возраст успешно изменен!')
			profile = db.get_profile(message.chat.id)
			keyboard = types.InlineKeyboardMarkup()
			button1 = types.InlineKeyboardButton('Изменить Имя', callback_data = 'change_name')
			button2 = types.InlineKeyboardButton('Изменить Возраст', callback_data = 'change_age')
			button3 = types.InlineKeyboardButton('Изменить\nОткуда Родом', callback_data = 'change_homeland')
			button4 = types.InlineKeyboardButton('Изменить О себе', callback_data = 'change_desc')
			keyboard.row(button1, button2)
			keyboard.row(button3, button4)
			cap = profile_info(profile)
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
			keyboard = types.InlineKeyboardMarkup()
			button1 = types.InlineKeyboardButton('Изменить Имя', callback_data = 'change_name')
			button2 = types.InlineKeyboardButton('Изменить Возраст', callback_data = 'change_age')
			button3 = types.InlineKeyboardButton('Изменить\nОткуда Родом', callback_data = 'change_homeland')
			button4 = types.InlineKeyboardButton('Изменить О себе', callback_data = 'change_desc')
			keyboard.row(button1, button2)
			keyboard.row(button3, button4)
			cap = profile_info(profile)
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
			keyboard = types.InlineKeyboardMarkup()
			button1 = types.InlineKeyboardButton('Изменить Имя', callback_data = 'change_name')
			button2 = types.InlineKeyboardButton('Изменить Возраст', callback_data = 'change_age')
			button3 = types.InlineKeyboardButton('Изменить\nОткуда Родом', callback_data = 'change_homeland')
			button4 = types.InlineKeyboardButton('Изменить О себе', callback_data = 'change_desc')
			keyboard.row(button1, button2)
			keyboard.row(button3, button4)
			cap = profile_info(profile)
			photo_id = db.get_profile_photo(profile[0])
			if photo_id == '0':
				bot.edit_message_text(chat_id = message.chat.id, message_id = last_mess_id, text = cap, reply_markup = keyboard, parse_mode = 'Markdown')
			else: 
				bot.edit_message_caption(chat_id = message.chat.id, message_id = last_mess_id, caption = cap, reply_markup=keyboard, parse_mode = 'Markdown')
			change_st = 0
	else:
		bot.send_message(message.chat.id, 'Чтобы выйти в главное меню выполните команду /menu')
@bot.message_handler(content_types = ['photo'])
def upload_photo(message):
	global allvars
	add_new_user(message.chat.id)
	u = allvars[message.chat.id]
	if (u.seeker_st == True or u.seeker_search_st == True) and u.mode == 18:
		u.seeker.photo_id.append(photos.document_handler(message, bot))
		if message.from_user.username is not None:
			u.seeker.telegram_username = message.from_user.username
		db.seeker_insert(u.seeker)
		bot.send_message(message.chat.id, 'Ваша анкета сформирована!')
		bot.send_chat_action(message.chat.id, 'typing')
		time.sleep(2)
		profile = db.get_profile(message.chat.id)
		cap = profile_info(profile)
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
		if u.seeker_st == True:
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
		elif u.seeker_search_st == True:
			bot.send_message(message.chat.id, '*Мы подбираем для Вас идеальных соседов по квартире...*', parse_mode = 'Markdown')
			bot.send_chat_action(message.chat.id, 'typing')
			time.sleep(5)
			u.seeker_search_st = False
			u.profiles = db.get_profiles_by_filters(u.seeker)
			u.seeker = Seeker()
			keyboard = types.InlineKeyboardMarkup();
			button = types.InlineKeyboardButton('Показать', callback_data = 'profile_next')
			keyboard.add(button)
			bot.send_message(message.chat.id, 'Люди найдены!', reply_markup = keyboard)
bot.polling(none_stop=True)
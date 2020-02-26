import telebot
import time
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
seeker = Seeker()
offerer = Offerer()
flat_matches = ""
flat_profiles = ""

flat_profile_st = False
seeker_st = False
sleep_places_st = False
offerer_st = False

@bot.message_handler(commands = ['start'])
def start(message):
	keyboard = types.ReplyKeyboardMarkup(True, True)
	keyboard.row('📋Добавить новое объявление')
	bot.send_message(message.chat.id, 'roomba - Hайди того самого соседа!\n\n'
	'@rroomba это:\n\n'
	'- поиск соседей по интересам\n'
	'- аренда комнат/квартир\n'
	'- взять на подселение\n'
	'- поиск компаньона для совместной аренды\n\n'
	'Соседство в стиле "Румба"!\n\n'
	'Для подачи объявления пишите на: @rroomba_info\n'
	'Правила размещения по ссылке: @rroomba_rules\n\n', reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call:True)
def callback(call):
	global mode, seeker_st, offerer_st, flat_id, flat_profile_st, flat_matches, cur_flat, sleep_places_st, cur_profile, flat_profiles
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
		elif call.data == 'matches_out' or call.data == 'matches_out_prev':
			flat_profile_st = False
			bot.delete_message(call.message.chat.id, call.message.message_id)
			if call.data == 'matches_out_prev':
				cur_flat -= 2
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
			if cur_flat + 1 <= len(flat_matches):
				button = types.InlineKeyboardButton('Следующая квартира >>', callback_data = 'matches_out')
				keyboard.add(button)
			if cur_flat > 1:
				button = types.InlineKeyboardButton('<< Предыдущая квартира', callback_data = 'matches_out_prev')
				keyboard.add(button)
			cap = '*Расположение квартиры:* '+ flat[1] + ' район, ' + flat[2] + '\n' + \
			 '*Цена аренды:* '+ str(flat[3]) + '\n' + '*Количество комнат:* ' + str(flat[4]) + '\n' + \
			 '*Количество спальных мест:* ' + str(flat[5]) + '\n' + '*Стоимость аренды на одного человека:*' + str(flat[6]) + \
			 '\n' + '*Описание:* '+ flat[7] + '\n' + '*Номер телефона:* ' + flat[8] + '\n' + '*Забронировали* ' + str(flat[9]) + ' *человек*'
			photo_id = db.get_flat_photo_file_id(flat_matches[cur_flat-1][0])
			if photo_id[0][0] == '0':
				bot.send_message(call.message.chat.id, cap, reply_markup = keyboard, parse_mode = 'Markdown')
			else: 
				photo = 'https://drive.google.com/file/d/'+str(photo_id[0][0])+'/view?usp=sharing'
				bot.send_photo(call.message.chat.id, photo, caption = cap, reply_markup = keyboard, parse_mode = 'Markdown')
		elif call.data == 'book_flat':
			db.book_flat(call.message.chat.id, flat_matches[cur_flat-1][0])
			if flat_matches[cur_flat-1][9] == 0:
				bot.send_message(flat_matches[cur_flat-1][11], 'Ваша квартира была забронирована одним человеком!')
			else:
				bot.send_message(flat_matches[cur_flat-1][11], 'Ваша квартира была забронирована еще одним человеком!')
			bot.send_message(call.message.chat.id, 'Квартира успешно забронирована!')
		elif call.data == 'book_profiles' or call.data == 'book_profiles_prev':
			if not flat_profile_st: 
				flat_profiles = db.get_flat_profiles(flat_matches[cur_flat-1][0])
				cur_flat -= 1
				cur_profile = 0
				flat_profile_st = True
			bot.delete_message(call.message.chat.id, call.message.message_id)
			if call.data == 'book_profiles_prev':
				cur_profile -= 2
			profile = db.get_profile_by_id(flat_profiles[cur_profile])
			cur_profile += 1
			keyboard = types.InlineKeyboardMarkup()
			button = types.InlineKeyboardButton('Назад к объявлению', callback_data = 'matches_out')
			keyboard.add(button)
			if cur_profile + 1 <= len(flat_profiles) - 1:
				button = types.InlineKeyboardButton('Следующий профиль >>', callback_data = 'book_profiles')
				keyboard.add(button)
			if cur_profile > 1:
				button = types.InlineKeyboardButton('<< Предыдущий профиль', callback_data = 'book_profiles_prev')
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
			 '*Откуда родом: * '+ profile[3] + '\n' + '*Пол:* ' + profile[4] + '\n' + \
			 '*Работник или студент:* ' + work + '\n' + '*Место:*' + profile[6] + \
			 '\n' + '*Режим сна:* '+ profile[7] + '\n' + '*Языки:* ' + profile[8] + '\n' + '*О себе: * ' + profile[13]
			photo_id = db.get_profile_photo(profile[0])
			if photo_id[0][0] == '0':
				bot.send_message(call.message.chat.id, cap, reply_markup = keyboard, parse_mode = 'Markdown')
			else: 
				photo = 'https://drive.google.com/file/d/'+str(photo_id[0][0])+'/view?usp=sharing'
				bot.send_photo(call.message.chat.id, photo, caption = cap, reply_markup = keyboard, parse_mode = 'Markdown')
		elif call.data == 'seeker_delete_true':
			db.seeker_delete(str(call.message.chat.id))
			bot.send_message(call.message.chat.id, 'Ваша анкета удалена')

@bot.message_handler(content_types = ['text'])
def name_insert_data(message):
	global seeker, mode, seeker_st, offerer_st, flat_matches, cur_flat, sleep_places_st
	if message.text == '📋Добавить новое объявление':
		keyboard = types.ReplyKeyboardMarkup(True, True)
		keyboard.row('👤Ищу соседей','🏠Предлагаю жилье')
		keyboard.row('🔙Назад в меню')
		bot.send_message(message.chat.id, 'Выберите что-то одно:\n1.👤Ищу соседей\n2.🏠Предлагаю жилье', reply_markup = keyboard)
	elif message.text == '🔙Назад в меню':
		seeker_st = offerer_st = sleep_places_st = mode = 0
		keyboard = types.ReplyKeyboardMarkup(True, True)
		keyboard.row('📋Добавить новое объявление' )
		bot.send_message(message.chat.id, 'Главное меню', reply_markup=keyboard)
	elif message.text == '👤Ищу соседей':
		chat_id = str(message.chat.id)
		'''
		if db.seeker_check_chat_id(chat_id) == True:
			keyboard = types.InlineKeyboardMarkup()
			button = types.InlineKeyboardButton('Показать подходящие квартиры', callback_data = 'matches_out')
			button = types.InlineKeyboardButton('Изменить данные анкеты', callback_data = 'change_profile')
			keyboard.add(button)
			button = types.InlineKeyboardButton('Удалить анкету', callback_data = 'seeker_delete_true')
			keyboard.add(button)
			bot.send_message(message.chat.id, 'Вы уже заполняли анкету', reply_markup = keyboard)
			return
		'''
		#------

		keyboard = types.ReplyKeyboardMarkup(True, False)
		keyboard.row('🔙Назад в меню')
		bot.send_message(message.chat.id, 'Прошу вас заполнить анкету', reply_markup=keyboard)
		time.sleep(1)
		bot.send_message(message.chat.id, 'Ваши ФИО:')
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
	elif seeker_st == True:	
		if mode == 1:
			seeker.chat_id = message.chat.id
			seeker.name = message.text
			mode = 2
			keyboard = types.ReplyKeyboardMarkup(True, True)
			keyboard.row('от 16 до 18', 'от 18 до 23')
			keyboard.row('от 23 до 29', 'от 29 до 35')
			keyboard.row('Другое', '🔙Назад в меню')
			bot.send_message(message.chat.id, 'Какой у вас возраст?', reply_markup = keyboard)
		elif mode == 2:
			if message.text == 'Другое':
				bot.send_message(message.chat.id, 'Введите ваш возраст. Прошу ввести вас целое число')
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
			bot.send_message(message.chat.id, 'Откуда вы? (Регион)')
		elif mode == 3:
			seeker.homeland = message.text
			mode += 1
			keyboard = types.ReplyKeyboardMarkup(True, False)
			keyboard.row('👱Мужчина', '👩Женщина')
			keyboard.row('🔙Назад в меню')
			bot.send_message(message.chat.id, 'Укажите ваш пол', reply_markup = keyboard)
		elif mode == 4:
			if message.text == '👱Мужчина':
				seeker.gender = 'Муж'
			elif message.text == '👩Женщина':
				seeker.gender = 'Жен'
			else:
				keyboard = types.ReplyKeyboardMarkup(True, False)
				keyboard.row('👱Мужчина', '👩Женщина')
				keyboard.row('🔙Назад в меню')
				bot.send_message(message.chat.id, 'Неправильный ввод! Прошу вас воспользоваться клавиатурой', reply_markup = keyboard)
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
				bot.send_message(message.chat.id, 'Где вы учитесь?', reply_markup=keyboard)
			elif message.text == 'работаю':
				seeker.worker_or_student = 'worker'
				keyboard.row('🔙Назад в меню')
				keyboard.row('Строительство', 'Торговля')
				keyboard.row('IT', 'Образование')
				keyboard.row('Госслужба', 'Работаю на себя')
				keyboard.row('Частная комания', 'Рестораны/кафе')
				keyboard.row('Другое...')
				bot.send_message(message.chat.id, 'Какая у вас сфера деятельности?', reply_markup=keyboard)
			elif message.text == 'не учусь и не работаю':
				seeker.worker_or_student = 'neither'
				mode += 2
				keyboard = types.ReplyKeyboardMarkup(True, False)
				keyboard.row('Казахский', 'Русский', 'Оба языка')
				keyboard.row('Назад в меню')
				bot.send_message(message.chat.id, 'Укажите языки, на которых вы говорите:', reply_markup=keyboard)
			else:
				bot.send_message(message.chat.id, 'Неправильный ввод!')
				return
			mode += 1
		elif mode == 6:
			status = seeker.worker_or_student
			if message.text == 'Другое...':
				if status == 'student':
					bot.send_message(message.chat.id, 'Напишите название места где вы учитесь')
				elif status == 'worker':
					bot.send_message(message.chat.id, 'Напишите сферу деятельности, в которой вы работаете')
			else:
				seeker.study_or_work_place = message.text
				mode += 1
				keyboard = types.ReplyKeyboardMarkup(True, False)
				if status == 'student':
					keyboard.row('Жаворонок', 'Сова')
					keyboard.row('🔙Назад в меню')
					bot.send_message(message.chat.id, 'Какой у вас режим?', reply_markup=keyboard)
				elif status == 'worker':
					keyboard.row('С утра до вечера', 'С утра')
					keyboard.row('Ночью', 'Вахтовые смены')
					keyboard.row('День-Ночь', '🔙Назад в меню')
					bot.send_message(message.chat.id, 'В какое время вы работаете?', reply_markup=keyboard)
		elif mode == 7:
			seeker.sleeping_mode = message.text
			mode += 1
			keyboard = types.ReplyKeyboardMarkup(True, False)
			keyboard.row('Казахский', 'Русский', 'Оба языка')
			keyboard.row('Назад в меню')
			bot.send_message(message.chat.id, 'Укажите языки, на которых вы говорите:', reply_markup=keyboard)
		elif mode == 8:
			lang = message.text
			if lang == 'Казахский' or lang == 'Русский' or lang == 'Оба языка': 
				seeker.langs = message.text
				mode += 1
				keyboard = types.ReplyKeyboardMarkup(True, False)
				keyboard.row('Алматинский', 'Байконурский')
				keyboard.row('Есильский', 'Сарыаркинский')
				keyboard.row('🔙Назад в меню')
				bot.send_message(message.chat.id, 'Желаемый район города', reply_markup = keyboard)
			else:
				bot.send_message(message.chat.id, 'Неправильный ввод!')
		elif mode == 9:
			distr = message.text
			if distr == 'Алматинский' or distr == 'Байконурский' or distr == 'Есильский' or distr == 'Сарыаркинский':
				seeker.distr = message.text
				mode += 1
				keyboard = types.ReplyKeyboardMarkup(True, True)
				keyboard.row('до 20.000 тенге', 'от 20.000 до 30.000 тенге')
				keyboard.row('от 30.000 до 40.000 тенге', 'от 40.000 до 50.000 тенге')
				keyboard.row('выше 50.000 тенге', '🔙Назад в меню')
				bot.send_message(message.chat.id, 'Желательная цена', reply_markup=keyboard)
			else:
				bot.send_message(message.chat.id, 'Неправильный ввод!')
		elif mode == 10:
			seeker.price = message.text
			keyboard = types.ReplyKeyboardMarkup(True, True)
			keyboard.row('Отдельную комнату', 'Можно с кем-нибудь в комнате')
			keyboard.row('Оба варианта')
			keyboard.row('🔙Назад в меню')
			bot.send_message(message.chat.id, 'Я ищу...', reply_markup=keyboard)
			mode += 1
		elif mode == 11:
			seeker.seeking_for = message.text
			mode += 1
			bot.send_message(message.chat.id, 'Расскажите о себе (интересы, хобби, путешествия, книги, фильмы)')
		elif mode == 12:
			seeker.interest = message.text
			mode += 1
			bot.send_message(message.chat.id, 'Введите ваш номер телефона (пример: 8-ххх-ххх-хх-хх)')
		elif mode == 13:
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
		elif mode == 14:
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

@bot.message_handler(content_types = ['photo'])
def upload_photo(message):
	global mode, offerer_st, offerer, seeker, seeker_st, flat_matches
	if offerer_st == True and mode == 8:
		offerer.photo_id.append(photos.document_handler(message, bot))
		print(offerer.photo_id)
		db.offerer_insert(offerer)
		bot.send_message(message.chat.id, 'Ваша квартира добавлена!')
		offerer_st = False
		mode = 0
	elif seeker_st == True and mode == 14:
		seeker.photo_id.append(photos.document_handler(message, bot))
		db.seeker_insert(seeker)
		bot.send_message(message.chat.id, '*Подбираем вам подходящие квартиры...*', parse_mode = "Markdown")
		bot.send_chat_action(message.chat.id, 'typing')
		time.sleep(3)
		seeker_st = False
		flat_matches = db.get_matches(seeker)
		keyboard = types.InlineKeyboardMarkup();
		button = types.InlineKeyboardButton('Показать квартиры', callback_data = 'matches_out')
		keyboard.add(button)
		bot.send_message(message.chat.id, 'Квартиры найдены', reply_markup = keyboard)

bot.polling(none_stop = True)
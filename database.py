import psycopg2
import telebot
import os
from users import Seeker, Offerer

token = "1012837410:AAFY0lxwBFgWPIbRO-lO_MumXnlYJl-1ReQ"
bot = telebot.TeleBot(token)

class SQL:
	def __init__(self):
		#local host------------------
		self.con = psycopg2.connect(
		  database = "roomba",
		  user ="postgres", 
		  password="sbazgugu", 
		  host="localhost", 
		  port="5432"
		)
		#----------------------------

		#heroku----------------------
		#DATABASE_URL = os.environ['DATABASE_URL']
		#self.con = psycopg2.connect(DATABASE_URL, sslmode='require')
		#----------------------------

		self.cur = self.con.cursor()
	def create_tables(self):
		self.cur.execute('''
			CREATE TABLE seeker (
				id SERIAL PRIMARY KEY,
				name TEXT,
				age INT,
				homeland TEXT,
				gender TEXT,
				worker_or_student TEXT,
				study_or_work_place TEXT,
				sleeping_mode TEXT,
				langs TEXT,
				distr TEXT,
				near_what TEXT,
				price TEXT, 
				seeking_for TEXT,
				interest TEXT, 
				phone_num TEXT,
				book_flat INT[] DEFAULT ARRAY[0],
				chat_id TEXT,
				photo_id TEXT[] DEFAULT ARRAY[0],
				bad_habits TEXT,
				telegram_username TEXT
			);
			CREATE TABLE offerer(
				id SERIAL PRIMARY KEY,
				distr TEXT,
				address TEXT,
				price INT,
				room_num INT,
				sleep_places INT,
				price_per_sleep_place INT,
				description TEXT,
				phone_num TEXT,
				book_num INT DEFAULT 0,
				book_seekers INT[] DEFAULT ARRAY[0],
				chat_id TEXT,
				photo_id TEXT[] DEFAULT ARRAY[0],
				telegram_username TEXT
			);''')
		self.con.commit()
	def drop_tables(self):
		self.cur.execute('''
			DROP TABLE seeker;
			DROP TABLE offerer;
			''')
	
	def seeker_insert(self, seeker):
		self.cur.execute('''
			INSERT INTO seeker(name, age, homeland, phone_num, gender, worker_or_student, study_or_work_place, sleeping_mode, langs, 
			distr, near_what, price, seeking_for, interest, chat_id, photo_id, bad_habits, telegram_username) 
			VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
			''', (seeker.name, seeker.age, seeker.homeland, seeker.phone_num, seeker.gender, seeker.worker_or_student, \
				seeker.study_or_work_place, seeker.sleeping_mode, seeker.langs, seeker.distr, seeker.near_what, seeker.price, \
				seeker.seeking_for, seeker.interest, seeker.chat_id, seeker.photo_id, seeker.bad_habits, seeker.telegram_username))
		self.con.commit()
	def seeker_check_chat_id(self, chat_id):
		self.cur.execute('SELECT * FROM seeker WHERE chat_id = %s', (chat_id,))
		if self.cur.rowcount > 0:
			return True
		else:
			return False
	def seeker_delete(self, chat_id):
		self.cur.execute('SELECT book_flat FROM seeker WHERE chat_id = %s', (chat_id,))
		book_flat = self.cur.fetchone()[0]
		self.cur.execute('SELECT id FROM seeker WHERE chat_id = %s', (chat_id,))
		seeker_id = self.cur.fetchone()[0]
		for flat_id in book_flat:
			if flat_id == 0:
				continue
			self.cur.execute('SELECT book_seekers FROM offerer WHERE id = %s', (str(flat_id),))
			flat = self.cur.fetchone()
			self.cur.execute('UPDATE offerer SET book_num = book_num - 1 WHERE id = %s', (str(flat_id), ))
			flat[0].remove(seeker_id)
			self.cur.execute('UPDATE offerer SET book_seekers = %s WHERE id = %s', (flat[0], str(flat_id), ))
		self.cur.execute('DELETE FROM seeker WHERE chat_id = %s', (chat_id,))
		self.con.commit()
	def offerer_insert(self, offerer):
		price_per_sleep_place = int(offerer.price/offerer.sleep_places)
		self.cur.execute('''
		INSERT INTO offerer(distr,address, price, room_num, sleep_places, description, phone_num, chat_id, \
		price_per_sleep_place, photo_id, telegram_username) 
			VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
			''', (offerer.distr, offerer.address, offerer.price, offerer.room_num, \
				offerer.sleep_places, offerer.description, offerer.phone_num, offerer.chat_id,\
				price_per_sleep_place, offerer.photo_id, offerer.telegram_username))
		self.con.commit()
	def offerer_delete(self, flat_id):
		self.cur.execute('SELECT book_seekers FROM offerer WHERE id = %s', (str(flat_id),))
		book_seekers = self.cur.fetchone()[0]
		for prof_id in book_seekers:
			if prof_id == 0:
				continue
			self.cur.execute('SELECT book_flat FROM seeker WHERE id = %s', (str(prof_id),))
			profile = self.cur.fetchone()
			tmp = profile[0]
			tmp.remove(int(flat_id))
			self.cur.execute('UPDATE seeker SET book_flat = %s WHERE id = %s', (tmp, str(prof_id),))
		self.cur.execute('DELETE FROM offerer WHERE id = %s', (str(flat_id), ))
		self.con.commit()
	def get_matches(self, seeker):
		if seeker.price == 'до 20.000 тенге':
			self.cur.execute('SELECT * FROM offerer WHERE price_per_sleep_place <= 20000 AND %s = distr', (str(seeker.distr), ))
		elif seeker.price == 'от 20.000 до 30.000 тенге':
			self.cur.execute('SELECT * FROM offerer WHERE price_per_sleep_place >= 20000 AND price_per_sleep_place <= 30000 AND %s = distr', (str(seeker.distr), ))
		elif seeker.price == 'от 30.000 до 40.000 тенге':
			self.cur.execute('SELECT * FROM offerer WHERE price_per_sleep_place >= 30000 AND price_per_sleep_place <= 40000 AND %s = distr', (str(seeker.distr), ))
		elif seeker.price == 'от 40.000 до 50.000 тенге':
			self.cur.execute('SELECT * FROM offerer WHERE price_per_sleep_place >= 40000 AND price_per_sleep_place <= 50000 AND %s = distr', (str(seeker.distr), ))
		elif seeker.price == 'выше 50.000 тенге':
			self.cur.execute('SELECT * FROM offerer WHERE price_per_sleep_place >= 50000 AND %s = distr', (str(seeker.distr), ))
		
		return self.cur.fetchall() 
	def get_rematches(self, chat_id):
		self.cur.execute('SELECT price, distr FROM seeker WHERE chat_id = %s', (str(chat_id), ))
		profile = self.cur.fetchone()
		seeker = Seeker()
		seeker.price = profile[0]
		seeker.distr = profile[1]
		return seeker
	def get_profiles_by_filters(self, distr, price):
		self.cur.execute('SELECT * FROM seeker')
		n = self.cur.rowcount
		profiles = self.cur.fetchall()
		# profiles[x][9] - distr
		# profiles[x][11] - price
		# sort by distr, price
		for i in range(n):
			for j in range(0, n-i-1):
				num1 = 0
				num2 = 0
				if distr is not None:
					if profiles[j][9] == distr:
						num1 += 1
					if profiles[j+1][9] == distr:
						num2 += 1
				if price is not None:
					if profiles[j][11] == price:
						num1 += 1
					if profiles[j+1][11] == price:
						num2 += 1
				if num2 > num1:
					profiles[j], profiles[j+1] = profiles[j+1], profiles[j]
		return profiles
	def get_flats_by_filters(self, distr, price):
		self.cur.execute('SELECT * FROM offerer')
		n = self.cur.rowcount
		flats = self.cur.fetchall()
		# profiles[x][1] - distr
		# profiles[x][3] - price
		# sort by distr, price
		for i in range(n):
			for j in range(0, n-i-1):
				if distr is not None:
					if flats[j+1][1] == distr and flats[j][1] != distr:
						flats[j+1], flats[j] = flats[j], flats[j+1]
					elif price is not None and abs(flats[j+1][3] - price) < abs(flats[j][3] - price):
						flats[j+1], flats[j] = flats[j], flats[j+1]
		return flats

	def book_flat(self, chat_id, flat_id):
		self.cur.execute('UPDATE offerer SET book_num = book_num + 1 WHERE id = %s', (str(flat_id), ))
		self.cur.execute('SELECT book_seekers FROM offerer WHERE id = %s', (str(flat_id), ))
		flat = self.cur.fetchone()
		self.cur.execute('SELECT id FROM seeker WHERE chat_id = %s', (str(chat_id), ))
		seeker_id = self.cur.fetchone()
		flat[0].insert(0, seeker_id[0])
		self.cur.execute('UPDATE offerer SET book_seekers = %s WHERE id = %s', (flat[0], str(flat_id), ))
		self.cur.execute('SELECT book_flat FROM seeker WHERE chat_id = %s', (str(chat_id), ))
		seeker = self.cur.fetchone()
		seeker[0].insert(0, flat_id)
		self.cur.execute('UPDATE seeker SET book_flat = %s WHERE id = %s', (seeker[0], str(seeker_id[0]), ))
		self.cur.execute('SELECT book_num, sleep_places FROM offerer WHERE id = %s', (str(flat_id), ))
		# num = self.cur.fetchone()
		# if num[0] == num[1]:
		# 	self.cur.execute('SELECT book_seekers FROM offerer WHERE id = %s', (str(flat_id), ))
		# 	book_seekers = self.cur.fetchone()
		# 	print(book_seekers)
		# 	for seeker in book_seekers[0]:
		# 		self.cur.execute('SELECT chat_id FROM seeker WHERE id = %s', (str(seeker), ))
		# 		chat_id = self.cur.fetchone()
		# 		bot.send_message(chat_id[0], 'Ваша квартира готова!')


		self.con.commit()
	def check_book(self, chat_id, flat_id):
		self.cur.execute('SELECT book_flat FROM seeker WHERE chat_id = %s', (str(chat_id), ))
		book_flats = self.cur.fetchall()
		for a in book_flats[0]:
			if a == flat_id:
				return True
		return False
	def get_flat_profiles(self, flat_id):
		self.cur.execute('SELECT book_seekers FROM offerer WHERE id = %s', (str(flat_id), ))
		flat_profiles = self.cur.fetchone()
		return flat_profiles[0]
	def get_profile(self, chat_id):
		self.cur.execute('SELECT * FROM seeker WHERE chat_id = %s', (str(chat_id), ))
		return self.cur.fetchone()
	def get_profile_by_id(self, prof_id):
		self.cur.execute('SELECT * FROM seeker WHERE id = %s', (str(prof_id), ))
		return self.cur.fetchone()
	def get_flat(self, chat_id):
		self.cur.execute('SELECT * FROM offerer WHERE chat_id = %s', (str(chat_id), ))
		return self.cur.fetchall()
	def get_flat_by_id(self, flat_id):
		self.cur.execute('SELECT * FROM offerer WHERE id = %s', (str(flat_id), ))
		return self.cur.fetchone()
	def get_flat_photo_file_id(self, flat_id):
	    self.cur.execute('SELECT photo_id FROM offerer WHERE id = %s', (str(flat_id), ))
	    photo_id = self.cur.fetchall()
	    return photo_id[0][0][0]
	def get_profile_photo(self, prof_id):
		self.cur.execute('SELECT photo_id FROM seeker WHERE id = %s', (str(prof_id), ))
		photo_id = self.cur.fetchall()
		print(photo_id)
		return photo_id[0][0][0]
	def close(self):
		self.con.close()
	def flat_out(self, idf):
		self.cur.execute('SELECT * FROM offerer WHERE id = %s', str(idf))
		return self.cur.fetchone()
	def flat_num(self):
		self.cur.execute('SELECT * FROM offerer')
		return self.cur.rowcount
	def change_name(self, chat_id, name):
		self.cur.execute('UPDATE seeker SET name = %s WHERE chat_id = %s', (str(name), str(chat_id)))
		self.con.commit()
	def change_age(self, chat_id, age):
		self.cur.execute('UPDATE seeker SET age = %s WHERE chat_id = %s', (age, str(chat_id)))
		self.con.commit()
	def change_homeland(self, chat_id, homeland):
		self.cur.execute('UPDATE seeker SET homeland = %s WHERE chat_id = %s', (homeland, str(chat_id)))
		self.con.commit()
	def change_desc(self, chat_id, desc):
		self.cur.execute('UPDATE seeker SET interest = %s WHERE chat_id = %s', (desc, str(chat_id)))
		self.con.commit()

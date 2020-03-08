import psycopg2
import telebot
import os
from users import Seeker

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
				telegram_username TEXT,
				hata BOOLEAN
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
			distr, near_what, price, seeking_for, interest, chat_id, photo_id, bad_habits, telegram_username, hata) 
			VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
			''', (seeker.name, seeker.age, seeker.homeland, seeker.phone_num, seeker.gender, seeker.worker_or_student, \
				seeker.study_or_work_place, seeker.sleeping_mode, seeker.langs, seeker.distr, seeker.near_what, seeker.price, \
				seeker.seeking_for, seeker.interest, seeker.chat_id, seeker.photo_id, seeker.bad_habits, seeker.telegram_username, seeker.hata))
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
	def get_rematches(self, chat_id):
		self.cur.execute('SELECT price, distr FROM seeker WHERE chat_id = %s', (str(chat_id), ))
		profile = self.cur.fetchone()
		seeker = Seeker()
		seeker.price = profile[0]
		seeker.distr = profile[1]
		return seeker
	def get_profiles_by_filters(self, seeker):
		self.cur.execute('SELECT * FROM seeker WHERE chat_id != %s', (str(seeker.chat_id), ))
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
					if profiles[j][9] == seeker.distr:
						num1 += 1
					if profiles[j+1][9] == seeker.distr:
						num2 += 1
				if price is not None:
					if profiles[j][11] == price:
						num1 += 1
					if profiles[j+1][11] == price:
						num2 += 1
				if num2 > num1:
					profiles[j], profiles[j+1] = profiles[j+1], profiles[j]
		return profiles

	def get_profile(self, chat_id):
		self.cur.execute('SELECT * FROM seeker WHERE chat_id = %s', (str(chat_id), ))
		return self.cur.fetchone()
	def get_profile_by_id(self, prof_id):
		self.cur.execute('SELECT * FROM seeker WHERE id = %s', (str(prof_id), ))
		return self.cur.fetchone()
	def get_profile_photo(self, prof_id):
		self.cur.execute('SELECT photo_id FROM seeker WHERE id = %s', (str(prof_id), ))
		photo_id = self.cur.fetchall()
		print(photo_id)
		return photo_id[0][0][0]
	def close(self):
		self.con.close()
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

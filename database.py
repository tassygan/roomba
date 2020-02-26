import psycopg2
import telebot
import os

token = "1012837410:AAFY0lxwBFgWPIbRO-lO_MumXnlYJl-1ReQ"
bot = telebot.TeleBot(token)

DATABASE_URL = os.environ['DATABASE_URL']

class SQL:
	def __init__(self):
		#local host------------------
		'''
		self.con = psycopg2.connect(
		  database = "roomba",
		  user ="postgres", 
		  password="sbazgugu", 
		  host="localhost", 
		  port="5432"
		)
		'''
		#----------------------------

		#heroku----------------------
		self.con = psycopg2.connect(DATABASE_URL, sslmode='require')
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
				photo_id TEXT[] DEFAULT ARRAY[0]
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
				photo_id TEXT[] DEFAULT ARRAY[0]
			);''')
		self.con.commit()

	def drop_tables(self):
		self.cur.execute('''
			DROP TABLE searchers;
			DROP TABLE tenants;
			''')
	
	def seeker_insert(self, seeker):
		self.cur.execute('''
			INSERT INTO seeker(name, age, homeland, phone_num, gender, worker_or_student, study_or_work_place, sleeping_mode, langs, 
			distr, near_what, price, seeking_for, interest, chat_id, photo_id) 
			VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
			''', (seeker.name, seeker.age, seeker.homeland, seeker.phone_num, seeker.gender, seeker.worker_or_student, \
				seeker.study_or_work_place, seeker.sleeping_mode, seeker.langs, seeker.distr, seeker.near_what, seeker.price, \
				seeker.seeking_for, seeker.interest, seeker.chat_id, seeker.photo_id))
		self.con.commit()

	def seeker_check_chat_id(self, chat_id):
		self.cur.execute('SELECT * FROM seeker WHERE chat_id = %s', (chat_id,))
		if self.cur.rowcount > 0:
			return True
		else:
			return False

	def seeker_delete(self, chat_id):
		self.cur.execute('DELETE FROM seeker WHERE chat_id = %s', (chat_id,))
		self.con.commit()

	def offerer_insert(self, offerer):
		price_per_sleep_place = int(offerer.price/offerer.sleep_places)
		self.cur.execute('''
		INSERT INTO offerer(distr,address, price, room_num, sleep_places, description, phone_num, chat_id, price_per_sleep_place, photo_id) 
			VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
			''', (offerer.distr, offerer.address, offerer.price, offerer.room_num, \
				offerer.sleep_places, offerer.description, offerer.phone_num, offerer.chat_id, price_per_sleep_place, offerer.photo_id))
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

	def get_flat_photo_file_id(self, flat_id):
	    self.cur.execute('SELECT photo_id FROM offerer WHERE id = %s', (str(flat_id), ))
	    photo_id = self.cur.fetchall()
	    return photo_id[0]

	def get_profile_photo(self, prof_id):
	    self.cur.execute('SELECT photo_id FROM offerer WHERE id = %s', (str(prof_id), ))
	    photo_id = self.cur.fetchall()
	    return photo_id[0]

	def close(self):
		self.con.close()
	
	def flat_out(self, idf):
		self.cur.execute('SELECT * FROM offerer WHERE id = %s', str(idf))
		return self.cur.fetchone()
	
	def flat_num(self):
		self.cur.execute('SELECT * FROM offerer')
		return self.cur.rowcount
'''
print("Database opened successfully")
cur = con.cursor()
cur.execute()

print("Table created successfully")
con.commit()  
con.close()
'''
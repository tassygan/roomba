import psycopg2
import telebot

token = "1012837410:AAFY0lxwBFgWPIbRO-lO_MumXnlYJl-1ReQ"
bot = telebot.TeleBot(token)

DATABASE_URL = 'postgres://ihnxtolnufgnvx:675ef2a0c99965db312a90aece18a70695340e410956f50ea989d6761e3806ee@ec2-3-220-86-239.compute-1.amazonaws.com:5432/dbu6jnnonf6vfl'

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
		#self.con = psycopg2.connect(DATABASE_URL, sslmode='require')
		#----------------------------

		self.cur = self.con.cursor()

	def create_tables(self):
		self.cur.execute('''
			CREATE TABLE searchers (
				id SERIAL PRIMARY KEY,
				name TEXT NOT NULL,
				age INT NOT NULL,
				sphere TEXT,
				langs TEXT,
				interest TEXT,
				distr TEXT,
				price INT, 
				require TEXT,
				phone_num TEXT,
				chat_id TEXT
			);
			CREATE TABLE sleep_place_seeker (
				id SERIAL PRIMARY KEY,
				name TEXT,
				age INT,
				sphere TEXT,
				langs TEXT,
				interest TEXT,
				distr TEXT,
				price INT, 
				require TEXT,
				phone_num TEXT,
				chat_id TEXT
			);
			CREATE TABLE tenants(
				id SERIAL PRIMARY KEY,
				distr TEXT,
				address TEXT,
				price INT,
				room_num INT,
				sleep_places INT,
				description TEXT,
				phone_num TEXT,
				book_num INT,
				chat_id TEXT,
				photo_id TEXT[]
			);''')
		self.con.commit()

	def drop_tables(self):
		self.cur.execute('''
			DROP TABLE searchers;
			DROP TABLE tenants;
			''')
	
	def search_insert(self, search):
		self.cur.execute('''
			INSERT INTO searchers(name, age, sphere, langs, interest, distr, price, require, phone_num, chat_id) 
			VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
			''', (search.name, search.age, search.sphere, search.langs, search.interest, \
				search.distr, search.price, search.require, search.phone_num, search.chat_id))
		self.con.commit()

	def sleep_insert(self, search):
		self.cur.execute('''
			INSERT INTO sleep_place_seeker(name, age, sphere, langs, interest, distr, price, require, phone_num, chat_id) 
			VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
			''', (search.name, search.age, search.sphere, search.langs, search.interest, \
				search.distr, search.price, search.require, search.phone_num, search.chat_id))
		self.con.commit()
	
	def search_check_chat_id(self, chat_id):
		self.cur.execute('SELECT * FROM searchers WHERE chat_id = %s', (chat_id,))
		if self.cur.rowcount > 0:
			return True
		else:
			return False

	def search_delete(self, chat_id):
		self.cur.execute('DELETE FROM searchers WHERE chat_id = %s', (chat_id,))
		self.con.commit()

	def tenant_insert(self, tenant):
		self.cur.execute('''
			INSERT INTO tenants(distr,address, price, room_num, sleep_places, description, phone_num, chat_id, photo_id) 
			VALUES (%s, %s, %s, %s, %s, %s, %s, %s, ARRAY['1_1', '1_2', '1_3'])
			''', (tenant.distr, tenant.address, tenant.price, tenant.room_num, \
				tenant.sleep_places, tenant.description, tenant.phone_num, tenant.chat_id))
		self.cur.execute('SELECT chat_id FROM sleep_place_seeker WHERE price >= %s AND distr = %s', (str(tenant.price), tenant.distr))
		matches = self.cur.fetchall()
		for a in matches[0]:
			bot.send_message(a, 'Добавлена новая квартира, которая вам подходит!')
		self.con.commit()	
	def get_matches(self, search):
		self.cur.execute('SELECT * FROM tenants WHERE %s >= price AND %s = distr', (search.price, search.distr))
		return self.cur.fetchall() 

	def book_flat(self, chat_id, flat_id):
		self.cur.execute('UPDATE tenants SET book_num = book_num + 1 WHERE id = %s', (str(flat_id), ))
		self.cur.execute('SELECT book_seekers FROM tenants WHERE id = %s', (str(flat_id), ))
		flat = self.cur.fetchone()
		self.cur.execute('SELECT id FROM sleep_place_seeker WHERE chat_id = %s', (str(chat_id), ))
		seeker_id = self.cur.fetchone()
		flat[0].insert(0, seeker_id[0])
		self.cur.execute('UPDATE tenants SET book_seekers = %s WHERE id = %s', (flat[0], str(flat_id), ))
		
		self.cur.execute('SELECT book_flat FROM sleep_place_seeker WHERE chat_id = %s', (str(chat_id), ))
		seeker = self.cur.fetchone()
		seeker[0].insert(0, flat_id)
		self.cur.execute('UPDATE sleep_place_seeker SET book_flat = %s WHERE id = %s', (seeker[0], str(seeker_id[0]), ))

		self.con.commit()

	def check_book(self, chat_id, flat_id):
		self.cur.execute('SELECT book_flat FROM sleep_place_seeker WHERE chat_id = %s', (str(chat_id), ))
		book_flats = self.cur.fetchall()
		for a in book_flats[0]:
			if a == flat_id:
				return True
		return False

	def close(self):
		self.con.close()
	
	def flat_out(self, idf):
		self.cur.execute('SELECT * FROM tenants WHERE id = %s', str(idf))
		return self.cur.fetchone()
	
	def flat_num(self):
		self.cur.execute('SELECT * FROM tenants')
		return self.cur.rowcount
'''
print("Database opened successfully")
cur = con.cursor()
cur.execute()

print("Table created successfully")
con.commit()  
con.close()
'''
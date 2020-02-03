import psycopg2

DATABASE_URL = 'postgres://ihnxtolnufgnvx:675ef2a0c99965db312a90aece18a70695340e410956f50ea989d6761e3806ee@ec2-3-220-86-239.compute-1.amazonaws.com:5432/dbu6jnnonf6vfl'

class SQL:
	def __init__(self):
		'''
		self.con = psycopg2.connect(
		  database = "roomba",
		  user ="postgres", 
		  password="sbazgugu", 
		  host="localhost", 
		  port="5432"
		)
		'''
		self.con = psycopg2.connect(DATABASE_URL, sslmode='require')
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
				price TEXT, 
				require TEXT,
				phone_num TEXT,
				chat_id TEXT
			);
			CREATE TABLE tenants(
				id SERIAL PRIMARY KEY,
				location TEXT,
				price TEXT,
				description TEXT,
				phone_num TEXT,
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
			INSERT INTO tenants(location, price, description, phone_num, photo_id) 
			VALUES (%s, %s, %s, %s, ARRAY['1_1', '1_2', '1_3'])
			''', (tenant.location, tenant.price, tenant.description, tenant.phone_num))
		self.con.commit()	
	
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
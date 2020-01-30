import psycopg2

class SQL:
	def __init__(self):
		self.con = psycopg2.connect(
		  database = "roomba",
		  user ="postgres", 
		  password="sbazgugu", 
		  host="localhost", 
		  port="5432"
		)
		self.cur = self.con.cursor()
	
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
			INSERT INTO tenants(location, price, description, phone_num) 
			VALUES (%s, %s, %s, %s)
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
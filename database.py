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
	def insert_data(self, name, age):
		self.cur.execute("INSERT INTO searchers(name, age) VALUES ('%s' , %s)" % (name, age))
		self.con.commit()
	def close(self):
		self.con.close()
'''
print("Database opened successfully")
cur = con.cursor()
cur.execute()

print("Table created successfully")
con.commit()  
con.close()
'''
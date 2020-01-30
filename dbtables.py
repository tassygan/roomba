import psycopg2
from database import SQL

db = SQL()

db.create_tables()

db.close()
import sqlite3

db = sqlite3.connect('database.db')
db.executescript(open('bak.sql').read())
db.commit()

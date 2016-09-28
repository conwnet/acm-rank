import sqlite3

db = sqlite3.connect('database.db')
cur = db.execute('select `id`, `name`, `email` from `acmers`')
acmers = cur.fetchall()
for acmer in acmers:
    print("insert into `acmers` (`id`, `name`, `email`, `status`) values ('%s', '%s', '%s', 1);" % (acmer[0], acmer[1], acmer[2]))

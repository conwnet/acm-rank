from flask import Flask, render_template, g
from bs4 import BeautifulSoup
import sqlite3
import urllib
import time
import re

app = Flask(__name__)

DATABASE = 'database.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def query(query, args=(), one=False):
    try:
        cur = get_db().execute(query, args)
        rv = cur.fetchall()
        cur.close()
        return (rv[0] if rv else None) if one else rv
    except:
        return None

def execute(query, args=()):
    try:
        db = get_db()
        db.cursor().execute(query, args)
        db.commit()
        return True
    except:
        return False

def install():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

def get_html(url):
    request = urllib.request.Request(url)
    try:
        with urllib.request.urlopen(request, timeout=10) as html:
            return html.read().decode()
    except:
        return ''

class Acmer:
    def __init__(self, acmer):
        self.id = acmer['id']
        self.name = acmer['name']
        self.email = acmer['email']
        self.solved = acmer['solved']
        self.submissions = acmer['submissions']
        self.solved_problem_list = acmer['solved_problem_list'].split()
        self.last_submit_time = acmer['last_submit_time']
        self.update_time = acmer['update_time']
        self.last_week_solved = acmer['last_week_solved']
        self.status = acmer['status']

    def update(self):
        try:
            url = "http://poj.org/userstatus?user_id=" + self.user_id
            html = get_html(url)
            soup = BeautifulSoup(html, 'html.parser')
            self.solved = soup.find(text='Solved:').find_next().a.string
            self.submissions = soup.find(text='Submissions:').find_next().a.string
            p_str = re.sub(r'\D', ' ', soup.find(text=re.compile(r'function p')))
            self.solved_problem_list = p_str.split()
            self.last_submit_time = 0
            self.update_time = time.time()
            return True
        except:
            return False
    
    def save(args=()):
        if args == ():
            execute("update `acmers` set `name`=?, `email`=?, `solved`=?, `submissions`=?, `solved_problem_list`=?, `last_submit_time`=?, `update_time`=?, `last_week_solved`=?, `status`=? where `id`=" + self.id, (self.name, self.email, self.solved, self.submissions, self.solved_problem_list, self.last_submit_time, self.update_time, self.last_week_solved, self.stauts))
        else:
            execute('update `acmers` set ' + ', '.join('`' + s + '`=?' for s in args) + ' where id=' + self.id, args)

def get_acmer(user_id):
    return query('select * from acmers where id=?', (user_id,), one=True)

@app.route('/')
def index():
    acmer = Acmer()
    acmer.update()
    return acmer.solved + ' ' + acmer.submissions + ' ' + ' '.join(acmer.solved_problem_list)

@app.route('/<user_id>')
def problem(user_id):
    acmer = get_acmer(user_id)
    if acmer is None:
        return 'user_id不正确！'
    else:
        return acmer['name']

@app.route('/test_insert')
def test_insert():
    if not execute("insert into acmers (`id`, `name`, `email`, `solved`, `submissions`, `solved_problem_list`, `last_submit_time`, `update_time`, `last_week_solved`, `status`) values ('QHearting', '张国庆', 'netcon@live.com', 3, 6, '1001 1002 1003', 1473779369, 1473779369, 2, 1)"):
        return 'False'
    return 'insert'

@app.route('/test_select')
def test_select():
    acmers = query("select * from acmers")
    return ','.join([acmer['id'] for acmer in acmers])

if __name__ == '__main__':
    app.run(debug=True)
    #open('web.html', 'w').write(get_solved_number('QHearting'))



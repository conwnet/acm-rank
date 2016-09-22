from flask import Flask, render_template, g, request, flash, redirect
from bs4 import BeautifulSoup
import sqlite3
import urllib
import time
import re

app = Flask(__name__)
app.secret_key = 'Author:netcon'

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
        self.solved_problem_list = acmer['solved_problem_list']
        self.last_submit_time = acmer['last_submit_time']
        self.update_time = acmer['update_time']
        self.last_week_solved = acmer['last_week_solved']
        self.status = acmer['status']
    
    @staticmethod
    def new(id):
        acmer = query('select * from `acmers` where id=?', (id,), one=True)
        if acmer is None:
            return None
        return Acmer(acmer)

    def update(self):
        try:
            url = "http://poj.org/userstatus?user_id=" + self.id
            soup = BeautifulSoup(get_html(url), 'html.parser')
            self.solved = soup.find(text='Solved:').find_next().a.string
            self.submissions = soup.find(text='Submissions:').find_next().a.string
            p_str = re.sub(r'\D', ' ', soup.find(text=re.compile(r'function p')))
            self.solved_problem_list = ' '.join(p_str.split())
            submit_times = re.findall(r'<td>(\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d)</td>', get_html('http://poj.org/status?user_id=' + self.id))
            if submit_times == []:
                self.last_submit_time = '9999-12-31 23:59:59'
            else:
                self.last_submit_time = submit_times[0]
            self.update_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            self.save()
            return True
        except:
            return False
    
    def save(self):
        execute("update `acmers` set `name`=?, `email`=?, `solved`=?, `submissions`=?, `solved_problem_list`=?, `last_submit_time`=?, `update_time`=?, `last_week_solved`=?, `status`=? where `id`=?", (self.name, self.email, self.solved, self.submissions, self.solved_problem_list, self.last_submit_time, self.update_time, self.last_week_solved, self.status, self.id))

    @staticmethod
    def all_acmers():
        all_acmers = []
        acmers = query('select id from acmers order by `solved` desc')
        if acmers is not None:
            for acmer in acmers:
                all_acmers.append(Acmer.new(acmer['id']))
        return all_acmers

def check_id(id, password):
    cp = urllib.request.HTTPCookieProcessor()
    opener = urllib.request.build_opener(cp)
    urllib.request.install_opener(opener)
    try:
        req = urllib.request.Request('http://poj.org/login', ('user_id1=%s&password1=%s' % (id, password)).encode())
        with urllib.request.urlopen(req, timeout=5):
            if re.search('Log Out', get_html('http://poj.org/login')) is None:
                return 1
        return 0
    except:
        return 2

@app.route('/handle', methods=['POST'])
def handle():
    check = check_id(request.form['id'], request.form['password'])
    if check == 1:
        flash('密码不正确！')
    elif check == 2:
        flash('POJ目前不可用，请稍后再试！')
    elif request.method == 'POST':
        id = request.form['id']
        if request.form['type'] == 'add':
            if Acmer.new(id) is None:
                name = request.form['name']
                email = request.form['email']
                execute('insert into `acmers` (`id`, `name`, `email`) values (?, ?, ?)', (id, name, email))
                acmer = Acmer.new(id)
                if acmer is not None and acmer.update():
                    flash('添加成功！')
                else:
                    flash('添加失败！')
        elif request.form['type'] == 'update':
            acmer = Acmer.new(id)
            if acmer is not None:
                if acmer.update():
                    flash('更新成功！')
                else:
                    flash('更新失败！')
        elif request.form['type'] == 'delete':
            execute('delete from `acmers` where `id`=?', (id,))
            flash('删除成功！')
    else:
        flash('我不明白你想做什么')
    return redirect('/')

@app.route('/')
def index():
    acmers = Acmer.all_acmers()
    return render_template('index.html', acmers=acmers)

@app.route('/updateall')
def updateall():
    acmers = Acmer.all_acmers()
    for acmer in acmers:
        acmer.update()
    return 'update successful!'

@app.route('/update/<id>')
def update(id):
    acmer = Acmer.new(id)
    if acmer is None:
        return 'id不正确！'
    else:
        acmer.update()
        return str(acmer.solved) + ' ' +  str(acmer.last_submit_time)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)






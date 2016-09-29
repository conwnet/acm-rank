from flask import Flask, render_template, g, request, flash, redirect
from bs4 import BeautifulSoup
import sqlite3, urllib, hashlib, time, re

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
        self.submissions = acmer['submissions']
        self.solved = acmer['solved']
        self.solved_problem_list = acmer['solved_problem_list']
        self.last_submit_time = acmer['last_submit_time']
        self.previous_solved = acmer['previous_solved']
        self.previous_solved_problem_list = acmer['previous_solved_problem_list']
        self.update_time = acmer['update_time']
        self.status = acmer['status']
    
    def update(self):
        try:
            url = "http://poj.org/userstatus?user_id=" + self.id
            soup = BeautifulSoup(get_html(url), 'html.parser')
            self.submissions = soup.find(text='Submissions:').find_next().a.string
            self.solved = soup.find(text='Solved:').find_next().a.string
            p_str = re.sub(r'\D', ' ', soup.find(text=re.compile(r'function p')))
            self.solved_problem_list = ' '.join(p_str.split())
            submit_times = re.findall(r'<td>(\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d)</td>', get_html('http://poj.org/status?user_id=' + self.id))
            if submit_times:
                self.last_submit_time = submit_times[0]
                html = get_html('http://poj.org/status?&result=0&user_id=' + self.id)
                submit_times = re.findall(r'<td>(\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d)</td>', html)

                self.previous_solved_problem_list = []
                while len(submit_times) == 20 and time.time() - time.mktime(time.strptime(submit_times[-1], '%Y-%m-%d %H:%M:%S')) < 604800:
                    self.previous_solved_problem_list += re.findall(r'<a href=problem\?id=\d\d\d\d>(\d\d\d\d)</a>', html)
                    next_page_urls = re.findall(r'Previous Page.*href=(.*)><font color=blue>Next Page', html)
                    html = get_html('http://poj.org/' + next_page_urls[0])
                    submit_times = re.findall(r'<td>(\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d)</td>', html)

                page_valid_count = 0
                for one_time in submit_times:
                    if time.time() - time.mktime(time.strptime(one_time, '%Y-%m-%d %H:%M:%S')) > 604800:
                        break
                    page_valid_count += 1

                self.previous_solved_problem_list += re.findall(r'<a href=problem\?id=\d\d\d\d>(\d\d\d\d)</a>', html)[0:page_valid_count]
                self.previous_solved_problem_list = list(set(self.previous_solved_problem_list))
                self.previous_solved = len(self.previous_solved_problem_list)
                self.previous_solved_problem_list = ' '.join(self.previous_solved_problem_list)
            else:
                self.last_submit_time = '9999-12-31 23:59:59'
                self.previous_solved_problem_list = ''
                self.previous_solved = 0
            self.update_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            self.save()
            return True
        except:
            return False
    
    def save(self):
        execute("update `acmers` set `name`=?, `email`=?, `submissions`=?, `solved`=?, `solved_problem_list`=?, `last_submit_time`=?, `previous_solved`=?, `previous_solved_problem_list`=?, `update_time`=?, `status`=? where `id`=?", (self.name, self.email, self.submissions, self.solved, self.solved_problem_list, self.last_submit_time, self.previous_solved, self.previous_solved_problem_list, self.update_time, self.status, self.id))

    @staticmethod
    def new(id):
        acmer = query('select * from `acmers` where id=?', (id,), one=True)
        if acmer is None:
            return None
        return Acmer(acmer)

    @staticmethod
    def all_acmers():
        all_acmers = []
        acmers = query('select id from acmers where `status`=1 order by `previous_solved` desc')
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
                execute('insert into `acmers` (`id`, `name`, `email`, `status`) values (?, ?, ?, 1)', (id, name, email))
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

def hash(password):
    return hashlib.sha256((password + '+' + app.secret_key).encode()).hexdigest()

@app.route('/')
def index():
    acmers = Acmer.all_acmers()
    return render_template('index.html', acmers=acmers, update_time=Acmer.new('0').update_time)

@app.route('/updateall/<password>')
def updateall(password):
    if hash(password) != Acmer.new('0').name:
        return '密码错误！'
    acmers = Acmer.all_acmers()
    for acmer in acmers:
        acmer.update()
    return '更新完成！'

@app.route('/update/<id>/<password>')
def update(id, password):
    if hash(password) != Acmer.new('0').name:
        return '密码错误！'
    acmer = Acmer.new(id, password)
    if acmer is None:
        return 'id不正确！'
    else:
        acmer.update()
        return str(acmer.solved) + ' ' +  str(acmer.last_submit_time)

@app.route('/add/<id>/<name>/<email>/<password>')
def add(id, name, email, password):
    if hash(password) != Acmer.new('0').name:
        return '密码错误！'
    execute('insert into `acmers` (`id`, `name`, `email`) values (?, ?, ?)', (id, name, email))
    return '添加成功！'

@app.route('/delete/<id>/<password>')
def delete(id, password):
    if hash(password) != Acmer.new('0').name:
        return '密码错误！'
    execute('delete from `acmers` where `id`=?', (id,))
    return '删除成功！'
    

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)






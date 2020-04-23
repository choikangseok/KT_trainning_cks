import os
import pymysql
from flask import Flask, render_template
from flask import request, redirect, abort, session

app = Flask(__name__, 
            static_folder="static",
            template_folder="views")
app.config['ENV'] = 'development'
app.config['DEBUG'] = True
app.secret_key = 'sookbun'

db = pymysql.connect(
    user='root',
    passwd='',
    host='localhost',
    db='web',
    charset='utf8',
    cursorclass=pymysql.cursors.DictCursor
)

members = [
    {"id": "sookbun", "pw": "111111"},
    {"id": "duru", "pw": "222222"},
]

def get_menu():
    cursor = db.cursor()
    cursor.execute("select id, title from topic")
    menu = [f"<li><a href='/{row['id']}'>{row['title']}</a></li>"
            for row in cursor.fetchall()]
    return '\n'.join(menu)
    
def get_template(filename):
    with open('views/' + filename, 'r', encoding="utf-8") as f:
        template = f.read()
        
    return template

@app.route("/")
def index():    
    if 'user' in session:
        title = 'Welcome ' + session['user']['id']
    else:
        title = 'Welcome'
        
    content = 'Welcome Python Class...'
    return render_template('template.html',
                           title=title,
                           content=content,
                           menu=get_menu())

@app.route("/<id>")
def html(id):
    cursor = db.cursor()
    cursor.execute(f"select * from topic where id = '{id}'")
    topic = cursor.fetchone()
    
    if topic is None:
        abort(404)

    return render_template('template.html',
                           title=topic['title'],
                           content=topic['description'],
                           menu=get_menu())

@app.route("/delete/<title>")
def delete(title):
    os.remove(f"content/{title}")
    return redirect("/")

@app.route("/create", methods=['GET', 'POST'])
def create():
    if request.method == 'GET':
        return render_template('create.html', 
                               message='', 
                               menu=get_menu())
    
    elif request.method == 'POST':
        # request.form['title'], request.form['desc']
        with open(f'content/{request.form["title"]}', 'w') as f:
            f.write(request.form['desc'])

        return redirect('/')

@app.route("/login", methods=['GET', 'POST'])
def login():
    message = ""
    if request.method == 'POST':
        m = [e for e in members if e['id'] == request.form['id']]
        
        if len(m) == 0:
            message = "<p>회원이 아닙니다.</p>"
        elif request.form['pw'] != m[0]['pw']:
            message = "<p>패스워드를 확인해 주세요</p>"
        else:
            # 로그인 성공에는 메인으로
            session['user'] = m[0]
            return redirect("/")
    
    return render_template('login.html', 
                           message=message, 
                           menu=get_menu())

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')

@app.route("/favicon.ico")
def favicon():
    return abort(404)

@app.route("/dbtest")
def dbtest():
    cursor = db.cursor()
    cursor.execute("select * from topic")
    return str(cursor.fetchall())

app.run(port=8008)
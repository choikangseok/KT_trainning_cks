from flask import Flask
from flask import request, redirect, abort
import os
import time

# app = Flask("flask")
app = Flask(__name__, static_folder="static")

members = [
    {'id': 'sook', 'pw': '111'},
    {'id': 'duru', 'pw': '222'}
]
def get_menu():
    menu=[e for e in os.listdir('content') if e[0] != '.']
    menu_temp = "<li><a href='/{0}'>{0}</a></li>"
    return "\n".join([menu_temp.format(m) for m in menu])


def get_template(filename):
    with open(filename, 'r', encoding="utf-8") as f:
        return f.read()



@app.route('/')
def index():
    id = request.args.get('key', '')
    title ='Welcome ' + id    
    content = 'Welcome Python Class...'
    menu = get_menu()
    return get_template("main.html").format(title, content, menu)

@app.route('/search')
def search():
    template = get_template("search.html")
    q = request.args.get('q', '')
    result = [filename for filename in os.listdir('content') if q in filename]
    menu_temp = "<li><a href='/{0}'>{0}</a></li>"
    menu = "\n".join([menu_temp.format(m) for m in result if m[0] != '.'])

    return template.format('','',menu)

# @app.route('/search')
# def result():
#     id = request.args.get('key', '')
    
#     return get_template("result.html").format(id)

@app.route('/<title>')
def html(title):
    template = get_template("template.html")
    menu = get_menu()
    with open(f'content/{title}', 'r') as f:
        content = f.read()
        mytext = "<br />".join(content.split("\n"))
    return template.format(title, mytext, menu)

@app.route("/create", methods=['GET', 'POST'])
def create():
    template = get_template('create.html')
    menu= get_menu()
    if request.method=="GET":
        return template.format('', menu)
    elif request.method=="POST":
        # result = [filename for filename in os.listdir('content') if q in filename]
        # if request.form["title"] in result:
        #     alert("중복입니다. 다시 입력해주세요")
        #     return redirect('/create')
        title = request.form["title"]
        if title == "":
            title = time.strftime("%Y%m%d-%I.%M.%S",time.localtime(time.time()))
            
            
        with open(f'content/{title}','w') as f:
            f.write(request.form['desc'])
        return redirect('/')

# @app.route('/modify/<title>', methods=['GET', 'POST'])
# def modify(title):
#     template = get_template('modify.html')
#     menu= get_menu()
#     with open(f'content/{title}', 'r') as f:
#         content = f.read()
    
#     if request.method=="GET":
#         print("get")
#         return template.format('', menu)
#     elif request.method=="POST":
#         with open(f'content/{request.form["title"]}','w') as f:
#             f.write(request.form['content'])
#         return redirect('/')
@app.route('/modify/<title>')
def modify(title):
    template = get_template("modify.html")
    menu = get_menu()
    with open(f'content/{title}', 'r') as f:
        content = f.read()
    return template.format(title, content, menu)
        
@app.route('/delete/<path>')
def delete(path):
    os.remove(f"content/{path}")
    return redirect("/")

@app.route('/login', methods=['GET', 'POST'])
def login():
    title, message= 'login', ''
    login = get_template("login.html")
    menu = get_menu()
    # return get_template("login.html")
    id= "key=Hyun"
    if request.method=="GET":
        return login.format(title, "GET", menu)
    elif request.method=="POST":
        #만약 회원이 아니면, 회원이 없습니다 출력
        m = [e for e in members if e['id'] == request.form['id']]
        if len(m) == 0:
            return login.format('회원이 아닙니다.', menu)
        if request.form['pw'] != m[0]['pw']:
            return login.format("패스워드를 확인해 주세요", menu)
        # return login.format(title, request.form)
        # return redirect("/?id=" + m[0]['id'])
        
        return redirect("/?"+id)
        # return login.format(title, 'POST')


@app.route("/favicon.ico")
def favicon():
    return abort(404)

# @app.route("/kt")
# def kt():
#     with open("kt.html", 'r', encoding="utf-8") as f:
#         ret = f.read()
#     return ret

# @app.route("/Comparison")
# def Comparison():
#     with open("Comparison.html", 'r', encoding="utf-8") as f:
#         ret = f.read()
#     return ret

# @app.route("/Advertising")
# def Advertising():
#     with open("Advertising.html", 'r', encoding='utf-8') as f:
#         ret = f.read()
#     return ret
    
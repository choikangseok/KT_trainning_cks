from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup



app = Flask(__name__, template_folder="templates", static_folder ='static')

app.config['ENV'] = 'development'
app.config['DEBUG'] = True

@app.route('/')
def index():
    return "welcome, day8 class"

@app.route('/verify_jumin', methods=['get', 'post'])
def verify():
    result = True
    total =0
    code = 0
    if request.method == 'POST':
        numbers = request.form['numbers'].replace("-","").strip()
        numbers = [int(s) for s in numbers]
        print(numbers)
        for i in range(8):
            total = total + (numbers[i] * (i+2))
        for i in range(8,12):
            total = total + (numbers[i] * (i-6))

        print(total)
        check_num = 11 - (total % 11)
        print(check_num)
        print(numbers[-1])

        if check_num % 10 == numbers[-1]:
            result =True
        else:
            result = False



    return render_template('base.html',
                           title="주민번호 확인",
                           result=result,
                           site="verify_jumin",
                           placehoder="xxxxxx-xxxxxxx")

# @app.route('/crawler/naver/<word>')
# def crawler_naver(word):
#     result = ''
#     url = f'https://search.naver.com/search.naver'
#     query= {
#     "where": "image",
#     "sm" : "tab_jum",
#     "qurey" : word
#     }
#     response = requests.get(url, params=query)
#     soup = BeautifulSoup(response.content, 'html.parser')
#     tags=soup.select('img._img')
#
#     return render_template('crawler.html', result = tags[0].prettify())


@app.route('/crawler/naver/<word>')
def crawler_naver(word):
    def download_img_from_tag(tag, filename):
        response = requests.get(tag['data-source'])
        with open(filename, 'wb') as f:
            f.write(response.content)

    url = f"https://search.naver.com/search.naver"
    query = {
        "where": "image",
        "sm": "tab_jum",
        "query": word
    }
    response = requests.get(url, params=query)
    soup = BeautifulSoup(response.content, 'html.parser')
    tags = soup.select('img._img')

    filenames = []
    for i, tag in enumerate(tags):
        # tag를 던지면 이미지를 저장하고 이미지명을 반환
        filename = f'static/{word}{i}.jpg'
        download_img_from_tag(tag, filename)
        filenames.append(filename)

    return render_template('crawler.html',
                           files=filenames)

@app.route('')

# @app.route('/crawler/naver/<word>')
# def crawler_naver(word):
#     result = ''
#
#     url = f"https://search.naver.com/search.naver"
#     query = {
#         "where": "image",
#         "sm": "tab_jum",
#         "query": word
#     }
#     response = requests.get(url, params=query)
#     soup = BeautifulSoup(response.content, 'html.parser')
#     tags = soup.select('img._img')
#
#     # print(tags[0]['data-source'])
#
#     for i in range(len(tags)):
#         img_url = tags[i]['data-source']
#         res_img = requests.get(img_url)
#         filename = f'static/{word}{i}.jpg'
#         with open(filename, 'wb') as f:
#             f.write(res_img.content)
#         result = result + f"<div><img src=/{filename}></div>"
#
#     # img_url = tags[0]['data-source']
#
#
#
#
#     return render_template('crawler.html',
#                            result=result)





app.run(port=8000)

import re
import json
import requests
from datetime import date, timedelta
from bs4 import BeautifulSoup
import requests
from flask import Flask, render_template, request

app = Flask(__name__, template_folder="templates")

# 자동갱신 되도록 설정
app.config['ENV'] = 'development'
app.config['DEBUG'] = True

@app.route("/")
def index():
    return "welcome day7 class 2222"

@app.route("/exam01", methods=['get', 'post'])
def exam01():
    result = ''
    if request.method == 'POST':
        result = request.form['numbers']
        result = [int(s.strip()) for s in result.split(',')]
        min_number = min(result)
        
        if min_number % 2 == 0:
            result = f'가장 작은 수 {min_number}는 짝수'
        else:
            result = f'가장 작은 수 {min_number}는홀수'
        
    return render_template('base.html', 
                           title="가장 작은 수 찾기",
                           result=result,
                           site="exam01",
                           placehoder="num1, num2, num3")

@app.route('/daum')
def daum():
    res = requests.get('http://daum.net')
    return res.text.replace('https://t1.daumcdn.net/daumtop_chanel/op/20170315064553027.png', 'https://ssl.pstatic.net/sstatic/search/nlogo/20200421102755.png')

@app.route('/pub/<sub>')
def daum_sub(sub):
    res = requests.get(f'http://daum.net/pub/{sub}',
                       params=request.args)
    return res.text

# 사용자로부터 2 ~ 9 사이의 숫자를 입력 받은 후, 
# 해당 숫자에 대한 구구단을 출력하세요.
@app.route('/gugu', methods=['get', 'post'])
def gugu():
    result = []
    if request.method == 'POST':
        number = int(request.form['numbers'].strip())
        for i in range(9):
            result.append(f'{number} * {i + 1} = {number * (i + 1)}')
        
    return render_template('base.html', 
                           title="구구단 출력하기",
                           result="<br>".join(result),
                           site="gugu",
                           placehoder="num")

# 사용자로부터 숫자를 N을 입력받은 후 
# 1부터 N까지의 숫자 중 3의 배수만 출력하세요.
@app.route('/multiple', methods=['get', 'post'])
def multiple():
    result = ''
    if request.method == 'POST':
        num = int(request.form['numbers'].strip())
        result = [str(i) for i in range(1, num + 1) if i % 3 == 0]
        
    return render_template('base.html', 
                           title="3의 배수 출력하기",
                           result=','.join(result),
                           site="multiple",
                           placehoder="num")

# *트리 출력
@app.route('/tree', methods=['get', 'post'])
def tree():
    # "&nbsp;"
    result = []
    for i in range(5):
        row = ""
        for j in range(i + 1):
            row += '*'
        result.append(row)
    
    return render_template('base.html', 
                           title="* 트리 출력하기",
                           result="<br>".join(result),
                           site="tree",
                           placehoder="num")

# 금지어 체크
@app.route('/reject', methods=['get', 'post'])
def reject():
    금지어 = ['볼드모트', '이숙번', '강두루', '이고잉']
    result = ''
    
    if request.method == 'POST':
        # 문자열을 text 변수에 받아서
        text = request.form['numbers']
        
        # 금지어 목록에서 하나씩 단어를 가져와서 
        for word in 금지어:
            # 금지어를 *** 로 replace
            text = text.replace(word, '***')
            
        result = text
    
    return render_template('base.html', 
                           title="금지어 체크하기",
                           result=result,
                           site="reject",
                           placehoder="문장을 입력해 주세요")

def get_hit_movies(date):
    # https://movie.daum.net/boxoffice/weekly?startDate=20200408
    res = requests.get(
        'https://movie.daum.net/boxoffice/weekly',
        params={'startDate': date.strftime("%Y%m%d")}
    )
    soup = BeautifulSoup(res.content, 'html.parser')

    movies = []
    for tag in soup.select('.desc_boxthumb'):
        text = tag.select(".list_state")[0].get_text()    
        regex = re.compile("주간관객 (\d+)명\n개봉일\n([0-9.]+) 개봉")
        관객수, 개봉일 = re.findall(regex, text)[0]
        movies.append({
            '제목': tag.select(".link_g")[0].get_text(),
            '평점': tag.select(".emph_grade")[0].get_text(),
            '관객수': 관객수,
            '개봉일': 개봉일,
        })
        
    return movies

@app.route('/daum/movies')
def movies():
    week = int(request.args.get('week', '1'))

    # weeks를 만들거에요
    # week이 1이면, [20200415]
    # week이 2이면, [20200415, 20200408]
    # week이 3이면, [20200415, 20200408, 20200401]
    weeks = []
    w = date.today()
    for i in range(week):
        w = w - timedelta(days=7)
        weeks.append(w)

    movies = {}
    for w in weeks:
        movies[w.strftime("%Y%m%d")] = get_hit_movies(w)
        
    return json.dumps(movies)

@app.route('/naver/realtime')
def realtime():
    realtime = []
    res = requests.get("https://www.naver.com/srchrank?frm=main&ag=40s&gr=4&ma=-2&si=0&en=0&sp=0")
    result = res.json()
    
    return json.dumps(result['data'])

@app.route("/findnum")
def findnum():
    import random
    
    def find_duplicated_num(nums):
        return sum(nums) - ((len(nums) - 1) *  (len(nums)) / 2)
        
#        return sum(nums) - sum(set(nums))
    
#         check = []
#         for i in nums:
#             if i not in check:
#                 check.append(i)
#             else:
#                 return i

        return 0

    num = int(request.args.get('num', '10'))
    numbers = list(range(1, num + 1))
    numbers.insert(random.randint(1, num), random.randint(1, num))
    print(numbers)

    num = find_duplicated_num(numbers)
    return str(numbers) + '<br>' + str(num)


@app.route('/rating')
def rating():
    ratings = {
        '이숙번': {'1917': 5, '엽문4': 2, '라라랜드': 3, '주디': 5},
        '강두루': {'1917': 4, '라라랜드': 3, '신과나': 5},
        '이고잉': {'라라랜드': 4, '엽문4': 4, '주디': 1},
        '정원혁': {'엽문4': 3, '신과나': 5, '1917': 4, '주디': 2}
    }
    
    # 영화를 평균평점순으로 정렬
    def pivot_by_movies(ratings):
        movies = {}
        for name, records in ratings.items():
            for m_name, m_rate in records.items():
                if m_name not in movies:
                    movies[m_name] = []
                movies[m_name].append(m_rate)

        return list(movies.items())
#         return [
#             ('1917', [5, 1, 3]),
#             ('엽문4', [3, 1, 2])
#         ]

    movies = pivot_by_movies(ratings)
    sorted_movies = sorted(movies, 
                           key=lambda x: sum(x[1]) / len(x[1]),
                           reverse=True)
    return str(sorted_movies)

# python 파일명으로 실행을 위해서 필요
app.run(port=8001)
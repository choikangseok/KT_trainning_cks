
def add(a,b):
    return a+b

add2 = lambda a,b: a + b
print(add2(3,5))



members = [
{'id' : 'kangseok', '영어': 60, '수학' :80},
{'id' : 'stone', '영어': 100, '수학' :90},
{'id' : 'rock', '영어': 90, '수학' :70},
]
points = [60,90,100]
#어 정렬을 하고싶네?
#각각의 데이터에 적용할 함수 - 람
print(sorted(members, key=lambda x: (x['수학'] + x['영어']) /2))
print(list(map(lambda x: (x['수학'] + x['영어']), members)))

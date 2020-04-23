import random 

# 메일 내용을 message 변수에 담고
message = """안녕하세요, {0}님
파이썬 수업에 오신걸 환영합니다. 
오늘의 행운 로또번호는 {1} 입니다.. 
남은 기간 즐겁고 행복한 공부가 되길 기원합니다.
"""

def make_lotto():
    lotto = []
    while len(lotto) < 6:
        num = random.randint(1, 46)
        if num not in lotto:
            lotto.append(num)
    return lotto

# 누구에게 보낼지 이름을 입력을 받아서
who = input("누구에게 보낼건가요? ")
lotto = make_lotto()

# 메일 내용을 완성
complete_message = message.format(who, lotto)

# 화면에 출력한다.
print()
print("*" * 50)
print("메일 내용입니다.")
print("*" * 50)
print(complete_message)

# f = open('./mail.txt', 'w')
# f.write(complete_message)
# f.close()

with open('./mail.txt', 'w', encoding="utf-8") as f:
    f.write(complete_message)

# 메일을 바로 발송
# send_mail(complete_message)

lyrics = """When I find myself in times of trouble
Mother Mary comes to me
Speaking words of wisdom, let it be.
And in my hour of darkness
She is standing right in front of me
Speaking words of wisdom, let it be.
Let it be, let it be.
Whisper words of wisdom, let it be.
And when the broken hearted people
Living in the world agree,
There will be an answer, let it be.
For though they may be parted there is
Still a chance that they will see
There will be an answer, let it be
Let it be, let it be. Yeah
There will be an answer, let it be.
And when the night is cloudy,
There is still a light that shines on me,
Shine on until tomorrow, let it be.
I wake up to the sound of music
Mother Mary comes to me
Speaking words of wisdom, let it be.
Let it be, let it be.
There will be an answer, let it be.
Let it be, let it be,
Whisper words of wisdom, let it be.
"""


lyrics = lyrics.lower()

# 특수문자 찾기
chrs = set(lyrics) - set(' abcdefghijklmnopqrstuvwxyz')
print(chrs)

# chrs의 특수문자를 하나씩 꺼내서 lyrics 문자열 replace
for c in chrs:
    lyrics = lyrics.replace(c, '')

print(lyrics)

words= lyrics.split(' ')

word_dict ={}

print('word' in {'word' :1, 'when' :1, 'i': 3})
print('you' in {'word' :1, 'when' :1, 'i': 3})

for w in words:
    if w not in word_dict:
        word_dict[w] = 1
    else:
        word_dict[w] = word_dict[w] + 1
print(word_dict)

list(word_dict.items())

#튜플의 1번째 요소 변경
sorted_words = sorted(word_dict.items(), key=lambda x:x[1])
print(sorted_words[-10:])
selected = [e[0] for e in sorted_words[-10:]]
print(selected)
#lambda 함수는매우 어려움 사용하다보면 경험적으로 ..3가지경
#람다는 함수를 만드는 문법이다.

#재 사용성을 높인다는 말은?

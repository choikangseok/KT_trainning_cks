import re
from konlpy.tag import Kkma
kkma = Kkma()

lyrics = """When I find myself in times of trouble
Mother Mary comes to me
Speaking words of wisdom, let it be.
And in my hour of darkness
She is standing right in front of me
Speaking words of wisdom, let it be.
Let it be, let it be.
Whisper words of wisdom, let it be.
And when the broken hearted people@hanmail.net
Living in the world agree@singsing.com,
There will be an answer, let it begoing@asdasd.company.
For though they may be parted there is
Still a chance that they will see
There will be an answer, let it be
Let it be, let it be. Yeahss
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

# regex = re.compile("((\w+)@(\w+).(\w+))")
regex = re.compile("((\w{3})\w+@(\w+).(\w{2,5}))")
print(re.findall(regex, lyrics))
# print(re.sub(regex, "******", lyrics))
# print(re.sub(regex, "\g<2>@gmail.com", lyrics))
print(re.sub(regex, "\g<2>***@\g<3>", lyrics))

import requests
import re
from IPython.display import Image, display





response = requests.get('https://cafeptthumb-phinf.pstatic.net/20160429_3/joejoejoeyou_1461914353391F6y6p_JPEG/%BB%E7%C0%CC%C6%C7_%C0%DA%C0%AF%BF%A9%C7%E00429-0004-201604290003.JPG?type=w740')


with open('sample.jpg', 'wb') as f :
    f.write(response.content)


display(Image('sample.jpg', width=200))





# # print(re.sub(regex, "******", lyrics))
# # print(re.sub(regex, "\g<2>@gmail.com", lyrics))
# print(re.sub(regex, "\g<2>***@\g<3>", lyrics))

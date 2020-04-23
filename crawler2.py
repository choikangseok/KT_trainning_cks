import requests
import re




def get_urls(domain, path):
    response = requests.get(domain + path)

    if response.status_code == 200 :
        regex = re.compile('(href|HREF)="([^>"]+)"[^>]*>')
        urls = re.findall(regex, response.text)
        urls = [(domain, e) for e in urls]
        return urls

    else:
        return []
# regex = re.compile("<a href=")
# regex = re.compile('(a href="(http.+))"')

for item in get_urls('http://localhost:5000', '/'):
    print(item)




# # print(re.sub(regex, "******", lyrics))
# # print(re.sub(regex, "\g<2>@gmail.com", lyrics))
# print(re.sub(regex, "\g<2>***@\g<3>", lyrics))

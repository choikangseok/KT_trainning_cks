import requests

headers = {
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7,es;q=0.6',
}

response = requests.get('http://info.cern.ch/', headers=headers, verify=False)
print(response.text)



#꿀팁 소개
#curl과 자동생성


##https://curl.trillworks.com/
#curl코드를 넣으면 python reqeust 코드로 바뀜

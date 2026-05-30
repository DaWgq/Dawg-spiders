import requests


headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Cache-Control": "max-age=0",
    "Connection": "keep-alive",
    "Referer": "https://m.dianping.com/",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-site",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36",
    "sec-ch-ua": "\"Chromium\";v=\"148\", \"Google Chrome\";v=\"148\", \"Not/A)Brand\";v=\"99\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\""
}
cookies = {
    "logan_session_token": "c0v3jk617a0cliodpy71",
    "_lxsdk_cuid": "19e347686bac8-00b8124b241fd9-26061151-1fa400-19e347686bbc8",
    "_lxsdk": "19e347686bac8-00b8124b241fd9-26061151-1fa400-19e347686bbc8",
    "_hc.v": "b0ee079b-965f-ca15-3c63-af194841cca7.1778996644",
    "fspop": "test",
    "WEBDFPID": "1778996657507YOWSIIWfd79fef3d01d5e9aadc18ccd4d0c95072385-1778996657507-1778996657507YOWSIIWfd79fef3d01d5e9aadc18ccd4d0c95072385",
    "qruuid": "e8cb0f2a-a2de-4ad4-95bd-c393d180f98e",
    "dper": "0202f0235fc108a3340af1c8347aecd598c0e5bae238d67b76e2db5965c695573c458352cabcca952a3598c14801843e898e8ee74a25160bafea0000000013350000321d136ff03bb6f0c599de1167379e924d7eb2d0d24e6b35e3a498c789277eeb57cbfffba14223b8aaccf516bf60c2cb",
    "s_ViewType": "10",
    "ll": "7fd06e815b796be3df069dec7836c3df",
    "Hm_lvt_602b80cf8079ae6591966cc70a3940e7": "1778996760",
    "Hm_lpvt_602b80cf8079ae6591966cc70a3940e7": "1778996760",
    "HMACCOUNT": "45FC6488ADA4CC26",
    "_lxsdk_s": "19e347686bb-2c5-3ec-46a%7C%7C98"
}
url = "https://www.dianping.com/search/keyword/1/0_%E9%A6%99%E6%B8%AF"
response = requests.get(url, headers=headers, cookies=cookies)

print(response.text)
print(response)
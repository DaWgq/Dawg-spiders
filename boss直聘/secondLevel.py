import requests


headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0",
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "sec-ch-ua-platform": "\"Windows\"",
    "sec-ch-ua": "\"Chromium\";v=\"148\", \"Microsoft Edge\";v=\"148\", \"Not/A)Brand\";v=\"99\"",
    "sec-ch-ua-mobile": "?0",
    "zp_token": "V2RNMuFOf031xoVtRuxxwbLiyy7DrSzSg~|RNMuFOf031xoVtRuxxwbLiyy7Drfwik~",
    "x-requested-with": "XMLHttpRequest",
    "traceid": "F-0019e915d241eTP0ivi0yh",
    "token": "7PXlYq2jGhJWY52s",
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://www.zhipin.com/web/geek/jobs?city=101280600&query=ai%E5%AE%9E%E4%B9%A0",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
    "priority": "u=1, i"
}
cookies = {
    "Hm_lvt_194df3105ad7148dcf2b98a91b5e727a": "1780551145",
    "HMACCOUNT": "4218FB3A02F37806",
    "__g": "sem_bingpc",
    "wt2": "Do0yiyFcgkcp6Daghvb0Kprb3lVp3tnYNMHUlaSzB5sbV_4WPl_3SuQzzwMzSqarm7ongohk03-AIjTr3r5HKtQ~~",
    "wbg": "0",
    "zp_at": "Cc4_1UN3Piq7pI2XgCwUc6jmUixEfXvmaU7LxMimCAU~",
    "ab_guid": "816c5654-f1a4-4058-ac55-760f1e1dd3cb",
    "lastCity": "101280100",
    "__zp_seo_uuid__": "94363b9c-c3e7-4290-8630-51db37fcbd46",
    "__l": "r=https%3A%2F%2Fcn.bing.com%2F&l=%2Fwww.zhipin.com%2Fsem%2F10.html%3F_ts%3D1780552650819%26sid%3Dsem_bingpc%26qudao%3Dbing_pc_H120003UY5%26plan%3DBOSS-%25E5%25BF%2585%25E5%25BA%2594-%25E5%2593%2581%25E7%2589%258C%26unit%3D%25E7%25B2%25BE%25E5%2587%2586%26keyword%3Dboss%25E7%259B%25B4%25E8%2581%2598%26msclkid%3D905c111b130a188a2b057b3a00c306fa&s=1&g=%2Fwww.zhipin.com%2Fsem%2F10.html%3F_ts%3D1780552650819%26sid%3Dsem_bingpc%26qudao%3Dbing_pc_H120003UY5%26plan%3DBOSS-%25E5%25BF%2585%25E5%25BA%2594-%25E5%2593%2581%25E7%2589%258C%26unit%3D%25E7%25B2%25BE%25E5%2587%2586%26keyword%3Dboss%25E7%259B%25B4%25E8%2581%2598%26msclkid%3D905c111b130a188a2b057b3a00c306fa&s=3&friend_source=0",
    "Hm_lpvt_194df3105ad7148dcf2b98a91b5e727a": "1780552652",
    "__zp_stoken__": "0df7gNTTDn8K4w6TCtlFBO1I1KDk3TjU0TzVMNTR8JDo6S1BQTRjDnsOPw4QZFW3DoMSRw5E0KU83UjU0OTc1UBlPQzo6NFA2OsWLw4s4NjrCsjU%2FI8OGwrXDhyMXbMOKB8OtwrgGwrLDi0HEgsK1BhscwojCuig7HgRWBSJtYx0FIWsEBApWChNVByFaVFRXVGwHIAVWIAgaFU4IwrTCusODQ8OMwrjDgzvCt2zCtTo6S1AoNjrCuzQoUTQ3T1A3xYvEusWRxLnEuMWLxLrFkcOhxIvDr8S6xZHEucOLxYvEusWRw7nDq8WLxLrFkcS5w7rCuj1PwqHCusKjxK7CuXPDqsSUwprDi8SOw4vCrEjCicK9wrZdwqJiXH3ChGVTbFNbwqTDjmFrwr1da2Fdw4PDjcK2wqTCg2hjdGtpHMKQwoHDknMgHlRyBDYTFXHDig%3D%3D",
    "__c": "1780551146",
    "__a": "48939414.1780551145..1780551146.21.1.21.21",
    "bst": "V2RNMuFOf031xoVtRuxxwbLiyy7DrSzSg~|RNMuFOf031xoVtRuxxwbLiyy7Drfwik~",
    "__zp_sseed__": "QxG307Q2Z07rxdsOa7bgENDI7nrnFXFIgF6bTRxXpfk=",
    "__zp_sname__": "0f41efed",
    "__zp_sts__": "1780555262511"
}
url = "https://www.zhipin.com/wapi/zpgeek/job/detail.json"
params = {
    "securityId": "WxnNjG5k3oH4C--1ks5nJjZCvOaZ0d90LuOA3XDgrLAoK57EDJ2bwrs0OFS9lZQFH_GqEdfX48TBykzZD6UeaYT9AGb9a3nVzf0JMq5THRFR2OJwwCJejFSYfC0a9qhAsLcSUsD1VviSUOVY9vEhSKOOcCYf8oB5bBoXp-Mrpxk99mdL6qHhlNnsNjnIgSJarQiDX_EPwSsfiJm-ZLvEpP1uqKI4fRZ6kJpfCiNwiu1nisif1ZrLEY16u8JFg0A9ghkQ9IX2hbXlVC9MyIJ-16r2qQVodxTx6mYekoN5z9Cmwo8vz3XjmqK_zM07V1GF7AW3Y-8~",
    "lid": "34ZmDcvZWAp.search.1",
    "_": "1780555260958"
}
response = requests.get(url, headers=headers, cookies=cookies, params=params)

print(response.text)
print(response)
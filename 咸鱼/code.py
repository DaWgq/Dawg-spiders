import requests


headers = {
    "Accept": "application/json",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Connection": "keep-alive",
    "Content-type": "application/x-www-form-urlencoded",
    "Origin": "https://www.goofish.com",
    "Referer": "https://www.goofish.com/",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-site",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36",
    "sec-ch-ua": "\"Google Chrome\";v=\"147\", \"Not.A/Brand\";v=\"8\", \"Chromium\";v=\"147\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\""
}
cookies = {
    "cna": "Gm5/In55snoCAbz9BOPVXW4C",
    "t": "dd5e21f58f5f44183bf0d6615ff5f601",
    "xlly_s": "1",
    "tracknick": "tb975336787",
    "unb": "2209394220946",
    "havana_lgc2_77": "eyJoaWQiOjIyMDkzOTQyMjA5NDYsInNnIjoiYmQxNWM3MDVhYmE4M2UzZjY0YTcwZGQ1ZDcyYTg5OWEiLCJzaXRlIjo3NywidG9rZW4iOiIxLU5VUnYtd2dmQjR3ZVM0TURMWktTdyJ9",
    "_hvn_lgc_": "77",
    "havana_lgc_exp": "1780554142056",
    "mtop_partitioned_detect": "1",
    "_m_h5_tk": "ad8015e1f81f7125d1673b09342f385a_1778147590093",
    "_m_h5_tk_enc": "37e5b311f601585cf09e3c496976ac8d",
    "cookie2": "1f16870213c08a9595b83b694762b0c2",
    "_samesite_flag_": "true",
    "_tb_token_": "fed7b557655b9",
    "sdkSilent": "1778226579919",
    "sgcookie": "E100NS9kcTxAvdDiQmtTK%2F0g873dpABw7hHb5BN%2FC7WrtYEZnQjBYBaCLngRMm%2BsYHC36eZNdIWg%2BB%2F2Gou8p3s%2F6Y0lpTIo1fnRCeA%2FZQrLrBI%3D",
    "csg": "68bc5391",
    "tfstk": "gghoAnGJRYy7ySS2sMPWnW08MxJYP7NQVDCLvWEe3orbvUZ822on-VyE27FRKB0E4Jl8w4nmt0nxy3iLwMAnmond94hnh60sRbL79UNSPWNeXhdtx4g7O3weY1lu0rz-uyWU8KFqVrI7nhd9649HwVOWXYITlzUQ8Wzz4Wy2oPUUT_zrYoy47PIzTWoeoSz8Jy5z86743PE4YWPEYq80RozzTWoEuE4INC1UjXljghwripOaXoc0r8qZod1Ft-CTUlz8m6-ZizjUb4rcT6rNtL4ro4Kl1qFSsc4t2I5ojVGjmrowtnVIcvoU-mR1v7MtVfwmld5qr7qbQvyDzQu0Zu2tTRbdF7DEVX2SEwTsu7ojClwyhnamwfe3f-j24q304RDn2n1U2A0qmRhAD1FIcvoU-mSl46WVQhA5Or8Ki96QUra0XCYD1gEDLch6oEX6F8zbyhLDo96QUra0XEYcCgwzlzKO."
}
url = "https://h5api.m.goofish.com/h5/mtop.taobao.idlemtopsearch.pc.search/1.0/"
params = {
    "jsv": "2.7.2",
    "appKey": "34839810",
    "t": "1778140200967",
    "sign": "bcb91b6ac29bf203ecfd326a63d78179",
    "v": "1.0",
    "type": "originaljson",
    "accountSite": "xianyu",
    "dataType": "json",
    "timeout": "20000",
    "api": "mtop.taobao.idlemtopsearch.pc.search",
    "sessionOption": "AutoLoginOnly",
    "spm_cnt": "a21ybx.search.0.0",
    "spm_pre": "a21ybx.home.searchHistory.1.4c053da60OhhHx",
    "log_id": "4c053da60OhhHx"
}
data = {
    "data": "{\"pageNumber\":1,\"keyword\":\"手机\",\"fromFilter\":false,\"rowsPerPage\":30,\"sortValue\":\"\",\"sortField\":\"\",\"customDistance\":\"\",\"gps\":\"\",\"propValueStr\":{},\"customGps\":\"\",\"searchReqFromPage\":\"pcSearch\",\"extraFilterValue\":\"{}\",\"userPositionJson\":\"{}\"}"
}
response = requests.post(url, headers=headers, cookies=cookies, params=params, data=data)

print(response.text)
print(response)
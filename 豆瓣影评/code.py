import requests


headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
    "cache-control": "max-age=0",
    "priority": "u=0, i",
    "referer": "https://movie.douban.com/subject/37311135/",
    "sec-ch-ua": "\"Chromium\";v=\"148\", \"Google Chrome\";v=\"148\", \"Not/A)Brand\";v=\"99\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "same-origin",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36"
}
cookies = {
    "bid": "Htiy226TElU",
    "__utmz": "223695111.1778748586.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none)",
    "dbcl2": "\"295041390:eA11Lf61S2M\"",
    "push_noty_num": "0",
    "push_doumail_num": "0",
    "ck": "EAt6",
    "_gid": "GA1.2.1176574715.1778748564",
    "ll": "\"108288\"",
    "_ga": "GA1.2.1051032409.1778748564",
    "_ga_Y4GN1R87RG": "GS2.1.s1778748564$o1$g1$t1778748580$j44$l0$h0",
    "_pk_ref.100001.4cf6": "%5B%22%22%2C%22%22%2C1778748582%2C%22https%3A%2F%2Fm.douban.com%2F%22%5D",
    "_pk_id.100001.4cf6": "0f0a2bed7637f8f7.1778748582.",
    "_pk_ses.100001.4cf6": "1",
    "frodotk_db": "\"0e9d90a34a31fdf92bd8b1e9de95f9eb\"",
    "__utma": "223695111.1051032409.1778748564.1778748586.1778748586.1",
    "__utmb": "223695111.0.10.1778748586",
    "__utmc": "223695111",
    "ap_v": "0,6.0"
}
url = "https://movie.douban.com/subject/37311135/comments"
params = {
    "start": "40",
    "limit": "20",
    "status": "P",
    "sort": "new_score"
}
response = requests.get(url, headers=headers, cookies=cookies, params=params)

print(response.text)
print(response)
import requests


headers = {
    "accept": "*/*",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
    "origin": "https://www.bilibili.com",
    "priority": "u=1, i",
    "referer": "https://www.bilibili.com/video/BV1A498BRE5n/?spm_id_from=333.1007.tianma.1-1-1.click&vd_source=3456678bb253224e626749aced66d92d",
    "sec-ch-ua": "\"Google Chrome\";v=\"147\", \"Not.A/Brand\";v=\"8\", \"Chromium\";v=\"147\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36"
}

cookies = {
    "buvid3": "56FEC1DF-5748-D67A-3738-6FB0C2A211B897753infoc",
    "b_nut": "1774279197",
    "buvid_fp": "d40b9a502557c4478d29ffe87b8a9238",
    "_uuid": "7A6E2E4F-CC9E-ED96-41051-101484110621A836891infoc",
    "home_feed_column": "5",
    "browser_resolution": "1920-911",
    "buvid4": "95260B2C-C5E7-11D3-8BA4-B59BD39E0CC299830-026032323-jXAwpThs/uHcVLyEMMrcEA%3D%3D",
    "CURRENT_QUALITY": "0",
    "rpdid": "|(Jlk)RJuu|~0J'u~~Yl||J~R",
    "SESSDATA": "5efc8e10%2C1792052401%2C7fd53%2A41CjBvo3tsfUYzNiZGgz23jnfTX7NsY_jgEW8FdF6XXrzFOCwD5e2dO5nhvl6Zv0jvdIUSVk56dUMzYXVzMk1XZTlIdWdWNXBBN0tMdjdjVkFpYlVKa3BZMlQ2Z0JEb3FmTHB0aEFtODRoZ3NreFZURzY4X21ObVBnVmFNNVJRYk5rYW5FVlEtdjRnIIEC",
    "bili_jct": "d72ba988e8ee8af4f73a2d8a06363fdd",
    "DedeUserID": "437579001",
    "DedeUserID__ckMd5": "d4fd9e3306c0831a",
    "theme-tip-show": "SHOWED",
    "theme-avatar-tip-show": "SHOWED",
    "bp_t_offset_437579001": "1201165188615634944",
    "bili_ticket": "eyJhbGciOiJIUzI1NiIsImtpZCI6InMwMyIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3Nzg3Njg5MjMsImlhdCI6MTc3ODUwOTY2MywicGx0IjotMX0.2V57YPqVPpkXRtnfAiMYivlBkFLM_R2Z-BKzsi-2Log",
    "bili_ticket_expires": "1778768863",
    "CURRENT_FNVAL": "4048",
    "sid": "glo0eor7",
    "b_lsid": "F43C722C_19E1B3FB682"
}

url = "https://api.bilibili.com/x/v2/reply/wbi/main"

params = {
    "oid": "116492163095535",
    "type": "1",
    "mode": "3",
    "pagination_str": "%7B%22offset%22:%22%22%7D",
    "plat": "1",
    "seek_rpid": "",
    "web_location": "1315875",
    "w_rid": "d7b139c05244b6a5ff27453758584f07",
    "wts": "1778573621"
}

response = requests.get(url, headers=headers, cookies=cookies, params=params)

print(response.text)
print(response)
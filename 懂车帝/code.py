import random
import time

import requests


headers = {
    "accept": "*/*",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
    "content-type": "application/x-www-form-urlencoded",
    "origin": "https://www.dongchedi.com",
    "priority": "u=1, i",
    "referer": "https://www.dongchedi.com/auto/library/x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-3-x-x",
    "sec-ch-ua": "\"Google Chrome\";v=\"147\", \"Not.A/Brand\";v=\"8\", \"Chromium\";v=\"147\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36",
    "x-real-ip;": ""
}
cookies = {
    "ttwid": "1%7CeKISQ7wInDSnZx3t3P02vdOdlLHiINDoYTYlJLw6Iew%7C1778151588%7Cb1cae4636e4ac6b1d3471cdbc1b8fa18b21a6942166ad4401de8ecc7bdccf715",
    "tt_webid": "7637102832361948697",
    "tt_web_version": "new",
    "is_dev": "false",
    "is_boe": "false",
    "gfkadpd": "1839,45203",
    "x-web-secsdk-uid": "3bd78cd6-4bdf-4297-a347-954e4531ed95",
    "s_v_web_id": "verify_movdjo5d_T8f6CQNj_LvVG_4Obi_AWHr_g4IjC4LDVj73",
    "Hm_lvt_3e79ab9e4da287b5752d8048743b95e6": "1778151590",
    "HMACCOUNT": "45FC6488ADA4CC26",
    "city_name": "%E5%8C%97%E4%BA%AC",
    "_gid": "GA1.2.1288839844.1778151603",
    "Hm_lpvt_3e79ab9e4da287b5752d8048743b95e6": "1778151635",
    "_ga": "GA1.2.964505362.1778151589",
    "_gat_gtag_UA_138671306_1": "1",
    "_ga_YB3EWSDTGF": "GS2.1.s1778151588$o1$g1$t1778151697$j39$l0$h0"
}
url = "https://www.dongchedi.com/motor/pc/car/brand/select_series_v2"
params = {
    "aid": "1839",
    "app_name": "auto_web_pc",
    "msToken": "cHM8PsvimjYAnx9n4wpWFJTNdlzprm-gnSRoecVl68KUYOii6Upyj2hqJ6tBV3bGYuh2xCaDPSA9t25wo1f52wXga6g1uUTfs72yziKPUxm2oEtTxsil_miY4Adnujei7ZIoJYWzqkyJPIGrC8cfNns08wXTjjLdCOjui05He2im",
    "a_bogus": "D6U5h7UEEqAcOpCbYOQMt4/UDCDlNsWy93TObJTkCPOjahtPsLPxR9DcnKi-TppyA8B9oHI7ndsKbnjcmo6j6l9kLmZfSBwbb0VCIh8ogqwsTMiQDq6MC0YzuwMNUcGql557iIR62UJq6fnAhHdE/pl9SKoe5RWBBZOWk/ucx9sh1FLAEpnaPQtdNhPz0Inv"
}
# data = {
#     "brand": "3",
#     "sort_new": "hot_desc",
#     "city_name": "北京",
#     "limit": "30",
#     "page": "3"
# }

for i in range(10):
    data = {
        "brand": "3",
        "sort_new": "hot_desc",
        "city_name": "北京",
        "limit": "30",
        "page": f"{i}"
    }
    time.sleep(random.randint(1, 3))
    print(requests.post(url, headers=headers, cookies=cookies, params=params, data=data).text)

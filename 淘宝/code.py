import requests


headers = {
    "accept": "*/*",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
    "referer": "https://s.taobao.com/",
    "sec-ch-ua": "\"Google Chrome\";v=\"147\", \"Not.A/Brand\";v=\"8\", \"Chromium\";v=\"147\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "sec-fetch-dest": "script",
    "sec-fetch-mode": "no-cors",
    "sec-fetch-site": "same-site",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36"
}
cookies = {
    "mtop_partitioned_detect": "1",
    "_m_h5_tk": "df86c2085ed32a1cc02145dc76aa5eae_1777012594987",
    "_m_h5_tk_enc": "b43e91add7dc99aed1f6ab43209a351b",
    "xlly_s": "1",
    "t": "6878bc5521b1a890bc9175e0cc65a788",
    "_tb_token_": "07bf34b97eee",
    "sca": "b8871d5e",
    "thw": "xx",
    "cookie2": "27e4375021d34bb74af7e8b36fc9a1ef",
    "_samesite_flag_": "true",
    "cna": "h9dxItxF4UYCAbz9BOOXFEJX",
    "3PcFlag": "1777002895575",
    "unb": "2209394220946",
    "lgc": "tb975336787",
    "cancelledSubSites": "empty",
    "cookie17": "UUphw2ZQNahEaWo%2FnA%3D%3D",
    "dnk": "tb975336787",
    "tracknick": "tb975336787",
    "_l_g_": "Ug%3D%3D",
    "sg": "765",
    "_nk_": "tb975336787",
    "cookie1": "AiPMjv1hZo%2F57GGgm%2BFAgIDTfI7P9Gs9DRgz5RJrrm0%3D",
    "sgcookie": "E100VWFVhF17mzHG3bCMh4aRF7wyEFzn7irxX6ww7GFfWg0fZK6ZIFFhQHLgW6OzTGLiPXF7cZowlxo53KQOpW7J2y%2BNb39zDqTLsVRmcYMRqGA%3D",
    "havana_lgc2_0": "eyJoaWQiOjIyMDkzOTQyMjA5NDYsInNnIjoiN2JkN2VlOWI3OTJlMWIyNmRhOWZhYjAzMGZhYWIwNWYiLCJzaXRlIjowLCJ0b2tlbiI6IjFYbTRwYUI3TzJZZEMxRVJ2Qzh6UTBnIn0",
    "_hvn_lgc_": "0",
    "havana_lgc_exp": "1808106922176",
    "cookie3_bak": "27e4375021d34bb74af7e8b36fc9a1ef",
    "cookie3_bak_exp": "1777262122176",
    "wk_cookie2": "16ed12d665ba7a8471e771307594d290",
    "wk_unb": "UUphw2ZQNahEaWo%2FnA%3D%3D",
    "uc1": "pas=0&cookie14=UoYZbYrVSRUuPg%3D%3D&existShop=false&cookie16=VT5L2FSpNgq6fDudInPRgavC%2BQ%3D%3D&cookie15=URm48syIIVrSKA%3D%3D&cookie21=WqG3DMC9FxUx",
    "uc3": "vt3=F8dD29octsCXimHjx7M%3D&id2=UUphw2ZQNahEaWo%2FnA%3D%3D&nk2=F5RMHl%2F297M0iBI%3D&lg2=U%2BGCWk%2F75gdr5Q%3D%3D",
    "csg": "7e3ecd6f",
    "env_bak": "FM%2BgmqK9a2XF76NvndNHX7%2BjLjqp0DtZo8bUc%2BiHXw2L",
    "skt": "6530ca6c6704441b",
    "existShop": "MTc3NzAwMjkyMg%3D%3D",
    "uc4": "id4=0%40U2grGNnTItmXNBbFQzVjcG%2BYlIXKQMGz&nk4=0%40FY4HWyoAUY1pHUtsE%2FaR%2BwN7nDFdog%3D%3D",
    "_cc_": "U%2BGCWk%2F7og%3D%3D",
    "tfstk": "gFOZBy6Itfhw_NnkzUfqLvmEbJCOZsoS_IsfoEYc5GjGfEbcgHxjWGTmXnRVxEpsWtiTuPde4SNsXAL0gs1mV0GSNF3OMsmWWKdukGQv-i0CIl8G6PfmV0GQdyXtfsY6PLgctJbRxNVGIt0FxabViZjMmMXhraZGisxm8Xb5oN2gi543tMQciixci25hvZ5cmnfm8ec5PFY0Ta6i77lQD0ufSOSkSMP2WB7GQRLGYSVDTpWNq7sUiSAFSEVI3cNrhgvRfTskxXNNgeb2fMtoZW5hULLfuhlas19HpCC6O0zRQnSFEB6UjRbP_GWks9UgieBDLB56smeJReSGU69Ipc6f_hJR2ODKvn8FfnANKloCcLTBs9-oAW-A3LLfuhlas3jywoQnixOvQo2VIwQFV2uEBAIhPu33fl2YH9fR8gg15-eAIwQFV2uUH-BhywSS5N1..",
    "isg": "BDY2Ve-MQ2sWTTcPOfb9Slc8h2w4V3qR9KOa_KAfIpm149Z9COfKoZyV-7-Py3Kp"
}
url = "https://h5api.m.taobao.com/h5/mtop.relationrecommend.wirelessrecommend.recommend/2.0/"
params = {
    "jsv": "2.7.4",
    "appKey": "12574478",
    "t": "1777003078691",
    "sign": "3ab44836f855ec0729dbc1429c2074bb",
    "api": "mtop.relationrecommend.wirelessrecommend.recommend",
    "v": "2.0",
    "timeout": "10000",
    "type": "jsonp",
    "dataType": "jsonp",
    "callback": "mtopjsonp6",
    "data": "{\"appId\":\"34385\",\"params\":\"{\\\"device\\\":\\\"HMA-AL00\\\",\\\"isBeta\\\":\\\"false\\\",\\\"grayHair\\\":\\\"false\\\",\\\"from\\\":\\\"nt_history\\\",\\\"brand\\\":\\\"HUAWEI\\\",\\\"info\\\":\\\"wifi\\\",\\\"index\\\":\\\"4\\\",\\\"rainbow\\\":\\\"\\\",\\\"schemaType\\\":\\\"auction\\\",\\\"elderHome\\\":\\\"false\\\",\\\"isEnterSrpSearch\\\":\\\"true\\\",\\\"newSearch\\\":\\\"false\\\",\\\"network\\\":\\\"wifi\\\",\\\"subtype\\\":\\\"\\\",\\\"hasPreposeFilter\\\":\\\"false\\\",\\\"prepositionVersion\\\":\\\"v2\\\",\\\"client_os\\\":\\\"Android\\\",\\\"gpsEnabled\\\":\\\"false\\\",\\\"searchDoorFrom\\\":\\\"srp\\\",\\\"debug_rerankNewOpenCard\\\":\\\"false\\\",\\\"homePageVersion\\\":\\\"v7\\\",\\\"searchElderHomeOpen\\\":\\\"false\\\",\\\"search_action\\\":\\\"initiative\\\",\\\"sugg\\\":\\\"_4_1\\\",\\\"sversion\\\":\\\"13.6\\\",\\\"style\\\":\\\"list\\\",\\\"ttid\\\":\\\"600000@taobao_pc_10.7.0\\\",\\\"needTabs\\\":\\\"true\\\",\\\"areaCode\\\":\\\"CN\\\",\\\"vm\\\":\\\"nw\\\",\\\"countryNum\\\":\\\"156\\\",\\\"m\\\":\\\"pc\\\",\\\"page\\\":1,\\\"n\\\":48,\\\"q\\\":\\\"%E6%89%8B%E6%9C%BA\\\",\\\"qSource\\\":\\\"url\\\",\\\"pageSource\\\":\\\"a21bo.jianhua/a.search_manual.0\\\",\\\"channelSrp\\\":\\\"\\\",\\\"tab\\\":\\\"all\\\",\\\"pageSize\\\":48,\\\"totalPage\\\":100,\\\"totalResults\\\":4800,\\\"sourceS\\\":\\\"0\\\",\\\"sort\\\":\\\"_coefp\\\",\\\"bcoffset\\\":\\\"\\\",\\\"ntoffset\\\":\\\"\\\",\\\"filterTag\\\":\\\"\\\",\\\"service\\\":\\\"\\\",\\\"prop\\\":\\\"\\\",\\\"loc\\\":\\\"\\\",\\\"start_price\\\":null,\\\"end_price\\\":null,\\\"startPrice\\\":null,\\\"endPrice\\\":null,\\\"itemIds\\\":null,\\\"p4pIds\\\":null,\\\"p4pS\\\":null,\\\"categoryp\\\":\\\"\\\",\\\"ha3Kvpairs\\\":null,\\\"myCNA\\\":\\\"h9dxItxF4UYCAbz9BOOXFEJX\\\",\\\"screenResolution\\\":\\\"1920x1080\\\",\\\"viewResolution\\\":\\\"1905x457\\\",\\\"userAgent\\\":\\\"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36\\\",\\\"couponUnikey\\\":\\\"\\\",\\\"subTabId\\\":\\\"\\\",\\\"np\\\":\\\"\\\",\\\"clientType\\\":\\\"h5\\\",\\\"isNewDomainAb\\\":\\\"false\\\",\\\"forceOldDomain\\\":\\\"false\\\"}\"}",
    "bx-ua": "fast-load"
}
response = requests.get(url, headers=headers, cookies=cookies, params=params)

print(response.text)
print(response)
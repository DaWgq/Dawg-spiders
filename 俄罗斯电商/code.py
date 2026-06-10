import requests


headers = {
    "accept": "*/*",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
    "referer": "https://s.1688.com/",
    "sec-ch-ua": "\"Chromium\";v=\"148\", \"Google Chrome\";v=\"148\", \"Not/A)Brand\";v=\"99\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "sec-fetch-dest": "script",
    "sec-fetch-mode": "no-cors",
    "sec-fetch-site": "same-site",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36"
}
cookies = {
    "leftMenuLastMode": "COLLAPSE",
    "mtop_partitioned_detect": "1",
    "_m_h5_tk": "b4228dfaba0dad71f358f8a1542c2b59_1780395299419",
    "_m_h5_tk_enc": "cfa02086c564b950d107b0b597a30b40",
    "oversearegion": "CN",
    "overseaRegionName": "%E7%AE%80%E4%BD%93%E4%B8%AD%E6%96%87",
    "oversealanguage": "zh",
    "overseacurrency": "CNY",
    "leftMenuModeTip": "shown",
    "xlly_s": "1",
    "plugin_home_downLoad_cookie": "%E4%B8%8B%E8%BD%BD%E6%8F%92%E4%BB%B6",
    "cookie1": "AiPMjv1hZo%2F57GGgm%2BFAgIDTfI7P9Gs9DRgz5RJrrm0%3D",
    "cookie2": "1ef075f743df3e52c1e8ce194d37f812",
    "cookie17": "UUphw2ZQNahEaWo%2FnA%3D%3D",
    "sgcookie": "E100hvWMrgAzItEtgCY%2FoFB2oNXir8v4sgPF%2FYluMsenwrx5htD6NnjKGdzmS9FQJ2N4lc02zhEfpXtU%2FeE4Q1aOrOWnLe5wSL20Hnrz5s%2BVLvc%3D",
    "t": "6878bc5521b1a890bc9175e0cc65a788",
    "_tb_token_": "5e3ee7b81970a",
    "sg": "765",
    "csg": "55bb458e",
    "lid": "tb975336787",
    "unb": "2209394220946",
    "uc4": "nk4=0%40FY4HWyoAUY1pHUtsE%2FaeKweOFFx8DQ%3D%3D&id4=0%40U2grGNnTItmXNBbFQzVjcGAPPMomT7dG",
    "_nk_": "tb975336787",
    "_csrf_token": "1780384883932",
    "__cn_logon__": "true",
    "__cn_logon_id__": "tb975336787",
    "__last_loginid__": "b2b-220939422094652e04",
    "__last_memberid__": "b2b-220939422094652e04",
    "last_mid": "b2b-220939422094652e04",
    "cna": "WnKlIoXQdCwCAbnc7ry7lIcF",
    "isg": "BIWF8qKdQxp302dGc8FwW1mjlMG_QjnUxyc0oofqQbzLHqWQT5JJpBPsKkLoXlGM",
    "keywordsHistory": "%E7%BA%A2%E7%B1%B3%E6%89%8B%E6%9C%BA",
    "_user_vitals_session_data_": "{\"user_line_track\":true,\"ul_session_id\":\"9fugrvtv07\",\"last_page_id\":\"s.1688.com%2Fyno4j0o43vj\"}",
    "tfstk": "gIGZA42BtCdw8k-oz4V2UDzc3sNTNS-7IjZboq005lqgfqVhKPUgnfNs5DrmVDVbfELAg-qnvxMXW-iQm0i4lfGjoZzmA52xCoZ_0Sux4etWNQgtWSFHV3O7hhU2mSEDGSvQtnEPRHtWNQgMIPFj-3Mfurezuz10iRqgKBqLrPjmmofH8r4fjtfim2YUvrrcjSf0xW48utV0im0H8rE3SS2im2YUkkqmNAuio6z7IF_LBOGpcPwaqVqFa2hUSy6tSk5GsXkUQuj7YsfmTPuY5wDlaKZoelw7qDAC_Su3ucZIqQfUt8k-lrow_1VsKvhT1XtPyRo4Y8cQLGXgz5raEf2dSs0LnvlU1fxAe2gUj8PIdpK_h5oZeueMpHnq8lim_JjwAoMSRf2EqH1ED-k-lrow_1ml4IjY-IvjMASc3R4L8uTe8LEbuU5bZZkhHte3wyrW5P6AHR4L8uTe8tBYKzUUVFa1."
}
url = "https://h5api.m.1688.com/h5/mtop.relationrecommend.wirelessrecommend.recommend/2.0/"
params = {
    "jsv": "2.7.4",
    "appKey": "12574478",
    "t": "1780384930946",
    "sign": "2aa8c0825f81c15f98eb117cca112af5",
    "api": "mtop.relationrecommend.WirelessRecommend.recommend",
    "v": "2.0",
    "jsonpIncPrefix": "reqTppId_32517_getOfferList",
    "excludeKeys": "",
    "type": "jsonp",
    "dataType": "jsonp",
    "callback": "mtopjsonpreqTppId_32517_getOfferList2",
    "data": "{\"appId\":32517,\"params\":\"{\\\"beginPage\\\":1,\\\"pageSize\\\":60,\\\"method\\\":\\\"getOfferList\\\",\\\"pageId\\\":\\\"j0oooCBwfW8Rwx0JCPLOMEuQE0yo3WtQp7BO3xhLTozP9fct\\\",\\\"verticalProductFlag\\\":\\\"pcmarket\\\",\\\"searchScene\\\":\\\"pcOfferSearch\\\",\\\"charset\\\":\\\"GBK\\\",\\\"spm\\\":\\\"a260k.home2025.searchbox.0\\\",\\\"keywords\\\":\\\"%BA%EC%C3%D7%CA%D6%BB%FA\\\"}\"}"
}
response = requests.get(url, headers=headers, cookies=cookies, params=params)

print(response.text)
print(response)
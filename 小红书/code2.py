import requests


headers = {
    "accept": "application/json, text/plain, */*",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
    "origin": "https://www.xiaohongshu.com",
    "priority": "u=1, i",
    "referer": "https://www.xiaohongshu.com/",
    "sec-ch-ua": "\"Chromium\";v=\"148\", \"Google Chrome\";v=\"148\", \"Not/A)Brand\";v=\"99\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36",
    "x-b3-traceid": "0bd1282876c82d49",
    "x-s": "XYS_2UQhPsHCH0c1PUhMHjIj2erjwjQhyoPTqBPT49pjHjIj2eHjwjQgynEDJ74AHjIj2ePjwjQTJdPIPAZlg94aGLTlqnhhJD8GnpDMLpzbzemk8rpUJLMyygQawepn/URx2bSoyFDUy0mP+FDF8oH6ad4FzFp1J/znLgSI+eStyDMYGS8L4fqIankHLnRopbZEPbmhwoYdL0c9/0z0Pbzh2f4B4oYka/4YPd4NJLEL/BQmPrkHaMY/4bSPz9DlPaT+c9EIqMQCLDkcpnbLP9lrJrT/Jfznnfl0yLLIaSQQyAmOarEaLSz+q7b6aFHI2Lc9a/YTpjR9/MYjwomc/aHVHdWFH0ijHdF=",
    "x-s-common": "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",
    "x-t": "1778911906427",
    "x-xray-traceid": "cf17b4c51f912c71bdf78168909b0f89"
}
cookies = {
    "abRequestId": "8fb1f146-0519-522c-a76e-60bfc72f047a",
    "ets": "1777896065160",
    "xsecappid": "xhs-pc-web",
    "a1": "19df2dd08e1408ye9unxy1rr8cuhsb7xaqpruuv1650000402431",
    "webId": "aa22da5c093a56f2c342538330d9016e",
    "gid": "yjfiJffJSS0jyjfiJff8YA7hdy48Yvdj7ICvUyKyFFYS7F28xMDWC788848J4qy84WDKJWDq",
    "web_session": "040069b60e287e3396574dc3cd3b4b21504ee0",
    "id_token": "VjEAAFqe5rGutQtuqUQ+4hMXJ3h0MQ8guVS6sMdK2ud8Tu8TVZrA9ZP17CV3L4D3LoXKl8WrqswRpJAIhImCkRMNarRhEvhBpIygunadHpC4KrLuRWRkmWDhegoJNRwyx1g2I45Z",
    "webBuild": "6.11.1",
    "loadts": "1778908621420",
    "unread": "{%22ub%22:%2269f03b27000000001b022021%22%2C%22ue%22:%226a06c204000000003502ab02%22%2C%22uc%22:28}",
    "websectiga": "2845367ec3848418062e761c09db7caf0e8b79d132ccdd1a4f8e64a11d0cac0d",
    "sec_poison_id": "c754ca5f-edee-40dc-8e95-01dd488f3fe7",
    "acw_tc": "0a0bb1e217789119072708349e6c44970509ad2c59e446204a01879b41768f"
}
url = "https://edith.xiaohongshu.com/api/sns/web/v2/comment/page"
params = {
    "note_id": "69ef7e8b000000003502576c",
    "cursor": "",
    "top_comment_id": "",
    "image_formats": "jpg,webp,avif",
    "xsec_token": "ABBIDOZGS9FiOA8KJ7T6x0az85KLMNfDd78Yuhxg5E-U8="
}
response = requests.get(url, headers=headers, cookies=cookies, params=params)

print(response.text)
print(response)
import requests
import json
import requests


headers = {
    "accept": "*/*",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
    "cccllpptttgt": "ca67beb1dd9c73b086abbb9c4e8e8b3e",
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    "g-program": "p",
    "origin": "https://www.aigei.com",
    "priority": "u=1, i",
    "referer": "https://www.aigei.com/sound/class/fight",
    "sec-ch-ua": "\"Google Chrome\";v=\"147\", \"Not.A/Brand\";v=\"8\", \"Chromium\";v=\"147\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36",
    "x-requested-etag": "34X2ClA6eOCjMz/iRn0rH+jCv2fxB5+/4lxQSe7i7Ak+5JUGoLuzKt3k8VSdcEz7ZyfJwPPg0nFsUhugSi+b3gwmgncbaJ9FaP4t/sYL59uhrMnq23fYFFRWGwpQqnXLoCRzk6YmIKg=",
    "x-requested-with": "XMLHttpRequest"
}
cookies = {
    "gei_d_u": "e91bfdb8d3614ef0b5c4aaf4b6fbc0f0",
    "oOO0OO0oOO00oo0o": "true",
    "OooOO000oOOO00o": "cd2a978d0220451987411fde2275beaf",
    "gei_d_1": "d9e38d327d1093e85bd4dc04527e87c5aa67fd5d123c9601cd4975d167d575708b914fab946ee3ffe29fcec9b179ab721593f08b829d5178fe15fcf6341e8c07",
    "SESSION": "bc33863a-5e1e-4f73-9eb3-dbc82fc2eb98",
    "Hm_lvt_0e0ebfc9c3bdbfdcaa48ccbc43e864f9": "1776676674,1776841353,1776926970",
    "HMACCOUNT": "45FC6488ADA4CC26",
    "hhhssi1ill1i": "5515613e1370297488487dcd3f1c6c4f-ed95bbdd019c0ae4c174056d1ac8d078-af2428b960c8a21aa40a85204b459854",
    "wueiornjk234kj": "d30574031aba43459f322ca8d40588fc",
    "Hm_lpvt_0e0ebfc9c3bdbfdcaa48ccbc43e864f9": "1776928297",
    "SERVERID": "98d9647cdfadc76703e3b0e814607a21|1776928652|1776926971"
}
url = "https://www.aigei.com/f/d"
data = {
    "v": "WMZ0h+I5D+CNIQj0fwcAOTaed8kfNbdq1hpo4RKqp06c/FFxoAsd4lekQSf+ZFtTkTgStOmWRLjIEszhW7lxzZpLQW9okZNskv2QERlfpm3lX6DBwCq8FVgJhJozpmb1ZizlN3iUAUl8G/CArxSc0eluZK7Fn1L3xpYskf1KlDsF0U37F5ULqmv/F8I7DOSbtI+6JmsjpEdAkxundob39M1D82yu4WcKzSAstkfMHlZXgSZ52xBcv/kNqueKuiXHvwalia1j3XnwAdm2TiQer+Jdy8LiwOFXEEKqTfTTpoEmYwFBNgDDEtNrdgsBYBuYn/D2O9cIIAbV9DzceYsVhUkLVvYYqc52wh2Xwulr0HNL6kPL4cHq0Sg=="
}
response = requests.post(url, headers=headers, cookies=cookies, data=data)
print(response.json().get('message'))

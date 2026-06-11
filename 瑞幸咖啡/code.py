import random
import time

import requests
import json


headers = {
    "accept": "application/json",
    "accept-language": "zh-CN,zh;q=0.9",
    "content-type": "application/json",
    "open-id": "oMwzt0ANs7EyP0nIig0GIhJY7R0g",
    "pp-os": "0",
    "pp-placeid": "40745daf-95bb-4707-b773-a1b40e10c7c1",
    "pp-placezip": "350206",
    "pp-seqid": "qaqvJ7hSRSYnQvEhH5VU58AUXNInVe9G5dLgcvTF3omwVD1J7FrK/VwYjXL6FW6IBw0g5Olzev+80SdlIWvvdQ==",
    "pp-suid": "ab50796d-0062-487b-a1d2-e7cbfecbb99a",
    "pp-userid;": "",
    "pp-version": "2026060820",
    "pp_current_page_name": "scene_page",
    "pp_store_city_zip": "350200",
    "pp_storeid": "a9d82b69-3926-4c4c-a29a-4f66b27fc4c8",
    "priority": "u=1, i",
    "referer": "https://servicewechat.com/wx122ef876a7132eb4/762/page-frame.html",
    "seal-v2": "{\"a\":\"c353790e6856636c3f7d0efca4784906eiJx76C0\",\"b\":\"l8Maig8G\",\"c\":\"eNckrD0b\",\"d\":\"2c41ZTi1\",\"f\":\"HiJEKr9/n3HgtJyiToeiuCG201PzWswm2AaWdwp4b4FcQtoZ6xPaY5Bq+zySLqZU+TmZCVyWZSUZRWWKfEmdCUE/C8GV1bME4D0wPpGs5uKyY05X/knc/+vteRDw6aKItA0n3c0qBXjUXPInae7fE/aZEVen/DbZHfSfmY\"}",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "cross-site",
    "sign-v2": "e5767dc24cb570b569279ac3accd3aa8",
    "timestamp": "1781198074896",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090a13) UnifiedPCWindowsWechat(0xf2541a1f) XWEB/19921",
    "xweb_xhr": "1"
}
url = "https://j1.pupuapi.com/client/marketing/scenes/component/v2/scene/019ca2d7-7e4d-7fd1-8cd0-fdd4d3700193/group/019ca2d7-7e57-7a63-ba6b-50c3379d6d93/product_config/products"

for i in range(1, 10):
    time.sleep(random.uniform(2.5, 5))
    data = {
        "size": 36,
        "product_card_styles": [
            {
                "layout_style": 30,
                "product_card_style": 10,
                "product_num": 36
            }
        ],
        "page": i
    }
    data = json.dumps(data, separators=(',', ':'))
    response = requests.post(url, headers=headers, data=data)
    print(response.text)
    print(response)


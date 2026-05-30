import requests
import json
import time
import signal
import sys
from urllib3.exceptions import SSLError


headers = {
    "accept": "application/json, text/plain, */*",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
    "content-type": "application/json;charset=UTF-8",
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
    "x-b3-traceid": "849f76c6172536b6",
    "x-rap-param": "ByQBBQAAAAEAAAAUAAAClB9zdDoAACfZAAAAKQAAAAAAAAAAMWQ5cncv2IF3U4LCOOFvWi5PfWOVAAAAED3I/B2uQQmdigHbwkXqziRWYHCn17RUFfmnB+LQDlSjUINa9RcO6H2d3rKNdOMzf9OfLbJfkywNBYY4axkHy0bYSPfIX2s4s+7JPBsKf83MBLpBsodn3WztlGM5m0O2Ak9HwM5QxBUAF/fC/fHwdv+TuNSc/EWH4hjB1wmh2QLTyt1oEcgV6bULhOjXv1DaqBWJtbjWKS9/Nq7QNP6/KJLOafW8dEPEI1eGSLvfiN07VJK0F6+aFZM2FVQAZG13jQBlalFJK8HRmvXfviG1xXtBLJa/v3heKgo7Qf+9i6wmMA0lCj/JjoOklLmTIIFlbnG9EYRShyEugxD3mZ0DzeZS8A3xlBvDSuY8YLHnEvHf3RNVxpKvdjZw9Tx8zzigBFauF/ylizHVacbFtfxwpm11WA1vmE8v64vAjh3vv7nRKJWyLElEkMgyOeVglHc1mhzh69LvKEd0stb7ppvQeiK3bLZ3MpxBmVbNiJ3TGk0Ecd+gHtmTRkLtSx99uXq7yLHyaXr6imLsDo/v3zeEeXZGfXileFSb2BcIDBouJAUHQwMwafAmwxRQuZ4VS65it6HX6e9p04EMeMlHKCFOhaPZwBQZ33NusQqLCjpBgSQMYyNo/qO3qV1kRfOlALybKu800Q12oT3HR3lUftmErYbMeexcotW8SekCHO1nhyb3iwBRrp/avUcBnOGqIUEO8Mur9XdzMTGPbnKjUtcgyD93iFy4m+7iPvrRhRhaKL9L0fgNe1h6gaZV90l/0bYNGxg3JI+6rINNd5nOrdaZy1LYiPPCxkC9ZMS4DPBDpPt9KTOpy2aaddqCuIEuhE8rlytjQ2XzFufESF8NH0jfe8Eg7m9yorZOd5bcZh1QMcj/AAACgQ==",
    "x-s": "XYS_2UQhPsHCH0c1PUhMHjIj2erjwjQhyoPTqBPT49pjHjIj2eHjwjQgynEDJ74AHjIj2ePjwjQTJdPIPAZlg94aGLTl8FMoyemBzFE+cpzbzemk8rpUJLMyygQawepn4f4x2bSoGFDUy0mD+7iF8BbfJoQYapzgPFTjLgSI+eStyDMYGS8L4fqIankHLnRopbZEPbmhwoYdL0c9/0z0Pbzh2f4B4oYka/4YPd4NJLEL/BQmPrkHaMY/4bSPz9DlPaT+c9EIqMQCLDkcpnbLP9lb2rT/Jfznnfl0yLLIaSQQyAmOarEaLSz+GD89LF8+LLS7tA8b4DpYt9H6G0DhPaHVHdWFH0ijJ9Qx8n+FHdF=",
    "x-s-common": "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",
    "x-t": "1778908640233",
    "x-xray-traceid": "cf179bd9e2912bd9a5345b26dc29f9c8"
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
    "acw_tc": "0a8f06e817789082800945009e0fea1e8b0e4cea3dcf1dea6482a2e01e4107",
    "loadts": "1778908621420",
    "unread": "{%22ub%22:%2269f03b27000000001b022021%22%2C%22ue%22:%226a06c204000000003502ab02%22%2C%22uc%22:28}",
    "websectiga": "f47eda31ec99545da40c2f731f0630efd2b0959e1dd10d5fedac3dce0bd1e04d",
    "sec_poison_id": "fbebc773-f112-4a22-a6b9-f9d783a46b54"
}
url = "https://edith.xiaohongshu.com/api/sns/web/v1/search/notes"

# 设置爬取的页面范围
start_page = 1
end_page = 10  # 可以根据需要修改结束页码

all_results = []
interrupted_page = None

# 定义信号处理函数，用于保存已爬取的数据
def save_on_interrupt(signum, frame):
    print("\n\n检测到中断信号，正在保存已爬取的数据...")
    if all_results:
        filename = f'xiaohongshu_interrupted_page_{interrupted_page}.json'
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(all_results, f, ensure_ascii=False, indent=2)
        print(f"已保存 {len(all_results)} 页数据到 {filename}")
    else:
        print("没有可保存的数据")
    sys.exit(0)

# 注册信号处理器（Windows 下只支持 SIGINT，即 Ctrl+C）
signal.signal(signal.SIGINT, save_on_interrupt)

for page in range(start_page, end_page + 1):
    interrupted_page = page  # 记录当前页码，用于中断时保存文件名
    print(f"正在爬取第 {page} 页...")
    
    data = {
        "keyword": "香港",
        "page": page,
        "page_size": 20,
        "search_id": "2gdh22bqseno2zju5jpg9",
        "sort": "general",
        "note_type": 0,
        "ext_flags": [],
        "filters": [
            {
                "tags": [
                    "general"
                ],
                "type": "sort_type"
            },
            {
                "tags": [
                    "不限"
                ],
                "type": "filter_note_type"
            },
            {
                "tags": [
                    "不限"
                ],
                "type": "filter_note_time"
            },
            {
                "tags": [
                    "不限"
                ],
                "type": "filter_note_range"
            },
            {
                "tags": [
                    "不限"
                ],
                "type": "filter_pos_distance"
            }
        ],
        "geo": "",
        "image_formats": [
            "jpg",
            "webp",
            "avif"
        ]
    }
    data = json.dumps(data, separators=(',', ':'))
    
    # 添加重试机制，最多重试3次
    max_retries = 3
    retry_count = 0
    success = False
    
    while retry_count < max_retries and not success:
        try:
            response = requests.post(url, headers=headers, cookies=cookies, data=data, timeout=30)
            print(f"第 {page} 页响应状态: {response.status_code}")
            
            try:
                result = response.json()
                all_results.append(result)
                print(f"第 {page} 页数据获取成功")
                success = True
            except Exception as e:
                print(f"第 {page} 页解析失败: {e}")
                success = True  # 即使解析失败也标记为成功，避免重复请求
                
        except (SSLError, requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
            retry_count += 1
            print(f"第 {page} 页请求失败 ({e.__class__.__name__}): {e}")
            if retry_count < max_retries:
                wait_time = 3 * retry_count  # 递增等待时间：3秒、6秒、9秒
                print(f"第 {retry_count} 次重试，{wait_time}秒后重试...")
                time.sleep(wait_time)
            else:
                print(f"第 {page} 页已达到最大重试次数({max_retries})，跳过")
    
    # 每页之间延迟，避免请求过快
    if page < end_page:
        time.sleep(2)

print(f"\n总共爬取了 {len(all_results)} 页数据")

# 保存所有结果到文件
with open('xiaohongshu_all_pages.json', 'w', encoding='utf-8') as f:
    json.dump(all_results, f, ensure_ascii=False, indent=2)

print("数据已保存到 xiaohongshu_all_pages.json")
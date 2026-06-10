import requests


headers = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Connection": "keep-alive",
    "Origin": "https://user.mihoyo.com",
    "Referer": "https://user.mihoyo.com/",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-site",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36",
    "sec-ch-ua": "\"Chromium\";v=\"148\", \"Google Chrome\";v=\"148\", \"Not/A)Brand\";v=\"99\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "x-rpc-app_id": "dw9y09jqjpxc",
    "x-rpc-client_type": "4",
    "x-rpc-device_fp": "38d818f8368c1",
    "x-rpc-device_id": "f7cab285-9b80-4a55-82bb-4fd1b5a2da48",
    "x-rpc-device_model": "Chrome%20148.0.0.0",
    "x-rpc-device_name": "Chrome",
    "x-rpc-device_os": "Windows%2010%2064-bit",
    "x-rpc-game_biz": "plat_cn",
    "x-rpc-lifecycle_id": "82dec4716c",
    "x-rpc-mi_referrer": "https://user.mihoyo.com/login-platform/index.html?app_id=dw9y09jqjpxc&theme=passport&token_type=4&game_biz=plat_cn&steps_bar=1&uc_type=3&redirect_url=https%253A%252F%252Fuser.mihoyo.com%252Fpassport%252Findex.html%2523%252Fhome%252Fsecurity&st=https%253A%252F%252Fuser.mihoyo.com%252Fpassport%252Findex.html%2523%252Fhome%252Fsecurity&succ_back_type=redirect&fail_back_type=reLogin&ux_mode=redirect#/account/activity",
    "x-rpc-sdk_version": "2.52.0"
}
cookies = {
    "_MHYUUID": "f7cab285-9b80-4a55-82bb-4fd1b5a2da48",
    "DEVICEFP_SEED_ID": "6bc4e8b35944de4b",
    "DEVICEFP_SEED_TIME": "1780302748665",
    "aliyungf_tc": "f95a84f1ade6ff3745982f5335989f1ffbed34f46abd0c3dc2d3ea8f4aca0e87",
    "DEVICEFP": "38d818f8368c1",
    "MIHOYO_LOGIN_PLATFORM_ACCOUNT_SYSTEM_PIPELINE": "{%22actionType%22:%22forget_password%22%2C%22meta%22:{%22defaultAccount%22:%2215322349311%22}}",
    "cookie_token_v2": "v2_1vA8rZlF3xru84XfSLy7J1d918o1QyHXVfRnrACDtdkTRzrE9Gl__OqiFUQ9ogTYvFklHaSulxyy3M-72Yci2mwdlzsv8aTHRRVxeEDCIgdMBviRmIunRoFbspaYAChT3b4C_eLUCfFvHQ==.CAE=",
    "account_mid_v2": "0nlttllu9f_mhy",
    "account_id_v2": "466592667",
    "ltoken_v2": "v2_oL9e3TCm4f96vKSPb0G4XkzZcs8ZboqJp2NuciSTLJNYYLaXlV5s-8i49OLHpTO5bOXr7Qriu-xb_EgHpRHfwUH1KUd9eunGSSb8c7wyP1bJwsX3dBvTurJHPWTSPeT01MWWOzbNQbxSyw==.CAE=",
    "ltmid_v2": "0nlttllu9f_mhy",
    "ltuid_v2": "466592667",
    "cookie_token": "TVFkrmtRSVSGmRnSBikvom0uJS4yP5S56vuedibq",
    "account_id": "466592667",
    "ltoken": "2t4dD0gg9QU6h1Q8Y2SnKmSalq8JNTIFagfEvCEb",
    "ltuid": "466592667",
    "MIHOYO_LOGIN_PLATFORM_LIFECYCLE_ID": "82dec4716c"
}
url = "https://passport-api.mihoyo.com/account/ma-cn-passport/passport/getActionLogs"
params = {
    "start_time": "1777711719",
    "end_time": "1780303719"
}
response = requests.get(url, headers=headers, cookies=cookies, params=params)

print(response.text)
print(response)
"""
data_structure:
{
    "retcode": 0,
    "message": "OK",
    "data": {
        "logs": [
            {
                "action": 1,
                "biz": "网页",
                "device_name": "Chrome",
                "addr": "广西壮族自治区，钦州市",
                "ip": "111.59.***.12",
                "log_time": "1780303610"
            },
            {
                "action": 1,
                "biz": "网页",
                "device_name": "Chrome",
                "addr": "广西壮族自治区，钦州市",
                "ip": "111.59.***.12",
                "log_time": "1780303597"
            },
            {
                "action": 1,
                "biz": "网页",
                "device_name": "Chrome",
                "addr": "广西壮族自治区，钦州市",
                "ip": "111.59.***.12",
                "log_time": "1780303318"
            },
            {
                "action": 402,
                "biz": "网页",
                "device_name": "Chrome",
                "addr": "广西壮族自治区，钦州市",
                "ip": "111.59.***.12",
                "log_time": "1780303295"
            },
            {
                "action": 100,
                "biz": "网页",
                "device_name": "Chrome",
                "addr": "广西壮族自治区，钦州市",
                "ip": "111.59.***.12",
                "log_time": "1780303245"
            }
        ]
    }
}
"""
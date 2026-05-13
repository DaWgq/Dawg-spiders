import requests


headers = {
    "accept": "application/json, text/plain, */*",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
    "content-type": "application/x-www-form-urlencoded",
    "origin": "https://item.jd.com",
    "priority": "u=1, i",
    "referer": "https://item.jd.com/",
    "sec-ch-ua": "\"Chromium\";v=\"148\", \"Google Chrome\";v=\"148\", \"Not/A)Brand\";v=\"99\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36",
    "x-referer-page": "https://item.jd.com/100310496358.html",
    "x-rp-client": "h5_2.1.0"
}
cookies = {
    "__jdv": "95931165|www.google.com|-|referral|-|1778575572382",
    "__jdu": "17785755723822032290501",
    "jcap_dvzw_fp": "P2orBIltboeGnt9L1EAwvz_BIc8NKPD3zbO9v3cWNRDNYBwya5yFhkQRy3yd4-txhflyiLSTDz83RlrPtR_Dza44UZ0=",
    "pinId": "U08qodXJNZu1ffsfn98I-w",
    "pin": "haha6486",
    "unick": "mj5zpthwq3zwdy",
    "_tp": "hQJRug6zIIgo2S3ZBVxYxA%3D%3D",
    "_pst": "haha6486",
    "TrackID": "1MxieXnji-TjhfcB836ZM0r1VtX9sil6Gg0cosq0-UzfH7NZzWFJOAVj6lllQcfp7ZqUXsmnl4StiYKJ5IJYBQEtL4vHbAid7IYQv1VtXf7c",
    "light_key": "AASBKE7rOxgWQziEhC_QY6yaMd6KgjOZa5zDzQ8mxM-ww_amqWOKxslXLFkh7_8dPlz9nsqk",
    "shshshfpa": "4fba695c-1028-f8aa-3bf5-a80a03be2509-1778575753",
    "shshshfpx": "4fba695c-1028-f8aa-3bf5-a80a03be2509-1778575753",
    "3AB9D23F7A4B3CSS": "jdd03PP2G7TG4OTHAB4ZBMMPVZZMAVPAY7A4YVGH2ZFDK7ZPEPGBCYKWZQX5QHBWI4FJDFFIJTQLLHHBC6RKOCWPY345U7QAAAAM6EC6QW4QAAAAACEPVYTDAGCRS4EX",
    "areaId": "20",
    "cn": "0",
    "cid": "9",
    "ipLoc-djd": "20-1753-1755-25245",
    "3AB9D23F7A4B3C9B": "PP2G7TG4OTHAB4ZBMMPVZZMAVPAY7A4YVGH2ZFDK7ZPEPGBCYKWZQX5QHBWI4FJDFFIJTQLLHHBC6RKOCWPY345U7Q",
    "thor": "9F8C95FA9A1751D48A7F1175D69F913334B3BCDB0EC9A233DFC16AEB2752683AE4D8D0EBC33508DCB1F6D410CA7F181130F8ACD6EBC730CA8F3BC88B026A06F0D01C7A2D84A78D0D5D32DBEA2578155D87FE7B7E6572B966E70B4EB2F71558919D9B089F6DF478F859EB3231D262180FA04214862FADB1F67F538BD0214FC738CE94CB5A3890F7E7A832B2C9159400F4",
    "token": "4c44b7f4374bf5a084e0a2da387ac716,3,988147",
    "__jda": "181111935.17785755723822032290501.1778575572.1778595339.1778665712.3",
    "__jdc": "181111935",
    "flash": "3_HmUdhuO1QvXoZV15EeD_fGo1jmxJmhhLUqsD-T8B_T1oBGb3l-Fscqm8SjXbLNkbBLtu2hgoU2eYMA2LDae4G0N4gwDg6zMJEAPr92d_ZZO3D4521ypLXRX13Qy7bWVek6P8NgL18gd1XfZdVOrPR8MkRPacEJZcIpBg5NBGyUP*",
    "__jdb": "181111935.9.17785755723822032290501|3.1778665712",
    "shshshfpb": "BApXWGXO2I_tATMdM4m8WHok8wX24eJTTBjoWUHxp9xJ1OtRadYeAxkK9fKKYOeYQHecK46LWhZU2cbEw6vtd3vSTaw",
    "sdtoken": "AAbEsBpEIOVjqTAKCQtvQu17cEzP9mLfW1uiyr7lyJnhtOfu3vZXBX3JzfxhipZr_DN0oGVamsBibBTiQvoqBz6xXnD5OAqu52Wq2d8rjL0_sc-xy9bVWt7KKB6YuN4l7ZXY4zI_cOKb-fECB4vWjG4DBpoT_Cvfjibi4P6SMLA-Zx7ZnOGwSYeE4rs0-A3B_nY5SLSq4YdF"
}
url = "https://api.m.jd.com/client.action"
data = {
    "appid": "pc-rate-qa",
    "body": "{\"requestSource\":\"pc\",\"shopComment\":0,\"sameComment\":0,\"channel\":null,\"extInfo\":{\"isQzc\":\"0\",\"spuId\":100310496358,\"commentRate\":\"1\",\"needTopAlbum\":\"1\",\"bbtf\":\"\",\"userGroupComment\":\"1\"},\"num\":\"10\",\"pictureCommentType\":\"A\",\"scval\":null,\"shadowMainSku\":\"0\",\"shopType\":\"0\",\"shopId\":\"1000000904\",\"firstCommentGuid\":\"T6NaPsd3jZgtdRKCXqWYw3mE\",\"sku\":100310496358,\"category\":\"9987;653;655\",\"shieldCurrentComment\":\"1\",\"pageSize\":\"10\",\"isFirstRequest\":false,\"isCurrentSku\":true,\"sortType\":\"5\",\"tagId\":\"\",\"tagType\":\"\",\"type\":\"0\",\"pageNum\":\"1\"}",
    "client": "pc",
    "clientVersion": "1.0.0",
    "functionId": "getCommentListPage",
    "h5st": "20260513175043328;5nbnpe5ni5m7bei1;01a47;tk03wa2191be018nllmDT6Bk2itZ_b2EbcbI3ILmjWqlw2Egw4r674kL5W--Ie_cyTaCG9sEQIwgw0_givpBeB0-jQbK;4fb4bc7650bc8a18564b4aa168eac4a3;5.3;1778665838328;pjbMhjpd9nIg7jpjxjZf2iFjLrJp-jZfCWFT03VeCyVeGqEQJyVeJrJdJrESJrpjh7Jf6rJdJz1TIipjLDrgJXof1nle7XYT6jYf4TYe3Pod4Loe4boSFSVT7fISJSldJrJdJrEa-OFTGOEjLrJp-jZTFeYfFOYdIm1e5r4T1T1eGK4f5Hof7n1T7PYf5HIfHipjxj5PKSEQKeFjLrJp-jZf_jpjxjpe2iFjLrJp-j5f9fIg2T0UG6VRFuWeDipjxjJOJrpjh7JjbylP721Y4LIVFOFjLDIj_ulS9mFPJrpjh7Jj5fIQCOGjLDIjFqEjLrJp-3kjLDLj1SHjLDIj4nYOJipjLrpjh75fLDIj6nYOJipjLrpjh7pe6rJdJrYf2iFjLrpjLDrgz3pjxjJf6XETJrpjLrJp-jpPJiUSy7VdeeoR2amPJrJdJ31QHyVT5ipjLrpjh7pfLDIjzXETJrpjLrJp-rojxj5e2iFjLrpjLDrg2jojxjJe2iFjLrpjLDrg7rJdJXYOJipjLrpjh7pfLDIj3XETJrpjLrJp-L4fLDIj4XETJrpjLrJp-jZd9nIg7jpjxjZf2iFjLrpjLDrg7rJdJ-1OJrpjLrJp-Xojxj5P-ipjLrpjh7pfLDIj-ipjLrpjh7pfLDIjHOEjLrpjLD7NLDIjHyVS3KUSJrpjh7ZMLrJpJTod3TYTDmlRJrJdJjoPJrpjLrJpwqJdJrkPJrpjh7Jj3ToNL-oe1zVRUq5d7zpf6rpWdq5P0ulS9G1WJrJdJnVO4ipjLD7N;230f0b0e38a9516bf998120fe13fa0ef;qbkgHGHQ8GlOIyVOF6JQ8G1P5WFW3yVSC61T-bEQGGlQI6ZNHuFT-bVR7qUT",
    "loginType": "3",
    "t": "1778665838326",
    "uuid": "17785755723822032290501"
}
response = requests.post(url, headers=headers, cookies=cookies, data=data)

print(response.text)
print(response)
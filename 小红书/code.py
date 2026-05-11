import requests
import json


headers = {
    "accept": "application/json, text/plain, */*",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
    "content-type": "application/json;charset=UTF-8",
    "origin": "https://www.xiaohongshu.com",
    "priority": "u=1, i",
    "referer": "https://www.xiaohongshu.com/",
    "sec-ch-ua": "\"Google Chrome\";v=\"147\", \"Not.A/Brand\";v=\"8\", \"Chromium\";v=\"147\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36",
    "x-b3-traceid": "418654191cb8e5aa",
    "x-rap-param": "ByQBBgAAAAEAAAAUAAABlCB0b68AACfZAAAAJAAAAAAAAAAAZXNob24ytJ2wi/h/FGLowAmO0JlImAAAABBRosBNvDoMJkmYowcf51ZTPSWjqj8GJyYKfLZYrrXbiFeNy6CsbgGGNIn8aKW/9gOtM1s5HbyTzANL+Jq16H+HQHmkPxJcfCW/enZBuICo9qVuAKA6EPei8oX+I3XxwpotTBw8QMM40rA+AeOEICIrFz0M777oOvttNNnIWm8Q4jb31mdmCpB47vspQ4i8RsJjyf2eNYNBG4vqwrEmTvEtb5E5f7/XIj+h+7bSUDm9cOB3q3Tdq++lhoarDnfZzdXV9zdiC/wSlULAu7xib0CIZPiTiU5p7mTT5B0ZXEMGEeFreGZjBlkx+ZnCKMCNxhzb59sLw56sAm/lmQXmMZp6HuZEeUsNakUDLjVDnq16252oVRqySlVVwoFnGoiX6H6WAit7EAomjdr79CGOtZL7nMHUvriAHxCxMSfFVsjh2AObIlVBz+zbdWavxqVtvq8xoM4wryVIqxl4ceJ4gStGfJTNFcvv2AwQLnPiIEdcTmWB7Xb1Z2fPoV4QChWfP8GIH/ALfpv/vnMdhtW+R7SKAAABiQ==",
    "x-s": "XYS_2UQhPsHCH0c1PUhMHjIj2erjwjQhyoPTqBPT49pjHjIj2eHjwjQgynEDJ74AHjIj2ePjwjQTJdPIPAZlg94aGLTlLp+ccnkNNAqU2Blbqemk8eQVyppfL9+awepnJaRx2bSoyFDUyfE++7iF8oksa0Qm2rpfnoptLgSI+eStyDMYGS8L4fqIankHLnRopbZEPbmhwoYdL0c9/0z0Pbzh2f4B4oYka/4YPd4NJLEL/BQmPrkHaMY/4bSPz9DlPaT+c9EIqMQCLDkcpnbLP9II8LT/Jfznnfl0yLLIaSQQyAmOarEaLSz+GSW949HUaozwqrpoqg4C+bm74BkynaHVHdWFH0ijJ9Qx8n+FHdF=",
    "x-s-common": "2UQAPsHC+aIjqArjwjHjNsQhPsHCH0rjNsQhPaHCH0c1PUhMHjIj2eHjwjQgynEDJ74AHjIj2ePjwjQhyoPTqBPT49pjHjIj2ecjwjH9N0W1PaHVHdWMH0ijP/SD80QD8eZh8/rFPeYE8/SMJdYEPgQUwB+Myo+j+7YYqgmU4gp9P/GMPeZIPecIP0cAPaHVHdW9H0ijHjIj2eqjwjHjNsQhwsHCHDDAwoQH8B4AyfRI8FS98g+Dpd4daLP3JFSb/BMsn0pSPM87nrldzSzQ2bPAGdb7zgQB8nph8emSy9E0cgk+zSS1qgzianYt8p+s/LzN4gzaa/+NqMS6qS4HLozoqfQnPbZEp98QyaRSp9P98pSl4oSzcgmca/P78nTTL08z/sVManD9q9z1J9p/8db8aob7JeQl4epsPrz6agW3Lr4ryaRApdz3agYDq7YM47HFqgzkanYMGLSbP9LA/bGIa/+nprSe+9LI4gzVPDbrJg+P4fprLFTALMm7+LSb4d+kpdzt/7b7wrQM498cqBzSpr8g/FSh+bzQygL9nSm7qSmM4epQ4flY/BQdqA+l4oYQ2BpAPp87arS34nMQyFSE8nkdqMD6pMzd8/4SL7bF8aRr+7+rG7mkqBpD8pSUzozQcA8Szb87PDSb/d+/qgzVJfl/4LExpdzQ4fRSy7bFP9+y+7+nJAzdaLp/2LSizLi3wLzpag8C2/zQwrRQynP7nSm7pLS9yLPFJURAzrlDqA8c4M8QcA4SL9c7qAGEanMQye8AP7kU8bbM4epQznRAP9iM8gYPad+nLo40q0SdqM+c4oYQcFMc/B468n8M4ApCJ0pApM87qDDAL7kQP7m/qS87LsRM4Fk6yfSP2LlOqFcI/9ph4gzTanTt8pSYN7+hNMbsag8O8/8S+npgJbQUag8wqFzl4FYQyFYk4Mm7/rEn4e8QPFRSygpF8rSbcg+kqg4VanW68Lzl4rbw4g4cJp87zrShJgYQ4SbILBzQLDkP4fLAqgziaLprGLS3PBp84g4znfQbqnhIPo+x8LY/aLp8aMmn4MbA4gzYanTt8p8c4FzNp94AyMD68/8jzgSQzLkSy9c6q9Tl4o+1Lo4laL+t8p+c49SQyepSpDbQ/rS9+np8JURSPbmFLFSea7P9Lo4n+BRTqLSiaBpQc94SpDl68pzd4fp8G08AL7p7/FS9Jg4QybkD+b87arDAndmQ2e+S8fMjJob++np84gq9agYoy9+c4FlO894SynHM8p4n4e8d4g4CagYkcFSb+BEjpdzT8gb7/FSh+7+nJnzSPgp7aB4n4o8Qz/W6JMmF/LDAzd+spMkhanT9qAmf+g+k+9pSpS87aDQl4okQyLzhanT6q9Tn4okQcA4SyfQ8cLSiLnQsnnTPaL+8aFSiafpxLoq7qgpFpMmM4BzQ2bkyanYwqAbx4fpkqg4yGM+oPLS9G9zELocUqSmFPDS3zfbQ2bbha/+z+LSiafpn+FbAPnQC+dzM49TQ4DDl2S87NMkc49zQzaRS+fEyNFSkqDF6cd8SypmFnfpM4b8wnSmsJ7QkprS3+e40pdq3anTNqFzgzLkQyFpOGSm7zLS3woSc4gc3ab8FaFSeLobQ4fMraLp8ndQc47pQyMmoaL+9q7Yc4Fpj20zmanYBpDS9/7+D8DRA+Sm7+FSi2dSQyr4Hz9MPyrSiJrb1nSmQag8mqMSf/fpgqg4lanW9qM8M4omQyBSDagG6q9kc47mQcM+64ob7/FS9ad+DqFls87bF8g4n4eQQcAmS8bmFJDS9/d+8z0zBaLP7qMS/a7PlLoz14rSwqA+l49Rz8FEAPgpFnDS3/d+3J/8S+S8FarSbpA+Qypz98p87a74mt7kQPFRS8S87PSkT+fprGUTI4obF/FSh2S4QyaRA8bSTqrDAafLIqgzaaL+0arSb4fprqbzHanYB/rSka/Hh+9TaagG98pzAqpQQyBIEanTPyDS9a7+8ppQIqSmF2dkM4oYY/sRAzrlm8Lzn4FpQP9pALMSd8/+l4URULo4da/+3+B+n4Am6pdc6zM87pjTc4b+t4g4DP0S98/b8afphyd8APLlN8p8l4rTQzpQjanW3PFShzSzQcFkSyAqIqM8YqDMlqgz6anYP4rQc49MwcLbSP7bFaFSecg+fpFRS8o+i8FShPo+f4gchar8rpFS9P9pgqgzxag8wqA+n4b+H4gztagYwqM4mzD474g4j2fptq9zVzoYQyaRSp7pFnfRM4bS0wnzSpob7zfpM4BMIpd4NagY/4rSbprb0p94SnL8Oq9SM47pQ40pSPp8FG7kc4rkE+FTAPp+C4fRAJebtGDqI8M8Fq9pc4sTQ2rp3agYUGFS9zfTwG08SpB4/zFShzFQQPFSC87pF8LSh/BDjNsQhwaHCP/G7+AP9w/PU+aIj2erIH0iINsQhP/rjwjQ1J7QTGnIjNsQhP/HjwjHl+Aq7weD9PAcU+AG7wAr7+ALl+eL7P0r7P0cjKc==",
    "x-t": "1777896353402",
    "x-xray-traceid": "cef970b731ada849012b54b4ac109890",
    "xy-direction": "68"
}
cookies = {
    "abRequestId": "8fb1f146-0519-522c-a76e-60bfc72f047a",
    "ets": "1777896065160",
    "webBuild": "6.8.1",
    "xsecappid": "xhs-pc-web",
    "a1": "19df2dd08e1408ye9unxy1rr8cuhsb7xaqpruuv1650000402431",
    "webId": "aa22da5c093a56f2c342538330d9016e",
    "acw_tc": "0a8f06e917778960701002631eaad0179a21c769a2cd04a16eee7fc9459495",
    "websectiga": "3633fe24d49c7dd0eb923edc8205740f10fdb18b25d424d2a2322c6196d2a4ad",
    "sec_poison_id": "b42cd05e-0876-4824-b112-cd205796ffe8",
    "gid": "yjfiJffJSS0jyjfiJff8YA7hdy48Yvdj7ICvUyKyFFYS7F28xMDWC788848J4qy84WDKJWDq",
    "web_session": "040069b60e287e3396574dc3cd3b4b21504ee0",
    "id_token": "VjEAAFqe5rGutQtuqUQ+4hMXJ3h0MQ8guVS6sMdK2ud8Tu8TVZrA9ZP17CV3L4D3LoXKl8WrqswRpJAIhImCkRMNarRhEvhBpIygunadHpC4KrLuRWRkmWDhegoJNRwyx1g2I45Z",
    "loadts": "1777896341570",
    "unread": "{%22ub%22:%2269da3fdd000000002301f914%22%2C%22ue%22:%2269ed97880000000035021498%22%2C%22uc%22:30}"
}
url = "https://edith.xiaohongshu.com/api/sns/web/v1/homefeed"
data = {
    "cursor_score": "",
    "num": 31,
    "refresh_type": 1,
    "note_index": 35,
    "unread_begin_note_id": "",
    "unread_end_note_id": "",
    "unread_note_count": 0,
    "category": "homefeed_recommend",
    "search_key": "",
    "need_num": 6,
    "image_formats": [
        "jpg",
        "webp",
        "avif"
    ],
    "need_filter_image": False
}
data = json.dumps(data, separators=(',', ':'))
response = requests.post(url, headers=headers, cookies=cookies, data=data)

print(response.text)
print(response)
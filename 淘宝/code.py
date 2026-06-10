import requests


headers = {
    "accept": "*/*",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
    "referer": "https://s.taobao.com/search?_input_charset=utf-8&clientPreloadId=preload_1780840876058&commend=all&ie=utf8&initiative_id=tbindexz_20170306&page=2&preLoadOrigin=https%3A%2F%2Fwww.taobao.com&q=%E5%BD%B1%E7%9F%B3g03s&search_type=item&source=suggest&sourceId=tb.index&spm=a21bo.jianhua%2Fa.search_downSideRecommend.d6&ssid=s5-e&suggest=0_6&suggest_query=%E5%BD%B1%E7%9F%B3&tab=all&wq=%E5%BD%B1%E7%9F%B3",
    "sec-ch-ua": "\"Microsoft Edge\";v=\"149\", \"Chromium\";v=\"149\", \"Not)A;Brand\";v=\"24\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "sec-fetch-dest": "script",
    "sec-fetch-mode": "no-cors",
    "sec-fetch-site": "same-site",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36 Edg/149.0.0.0"
}
cookies = {
    "xlly_s": "1",
    "t": "3e09793800b4a24b9786b3e02927e4c4",
    "_tb_token_": "e384e36e7b6f3",
    "mtop_partitioned_detect": "1",
    "_m_h5_tk": "80ac1d6f283cc8b3b54bee5ad150f180_1780848058330",
    "_m_h5_tk_enc": "e60c9706b1d24391978cd57eddb4435b",
    "thw": "cn",
    "sca": "ecc9733d",
    "cna": "mmesIqivSyQCAW87swyQMOaD",
    "cookie2": "20c8c79dc99b5982e872e3c8913695a0",
    "_samesite_flag_": "true",
    "3PcFlag": "1780840879704",
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
    "sgcookie": "E100ndjhVPrY7%2B4hCJ0mqBCpxw0wZhSPyaIQU83mq4mOnxcnSTlnuF17MhvXRO0ZSgqM17Mfaz%2F1HiYxvLIMlg2wg%2FqqSDVd3%2BwtuitPNyTnKHM%3D",
    "wk_cookie2": "1efbd04307d0638ad81f38092a76c6da",
    "wk_unb": "UUphw2ZQNahEaWo%2FnA%3D%3D",
    "uc1": "cookie15=UtASsssmOIJ0bQ%3D%3D&pas=0&existShop=false&cookie21=Vq8l%2BKCLjA%2Bl&cookie14=UoYWPUhmYwg%2FOA%3D%3D&cookie16=V32FPkk%2FxXMk5UvIbNtImtMfJQ%3D%3D",
    "uc3": "id2=UUphw2ZQNahEaWo%2FnA%3D%3D&vt3=F8dD1NM1uXnr7HlZB%2FE%3D&nk2=F5RMHl%2F297M0iBI%3D&lg2=UtASsssmOIJ0bQ%3D%3D",
    "csg": "a9c621c3",
    "skt": "38d79dea2b670b39",
    "existShop": "MTc4MDg0MDkwNw%3D%3D",
    "uc4": "nk4=0%40FY4HWyoAUY1pHUtsE%2FaeKwxLTfHwKg%3D%3D&id4=0%40U2grGNnTItmXNBbFQzVjcGAPN8SAy%2F9%2B",
    "_cc_": "Vq8l%2BKCLiw%3D%3D",
    "tfstk": "hORtsYqaX87IGs3neYnwL41Dp2muXIbflE84lG11jpQXmHuq71YfDnKhY5viQtjYksfjqRG3rTqNra_siG_fOc4CMXmoZbYZCN5DRE0TnNFCya1f5Gs6R2QAoia6ctNBRM7Vll_b12LCYZ1flSN_OM_fWosfhnTIJZSCcs66c6gduMsfGs_WcOggIBcho5PC_RlPvSN8zNMNXbSQMSdppwjSsMniTaM5dEWvgrPvBF9y0at_f0XwlpKdWsh3C_Tph3QeYSAmR-MVY3JlEJ0E0ISpQKxLjRnjfG9kXEUr7DkM-Kp2PxmoomSez35LscRibLWXTTVKC0oeG3RBOfqoEI9y-FYSOPOpZA_UVKGhxvi73D_dqVhY3-WE8wIoJ2e43O_FJg0tk-yVL25..",
    "isg": "BLq6nHchhBCatwj8jbr02gQKC-Dcaz5FaZmBScS7983wt1jxrfmyVLGBB0NrJ7bd"
}
url = "https://h5api.m.taobao.com/h5/mtop.relationrecommend.wirelessrecommend.recommend/2.0/"
params = {
    "jsv": "2.7.4",
    "appKey": "12574478",
    "t": "1780841192694",
    "sign": "1a85ad28ad3c65785c600c3a1b867f15",
    "api": "mtop.relationrecommend.wirelessrecommend.recommend",
    "v": "2.0",
    "timeout": "10000",
    "type": "jsonp",
    "dataType": "jsonp",
    "callback": "mtopjsonp37",
    "data": "{\"appId\":\"34385\",\"params\":\"{\\\"device\\\":\\\"HMA-AL00\\\",\\\"isBeta\\\":\\\"false\\\",\\\"grayHair\\\":\\\"false\\\",\\\"from\\\":\\\"nt_history\\\",\\\"brand\\\":\\\"HUAWEI\\\",\\\"info\\\":\\\"wifi\\\",\\\"index\\\":\\\"4\\\",\\\"rainbow\\\":\\\"\\\",\\\"schemaType\\\":\\\"auction\\\",\\\"elderHome\\\":\\\"false\\\",\\\"isEnterSrpSearch\\\":\\\"true\\\",\\\"newSearch\\\":\\\"false\\\",\\\"network\\\":\\\"wifi\\\",\\\"subtype\\\":\\\"\\\",\\\"hasPreposeFilter\\\":\\\"false\\\",\\\"prepositionVersion\\\":\\\"v2\\\",\\\"client_os\\\":\\\"Android\\\",\\\"gpsEnabled\\\":\\\"false\\\",\\\"searchDoorFrom\\\":\\\"srp\\\",\\\"debug_rerankNewOpenCard\\\":\\\"false\\\",\\\"homePageVersion\\\":\\\"v7\\\",\\\"searchElderHomeOpen\\\":\\\"false\\\",\\\"search_action\\\":\\\"initiative\\\",\\\"sugg\\\":\\\"_4_1\\\",\\\"sversion\\\":\\\"13.6\\\",\\\"style\\\":\\\"list\\\",\\\"ttid\\\":\\\"600000@taobao_pc_10.7.0\\\",\\\"needTabs\\\":\\\"true\\\",\\\"areaCode\\\":\\\"CN\\\",\\\"vm\\\":\\\"nw\\\",\\\"countryNum\\\":\\\"156\\\",\\\"m\\\":\\\"pc\\\",\\\"page\\\":3,\\\"n\\\":48,\\\"q\\\":\\\"%E5%BD%B1%E7%9F%B3g03s\\\",\\\"qSource\\\":\\\"url\\\",\\\"pageSource\\\":\\\"a21bo.jianhua/a.search_downSideRecommend.d6\\\",\\\"channelSrp\\\":\\\"\\\",\\\"tab\\\":\\\"all\\\",\\\"pageSize\\\":\\\"49\\\",\\\"totalPage\\\":\\\"36\\\",\\\"totalResults\\\":\\\"1730\\\",\\\"sourceS\\\":\\\"2\\\",\\\"sort\\\":\\\"_coefp\\\",\\\"bcoffset\\\":\\\"-22\\\",\\\"ntoffset\\\":\\\"0\\\",\\\"filterTag\\\":\\\"\\\",\\\"service\\\":\\\"\\\",\\\"prop\\\":\\\"\\\",\\\"loc\\\":\\\"\\\",\\\"start_price\\\":null,\\\"end_price\\\":null,\\\"startPrice\\\":null,\\\"endPrice\\\":null,\\\"categoryp\\\":\\\"\\\",\\\"ha3Kvpairs\\\":null,\\\"myCNA\\\":\\\"mmesIqivSyQCAW87swyQMOaD\\\",\\\"screenResolution\\\":\\\"1920x1080\\\",\\\"viewResolution\\\":\\\"1897x3574\\\",\\\"userAgent\\\":\\\"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36 Edg/149.0.0.0\\\",\\\"couponUnikey\\\":\\\"\\\",\\\"subTabId\\\":\\\"\\\",\\\"np\\\":\\\"\\\",\\\"clientType\\\":\\\"h5\\\",\\\"isNewDomainAb\\\":\\\"false\\\",\\\"forceOldDomain\\\":\\\"false\\\"}\"}",
    "bx-ua": "234\\u0021ge6eKjMYeePWQANkO1pVvShwzIAqwKzkWPV1mcGLuiqpcJD7MH6Quu59IzaiXJOts7Y4A3xOC4TvEfu9QINW6ErwjuXW2Uqx+qiE2u+mYmovDCiRWkQzjCx470pH2rH9qrEACzflK+0KMhcjdSGRK7LDISAhanQBi45ImiKwTlY+Ul3Zn3UH9AJ7hwN+OUcOCd2wDo3eOQJNrUkZZ3wH9idThpoZnkp/cAjenL5cQCyN02cZn3UH9GgOj+qZ8ks/c24HeIoHOQYNhstZZ3wd9iJTCv2ZQkkwgsXH+lodOQ5Nhs5lZYEd9iyoCvr+8Lkfcs4HeVW7QCyNhsrkZ3wd9ibACPV+/3kCc2r7+lodQCymhxuZepUd9AdJhLoZQ8mzsXCiZ3oHQQVmhskZVPYQoaEZhL6TQps/cuWee3odnOYKKsLkVrwWiAxACNXVQppvcs4TnZoHvh6Nla5pSyQAzwTDvTypQppvc257VkZ6ZQ6FhVQWjpQHS7Y7hnoZQpU1AIUNOARsoNvDA4HUePkbWoOnaPa2S3lAEjE2WaCc+jvbEPYBB3SSEiebPevqAZvak0vQWSSutFrDaVUvyvk740uXPdHTXwlA5iDAaemcmq5jgbQ4dBki403Rpkv5a8ZnFc1O+7gvkTQ1mBaXBjkyun6CQxxPPLOhEU57YMJ6vCxE8gljpYzTC+CxYr3Wy29Qr5B5IpQvi4dXNvqBGDZMJWnpHa+mJhCJCfY+e2g5eybFXGd9DheE7ermn9C4rSzWsH3ygMZh/zqRqN63sJ1EJdun9UrKNmcK5Wr5qoaFSK5d9sjT1G4cqb1v+YlGGla/GCSjfV0g9eWWNs2rOUwLRVlZqbk6lYBE6lbEJtlimJ29ZGB3B0+cx83kfQXrQdZdi5CUCPcSgWbEqQtniJ9XfntuBaKwlBhmqFuM/l2hTA57QC4f+Rx8ebEbOzeGOnTK2PhnbW9iqTdDW94s/8PG/AM5YvnAV2OLf2Ng6ptsFBRa/xXvuWtWRGTdBojK+aqrse82wSX2t/QG0zd4Z+XzvZeJmtcZKUAUuE+GSGpFr0m0MyeU3aKBrYg/KsPNKeR78nGXzM3IdgpgHwH95mkk6k88rUSYGuTgMaETFUuKnvmQqgBdM4ObwrM0yvIjhbW4sLmdG8+9cTJc8NHvjLSLqarqBN7IXYSO2DQZeQZKHKXghZk75/7CD1Bg1Iwv6lAUWysjY0QgMMu1O7ZO4paytuoEZ/46zdSszGS8I0navtwG/WxPmBRgvFmg69Og69GQGOqaaTT3yHJ6CjW08fAOp/f4EbOU7R6yhQqsszWfOIJ32kFFSPE1P1wgpdo5B32kjMYyIqNGQCdoK9awAWuv3t+NhTs5WhC7ht+NHCN3Ay8zgqrOWTUpZLbgfbBXJkyHCaUviWKGB+G3lT4HdQKwDmlu8Xz2jLa2W9zPTdt+j+188IJRVYNS8KjgNx0STf+Gt1XjyUvXmcSr15QA9gQLkbastIDQKp6ZJdD/v/GbUFx5NMOyNb1NklMXHQEOA3JQsvXJvwYSnP9CZUG0yUj5XgWXJmJ8rVnez47GSarDAa8v4GQQxHjuMZynaqZaKKFizbVly7kCQs+jIn1ofMLLdUVI1LL23ltXItAaYkS++ielr3YT5oqbEGNBf8Ge2XQHf2AX7ck1Q+mwxBnqS6of+sN7ZwtS2aqyOBPPF8a3uaqc2Vx8GaGue/VMe2c0+37vSjxpXjz96x5B7oMBF4G1o4Ka4WaUFZ08+QtKlTXcRcCd/s/xEuHpjPnPCKBClgIPk3XBMcMiAksHE+NxmIdC0FXt4nVwMHRX0c0Pfs1XKVvvHitqpK5GJjW608ois7lw+rkcPhdkrXIi85rGjbobgJ==",
    "bx-umidtoken": "T2gAQF4Sk-YWskFxYv2hrZGwm9GEt9poPs0pVdqKm5ya2pk5-O_Ca7wa3cyafIV0IaY=",
    "bx_et": "hO5msmZ8DmLCZze--pxGZzz8C8FLDVbC8hhxQISkb3bUlne_hGXlbg9v0nUXsdSN0zEL9E7V0AAI3mJZX37yJKZ8y0FdlZOsoczdUOhuQmTnQfSw33Jyk38ZbfSwUb864j8ZgFozrFtybCJZ_0ly7FgqbCJara-W7Cl2_GRzrFKybCRNba7-UZ41XCA_tj4VcALWP_YzfHmDzUTo6Uv2YLSq_UClCUWoKnyIyhOvcF8cfWGXgdXCWFj0ijSGR_skzMPi9HzmQAmCPIQ-pDUUWs5Wg1HTnrPFdZRlNm48qu6e9t1qC5VaOZjWMgnIatzOSw_9ibg51kCP5Mb-akeVNTXNWMgY05CCWsUkvMJTTNt142U3rzDQhK8WkkUurAM63UTkvz4odm92PEEd."
}
response = requests.get(url, headers=headers, cookies=cookies, params=params)

print(response.text)
print(response)
"""
                    if (!0 === em.H5Request) {
                        var eS = "//" + (em.prefix ? em.prefix + "." : "") + (em.subDomain ? em.subDomain + "." : "") + em.mainDomain + "/h5/" + ep.api.toLowerCase() + "/" + ep.v.toLowerCase() + "/"
                          , eC = ep.appKey || ("waptest" === em.subDomain ? "4272" : "12574478")
                          , eT = (new Date).getTime()
                          , eM = eE(em.token + "&" + eT + "&" + eC + "&" + ep.data)
                          , eL = {
                            jsv: ez,
                            appKey: eC,
                            t: eT,
                            sign: eM
                        };
                        em.bxOption && Object.keys(em.bxOption).forEach(function(eo) {
                            eL["_" + eo] = em.bxOption[eo]
                        });
                        var eA = {
                            data: ep.data,
                            ua: ep.ua
                        };
                        Object.keys(ep).forEach(function(eo) {
                            void 0 === eL[eo] && void 0 === eA[eo] && "headers" !== eo && "ext_headers" !== eo && "ext_querys" !== eo && (eL[eo] = ep[eo])
                        }),
                        ep.ext_querys && Object.keys(ep.ext_querys).forEach(function(eo) {
                            eL[eo] = ep.ext_querys[eo]
                        }),
                        em.getJSONP ? eL.type = "jsonp" : em.getOriginalJSONP ? eL.type = "originaljsonp" : (em.getJSON || em.postJSON) && (eL.type = "originaljson"),
                        void 0 !== ep.valueType && ("original" === ep.valueType ? em.getJSONP || em.getOriginalJSONP ? eL.type = "originaljsonp" : (em.getJSON || em.postJSON) && (eL.type = "originaljson") : "string" === ep.valueType && (em.getJSONP || em.getOriginalJSONP ? eL.type = "jsonp" : (em.getJSON || em.postJSON) && (eL.type = "json"))),
                        !0 === em.useJsonpResultType && "originaljson" === eL.type && delete eL.type,
                        em.dangerouslySetProtocol && (eS = em.dangerouslySetProtocol + ":" + eS),
                        "5.0" === ep.SV && (eS += "5.0/",
                        ew()),
                        em.querystring = eL,
                        em.postdata = eA,
                        em.path = eS
                    }
                    eu()
"""
"""
             , eE = function(eo) {
                    function eu(eo, eu) {
                        return eo << eu | eo >>> 32 - eu
                    }
                    function ep(eo, eu) {
                        var ep, em, e_, ew, eS;
                        return e_ = 2147483648 & eo,
                        ew = 2147483648 & eu,
                        ep = 1073741824 & eo,
                        em = 1073741824 & eu,
                        eS = (1073741823 & eo) + (1073741823 & eu),
                        ep & em ? 2147483648 ^ eS ^ e_ ^ ew : ep | em ? 1073741824 & eS ? 3221225472 ^ eS ^ e_ ^ ew : 1073741824 ^ eS ^ e_ ^ ew : eS ^ e_ ^ ew
                    }
                    function em(eo, eu, ep) {
                        return eo & eu | ~eo & ep
                    }
                    function e_(eo, eu, ep) {
                        return eo & ep | eu & ~ep
                    }
                    function ew(eo, eu, ep) {
                        return eo ^ eu ^ ep
                    }
                    function eS(eo, eu, ep) {
                        return eu ^ (eo | ~ep)
                    }
                    function eC(eo, e_, ew, eS, eC, eE, eT) {
                        return eo = ep(eo, ep(ep(em(e_, ew, eS), eC), eT)),
                        ep(eu(eo, eE), e_)
                    }
                    function eE(eo, em, ew, eS, eC, eE, eT) {
                        return eo = ep(eo, ep(ep(e_(em, ew, eS), eC), eT)),
                        ep(eu(eo, eE), em)
                    }
                    function eT(eo, em, e_, eS, eC, eE, eT) {
                        return eo = ep(eo, ep(ep(ew(em, e_, eS), eC), eT)),
                        ep(eu(eo, eE), em)
                    }
                    function eM(eo, em, e_, ew, eC, eE, eT) {
                        return eo = ep(eo, ep(ep(eS(em, e_, ew), eC), eT)),
                        ep(eu(eo, eE), em)
                    }
                    function eL(eo) {
                        var eu, ep = "", em = "";
                        for (eu = 0; 3 >= eu; eu++)
                            ep += (em = "0" + (eo >>> 8 * eu & 255).toString(16)).substr(em.length - 2, 2);
                        return ep
                    }
                    var eA, eP, eI, eO, eD, eN, eR, eF, eB, eY = [], eZ = 7, eH = 12, eW = 17, ez = 22, eU = 5, eV = 9, eQ = 14, eK = 20, eG = 4, eX = 11, eJ = 16, e$ = 23, e0 = 6, e2 = 10, e5 = 15, e4 = 21;
                    for (eY = function(eo) {
                        for (var eu, ep = eo.length, em = ep + 8, e_ = (em - em % 64) / 64, ew = 16 * (e_ + 1), eS = Array(ew - 1), eC = 0, eE = 0; ep > eE; )
                            eu = (eE - eE % 4) / 4,
                            eC = eE % 4 * 8,
                            eS[eu] = eS[eu] | eo.charCodeAt(eE) << eC,
                            eE++;
                        return eu = (eE - eE % 4) / 4,
                        eC = eE % 4 * 8,
                        eS[eu] = eS[eu] | 128 << eC,
                        eS[ew - 2] = ep << 3,
                        eS[ew - 1] = ep >>> 29,
                        eS
                    }(eo = function(eo) {
                        eo = eo.replace(/\r\n/g, "\n");
                        for (var eu = "", ep = 0; ep < eo.length; ep++) {
                            var em = eo.charCodeAt(ep);
                            128 > em ? eu += String.fromCharCode(em) : em > 127 && 2048 > em ? eu += String.fromCharCode(em >> 6 | 192) + String.fromCharCode(63 & em | 128) : eu += String.fromCharCode(em >> 12 | 224) + String.fromCharCode(em >> 6 & 63 | 128) + String.fromCharCode(63 & em | 128)
                        }
                        return eu
                    }(eo)),
                    eN = 1732584193,
                    eR = 4023233417,
                    eF = 2562383102,
                    eB = 271733878,
                    eA = 0; eA < eY.length; eA += 16)
                        eP = eN,
                        eI = eR,
                        eO = eF,
                        eD = eB,
                        eN = eC(eN, eR, eF, eB, eY[eA + 0], eZ, 3614090360),
                        eB = eC(eB, eN, eR, eF, eY[eA + 1], eH, 3905402710),
                        eF = eC(eF, eB, eN, eR, eY[eA + 2], eW, 606105819),
                        eR = eC(eR, eF, eB, eN, eY[eA + 3], ez, 3250441966),
                        eN = eC(eN, eR, eF, eB, eY[eA + 4], eZ, 4118548399),
                        eB = eC(eB, eN, eR, eF, eY[eA + 5], eH, 1200080426),
                        eF = eC(eF, eB, eN, eR, eY[eA + 6], eW, 2821735955),
                        eR = eC(eR, eF, eB, eN, eY[eA + 7], ez, 4249261313),
                        eN = eC(eN, eR, eF, eB, eY[eA + 8], eZ, 1770035416),
                        eB = eC(eB, eN, eR, eF, eY[eA + 9], eH, 2336552879),
                        eF = eC(eF, eB, eN, eR, eY[eA + 10], eW, 4294925233),
                        eR = eC(eR, eF, eB, eN, eY[eA + 11], ez, 2304563134),
                        eN = eC(eN, eR, eF, eB, eY[eA + 12], eZ, 1804603682),
                        eB = eC(eB, eN, eR, eF, eY[eA + 13], eH, 4254626195),
                        eF = eC(eF, eB, eN, eR, eY[eA + 14], eW, 2792965006),
                        eR = eC(eR, eF, eB, eN, eY[eA + 15], ez, 1236535329),
                        eN = eE(eN, eR, eF, eB, eY[eA + 1], eU, 4129170786),
                        eB = eE(eB, eN, eR, eF, eY[eA + 6], eV, 3225465664),
                        eF = eE(eF, eB, eN, eR, eY[eA + 11], eQ, 643717713),
                        eR = eE(eR, eF, eB, eN, eY[eA + 0], eK, 3921069994),
                        eN = eE(eN, eR, eF, eB, eY[eA + 5], eU, 3593408605),
                        eB = eE(eB, eN, eR, eF, eY[eA + 10], eV, 38016083),
                        eF = eE(eF, eB, eN, eR, eY[eA + 15], eQ, 3634488961),
                        eR = eE(eR, eF, eB, eN, eY[eA + 4], eK, 3889429448),
                        eN = eE(eN, eR, eF, eB, eY[eA + 9], eU, 568446438),
                        eB = eE(eB, eN, eR, eF, eY[eA + 14], eV, 3275163606),
                        eF = eE(eF, eB, eN, eR, eY[eA + 3], eQ, 4107603335),
                        eR = eE(eR, eF, eB, eN, eY[eA + 8], eK, 1163531501),
                        eN = eE(eN, eR, eF, eB, eY[eA + 13], eU, 2850285829),
                        eB = eE(eB, eN, eR, eF, eY[eA + 2], eV, 4243563512),
                        eF = eE(eF, eB, eN, eR, eY[eA + 7], eQ, 1735328473),
                        eR = eE(eR, eF, eB, eN, eY[eA + 12], eK, 2368359562),
                        eN = eT(eN, eR, eF, eB, eY[eA + 5], eG, 4294588738),
                        eB = eT(eB, eN, eR, eF, eY[eA + 8], eX, 2272392833),
                        eF = eT(eF, eB, eN, eR, eY[eA + 11], eJ, 1839030562),
                        eR = eT(eR, eF, eB, eN, eY[eA + 14], e$, 4259657740),
                        eN = eT(eN, eR, eF, eB, eY[eA + 1], eG, 2763975236),
                        eB = eT(eB, eN, eR, eF, eY[eA + 4], eX, 1272893353),
                        eF = eT(eF, eB, eN, eR, eY[eA + 7], eJ, 4139469664),
                        eR = eT(eR, eF, eB, eN, eY[eA + 10], e$, 3200236656),
                        eN = eT(eN, eR, eF, eB, eY[eA + 13], eG, 681279174),
                        eB = eT(eB, eN, eR, eF, eY[eA + 0], eX, 3936430074),
                        eF = eT(eF, eB, eN, eR, eY[eA + 3], eJ, 3572445317),
                        eR = eT(eR, eF, eB, eN, eY[eA + 6], e$, 76029189),
                        eN = eT(eN, eR, eF, eB, eY[eA + 9], eG, 3654602809),
                        eB = eT(eB, eN, eR, eF, eY[eA + 12], eX, 3873151461),
                        eF = eT(eF, eB, eN, eR, eY[eA + 15], eJ, 530742520),
                        eR = eT(eR, eF, eB, eN, eY[eA + 2], e$, 3299628645),
                        eN = eM(eN, eR, eF, eB, eY[eA + 0], e0, 4096336452),
                        eB = eM(eB, eN, eR, eF, eY[eA + 7], e2, 1126891415),
                        eF = eM(eF, eB, eN, eR, eY[eA + 14], e5, 2878612391),
                        eR = eM(eR, eF, eB, eN, eY[eA + 5], e4, 4237533241),
                        eN = eM(eN, eR, eF, eB, eY[eA + 12], e0, 1700485571),
                        eB = eM(eB, eN, eR, eF, eY[eA + 3], e2, 2399980690),
                        eF = eM(eF, eB, eN, eR, eY[eA + 10], e5, 4293915773),
                        eR = eM(eR, eF, eB, eN, eY[eA + 1], e4, 2240044497),
                        eN = eM(eN, eR, eF, eB, eY[eA + 8], e0, 1873313359),
                        eB = eM(eB, eN, eR, eF, eY[eA + 15], e2, 4264355552),
                        eF = eM(eF, eB, eN, eR, eY[eA + 6], e5, 2734768916),
                        eR = eM(eR, eF, eB, eN, eY[eA + 13], e4, 1309151649),
                        eN = eM(eN, eR, eF, eB, eY[eA + 4], e0, 4149444226),
                        eB = eM(eB, eN, eR, eF, eY[eA + 11], e2, 3174756917),
                        eF = eM(eF, eB, eN, eR, eY[eA + 2], e5, 718787259),
                        eR = eM(eR, eF, eB, eN, eY[eA + 9], e4, 3951481745),
                        eN = ep(eN, eP),
                        eR = ep(eR, eI),
                        eF = ep(eF, eO),
                        eB = ep(eB, eD);
                    return (eL(eN) + eL(eR) + eL(eF) + eL(eB)).toLowerCase()
                }


"""




import requests
import json


headers = {
    "accept": "application/json, text/plain, */*",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
    "content-type": "application/json;charset=UTF-8",
    "origin": "https://www.xiaohongshu.com",
    "priority": "u=1, i",
    "referer": "https://www.xiaohongshu.com/",
    "sec-ch-ua": "\"Google Chrome\";v=\"149\", \"Chromium\";v=\"149\", \"Not)A;Brand\";v=\"24\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36",
    "x-b3-traceid": "8e23838a68298006",
    "x-s": "XYS_2UQhPsHCH0c1PUhMHjIj2erjwjQhyoPTqBPT49pjHjIj2eHjwjQgynEDJ74AHjIj2ePjwjQTJdPIPAZlg94aGLTlG98QyDbftFQg4Dkbzemk8rzGJDRl+gQawepnzrTx2bSocLDUy0bx+FDF8oQ7/DTpG7YI8/4jLgSI+eStyDMYGS8L4fqIankHLnRopbZEPbmhwoYdL0c9/0z0Pbzh2f4B4oYka/4YPd4NJLEL/BQmPrkHaMY/4bSPz9DlPaT+c9EIqMQCLDkcpnbLP9lt2rT/Jfznnfl0yLLIaSQQyAmOarEaLSz+GS8hz9Es2np7/Lp1qd+zyDS7/LLUaUHVHdWFH0ijJ9Qx8n+FHdF=",
    "x-s-common": "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",
    "x-t": "1781684718001",
    "x-xray-traceid": "cf6a57a4b394f2fb64cf7bdcf9e0f4bb"
}
cookies = {
    "abRequestId": "8fb1f146-0519-522c-a76e-60bfc72f047a",
    "a1": "19df2dd08e1408ye9unxy1rr8cuhsb7xaqpruuv1650000402431",
    "webId": "aa22da5c093a56f2c342538330d9016e",
    "gid": "yjfiJffJSS0jyjfiJff8YA7hdy48Yvdj7ICvUyKyFFYS7F28xMDWC788848J4qy84WDKJWDq",
    "ets": "1781166511877",
    "web_session": "040069b9ec60baf6e1c8723a1f384bad88ac54",
    "id_token": "VjEAAGmtr7MPlR6E2gaPr1mehHrNLr4Qj04n7xzNC1teWcTxD1Cw1XoB9ufg1avKTsiLJ4yj37P25BrGSuDTQupTCTYVGmHw6KK1Nxizc0KaeDjxUTn01EE8AvkCEnGY9mhHBvpR",
    "x-rednote-datactry": "CN",
    "x-rednote-holderctry": "CN",
    "x-user-id-creator.xiaohongshu.com": "689823f2000000002900b19e",
    "customer-sso-sid": "68c517650052407561699346sx4dlfps8cjc2blz",
    "customerClientId": "850482930985053",
    "access-token-creator.xiaohongshu.com": "customer.creator.AT-68c517650052407561699347cujwycbxazsufqga",
    "galaxy_creator_session_id": "HvBRXWoolSDTmJUjJorQLx9FUWQcpmBz7kY7",
    "galaxy.creator.beaker.session.id": "1781166626652097946090",
    "xsecappid": "xhs-pc-web",
    "webBuild": "6.19.4",
    "loadts": "1781684628855",
    "acw_tc": "0ad627c217816846317938188e0fd297432ba5a128d7c894a80e4e357c9388",
    "websectiga": "cffd9dcea65962b05ab048ac76962acee933d26157113bb213105a116241fa6c",
    "sec_poison_id": "2b803462-46a2-4cc8-9bb5-962699a02441",
    "unread": "{%22ub%22:%226a30f896000000000f01c67f%22%2C%22ue%22:%226a31367e000000001102ddb1%22%2C%22uc%22:45}"
}
url = "https://so.xiaohongshu.com/api/sns/web/v2/search/notes"
data = {
    "keyword": "编程",
    "page": 1,
    "page_size": 20,
    "search_id": "2gifsih1rcvg9qwob7nzd",
    "sort": "general",
    "note_type": 0,
    "ext_flags": [],
    "geo": "",
    "image_formats": [
        "jpg",
        "webp",
        "avif"
    ],
    "message_id": "sending"
}
data = json.dumps(data, separators=(',', ':'))
response = requests.post(url, headers=headers, cookies=cookies, data=data)

print(response.text)
print(response)
#x-s
"""
try {
                var P = "X-s"
                  , M = "X-t"
                  , U = getRealUrl(s, u, m)
                  , q = seccore_signv2;
                q && (a.headers[P] = q(U, w),
                a.headers[M] = +new Date + "")
            } catch (e) {}
"""
"""
function seccore_signv2(e, a) {
            var s = window.toString
              , u = e;
            "[object Object]" === s.call(a) || "[object Array]" === s.call(a) || (void 0 === a ? "undefined" : (0,
            eK._)(a)) === "object" && null !== a ? u += JSON.stringify(a) : "string" == typeof a && (u += a);
            var m = (0,
            eJ.Pu)([u].join(""))
              , w = (0,
            eJ.Pu)(e)
              , C = window.mnsv2(u, m, w)
              , R = {
                x0: eV.i8,
                x1: "xhs-pc-web",
                x2: window[eV.mj] || "PC",
                x3: C,
                x4: a ? void 0 === a ? "undefined" : (0,
                eK._)(a) : ""
            };
            return "XYS_" + (0,
            eJ.xE)((0,
            eJ.lz)(JSON.stringify(R)))
        }
"""
"""
      function seccore_signv2(e, a) {
            var s = window.toString
              , u = e;
            "[object Object]" === s.call(a) || "[object Array]" === s.call(a) || (void 0 === a ? "undefined" : (0,
            eK._)(a)) === "object" && null !== a ? u += JSON.stringify(a) : "string" == typeof a && (u += a);
            var m = (0,
            eJ.Pu)([u].join(""))
              , w = (0,
            eJ.Pu)(e)
              , C = window.mnsv2(u, m, w)
              , R = {
                x0: eV.i8,
                x1: "xhs-pc-web",
                x2: window[eV.mj] || "PC",
                x3: C,
                x4: a ? void 0 === a ? "undefined" : (0,
                eK._)(a) : ""
            };
"""
"""
 var _0x57c9e7 = function _0x30ce91() {
                    var _0x9eca1a = _0x5edc27
                      , _0x50f290 = arguments;
                    return _0x30ce91[_0x9eca1a(0x53)] > 0x0 || _0x30ce91['ΙII']++,
                    _0x31ad27(_0x30754b, _0x30ce91[_0x9eca1a(0x7b)], _0x30ce91[_0x9eca1a(0x5b)], _0x50f290, _0x30ce91[_0x4d21fc[_0x9eca1a(0x42)]], this, null, 0x0);
                };
"""
#x-s-common
"""
 function xsCommon(e, a) {
            var s, u;
            return signAdaptor_awaiter(this, void 0, void 0, function() {
                var m, w, C, R, P, M, U, q, j, G, K, Z, et, en;
                return signAdaptor_generator(this, function(er) {
                    switch (er.label) {
                    case 0:
                        if (er.trys.push([0, 2, , 3]),
                        m = e.platform,
                        w = a.url,
                        C = eV.yl.map(function(e) {
                            return new RegExp(e)
                        }).some(function(e) {
                            return e.test(w)
                        }),
                        !(0,
                        eH.hF)(w))
                            return [2, a];
                        return R = "",
                        P = "",
                        M = a.headers["X-Sign"] || "",
                        U = getSigCount(R && P || M),
                        q = localStorage.getItem(eV.q2),
                        j = localStorage.getItem(eV.z7) || eV.fI,
                        G = localStorage.getItem(eV.br) + ";" + window._dsl,
                        en = {
                            s0: (0,
                            eH.SW)(m),
                            s1: "",
                            x0: j,
                            x1: eV.i8,
                            x2: m || "PC",
                            x3: "xhs-pc-web",
                            x4: "6.19.2"
                        },
                        [4, getCookieValue(e, eV.o4)];
                    case 1:
                        return en.x5 = er.sent(),
                        en.x6 = R,
                        en.x7 = P,
                        en.x8 = q,
                        en.x9 = (0,
                        eJ.tb)("".concat(R).concat(P).concat(q)),
                        en.x10 = U,
                        en.x11 = "normal",
                        en.x12 = G,
                        K = en,
                        Z = eV.LN.map(function(e) {
                            return new RegExp(e)
                        }).some(function(e) {
                            return e.test(w)
                        }),
                        (null === (s = window.xhsFingerprintV3) || void 0 === s ? void 0 : s.getCurMiniUa) && Z ? null === (u = window.xhsFingerprintV3) || void 0 === u || u.getCurMiniUa(function(e) {
                            K.x8 = e,
                            K.x9 = (0,
                            eJ.tb)("".concat(R).concat(P).concat(e)),
                            a.headers["X-S-Common"] = (0,
                            eJ.xE)((0,
                            eJ.lz)(JSON.stringify(K)))
                        }) : a.headers["X-S-Common"] = (0,
                        eJ.xE)((0,
                        eJ.lz)(JSON.stringify(K))),
                        [3, 3];
                    case 2:
                        return et = er.sent(),
                        [3, 3];
                    case 3:
                        return [2, a]
                    }
                })
            })
        }
"""

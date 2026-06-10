import requests


headers = {
    "accept": "application/json",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
    "content-type": "application/x-www-form-urlencoded",
    "origin": "https://www.goofish.com",
    "priority": "u=1, i",
    "referer": "https://www.goofish.com/",
    "sec-ch-ua": "\"Chromium\";v=\"148\", \"Google Chrome\";v=\"148\", \"Not/A)Brand\";v=\"99\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36"
}
cookies = {
    "cna": "Gm5/In55snoCAbz9BOPVXW4C",
    "t": "dd5e21f58f5f44183bf0d6615ff5f601",
    "tracknick": "tb975336787",
    "xlly_s": "1",
    "cookie2": "13d72fed491666b5c835e2dbcf0eada9",
    "mtop_partitioned_detect": "1",
    "_m_h5_tk": "02c5aa30e078b31673f8b64cf803e612_1780839455122",
    "_m_h5_tk_enc": "9f407bf1b87031c0c8e89511e2419da0",
    "_samesite_flag_": "true",
    "_tb_token_": "efb87b41bb09",
    "sgcookie": "E100hNnf0E8vZMHBy9UgFDPRYTW89WWsGXBmDxCF0iA61mjqWDdYm%2BS%2BkzgA8hOEsXjn1IAq3Ehi%2B5FF%2B2gIpNDsVVZ%2Fgqoo%2BFEqBws1lA0bKIY%3D",
    "csg": "1a8c3c8d",
    "unb": "2209394220946",
    "havana_lgc2_77": "eyJoaWQiOjIyMDkzOTQyMjA5NDYsInNnIjoiY2UxNTE5OWJhY2Q3MTIxYWM4ZTVjNmI4NTZkZWFiM2MiLCJzaXRlIjo3NywidG9rZW4iOiIxckpJR1pNLWN0LXg4Zzc3ZUdzV3FDdyJ9",
    "_hvn_lgc_": "77",
    "havana_lgc_exp": "1783423759782",
    "sdkSilent": "1780918169293",
    "tfstk": "gBTjaymfR-2XlMcxB-lzO0NFIGb61buU5519tCU46ZQYBRddUKWVuf01BKXyutRVkSxkLBU2umba5ZbGWvkE82lDiNbTKWz3htAJZ1hPMthsArQGWvkz4PImRNv2Dlc1XQh5_1yTWdIvwuChe-UvBtI8e61hWOp9BaIR_1XTBrBYe_Bl6NB9BNh5yTf1WOpOWbO-NTVC1m6DGfvsGzWbsOdAFPU9kVjfdKZaWPL5GiT9MTOyaU1fc9I_AFKDkLR9uEjo2u_MaH96XdmUqZO9DZCeiqa5JIKy5_8Z_l6vnUOJygNU8p_XCMLAV5UwON6cP_LK_kXyPtJ9lghURG7J8MQv40DVbZ1BBEvb1PppaB8cqFMQeOxVtaCeiqa5JICO4RUFdNhLf7s35_6ENbZgj3ePvYK2SHydD_ff4bG7HhjAZ_6ENbZgjiClGTlSN-KG."
}
url = "https://h5api.m.goofish.com/h5/mtop.taobao.idlehome.home.webpc.feed/1.0/"
params = {
    "jsv": "2.7.2",
    "appKey": "34839810",
    "t": "1780831782260",
    "sign": "f422018b04d8f23307ab97316f230c68",
    "v": "1.0",
    "type": "originaljson",
    "accountSite": "xianyu",
    "dataType": "json",
    "timeout": "20000",
    "api": "mtop.taobao.idlehome.home.webpc.feed",
    "sessionOption": "AutoLoginOnly",
    "spm_cnt": "a21ybx.home.0.0"
}
data = {
    "data": "{\"itemId\":\"\",\"pageSize\":5,\"pageNumber\":1,\"machId\":\"165202_1\"}"
}
response = requests.post(url, headers=headers, cookies=cookies, params=params, data=data)

print(response.text)
print(response)

"""
  function i(a) {
        function b(a, b) {
            return a << b | a >>> 32 - b
        }
        function c(a, b) {
            var c, d, e, f, g;
            return e = 2147483648 & a,
            f = 2147483648 & b,
            c = 1073741824 & a,
            d = 1073741824 & b,
            g = (1073741823 & a) + (1073741823 & b),
            c & d ? 2147483648 ^ g ^ e ^ f : c | d ? 1073741824 & g ? 3221225472 ^ g ^ e ^ f : 1073741824 ^ g ^ e ^ f : g ^ e ^ f
        }
        function d(a, b, c) {
            return a & b | ~a & c
        }
        function e(a, b, c) {
            return a & c | b & ~c
        }
        function f(a, b, c) {
            return a ^ b ^ c
        }
        function g(a, b, c) {
            return b ^ (a | ~c)
        }
        function h(a, e, f, g, h, i, j) {
            return a = c(a, c(c(d(e, f, g), h), j)),
            c(b(a, i), e)
        }
        function i(a, d, f, g, h, i, j) {
            return a = c(a, c(c(e(d, f, g), h), j)),
            c(b(a, i), d)
        }
        function j(a, d, e, g, h, i, j) {
            return a = c(a, c(c(f(d, e, g), h), j)),
            c(b(a, i), d)
        }
        function k(a, d, e, f, h, i, j) {
            return a = c(a, c(c(g(d, e, f), h), j)),
            c(b(a, i), d)
        }
        function l(a) {
            for (var b, c = a.length, d = c + 8, e = (d - d % 64) / 64, f = 16 * (e + 1), g = new Array(f - 1), h = 0, i = 0; c > i; )
                b = (i - i % 4) / 4,
                h = i % 4 * 8,
                g[b] = g[b] | a.charCodeAt(i) << h,
                i++;
            return b = (i - i % 4) / 4,
            h = i % 4 * 8,
            g[b] = g[b] | 128 << h,
            g[f - 2] = c << 3,
            g[f - 1] = c >>> 29,
            g
        }
        function m(a) {
            var b, c, d = "", e = "";
            for (c = 0; 3 >= c; c++)
                b = a >>> 8 * c & 255,
                e = "0" + b.toString(16),
                d += e.substr(e.length - 2, 2);
            return d
        }
        function n(a) {
            a = a.replace(/\r\n/g, "\n");
            for (var b = "", c = 0; c < a.length; c++) {
                var d = a.charCodeAt(c);
                128 > d ? b += String.fromCharCode(d) : d > 127 && 2048 > d ? (b += String.fromCharCode(d >> 6 | 192),
                b += String.fromCharCode(63 & d | 128)) : (b += String.fromCharCode(d >> 12 | 224),
                b += String.fromCharCode(d >> 6 & 63 | 128),
                b += String.fromCharCode(63 & d | 128))
            }
            return b
        }
        var o, p, q, r, s, t, u, v, w, x = [], y = 7, z = 12, A = 17, B = 22, C = 5, D = 9, E = 14, F = 20, G = 4, H = 11, I = 16, J = 23, K = 6, L = 10, M = 15, N = 21;
        for (a = n(a),
        x = l(a),
        t = 1732584193,
        u = 4023233417,
        v = 2562383102,
        w = 271733878,
        o = 0; o < x.length; o += 16)
            p = t,
            q = u,
            r = v,
            s = w,
            t = h(t, u, v, w, x[o + 0], y, 3614090360),
            w = h(w, t, u, v, x[o + 1], z, 3905402710),
            v = h(v, w, t, u, x[o + 2], A, 606105819),
            u = h(u, v, w, t, x[o + 3], B, 3250441966),
            t = h(t, u, v, w, x[o + 4], y, 4118548399),
            w = h(w, t, u, v, x[o + 5], z, 1200080426),
            v = h(v, w, t, u, x[o + 6], A, 2821735955),
            u = h(u, v, w, t, x[o + 7], B, 4249261313),
            t = h(t, u, v, w, x[o + 8], y, 1770035416),
            w = h(w, t, u, v, x[o + 9], z, 2336552879),
            v = h(v, w, t, u, x[o + 10], A, 4294925233),
            u = h(u, v, w, t, x[o + 11], B, 2304563134),
            t = h(t, u, v, w, x[o + 12], y, 1804603682),
            w = h(w, t, u, v, x[o + 13], z, 4254626195),
            v = h(v, w, t, u, x[o + 14], A, 2792965006),
            u = h(u, v, w, t, x[o + 15], B, 1236535329),
            t = i(t, u, v, w, x[o + 1], C, 4129170786),
            w = i(w, t, u, v, x[o + 6], D, 3225465664),
            v = i(v, w, t, u, x[o + 11], E, 643717713),
            u = i(u, v, w, t, x[o + 0], F, 3921069994),
            t = i(t, u, v, w, x[o + 5], C, 3593408605),
            w = i(w, t, u, v, x[o + 10], D, 38016083),
            v = i(v, w, t, u, x[o + 15], E, 3634488961),
            u = i(u, v, w, t, x[o + 4], F, 3889429448),
            t = i(t, u, v, w, x[o + 9], C, 568446438),
            w = i(w, t, u, v, x[o + 14], D, 3275163606),
            v = i(v, w, t, u, x[o + 3], E, 4107603335),
            u = i(u, v, w, t, x[o + 8], F, 1163531501),
            t = i(t, u, v, w, x[o + 13], C, 2850285829),
            w = i(w, t, u, v, x[o + 2], D, 4243563512),
            v = i(v, w, t, u, x[o + 7], E, 1735328473),
            u = i(u, v, w, t, x[o + 12], F, 2368359562),
            t = j(t, u, v, w, x[o + 5], G, 4294588738),
            w = j(w, t, u, v, x[o + 8], H, 2272392833),
            v = j(v, w, t, u, x[o + 11], I, 1839030562),
            u = j(u, v, w, t, x[o + 14], J, 4259657740),
            t = j(t, u, v, w, x[o + 1], G, 2763975236),
            w = j(w, t, u, v, x[o + 4], H, 1272893353),
            v = j(v, w, t, u, x[o + 7], I, 4139469664),
            u = j(u, v, w, t, x[o + 10], J, 3200236656),
            t = j(t, u, v, w, x[o + 13], G, 681279174),
            w = j(w, t, u, v, x[o + 0], H, 3936430074),
            v = j(v, w, t, u, x[o + 3], I, 3572445317),
            u = j(u, v, w, t, x[o + 6], J, 76029189),
            t = j(t, u, v, w, x[o + 9], G, 3654602809),
            w = j(w, t, u, v, x[o + 12], H, 3873151461),
            v = j(v, w, t, u, x[o + 15], I, 530742520),
            u = j(u, v, w, t, x[o + 2], J, 3299628645),
            t = k(t, u, v, w, x[o + 0], K, 4096336452),
            w = k(w, t, u, v, x[o + 7], L, 1126891415),
            v = k(v, w, t, u, x[o + 14], M, 2878612391),
            u = k(u, v, w, t, x[o + 5], N, 4237533241),
            t = k(t, u, v, w, x[o + 12], K, 1700485571),
            w = k(w, t, u, v, x[o + 3], L, 2399980690),
            v = k(v, w, t, u, x[o + 10], M, 4293915773),
            u = k(u, v, w, t, x[o + 1], N, 2240044497),
            t = k(t, u, v, w, x[o + 8], K, 1873313359),
            w = k(w, t, u, v, x[o + 15], L, 4264355552),
            v = k(v, w, t, u, x[o + 6], M, 2734768916),
            u = k(u, v, w, t, x[o + 13], N, 1309151649),
            t = k(t, u, v, w, x[o + 4], K, 4149444226),
            w = k(w, t, u, v, x[o + 11], L, 3174756917),
            v = k(v, w, t, u, x[o + 2], M, 718787259),
            u = k(u, v, w, t, x[o + 9], N, 3951481745),
            t = c(t, p),
            u = c(u, q),
            v = c(v, r),
            w = c(w, s);
        var O = m(t) + m(u) + m(v) + m(w);
        return O.toLowerCase()
    }
    
    
         if (d.H5Request === !0) {
            var g = "//" + (d.prefix ? d.prefix + "." : "") + (d.subDomain ? d.subDomain + "." : "") + d.mainDomain + "/h5/" + c.api.toLowerCase() + "/" + c.v.toLowerCase() + "/"
              , h = c.appKey || ("waptest" === d.subDomain ? "4272" : "12574478")
              , j = (new Date).getTime()
              , k = i(d.token + "&" + j + "&" + h + "&" + c.data)
              , l = {
                jsv: A,
                appKey: h,
                t: j,
                sign: k
            }
              , m = {
                data: c.data,
                ua: c.ua
            };
            Object.keys(c).forEach(function(a) {
                "undefined" == typeof l[a] && "undefined" == typeof m[a] && "headers" !== a && "ext_headers" !== a && "ext_querys" !== a && (l[a] = c[a])
            }),
            c.ext_querys && Object.keys(c.ext_querys).forEach(function(a) {
                l[a] = c.ext_querys[a]
            }),
            d.getJSONP ? l.type = "jsonp" : d.getOriginalJSONP ? l.type = "originaljsonp" : (d.getJSON || d.postJSON) && (l.type = "originaljson"),
            "undefined" != typeof c.valueType && ("original" === c.valueType ? d.getJSONP || d.getOriginalJSONP ? l.type = "originaljsonp" : (d.getJSON || d.postJSON) && (l.type = "originaljson") : "string" === c.valueType && (d.getJSONP || d.getOriginalJSONP ? l.type = "jsonp" : (d.getJSON || d.postJSON) && (l.type = "json"))),
            d.useJsonpResultType === !0 && "originaljson" === l.type && delete l.type,
            d.dangerouslySetProtocol && (g = d.dangerouslySetProtocol + ":" + g),
            "5.0" === c.SV && (g += "5.0/",
            f()),
            d.querystring = l,
            d.postdata = m,
            d.path = g
        }
        b()
    }
"""
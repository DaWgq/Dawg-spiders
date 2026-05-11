"""
    返回数据的加密方法
   function w(G) {
        if (Object.prototype.toString.call(G) !== "[object String]")
            return G;
        let Te = null;
        try {
            const Me = gn.enc.Base64.parse(G).toString(gn.enc.Hex)
              , nt = gn.enc.Utf8.parse("68zhehao2O776519")
              , Ke = gn.enc.Utf8.parse("aa176b7519e84710")
              , ut = gn.lib.CipherParams.create({
                ciphertext: gn.enc.Hex.parse(Me)
            })
              , rn = gn.AES.decrypt(ut, nt, {
                iv: Ke,
                padding: gn.pad.Pkcs7
            });
            Te = gn.enc.Utf8.stringify(rn).replace(/\0.*$/g, "")
        } catch (Me) {
            console.warn("jm:" + Me)
        }
        return Te
"""
"""
加密
G = () => {
            A({
                requestUrl: "/app/appUser/followUser",
                methodVal: "post",
                data: {
                    data: b().encryptValue(JSON.stringify({
                        uid: t.result.userId,
                        wtId: t.wtId,
                        wtType: 1,
                        type: 3
                    }))
                }
            }).then(n => {
                n ? (t.resultRest.isFollow = !0,
                t.result.fansCount = Number(t.result.fansCount) + 1) : (t.resultRest.isFollow = !1,
                t.result.fansCount = Number(t.result.fansCount) - 1)
            }
            ).catch( () => {}
            )
        }
"""
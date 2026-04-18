const CryptoJS = require("crypto-js");

function getResCode() {
  const key = CryptoJS.enc.Utf8.parse(
    "1234567887654321"
  );

  const iv = CryptoJS.enc.Utf8.parse("1234567887654321");

  const data = CryptoJS.enc.Utf8.parse(
    Math.floor(Date.now() / 1000).toString()
  );

  const encrypted = CryptoJS.AES.encrypt(data, key, {
    iv: iv,
    mode: CryptoJS.mode.CBC,
    padding: CryptoJS.pad.Pkcs7
  });

  return CryptoJS.enc.Base64.stringify(encrypted.ciphertext);
}

console.log(getResCode());
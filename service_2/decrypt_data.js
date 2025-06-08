const crypto = require('crypto');
require('dotenv').config();
const {TokenIntegrityError} = require("./errors");

const decryptData = (encryptdData) => {
  const key = Buffer.from(process.env.ENCRYPTION_KEY, "base64");
  const token = Buffer.from(encryptdData.toString(), "base64");

  const version = token.slice(0, 1);  // Should be 0x80
  const timestamp = token.slice(1, 9);
  const iv = token.slice(9, 25);
  const ciphertext = token.slice(25, -32);
  const hmac = token.slice(-32);

  // Verify HMAC
  const computedHmac = crypto.createHmac('sha256', key).update(token.slice(0, -32)).digest();
  if (!crypto.timingSafeEqual(hmac, computedHmac)) {
     throw new TokenIntegrityError("Token integrity check failed — possible tampering");
  }

  // Decrypt
  const decipher = crypto.createDecipheriv('aes-128-cbc', key.slice(0, 16), iv);
  let decrypted = decipher.update(ciphertext);
  decrypted = Buffer.concat([decrypted, decipher.final()]);
  return JSON.parse(decrypted.toString());
}


module.exports = {decryptData}
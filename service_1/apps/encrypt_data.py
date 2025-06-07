import json
import os
import time
import base64
import hmac
import hashlib
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from django.conf import settings

def pad_pkcs7(data: bytes, block_size: int = AES.block_size) -> bytes:
    padding_len = block_size - len(data) % block_size
    return data + bytes([padding_len] * padding_len)

def encrypt_data(data):
    key = settings.ENCRYPTION_KEY
    key = base64.b64decode(key)
    iv = get_random_bytes(16)
    timestamp = int(time.time()).to_bytes(8, byteorder='big')

    plaintext = json.dumps(data).encode()
    #padded = plaintext + b"\0" * (AES.block_size - len(plaintext) % AES.block_size)
    padded = pad_pkcs7(plaintext)
    cipher = AES.new(key[:16], AES.MODE_CBC, iv)
    ciphertext = cipher.encrypt(padded)

    version = b"\x80"  # version byte
    body = version + timestamp + iv + ciphertext

    hmac_digest = hmac.new(key, body, hashlib.sha256).digest()
    token = body + hmac_digest  # final token = [version][timestamp][iv][ciphertext][hmac]
    return base64.b64encode(token).decode('utf-8')
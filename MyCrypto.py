import json
from hashlib import scrypt
from base64 import b64decode,b64encode
from Cryptodome.Random import get_random_bytes
from Cryptodome.Cipher import ChaCha20_Poly1305
from pyDH import DiffieHellman

class MyCrypto:
    def __init__(self, password):
        self.password = bytes(password, 'utf-8')

    def encrypt(self, plain_text):
        salt = get_random_bytes(32)
        nonce = get_random_bytes(24)
        header = b'header'

        key = scrypt(self.password, salt=salt, n=2 ** 14, r=8, p=1, dklen=32)

        # create cipher config
        cipher = ChaCha20_Poly1305.new(key=key, nonce=nonce)
        cipher.update(header)

        # return a dictionary with the encrypted text
        cipher_text, tag = cipher.encrypt_and_digest(bytes(plain_text, 'utf-8'))

        return json.dumps(
            {
                'nonce': b64encode(nonce).decode('utf-8'),
                'salt': b64encode(salt).decode('utf-8'),
                'header': b64encode(header).decode('utf-8'),
                'cipher_text': b64encode(cipher_text).decode('utf-8'),
                'tag': b64encode(tag).decode('utf-8')
            }
        )

    def decrypt(self, enc_json):
        encrypted = json.loads(enc_json)
        salt = b64decode(encrypted['salt'])
        nonce = b64decode(encrypted['nonce'])
        header = b64decode(encrypted['header'])
        cipher_text = b64decode(encrypted['cipher_text'])
        tag = b64decode(encrypted['tag'])

        key = scrypt(self.password, salt=salt, n=2 ** 14, r=8, p=1, dklen=32)
        cipher = ChaCha20_Poly1305.new(key=key, nonce=nonce)
        cipher.update(header)
        return cipher.decrypt_and_verify(cipher_text, tag)
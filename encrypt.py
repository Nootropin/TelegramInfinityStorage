from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Protocol.KDF import scrypt
import os

def encrypt_file(file_path, password, outputFileName):
    data = open(file_path, 'rb').read()
    
    salt = get_random_bytes(16)
    key = scrypt(password, salt, 32, N=2**14, r=8, p=1)
    
    cipher = AES.new(key, AES.MODE_GCM)
    ciphertext, tag = cipher.encrypt_and_digest(data)
    
    with open(outputFileName, 'wb') as file_out:
        [file_out.write(x) for x in (salt, cipher.nonce, tag, ciphertext)]

def decrypt_file(file_path, password, outputFileName):
    with open(file_path, 'rb') as file_in:
        salt, nonce, tag, ciphertext = [file_in.read(x) for x in (16, 16, 16, -1)]
        
    key = scrypt(password, salt, 32, N=2**14, r=8, p=1)
    
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    data = cipher.decrypt_and_verify(ciphertext, tag)
    
    with open(outputFileName, 'wb') as file_out:
        file_out.write(data)
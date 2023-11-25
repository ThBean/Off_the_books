import os
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes


def get_pub_key(password):
    with open("key","rb") as f:
        extern_key = f.read()
        f.close()

    key = RSA.import_key(extern_key=extern_key, passphrase=password)
    pub_key = key.public_key()
    exported_key = pub_key.export_key()
    
    return exported_key.decode()

def make_key():
    key = RSA.generate(4096)
    private_key = key.export_key("PEM")
    return private_key

def encrypt_text(key, data: str):   #Key is a byte map btw
    recipient_key = RSA.import_key(key)
    session_key = get_random_bytes(16)

    # Encrypt the session key with the public RSA key
    cipher_rsa = PKCS1_OAEP.new(recipient_key)
    enc_session_key = cipher_rsa.encrypt(session_key)

    # Encrypt the data with the AES session key
    cipher_aes = AES.new(session_key, AES.MODE_EAX)
    encoded_data = data.encode()
    ciphertext, tag = cipher_aes.encrypt_and_digest(encoded_data)

    with open("Message","wb") as file_out:
        for x in (enc_session_key, cipher_aes.nonce, tag, ciphertext):
            file_out.write(x)
        file_out.close()
    # this function does not return anything. Client.py needs something to be returned but idk what to return here

def decrypt_text(file):#Ensure key is in bytes
    with open(file,"rb") as f:
        data = f.read()
        f.close()

    with open("key", "rb") as f:
        key = f.read()
        f.close()

    private_key = RSA.import_key(key)

    enc_session_key, nonce, tag, ciphertext = \
        [ data for x in (private_key.size_in_bytes(), 16, 16, -1) ]

    # Decrypt the session key with the private RSA key
    cipher_rsa = PKCS1_OAEP.new(private_key)
    session_key = cipher_rsa.decrypt(enc_session_key)

    # Decrypt the data with the AES session key
    cipher_aes = AES.new(session_key, AES.MODE_EAX, nonce)
    data = cipher_aes.decrypt_and_verify(ciphertext, tag)
    return data.decode()


def password_decrypt(file, password):
    with open(file, "rb") as f:
        data = f.read()
        f.close()
    os.remove(file)

    with open("key", "rb") as f:
        key = f.read()
    f.close()
    
    with open("key", "rb") as f:
        extern_key = f.read()
        
    key = RSA.import_key(extern_key=extern_key, passphrase=password)

    enc_session_key, nonce, tag, ciphertext = \
        [data for x in (key.size_in_bytes(), 16, 16, -1)]

    # Decrypt the session key with the private RSA key
    cipher_rsa = PKCS1_OAEP.new(key)
    session_key = cipher_rsa.decrypt(enc_session_key)

    # Decrypt the data with the AES session key
    cipher_aes = AES.new(session_key, AES.MODE_EAX, nonce)
    data = cipher_aes.decrypt_and_verify(ciphertext, tag)
    return data.decode()

def password_encrypt(password, name, key, data: str):
    recipient_key = RSA.import_key(key, passphrase=password)

    session_key = get_random_bytes(16)

    # Encrypt the session key with the public RSA key
    cipher_rsa = PKCS1_OAEP.new(recipient_key)
    enc_session_key = cipher_rsa.encrypt(session_key)

    # Encrypt the data with the AES session key
    cipher_aes = AES.new(session_key, AES.MODE_EAX)
    encoded_data = data.encode()
    ciphertext, tag = cipher_aes.encrypt_and_digest(encoded_data)

    with open("Message","wb") as file_out:
        for x in (enc_session_key, cipher_aes.nonce, tag, ciphertext):
            file_out.write(x)
        file_out.close()


def password_make_key(password):
    key = RSA.generate(2048)
    with open("key", "wb") as f:
        f.write(key.export_key(passphrase=password, pkcs=8, protection="scryptAndAES128-CBC"))
        f.close()

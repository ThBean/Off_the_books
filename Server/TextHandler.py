from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes


def GetPubKey():
    return RSA.import_key(open("pubKey","rb").read()).export_key("PEM").decode()

def make_Key():
    key = RSA.generate(4096)
    private_key = key.export_key("PEM")
    open("key","wb").write(private_key)
    return private_key

def encryptText(Key,data):#Key is a byte map btw

    recipient_key = RSA.import_key(Key)
    session_key = get_random_bytes(16)

    # Encrypt the session key with the public RSA key
    cipher_rsa = PKCS1_OAEP.new(recipient_key)
    enc_session_key = cipher_rsa.encrypt(session_key)

    # Encrypt the data with the AES session key
    cipher_aes = AES.new(session_key, AES.MODE_EAX)
    ciphertext, tag = cipher_aes.encrypt_and_digest(data)

    file_out = open("Message","wb")
    [ file_out.write(x) for x in (enc_session_key, cipher_aes.nonce, tag, ciphertext) ]
    file_out.close()

def decryptText(file):#Ensure key is in bytes
    f = open(file,"rb")

    fk = open("key", "rb")
    Key = fk.read()
    fk.close()

    private_key = RSA.import_key(Key)

    enc_session_key, nonce, tag, ciphertext = \
        [ f.read(x) for x in (private_key.size_in_bytes(), 16, 16, -1) ]
    f.close()
    # Decrypt the session key with the private RSA key
    cipher_rsa = PKCS1_OAEP.new(private_key)
    session_key = cipher_rsa.decrypt(enc_session_key)

    # Decrypt the data with the AES session key
    cipher_aes = AES.new(session_key, AES.MODE_EAX, nonce)
    data = cipher_aes.decrypt_and_verify(ciphertext, tag)
    return data.decode('latin-1')


def PasswordDecrypt(file,password):

    f = open(file, "rb")
    data = f.read()
    f.close()

    f = open("key", "rb")
    Key = f.read()
    f.close()

    key = RSA.import_key(open("key", "rb").read(), passphrase=password)

    enc_session_key, nonce, tag, ciphertext = \
        [data for x in (key.size_in_bytes(), 16, 16, -1)]

    # Decrypt the session key with the private RSA key
    cipher_rsa = PKCS1_OAEP.new(key)
    session_key = cipher_rsa.decrypt(enc_session_key)

    # Decrypt the data with the AES session key
    cipher_aes = AES.new(session_key, AES.MODE_EAX, nonce)
    data = cipher_aes.decrypt_and_verify(ciphertext, tag)
    return data.decode()

def PasswordEncrypt(password,Name,key,data):
    recipient_key = RSA.import_key(key, passphrase=password)

    session_key = get_random_bytes(16)

    # Encrypt the session key with the public RSA key
    cipher_rsa = PKCS1_OAEP.new(recipient_key)
    enc_session_key = cipher_rsa.encrypt(session_key)

    # Encrypt the data with the AES session key
    cipher_aes = AES.new(session_key, AES.MODE_EAX)
    ciphertext, tag = cipher_aes.encrypt_and_digest(data.encode())

    file_out = open("Message","wb")
    [ file_out.write(x) for x in (enc_session_key, cipher_aes.nonce, tag, ciphertext) ]
    file_out.close()

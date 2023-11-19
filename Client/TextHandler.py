from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.Random import get_random_bytes
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256
def Sign(Data,Password):
    key = RSA.import_key(open("key", "rb").read(), passphrase=Password)

    digest = SHA256.new()
    digest.update(Data.encode('utf-8'))

    signer = PKCS1_v1_5.new(key)


    return signer.sign(digest).decode()

def Verify(Pubkey,Signiture):
    digest = SHA256.new()
    digest.update("MySignature".encode('utf-8'))
    print(Signiture[0][4:])

    sig = bytes.fromhex(Signiture[0][4:])  # convert string to bytes object

    # Load public key (not private key) and verify signature
    print(Pubkey)
    public_key = RSA.importKey(Pubkey)
    verifier = PKCS1_v1_5.new(public_key)
    return verifier.verify(digest, sig)

def PasswordMakeKey(password):
    key = RSA.generate(2048)
    open("key","wb").write(key.export_key(passphrase=password,pkcs=8,protection="scryptAndAES128-CBC"))
    
def GetPubKey(Password):
    return RSA.import_key(open("key","rb").read(), passphrase=Password).public_key().export_key("PEM").decode()

def encryptText(Key,data) -> str:#Key is a byte map btw
    out = b''

    recipient_key = RSA.import_key(Key)
    session_key = get_random_bytes(16)
    out = ""

    # Encrypt the session key with the public RSA key
    cipher_rsa = PKCS1_OAEP.new(recipient_key)
    enc_session_key = cipher_rsa.encrypt(session_key)

    # Encrypt the data with the AES session key
    cipher_aes = AES.new(session_key, AES.MODE_EAX)
    ciphertext, tag = cipher_aes.encrypt_and_digest(data.encode())
    [ file_out.write(x) for x in (enc_session_key, cipher_aes.nonce, tag, ciphertext) ]
    file_out.close()

def decryptText(Key,data):#Ensure key is in bytes

    private_key = RSA.import_key(Key)

    enc_session_key, nonce, tag, ciphertext = \
        [ data.encode() for x in (private_key.size_in_bytes(), 16, 16, -1) ]

    # Decrypt the session key with the private RSA key
    cipher_rsa = PKCS1_OAEP.new(private_key)
    session_key = cipher_rsa.decrypt(enc_session_key)

    # Decrypt the data with the AES session key
    cipher_aes = AES.new(session_key, AES.MODE_EAX, nonce)
    data = cipher_aes.decrypt_and_verify(ciphertext, tag)
    return data.decode()

def PasswordDecrypt(data,password):
    key =  RSA.import_key(open("key", "rb").read(), passphrase=password)

    enc_session_key, nonce, tag, ciphertext = \
        [data for x in (key.size_in_bytes(), 16, 16, -1)]

    # Decrypt the session key with the private RSA key
    cipher_rsa = PKCS1_OAEP.new(key)
    session_key = cipher_rsa.decrypt(enc_session_key)#Compains cipher text is the wrong length

    # Decrypt the data with the AES session key
    cipher_aes = AES.new(session_key, AES.MODE_EAX, nonce)
    data = cipher_aes.decrypt_and_verify(ciphertext, tag)
    return data.decode()

def PasswordEncrypt(password,Name,key,data):
    key = RSA.import_key(key, passphrase=password)

    session_key = get_random_bytes(16)

    # Encrypt the session key with the public RSA key
    cipher_rsa = PKCS1_OAEP.new(key)
    enc_session_key = cipher_rsa.encrypt(session_key)

    # Encrypt the data with the AES session key
    cipher_aes = AES.new(session_key, AES.MODE_EAX)
    ciphertext, tag = cipher_aes.encrypt_and_digest(data.encode())

    file_out = open(DIR+"/UserKeys/"+Name,"wb")
    [file_out.write(x) for x in (enc_session_key, cipher_aes.nonce, tag, ciphertext)]
    file_out.close()
import os
import socket
import random
from threading import Thread
from datetime import datetime
from time import sleep
from colorama import Fore, init
import Modules.TextHandler as text_handler

# init colors
init()

CHUNKSIZE = 1_000_000

# set the available colors
colors = [Fore.BLUE, Fore.CYAN, Fore.GREEN, Fore.LIGHTBLACK_EX,
    Fore.LIGHTBLUE_EX, Fore.LIGHTCYAN_EX, Fore.LIGHTGREEN_EX,
    Fore.LIGHTMAGENTA_EX, Fore.LIGHTRED_EX, Fore.LIGHTWHITE_EX,
    Fore.LIGHTYELLOW_EX, Fore.MAGENTA, Fore.RED, Fore.WHITE, Fore.YELLOW
]

# choose a random color for the client
client_color = random.choice(colors)

# server's IP address
SERVER_HOST = ""
SERVER_PORT = 5002 # server's port
SEPARATOR_TOKEN = "<SEP>" # we will use this to separate the client name & message
PUBKEY = ""
SIGNATURE = "MySignature"

# initialize TCP socket
s = socket.socket()
print(f"[*] Connecting to {SERVER_HOST}:{SERVER_PORT}...")
# connect to the server
s.connect((SERVER_HOST, SERVER_PORT))
print("[+] Connected.")

# functions:
def send(cs, data, pubkey):
    text_handler.encrypt_text(pubkey, data)

    filename = "Message"
    with cs, open(filename, 'rb') as f:
        cs.sendall(filename.encode() + b'\n')
        cs.sendall(f'{os.path.getsize(filename)}'.encode() + b'\n')

        # Send the file in chunks so large files can be handled.
        while True:
            data = f.read(CHUNKSIZE)
            if not data:
                break
            cs.sendall(data)
    os.remove("Message")


def listen_for_messages():#Used to assign a thread
    while True:
        with s, s.makefile('rb') as clientfile:
            filename = clientfile.readline().strip().decode()
            length = int(clientfile.readline())
            print(f'Downloading {filename}:{length}...')
            path = os.path.join(filename)

            # Read the data in chunks so it can handle large files.
            f = open("fileIn", "wb")
            while length:
                chunk = min(length, CHUNKSIZE)
                data = clientfile.read(chunk)
                if not data:
                    break  # socket closed
                f.write(data)
                length -= len(data)
            f.close()

            if length != 0:
                print('Invalid download.')
            else:
                print('Done.')

            return text_handler.password_decrypt("fileIn",password)

def listen_for_message():#Used to get only one message
    while True:
        with s, s.makefile('rb') as clientfile:
            filename = clientfile.readline().strip().decode()
            length = 1
            print(f'Downloading {filename}:{length}...')
            path = os.path.join(filename)

            # Read the data in chunks so it can handle large files.
            with open("fileIn", "wb") as f:
                while length:
                    chunk = min(length, CHUNKSIZE)
                    data = clientfile.read(chunk)
                    if not data:
                        break  # socket closed
                    f.write(data)
                    length -= len(data)
                f.close()

            if length != 0:
                print('Invalid download.')
            else:
                print('Done.')

            return text_handler.password_decrypt("fileIn",password)

def sign_up():
    user_name = input("Enter what you want to be called by: ")
    if user_name.isalpha():
        user_password = input("enter your password (the Longer the better;) : ")
        user_re_password = input("renter your password: ")
        if user_password == user_re_password:
            print("Signing Up!")

            text_handler.password_make_key(user_password)
            pub_key = text_handler.get_pub_key(user_password)

            to_send = "`/#signup#" + user_name + "#" + pub_key
            print(pub_key)
            s.send(to_send.encode())  #send request
            message_response = listen_for_message()
            if message_response == "USERNAME IN USE":
                print("Username already being used")
                sign_up()
            to_send = "`/#login " + "#" + user_name + "#" + sign(SIGNATURE,user_password)
            print("Logging In!")
            s.send(to_send.encode())
            return listen_for_message().split(" ")
        
        print("Passwords don't match!")
        sign_up()
    else:
        print("You can only have letters! try again.")
        sign_up()


# prompt the client for a name
attempt = True
tries = 0

while attempt:#Start login attempts for 5 tries
    print("enter 'sign up' to create account")
    name = input("Enter your name: ")#Ask for info
    if name.lower() == "sign up":
        keys = sign_up()
        attempt = False
    else:
        password = input("Enter your password: ")

        to_send = "`/#login#"+name
        s.send(to_send.encode())#send info with a `/ to tell the machine its a command

        response = listen_for_message()
        print(response)
        response = text_handler.password_decrypt(response,password)

        to_send = "`/#login2#"+name+"#"+response
        s.send(to_send.encode())

        response = listen_for_message()
        if response == "WRONG":
            print("Incorrect Information! Have you made a account")
            tries += 1
            if attempt == 5:
                print("TIMEOUT")
                exit()
        elif response == "SUCCESS":
            attempt = False
            print(response)


# make a thread that listens for messages to this client & print them
t = Thread(target=listen_for_messages)#Give the thread
# make the thread daemon so it ends whenever the main thread ends
t.daemon = True
# start the thread
t.start()

while True:
    sleep(1)
    # input message we want to send to the server
    to_send = input("Message: ")
    # a way to exit the program
    if to_send.lower() == 'x':
        break
    # add the datetime, name & the color of the sender
    date_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    to_send = f"{client_color} {to_send}{Fore.RESET}"
    #Encrypt the message
    encrypted_message = text_handler.encrypt_text(PubKey, to_send)
    # finally, send the message
    s.send(encrypted_message.encode())

# close the socket
s.close()

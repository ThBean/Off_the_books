import os
import socket
import random
from threading import Thread
from datetime import datetime
from colorama import Fore, init
from time import sleep
from TextHandler import *

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
separator_token = "<SEP>" # we will use this to separate the client name & message
PubKey = ""
ServerPub = ""

# initialize TCP socket
s = socket.socket()
print(f"[*] Connecting to {SERVER_HOST}:{SERVER_PORT}...")
# connect to the server
s.connect((SERVER_HOST, SERVER_PORT))
print("[+] Connected.")
password=""

def Send(cs,data,ServerPubKey):
    encryptText(ServerPubKey, data)

    filename = "Message"
    with cs, open(filename, 'rb') as f:
        cs.sendall(filename.encode() + b'\n')
        cs.sendall(f'{os.path.getsize(filename)}'.encode() + b'\n')

        # Send the file in chunks so large files can be handled.
        while True:
            data = f.read(CHUNKSIZE)
            if not data: break
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
                if not data: break  # socket closed
                f.write(data)
                length -= len(data)
            f.close()

            if length != 0:
                print('Invalid download.')
            else:
                print('Done.')

            return PasswordDecrypt("fileIn",password)

def listen_for_message(enc):#Used to get only one message
    if enc:
        while True:
            with s, s.makefile('rb') as clientfile:
                filename = clientfile.readline().strip().decode()
                length = 1
                print(f'Downloading {filename}:{length}...')
                path = os.path.join(filename)

                # Read the data in chunks so it can handle large files.
                f = open("fileIn", "wb")
                while length:
                    chunk = min(length, CHUNKSIZE)
                    data = clientfile.read(chunk)
                    if not data: break  # socket closed
                    f.write(data)
                    length -= len(data)
                f.close()

                if length != 0:
                    print('Invalid download.')
                else:
                    print('Done.')

                return PasswordDecrypt("fileIn",password)
    else:
            while True:
                return s.recv(1024).decode()

def SignUp():
    Name = input("Enter what you want to be called by: ")
    if Name.isalpha():
        Password = input("enter your password (the Longer the better;) : ")
        RePassword = input("renter your password: ")
        if Password == RePassword:
            print("Signing Up!")

            PasswordMakeKey(Password)
            PubKey = GetPubKey(Password)

            to_send = "`/#signup#" + Name + "#" + PubKey
            print(PubKey)
            s.send(to_send.encode())  #send request
            response = listen_for_message().decode()
            if response == "USERNAME IN USE":
                print("Username already being used")
                SignUp()
            to_send = "`/#login " + "#" + Name + "#" + Sign(signiture,Password)
            print("Logging In!")
            s.send(to_send.encode())
            return listen_for_message().decode().split(" ")
        else:
            print("Passwords dont match!")
            SignUp()
    else:
        print("you can only have letters! try again.")
        SignUp()

Attempt = True
tries = 0

print("GETTING SERVER KEY...")
to_send = "`/get"
s.send(to_send.encode())  # send info with a `/ to tell the machine its a command done in plain text since i dont have the PubKey
ServerPub = listen_for_message(False)

while Attempt:#Start login attempts for 5 tries
    print("enter 'sign up' to create account")
    name = input("Enter your name: ")#Ask for info
    if name.lower() == "sign up":
        keys = SignUp()
        Attempt = False
    else:
        password = input("Enter your password: ")
        PubKey = GetPubKey(password)

        print("GETTING SESSION ID...")
        to_send = "`/#login#"+name
        Send(s,to_send,ServerPub)  # send info with a `/ to tell the machine its a command done in plain text since i dont have the PubKey
        response = listen_for_message(True)
        print(response)

        response = PasswordDecrypt(response,password)#decrypt with our key

        to_send = "`/#login2#"+name+"#"+response#send back session id to prove who we be
        s.send(to_send.encode())

        response = listen_for_message(True).decode()
        if response == "WRONG":
            print("Incorrect Information! Have you made a account")
            tries += 1
            if Attempt == 5:
                print("TIMEOUT")
                exit()
        elif response == "SUCCESS":
            Attempt = False
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
    to_send =  input("Message: ")
    # a way to exit the program
    if to_send.lower() == 'x':
        break
    # add the datetime, name & the color of the sender
    date_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
    to_send = f"{client_color} {to_send}{Fore.RESET}"
    #Encrypt the message
    to_send = encryptText(PubKey,to_send)
    # finally, send the message
    s.send(to_send.encode())

# close the socket
s.close()
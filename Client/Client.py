import socket
import random
from threading import Thread
from datetime import datetime
from colorama import Fore, init
from time import sleep
from TextHandler import *

# init colors
init()

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
signiture = "MySignature"

# initialize TCP socket
s = socket.socket()
print(f"[*] Connecting to {SERVER_HOST}:{SERVER_PORT}...")
# connect to the server
s.connect((SERVER_HOST, SERVER_PORT))
print("[+] Connected.")
# prompt the client for a name

def listen_for_messages():#Used to assign a thread
    while True:
        message = s.recv(1024).decode()
        print("\n"+message)

def listen_for_message():#Used to get only one message
    while True:
        message = s.recv(1024)
        return message

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

while Attempt:#Start login attempts for 5 tries
    print("enter 'sign up' to create account")
    name = input("Enter your name: ")#Ask for info
    if name.lower() == "sign up":
        keys = SignUp()
        Attempt = False
    else:
        password = input("Enter your password: ")

        to_send = "`/#login#"+name
        s.send(to_send.encode())#send info with a `/ to tell the machine its a command

        response = listen_for_message()
        print(response)
        response = PasswordDecrypt(response,password)

        to_send = "`/#login2#"+name+"#"+response
        s.send(to_send.encode())

        response = listen_for_message().decode()
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
UIenabled = True  # in case you're a terminal enjoyed just change to 'False'

import socket
from threading import Thread, Event

if UIenabled:
    from tkinter import messagebox

from TextHandler import *

CHUNKSIZE = 1_000_000
#VARIABLES
ServerMessages = []
UnreadMessages = []

SvrMessage = Event()

# server's IP address
SERVER_HOST = ""
SERVER_PORT = 5002  # server's port
separator_token = "<SEP>"  # we will use this to separate the client name & message
PubKey = ""

# initialize TCP socket
s = socket.socket()
print(f"[*] Connecting to {SERVER_HOST}:{SERVER_PORT}...")
# connect to the server
try:
    s.connect((SERVER_HOST, SERVER_PORT))
except ConnectionRefusedError:
    print('The Server seems down right now?\nCheck that:\n1) ' + SERVER_HOST + 'Is the correct Host Address\n'
                                                                               '2) The Server is running')
    exit(404)
print("[+] Connected.")
password = ""

global SessionID


def receive_file(sck: socket.socket, Passphrase):
    print("Receiving...")
    l = sck.recv(1024).decode()
    if l == '`/#get' or l == 'WRONG':
        return l
    else:
        f = open('fileIn', 'wb')

        recursions = int(l) / CHUNKSIZE
        if recursions < 1: recursions = 1

        for x in range(0, recursions):
            print("Receiving...")
            l = sck.recv(1024)
            f.write(l)
        f.close()
        print("Done Receiving")
        return PasswordDecrypt('fileIn', Passphrase)


def Send(cs, data, Key):
    encryptText(Key, data)

    f = open('Message', 'rb')
    size = os.path.getsize('Message')
    cs.send(str(size).encode())

    recursions = size / CHUNKSIZE
    if recursions < 1: recursions = 1

    for x in range(0, recursions):  # loop through the number of time to send the data
        print('Sending...')
        l = f.read(CHUNKSIZE)
        cs.send(l)

    os.remove('Message')
    print('Done Sending')


def listen_for_messages(sck, Passphrase) -> str:  # Used to assign a thread
    print("Receiving...")
    l = sck.recv(1024).decode()
    if l == '`/#get' or l == 'WRONG':
        return l
    else:
        f = open('fileIn', 'wb')

        recursions = int(l) / CHUNKSIZE
        if recursions < 1: recursions = 1

        for x in range(0, recursions):
            print("Receiving...")
            l = sck.recv(1024)
            f.write(l)
        f.close()
        print("Done Receiving")
        msg =  PasswordDecrypt('fileIn', Passphrase)
        msgS = msg.split('#')
        if msgS[1] == 'message':
            if UIenabled:
                messagebox.showinfo("New Message!", "New message from:\n"+msgS[2])
            else:
                print('New Message From: '+msgS[2])
            yield [msgS[2], msgS[3]]  # print Name

        elif msgS[1] == 'key':  # a friendly user key!
            ServerMessages.append(msgS[2]) # append the key
            SvrMessage.set()



def Log_In(UserName, passphrase, Key):
    print("GETTING SESSION ID...")

    Send(s, "`/#login#" + UserName,
         Key)  # send info with a `/ to tell the machine it's a command done in plain text since I don't have the PubKey

    SessionID = receive_file(s, passphrase)
    if SessionID == 'WRONG': return False
    # send back session id to prove who we be
    Send(s, "`/#login2#" + UserName + "#" + SessionID, Key)

    response = receive_file(s, passphrase)
    if response == "WRONG":
        print("Incorrect Information! Have you made a account?")
        return False
    elif response == "SUCCESS":
        print(response)
        return SessionID


def SignUp():
    Name = input("Enter what you want to be called by: ")

    if Name.isalpha() and not '#' in Name:  # no Hashtags please! # Psst pen-testers it won't actually do anything!
        Password = input("enter your password (the Longer the better;) : ")
        RePassword = input("renter your password: ")
        if Password == RePassword:
            print("Signing Up!")

            PasswordMakeKey(Password)
            PublicKey = GetPubKey(Password)

            Send(s, "`/#signup#" + Name + "#" + PublicKey, ServerPub)  # Send Request

            response = receive_file(s, Password)
            if response == "USERNAME IN USE":
                print("Username already being used")
                return SignUp()
            else:
                return Name, Password
        else:
            print("Passwords dont match!")
            return SignUp()
    else:
        print("you can only have letters! try again.")
        return SignUp()


tries = 0

print("GETTING SERVER KEY...")
to_send = "`/#get"

try:  # see if server is up or not
    s.send(to_send.encode())  # send info with a `/ to tell the machine it's a command done in plain text since I don't
    # have the PubKey RFI (could store it)
except BrokenPipeError:
    print('The Server seems down right now?\nCheck that:\n1) ' + SERVER_HOST + 'Is the correct Host Address\n'
                                                                               '2) The Server is running')
    exit(404)

ServerPub = s.recv(1024)

while True:  # Start login attempts for 5 tries
    print("enter 'sign up' to create account")
    name = input("Enter your name: ")  # Ask for info

    if name.lower() == "sign up":
        name, password = SignUp()
        Log_In(name, password, ServerPub)
        break

    password = input("Enter your password: ")

    if CheckPassword(password):
        SessionID = Log_In(name, password, ServerPub)
        if SessionID:
            break
        else:
            print('Incorrect Username')
    else:
        print('Incorrect Password')

    if tries == 4:  # lockout function
        exit(401)
    else:
        tries += 1

# make a thread that listens for messages to this client & print them
t = Thread(target=listen_for_messages, args=(s, password))  # Give the thread
# make the thread daemon, so it ends whenever the main thread ends
t.daemon = True
# start the thread
UnreadMessages.append(t.start())


def SendMessage(s, Msg, ServerPub, name, SessionID, UsrKey):  # todo optimize
    # make a message to the server saying who it is we are sending a message too
    encryptText(UsrKey, Msg)  # encrypt data to User

    f = open('Message', 'rb')
    Emsg = f.read()
    f.close()
    Usize = os.path.getsize('Message')  # get size of the message
    # this how i tell the Server what this all means

    encryptText(ServerPub, name+' '+SessionID)  # encrypt the info for the server

    Ssize = os.path.getsize('Message')

    to_send = '`/msg#'+str(Ssize)+'#'+str(Usize)
    s.send(to_send.encode())

    f = open('Message', 'ab')  # append bytes mode
    f.write(Emsg)  # write the message data
    f.close()

    recursions = Ssize+Usize / CHUNKSIZE
    if recursions < 1: recursions = 1

    for x in range(0, recursions):  # loop through the number of time to send the data
        print('Sending...')
        l = f.read(CHUNKSIZE)
        s.send(l)

    os.remove('Message')
    print('Done Sending')


while True:
    try:  # try block
        os.system('clear')  # clear screen
        # Main Menu
        print('''
        1. Start a chat
        2. Open a chat
        3. Start a group
        4. Change password
        5. Delete account
        ''')
        choice = input()

        if choice == '1':
            name = input('Enter the users name:\n')

            Send(s, '`/#start#' + name + '#' + SessionID, ServerPub)  # Only if we dont already have it # todo make userdata
            SvrMessage.wait(timeout=10)

            run = True
            while run:  # wait for target pubkey
                Msg = input('Enter message ("#" to exit): \n')

                UsrKey = ServerMessages[0]
                ServerMessages.pop(0)

                SendMessage(s, Msg, ServerPub, name, SessionID, UsrKey)

                



    except:
        print('ERROR:\n    Press enter to return...')
        input()

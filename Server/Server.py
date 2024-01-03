import random
import socket
from threading import Thread

from TextHandler import *
from UserHandler import *

# todo encrypt login and signup
CHUNKSIZE = 1_000_000
PubKey = GetPubKey()


def Send(Socket, data, Key=''):
    if Key != '':  # if its encrypted
        encryptText(Key, data)

        ff = open('Message', 'rb')
        size = os.path.getsize('Message')
        Socket.send(str(size).encode())

        recursions = size / CHUNKSIZE
        if recursions < 1: recursions = 1

        b''
        for x in range(0, recursions):  # loop through the number of time to send the data
            print('Sending...')
            l = ff.read(CHUNKSIZE)
            Socket.send(l)
        os.remove('Message')
    else:  # RFI
        Socket.send(data.encode())


# server's IP address
SERVER_HOST = ""  # Using local
SERVER_PORT = 5002  # port we want to use
separator_token = "<SEP>"  # we will use this to separate the client name & message
DIR = os.path.dirname(os.path.realpath(__file__))

# initialize list/set of all connected client's sockets
client_sockets = set()
# create a TCP socket
s = socket.socket()
# make the port as reusable port
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# bind the socket to the address we specified
s.bind((SERVER_HOST, SERVER_PORT))
# listen for upcoming connections
s.listen(4)  # can only have 4 users at a time


def receive_file(sck: socket.socket):
    print("Receiving...")
    l = sck.recv(1024).decode()
    if l == '`/#get':
        return l
    elif l.split('#')[0] == '`/msg':  # a message to another user
        l = l.split('#')

        Ssize = int(l[1])
        Usize = int(l[2])

        fff = open('fileIn', 'wb')

        recursions = int(l[Ssize]) / CHUNKSIZE
        if recursions < 1: recursions = 1

        for x in range(0, recursions):
            print("Receiving...")
            l = sck.recv(1024)
            fff.write(l)
        fff.close()
        print("Done Receiving")

        fff = open('fileIn', 'rb')

        ffff = open('ServerMsg','wb')
        ffff.write(fff.read(Ssize))  # read the bytes for the server and decrypt
        ffff.close()
        info = decryptText('ServerMsg').split(' ')  # this will tell us who to send it to as well as the token


    else:
        fff = open('fileIn', 'wb')

        recursions = int(l) / CHUNKSIZE
        if recursions < 1: recursions = 1

        for x in range(0, recursions):
            print("Receiving...")
            l = sck.recv(1024)
            fff.write(l)
        fff.close()
        print("Done Receiving")
        return decryptText('fileIn')


OnlineClients = {}  # {'SessionID': [Username]} for the server management and checking that they are a logged-in user
LoggingClients = {}


def get_Users():
    ffff = open(DIR + "/Users", "r")  # open the file
    Users = ast.literal_eval(ffff.read())  # FORMAT IS Users = [Username]
    ffff.close()
    return Users


print(f"[*] Listening as {SERVER_HOST}:{SERVER_PORT}")


def listen_for_client(Socket):
    """
    This function keep listening for a message from `cs` socket
    Whenever a message is received, broadcast it to the other client
    """
    SessionID = ''
    while True:
            msg = receive_file(Socket)
        #try:  # try block
            print(msg)

            if msg.split("#")[0] == "`/":  # if command word
                msg = msg.split("#")  # msg = ["command","type", "Name"]
                if msg[1] == 'get':
                    print("Sending Pubkey")
                    Send(Socket, PubKey)

                elif msg[1] == "login":  # if command is login
                    fr = get_Users()
                    if msg[2] in Users.keys():  # if they are a user
                        LoggingClients[msg[2]] = str(random.randint(0, 9999999999999999999999999999999999))

                        Send(Socket, LoggingClients[msg[2]], fr[msg[2]])  # send random numbers

                    else:
                        Socket.send('WRONG'.encode())  # todo only allow 5 tries before blacklist

                elif msg[1] == "login2":
                    if msg[2] in LoggingClients.keys():
                        fr = get_Users()
                        if msg[3] == LoggingClients[msg[2]]:
                            SessionID = msg[3]  # update SessionID

                            Send(Socket, 'SUCCESS', fr[msg[2]])
                            print(msg[2] + ' Has logged in!')
                            LoggingClients.pop(msg[2])
                            OnlineClients[msg[3]] = msg[2]  # add SessionID
                        else:
                            Send(Socket, 'Nice try loser', fr[msg[2]])

                elif msg[1] == "signup":  # if command is addUser
                    if not '#' in msg[1]:  # no hashtags
                        if AddUser(msg[2], msg[3]):  # name pubkey
                            Send(Socket, 'SIGNED UP', msg[3])
                        else:
                            Send(Socket, 'USERNAME IN USE', msg[3])

                elif msg[1] == "start":  # command is to start a new conversation
                    if msg[3] in OnlineClients.keys():  # check session ID
                        fr = get_Users()
                        if msg[2] in fr.keys():  # check the user exists
                            Send(Socket, fr[msg[2]], Users[msg[3]])  # send targets pubkey
                        else:
                            Send(Socket, '404', Users[msg[3]])  # Tell them it doesn't exist
                    else:
                        cs.close()  # probably a hacker! # todo block that fucker


            '''except Exception as e:
                # client no longer connected
                # remove it from the set
                print(f"[!] Error: {e}")
                if msg == b'':
                    client_sockets.remove(Socket)
                    OnlineClients.pop(SessionID)'''


while True:
    # we keep listening for new connections all the time
    client_socket, client_address = s.accept()
    print(f"[+] {client_address} connected.")
    # add the new connected client to connected sockets
    client_sockets.add(client_socket)

    # start a new thread that listens for each client's messages
    t = Thread(target=listen_for_client, args=(client_socket,))
    # make the thread daemon, so it ends whenever the main thread ends
    t.daemon = True
    # start the thread
    t.start()

# close client sockets
for cs in client_sockets:
    cs.close()
# close server socket
s.close()

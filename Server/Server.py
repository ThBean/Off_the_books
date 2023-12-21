import socket
from threading import Thread
from TextHandler import *
from UserHandler import *

#todo encrypt login and signup
CHUNKSIZE = 1_000_000
PubKey = GetPubKey()

def Send(cs,data,PubKey=''):
    if PubKey != '':#if its enrypted
        encryptText(PubKey, data)

        f = open('Message', 'rb')
        size = os.path.getsize('Message')
        cs.send(str(size).encode())
        print(size)

        recursions = size / CHUNKSIZE
        if recursions < 1: recursions = 1

        l = b''
        for x in range(0, recursions):  # loop through the number of time to send the data
            print('Sending...')
            l = f.read(CHUNKSIZE)
            print(l)
            cs.send(l)
    else:#RFI
        cs.send(data.encode())


# server's IP address
SERVER_HOST = ""#Using local
SERVER_PORT = 5002 # port we want to use
separator_token = "<SEP>" # we will use this to separate the client name & message
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
s.listen(4)#can only have 4 users at a time

def receive_file(sck: socket.socket):

    print("Receiving...")
    l = sck.recv(1024).decode()
    if l == '`/#get':
            return l
    else:
        f = open('fileIn', 'wb')

        recursions = int(l) / CHUNKSIZE
        if recursions < 1: recursions = 1

        for x in range(0,recursions):
            print("Receiving...")
            l = sck.recv(1024)
            f.write(l)
        f.close()
        print("Done Receiving")
        return decryptText('fileIn')



OnlineClients = []#[["username","IP"]]
LoggingClients = {}

f = open(DIR+"/Users","r")#open the file
Users = ast.literal_eval(f.read())# FORMAT IS Users = [Username]
f.close()


print(f"[*] Listening as {SERVER_HOST}:{SERVER_PORT}")

def listen_for_client(cs):
    """
    This function keep listening for a message from `cs` socket
    Whenever a message is received, broadcast it to the other client
    """
    while True:
            msg=receive_file(cs)
            try:#try block
                print(msg)

                if msg.split("#")[0] == "`/":#if command word
                        msg = msg.split("#")# msg = ["command","type", "Name"]
                        if msg[1] == 'get':
                            print("Sending Pubkey")
                            Send(cs, PubKey)
                        elif msg[1] == "login":#if command is login
                            if msg[2] in Users.keys():
                                LoggingClients[msg[2]]=str(random.randint(0,999999))
                                f=open("Users","r")
                                fr=ast.literal_eval(f.read())
                                f.close()

                                Send(cs,LoggingClients[msg[2]],fr[msg[2]])#send random numbers

                            else:
                                Send(cs,PubKey,"WRONG".encode())#todo only allow 5 tries before blacklist

                        elif msg[1] == "login2":
                            if msg[2] in LoggingClients.keys():
                                if msg[3] == LoggingClients[msg[2]]:
                                    Send(cs,b'SUCCESS',PubKey)
                                else:
                                    Send(cs,b'Nice try glowie',PubKey)

                        elif msg[1] == "signup":#if command is addUser
                            if AddUser(msg[2],msg[3]):#name pubkey
                                Send(cs,b'SIGNED UP',PubKey)
                            else:
                                Send(cs,b'USERNAME IN USE',PubKey)

            except Exception as e:
                # client no longer connected
                # remove it from the set
                print(f"[!] Error: {e}")
                if msg.strip() == '':
                    client_sockets.remove(cs)


while True:
    # we keep listening for new connections all the time
    client_socket, client_address = s.accept()
    print(f"[+] {client_address} connected.")
    # add the new connected client to connected sockets
    client_sockets.add(client_socket)

    # start a new thread that listens for each client's messages
    t = Thread(target=listen_for_client, args=(client_socket,))
    # make the thread daemon so it ends whenever the main thread ends
    t.daemon = True
    # start the thread
    t.start()

# close client sockets
for cs in client_sockets:
    cs.close()
# close server socket
s.close()
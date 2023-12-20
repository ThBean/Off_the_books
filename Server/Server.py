import random
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

        filename = "Message"
        with cs, open(filename, 'rb') as f:
            # Send the file in chunks so large files can be handled.
            while True:
                data = f.read(CHUNKSIZE)
                if not data: break
                cs.sendall(data)
        os.remove("Message")

    else:
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
        msg=""

        try:#check for file or not
            msg = cs.recv(1024)
            if msg.decode()=="`/get":
                print("Sending Pubkey")
                Send(cs,PubKey)
        except UnicodeError:
            print("FILE INCOMING")
            try:#try block
                # keep listening for a message from `cs` socket
                with cs, cs.makefile('rb') as clientfile:
                    filename = clientfile.readline().strip()
                    #length = int(clientfile.readline())
                    print(f'Downloading {filename}...')
                    path = os.path.join(filename)

                    # Read the data in chunks so it can handle large files.
                    f = open("fileIn","wb")
                    while True:
                            data = clientfile.read(CHUNKSIZE)
                            print(data)
                            if not data or data==b'': break  # socket closed
                            f.write(data)
                    f.close()

                    print('Done.')

                    msg = decryptText("fileIn")
                    print(msg)


                if msg.split("#")[0] == "`/" and msg != "`/get":#if command word
                        print("Command Detected")
                        msg = msg.split("#")# msg = ["command","type", "Name"]
                        if msg[1] == "login":#if command is login
                            if msg[2] in Users.keys():
                                LoggingClients[msg[2]]=str(random.randint(0,999999))
                                f=open("Users","r")
                                fr=ast.literal_eval(f.read())
                                f.close()

                                Send(cs,Users[msg[2]],LoggingClients[msg[2]])#send random numbers

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
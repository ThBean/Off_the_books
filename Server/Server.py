import random
import socket
from threading import Thread
from TextHandler import *
from UserHandler import *

#todo encrypt login and signup

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
s.listen(5)


OnlineClients = []#[["username","IP"]]
LoggingClients = {}

f = open(DIR+"/Users","r")#open the file
Users = ast.literal_eval(f.read())# FORMAT IS Users = [Username]
f.close()


print(f"[*] Listening as {SERVER_HOST}:{SERVER_PORT}")

def listen_for_client(cs):#todo make it assign a thread while executing
    """
    This function keep listening for a message from `cs` socket
    Whenever a message is received, broadcast it to the other client
    """
    while True:
        try:
            # keep listening for a message from `cs` socket
            msg = cs.recv(1024).decode()
        except Exception as e:
            # client no longer connected
            # remove it from the set
            print(f"[!] Error: {e}")
            client_sockets.remove(cs)
        if msg.split("#")[0] == "`/":#if command word
                print("Command Detected")
                msg = msg.split("#")# msg = ["command","type", "Name"]
                if msg[1] == "login":#if command is login
                    if msg[2] in Users.keys():
                        LoggingClients[msg[2]]=str(random.randint(0,999999))
                        f=open("Users","r")
                        fr=ast.literal_eval(f.read())
                        f.close()
                        cs.send(encryptText(Users[msg[2]],LoggingClients[msg[2]]))#send them a encrypted version of the numbers
                    else:
                        cs.send("WRONG".encode())#todo only allow 5 tries before blacklist

                elif msg[1] == "login2":
                    if msg[2] in LoggingClients.keys():
                        if msg[3] == LoggingClients[msg[2]]:
                            cs.send(b'SUCCESS')
                        else:
                            cs.send(b'Nice try glowie')

                elif msg[1] == "signup":#if command is addUser
                    if AddUser(msg[2],msg[3]):#name pubkey
                        cs.send(b'SIGNED UP')
                    else:
                        cs.send(b'USERNAME IN USE')
        else:
                # if we received a message, replace the <SEP>
                # token with ": " for nice printing
                msg = msg.replace(separator_token, ": ")
                # iterate over all connected sockets
                print(msg)
                for client_socket in client_sockets:
                    # and send the message
                    client_socket.send(msg.encode())


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
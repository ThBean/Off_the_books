import os
import ast
import random
import socket
from threading import Thread
import Modules.TextHandler as text_handler
import Modules.UserHandler as user_handler

#todo encrypt login and signup
CHUNKSIZE = 1_000_000
def send(cs, data, pub_key):
    text_handler.encrypt_text(pub_key, data)

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


# server's IP address
SERVER_HOST = ""#Using local
SERVER_PORT = 5002 # port we want to use
SEPARATOR_TOKEN = "<SEP>" # we will use this to separate the client name & message
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

with open(f"{DIR}/Users","r") as f:   #open the file
    Users = ast.literal_eval(f.read())  # FORMAT IS Users = [Username]
    f.close()


print(f"[*] Listening as {SERVER_HOST}:{SERVER_PORT}")

def listen_for_client(cs):#todo make it assign a thread while executing
    """
    This function keep listening for a message from `cs` socket
    Whenever a message is received, broadcast it to the other client
    """
    while True:
        msg = ""
        try:
            # keep listening for a message from `cs` socket
            with cs, cs.makefile('rb') as clientfile:
                filename = clientfile.readline().strip().decode()
                length = int(clientfile.readline())
                print(f'Downloading {filename}:{length}...')
                path = os.path.join(filename)

                # Read the data in chunks so it can handle large files.
                with open("fileIn","wb") as f:
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

                msg = text_handler.decrypt_text("fileIn")

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
                        with open("Users","r") as f:
                            fr=ast.literal_eval(f.read())
                            f.close()

                        send(cs,LoggingClients[msg[2]],Users[msg[2]])#send random numbers

                    else:
                        cs.send("WRONG".encode())#todo only allow 5 tries before blacklist

                elif msg[1] == "login2":
                    if msg[2] in LoggingClients.keys():
                        if msg[3] == LoggingClients[msg[2]]:
                            cs.send(b'SUCCESS')
                        else:
                            cs.send(b'Nice try glowie')

                elif msg[1] == "signup":#if command is addUser
                    if user_handler.add_user(msg[2],msg[3]):#name pub_key
                        cs.send(b'SIGNED UP')
                    else:
                        cs.send(b'USERNAME IN USE')
        else:
                # if we received a message, replace the <SEP>
                # token with ": " for nice printing
                msg = msg.replace(SEPARATOR_TOKEN, ": ")
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

# Code unreachable!!!!

# close client sockets
for cs in client_sockets:
    cs.close()
# close server socket
s.close()

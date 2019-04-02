import socket
import threading

# Specs definition:
# ----------------
# item_type - can be either food, trap or training center
# 
# 
# ----------------


#constants definition
NULL = ''
TYPE = 0

#socket communication parameters
bind_ip = '127.0.0.1'
bind_port = 9993
MSG_SIZE = 1024

#possible messages
LOG = 'LOGIN'
PLACE_FOOD = 'PLACEF'
PLACE_TRAP = 'PLACET'
PLACE_CENTER = 'PLACEC'
SHOW_LOC = 'SHOW_LOCATION'
ATT = 'ATTACK'
EAT = 'EAT'
PRACT = 'PRACTICE'
TRP = 'TRAP'
KILL = 'KILL_SERVER' #for testing purposes

messages = [LOG, PLACE_FOOD, PLACE_TRAP, PLACE_CENTER, SHOW_LOC, ATT, EAT, PRACT, TRP]

#return codes
OK          = 'OK: '
NOT_OK      = 'NOK: '

#return sub-codes
LOG_OK      = 'login successful'
PLACE_OK = ' placed successfully'
LOCATION_OK = 'location has'
ATT_OK = 'attacked successfully'
EAT_OK = 'ate successfully'
PRACT_OK = 'practiced successfully'
TRAP_OK = 'trapped'

TRAP_NOK = 'cannot be trapped'
LOG_NOK  = 'failed to login'
LOCATION_NOK = 'location empty'
PLACE_NOK = 'unable to place'
ATT_NOK = 'attack failed'
EAT_NOK = 'cannot eat'
PRACT_NOK = 'cannot practice'
INV_MSG     = 'invalid message type'

#sockets initiation
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((bind_ip, bind_port))
server.listen(5)  # max backlog of connections

#generic functions

def handle_client_connection(client_socket):
    msg_from_client = client_socket.recv(1024)
    request = msg_from_client.decode()
    print('Received {}'.format(request))
    msg_to_client = 'ACK'.encode()
    print(msg_to_client)
    client_socket.send(msg_to_client)
    client_socket.close()

def find_client (addr, active_users):
    for key, val in list(active_users.items()):
        if val == addr:
            return key
    return NULL

def location_empty(player_name ): # receives player and returns true or false if location empty or not
    pass

#message handling functions

def login_client(msg_request, addr, active_users):
    pass

def place_item(addr, active_users, item_type):
    if (item_type == 1):
        #place food
        pass
    elif (item_type == 2):
        #place trap
        pass
    elif (item_type == 3):
        #place training center
        pass


def show_location(msg_request, addr, active_users): #receives player name, finds player name, returns everything on player location.
    pass

def attack_client(msg_request): # receives attacking player and attacked player
  pass

def client_eat(): # receives player , sees player position and tries to eat if location not empty
    pass


def client_practice():  # receives player , sees player position and tries to train if location not empty
    pass


def client_trap():  # receives player , sees player position and tries to trap him if location not empty
    pass

#main code

active_users = {} #dict: key: user_name; val:user_address info: example:'maria'= ('127.0.0.1',17234)

while True:
    client_sock, address = server.accept()
    print('Accepted connection from {}:{}'.format(address[0], address[1]))
    client_handler = threading.Thread(
        target=handle_client_connection,
        # without comma you'd get a... TypeError: handle_client_connection() argument after * must be a sequence, not _socketobject
        args=(client_sock,)
    )
    client_handler.start()

server_sock.close()

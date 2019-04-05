import socket
import threading
import random

#constants definition
NULL = ''
COMMAND = 0
FOOD = 1
TRAP = 2
CENTER = 3
IP = 0 # for identifying the ip address in vector address
PORT = 1  # for identifying the port in vector address

#socket communication parameters
bind_ip = '127.0.0.1'
bind_port = 12345
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
KILL = 'LOGOUT' #for testing purposes

messages = [LOG, PLACE_FOOD, PLACE_TRAP, PLACE_CENTER, SHOW_LOC, ATT, EAT, PRACT, TRP]

#return codes
OK          = 'OK: '
NOK      = 'NOK: '

#return sub-codes
LOG_OK      = 'login successful'
PLACE_OK = ' placed successfully'
LOCATION_OK = 'location has' #specifies what location has
ATT_OK = 'attacked successfully' # specifies life and attributes of each player
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
def handle_client_connection(client_socket, address): # place in while
    logged = 0
    while True:
        msg_from_client = client_socket.recv(MSG_SIZE)
        request = msg_from_client.decode()
        
        print('Received {} from {} , {}'.format(request, address[IP], address[PORT]))
       
        message = parse_message(request)
        
        if (len(message) == 1 and message[COMMAND] == LOG):
            if (logged == 0):
                logged = 1
                msg_to_client = OK + LOG_OK
            if (logged == 1):
                msg_to_client = NOK + LOG_NOK

        else:
            msg_to_client = execute_command(message)
           
        if (msg_to_client == KILL):
            break

        client_socket.send(msg_to_client.encode())

    # end of connection
    client_socket.close()
    active_users.remove(client_socket)

def parse_message(input_message):
    print (input_message.split(":"))
    return input_message.split(":") # Splits input message by its separation punctuation (:)

#function that 
def execute_command(message):
    if (message[COMMAND] in messages):  # if invalid command, no need to continue

        if (message[COMMAND] == PLACE_FOOD and len(message) == 1):
            msg_to_client = place_item(FOOD)  # type 1 is food

        elif (message[COMMAND] == PLACE_TRAP and len(message) == 1):
            msg_to_client = place_item(TRAP)  # type 1 is trap

        elif (message[COMMAND] == PLACE_CENTER and len(message) == 1):
            # type 1 is training center
            msg_to_client = place_item(CENTER)

        # receives command and player name
        elif (message[COMMAND] == SHOW_LOC and len(message) == 2):
            # message[1] : player_name
            msg_to_client = show_location(message[1])

        elif (message[COMMAND] == ATT and len(message) == 3):
            # message[1] : attacker_name / message[2] : attacked_name
            msg_to_client = attack_client(message[1], message[2])

        elif (message[COMMAND] == EAT):  # receives command and player name
            msg_to_client = client_eat(message[1])

        elif (message[COMMAND] == PRACT):  # receives command and player name
            msg_to_client = client_practice(message[1])

        elif (message[COMMAND] == TRP):  # receives command and player name
            msg_to_client = client_trap(message[1])

        elif (message[COMMAND] == KILL):
            return KILL
        else:
            msg_to_client = NOK + INV_MSG
    else:
        msg_to_client = NOK + INV_MSG

    return msg_to_client

#message handling functions
def place_item(item_type):
    if (item_type == FOOD):
        #place food
        return "food ok"
    elif (item_type == TRAP):
        #place trap
        return "trap ok"
    elif (item_type == CENTER):
        #place training center
        return "center ok"
    else:
        return ""


def show_location(player_name): #receives player name, finds player name, returns everything on player location.
    return "location ok"


def attack_client(attacker, attacked):  # receives attacking player and attacked player
    return "attack ok"


# receives player , sees player position and tries to eat if location not empty
def client_eat(player_name):
    return "eat ok"


# receives player , sees player position and tries to train if location not empty
def client_practice(player_name):
    return "practice ok"


# receives player , sees player position and tries to trap him if location not empty
def client_trap(player_name):
    return "trap ok"

#main code

active_users = []

while True:
    client_sock, address = server.accept()
    active_users.append(client_sock)
    print('Accepted connection from {}:{}'.format(address[IP], address[PORT]))
    client_handler = threading.Thread(
        target=handle_client_connection,
        # without comma you'd get a... TypeError: handle_client_connection() argument after * must be a sequence, not _socketobject
        args=(client_sock, address, )
    )
    client_handler.start()

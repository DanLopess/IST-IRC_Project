import socket
import threading
import random
import fileinput
from server_module import *

# **************************************************************************************
#
#                             IRC PROJECT - SERVER
#                             AUTHOR - DANIEL LOPES
#
#           NOTE: ALL DEFINITIONS AND MESSAGES TYPES ARE IN SERVER_MODULE (import)
#
# Project source files: server.py, client.py, server_modules.py, map.save, players.save
# **************************************************************************************

#sockets initiation
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# the SO_REUSEADDR flag reuses a local socket in TIME_WAIT state, without waiting for its natural timeout to expire.
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((bind_ip, bind_port))
server.listen(5)  # max backlog of connections

# ******************** generic functions ********************

def handle_client_connection(client_socket, address): # place in while
    logged = 0 # variable to check if client has already logged in
    while True:
        msg_from_client = client_socket.recv(MSG_SIZE)
        request = msg_from_client.decode()
        
        print('Received {} from {} , {}'.format(request, address[IP], address[PORT]))
       
        # Splits input message by its separation punctuation (:)
        message = request.split(":")
        
        if (len(message) == 1 and message[COMMAND] == LOG):
            if (logged == 0):
                logged = 1
                msg_to_client = OK + LOG_OK
            elif (logged == 1):
                msg_to_client = NOK + LOG_NOK
        else:
            msg_to_client = execute_command(message)
           
        if (msg_to_client == KILL):
            client_socket.send(msg_to_client.encode())
            break

        client_socket.send(msg_to_client.encode())

    # end of connection
    client_socket.close()
    active_users.remove(client_socket)

def find_data (filename, data):
    #data can be either player_name or coordinates, filename is either map or players
    #this function returns the correspondent lines of either a specific coordinate or player
    with open(filename, "r") as f:
        for line in f:
            found_data = line.find(str(data))
            if (found_data != -1):
                 return line
    return ""

def replace_data (filename, oldline, newline):
    # replaces data in a given file
    with fileinput.FileInput(filename, inplace=True, backup='.bak') as file: 
        for line in file:
            print(line.replace(oldline, newline), end='')

def execute_command(message):
    #function that executes all actions based on command input
    if (message[COMMAND] in messages):  # if invalid command, no need to continue
        
        if (message[COMMAND] == PLACE_FOOD and len(message) == 1):
            msg_to_client = place_item(FOO)  # type 1 is food

        elif (message[COMMAND] == PLACE_TRAP and len(message) == 1):
            msg_to_client = place_item(TRP)  # type 1 is trap

        elif (message[COMMAND] == PLACE_CENTER and len(message) == 1):
            # type 1 is training center
            msg_to_client = place_item(CTR)

        # receives command and player name
        elif (message[COMMAND] == SHOW_LOC and len(message) == 2):
            # message[PLAYER_NAME] : player_name
            msg_to_client = show_location(message[PLAYERS])

        elif (message[COMMAND] == ATT and len(message) == 3):
            # message[PLAYERS] : attacker_name / message[PLAYERS+1] : attacked_name
            msg_to_client = attack_player(message[PLAYERS], message[PLAYERS+1])

        elif (message[COMMAND] == EAT):  # receives command and player name
            msg_to_client = player_eat(message[PLAYERS])

        elif (message[COMMAND] == PRACT):  # receives command and player name
            msg_to_client = player_practice(message[PLAYERS])

        elif (message[COMMAND] == TRP):  # receives command and player name
            msg_to_client = player_trap(message[PLAYERS])

        elif (message[COMMAND] == KILL):
            msg_to_client = OK + LOG_OUT

        else:
            print (message[COMMAND])
            msg_to_client = NOK + INV_MSG
    else:
        msg_to_client = NOK + INV_MSG

    return msg_to_client

#************** commands handling functions **********************

def place_item(item_type):
    # generate random coordinates
    x = random.randint(0, 4)
    y = random.randint(0, 4)
    coordinate = "(" + str(x)+","+str(y)+")"
    location_line = find_data(MAP, coordinate)
   
    if (item_type == FOO):
        if ("FOOD:" in location_line):
            line = location_line.split(";") 
            # obtains food quantity (splits "FOOD: x" , and x is in index 1)
            food = eval((line[FOOD].split(":"))[VALUE_INDEX])
            food += 1 # increases food quantity by 1
            replace_data(MAP, location_line,
                         location_line.replace(line[FOOD], (" FOOD: " + str(food))))

            return OK + FOO + PLACE_OK
        return NOK + FOO + PLACE_NOK

    elif (item_type == TRP):
        if ("TRAP: False" in location_line):
            replace_data(MAP, location_line, location_line.replace(
                "TRAP: False", "TRAP: True"))
            return OK + TRP + PLACE_OK
        return NOK + TRP + PLACE_NOK + " [location already has trap]"

    elif (item_type == CTR):
        if ("CENTER: False" in location_line):
            replace_data(MAP, location_line, location_line.replace(
                "CENTER: False", "CENTER: True"))
            return OK + CTR + PLACE_OK
        return NOK + CTR + PLACE_NOK + " [location already has training center]"
    else:
        # will not enter here
        return ""


def show_location(player_name): #receives player name, finds player name, returns everything on player location.
    "\n".join([x for x in find_data(MAP, player_name).split(";")])
    return OK + LOCATION_OK + "\n".join([x for x in find_data(MAP, player_name).split(";")])


def attack_player(attacker, attacked):  # receives attacking player and attacked player
    return "attack ok"


# receives player , sees player position and tries to eat if location not empty
def player_eat(player_name):
    player_line = find_data(PLAYERS, player_name)

    # splits "COORDINATES: (x,y)" and (x,y) is at index 1
    coordinates = ((player_line.split(";"))[COORDINATES].split(":"))[VALUE_INDEX]
    
    location_line = find_data(MAP, coordinates)

    line = location_line.split(";")
    food = eval((line[FOOD].split(":"))[VALUE_INDEX])
    # splits "FOOD: x" , and x is at index 1

    if (food > 0):
        food -= 1
        replace_data(MAP, location_line,
                        location_line.replace(line[FOOD], (" FOOD: " + str(food))))
        if ("ENRGY: 10" not in player_line):
            line = player_line.split(";")
            # obtains food quantity
            energy = eval((line[ENRGY].split(":"))[VALUE_INDEX])
            energy += 1
            replace_data(PLAYERS, player_line,
                        player_line.replace(line[ENRGY], (" ENRGY: " + str(energy))))
        
            return OK + player_name + EAT_OK

        return NOK + player_name + EAT_NOK + " [player's energy full]"

    return NOK + player_name + EAT_NOK + " [location has no food available]"


# receives player , sees player position and tries to train if location not empty
def player_practice(player_name):
    location_line = find_data(PLAYERS, player_name)
    return ""


# receives player , sees player position and tries to trap him if location not empty
def player_trap(player_name):
    return "trap ok"

def add_player(player_name):
    pass

def mov_player(player_name):
    pass

#******************* main code **********************

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

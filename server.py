import sys
import os
import time
import socket
import threading
import random
import fileinput
import signal
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

# NOTE: TO SELF
# TODO: player attack (nothing done)

# ******************** generic functions ********************
def signal_handler(sig, frame):
    print('You pressed Ctrl+C. Leaving...') 
    sys.exit(0) #if multiple threads, must receive command twice

def end_connections(active_users):
    # terminates all server-client sockets
    for i in active_users:
        i.close()
        active_users.remove(i)

def handle_client_connection(client_socket, address): # place in while
    logged = 0 # variable to check if client has already logged in
    while True:
        msg_from_client = client_socket.recv(MSG_SIZE)
        request = msg_from_client.decode()
        
        print('Received {} from {} , {}'.format(request, address[IP], address[PORT]))
       
        # Splits input message by its separation punctuation (:)
        message = request.split(":")
        
        if (len(message) == 1 and message[COMMAND] == LOG): #LOGIN
            if (logged == 0):
                logged = 1
                msg_to_client = OK + LOG_OK
            elif (logged == 1):
                msg_to_client = NOK + LOG_NOK
        elif (len(message) == 1 and message[COMMAND] == LOGOUT):  # LOGOUT
            break
        elif (len(message) == 1 and message[COMMAND] == KILL):  # KILL_SERVER
            end_connections(active_users)
            exit(0)  # end thread
        else:
            msg_to_client = execute_command(message)
           
        client_socket.send(msg_to_client.encode())

    # end of connection
    client_socket.close()
    active_users.remove(client_socket)
    threads.remove(threading.current_thread())

def generate_save():
    # creates game map
    if not os.path.exists(MAP):
        with open(MAP, "w") as fn:
            for i in range(0,5):
                for f in range(0,5):
                    fn.write(str((i,f))+" ; PLAYERS: NULL; FOOD: 0; TRAP: False; CENTER: False;\n")

def find_data (filename, data):
    #data can be either player_name or coordinates, filename is either map or players
    #this function returns the correspondent lines of either a specific coordinate or player
    rw.acquire_read() # many threads can read, if none is writting
    try:
        with open(filename, "r") as f:
            for line in f:
                found_data = line.find(str(data))
                if (found_data != -1):
                    return line
        return ""
    finally:
        rw.release_read()

def replace_data (filename, oldline, newline):
    rw.acquire_write()  # only one thread a time can write to file
    print(oldline)
    print(newline)
    try:
        if (oldline != ""):
            with fileinput.FileInput(filename, inplace=True, backup='.bak') as file:   
                for line in file:
                    print(line.replace(oldline, newline), end='')
                    # replaces data in a given file
        else:
            if not os.path.exists(PLAY):
                with open(filename, "w") as f:
                    f.write(newline)  # adds new data
            else:
                with open(filename, "a+") as f:
                    f.write(newline)  # adds new data
    finally:
        rw.release_write()

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
            if (find_data(PLAY, message[PLAYERS]) != ""):  # if player exists
                msg_to_client = show_location(message[PLAYERS])
            else:
                msg_to_client = NOK + INV_PLAYER

        elif (message[COMMAND] == ATT and len(message) == 3):
            # message[PLAYERS] : attacker_name / message[PLAYERS+1] : attacked_name
            if (find_data(PLAY, message[PLAYERS]) != ""):
                msg_to_client = attack_player(message[PLAYERS], message[PLAYERS+1])
            else:
                msg_to_client = NOK + INV_PLAYER

        elif (message[COMMAND] == EAT and len(message) == 2):  # receives command and player name
            if (find_data(PLAY, message[PLAYERS]) != ""):
                msg_to_client = player_eat(message[PLAYERS])
            else:
                msg_to_client = NOK + INV_PLAYER

        # receives command and player name
        elif (message[COMMAND] == PRACT and len(message) == 3):
            if (find_data(PLAY, message[PLAYERS]) != ""):
                msg_to_client = player_practice(message[PLAYERS], message[PLAYERS+1])
            else:
                msg_to_client = NOK + INV_PLAYER

        # receives command and player name
        elif (message[COMMAND] == TRP and len(message) == 2):
            if (find_data(PLAY, message[PLAYERS]) != ""):
                msg_to_client = player_trap(message[PLAYERS])
            else:
                msg_to_client = NOK + INV_PLAYER
           
        elif (message[COMMAND] == ADD_PLAYER and len(message) == 4):
            msg_to_client = add_player(message[PLAYERS], message[PLAYERS+1], message[PLAYERS+2])
        
        else:
            msg_to_client = NOK + INV_MSG
    else:
        msg_to_client = NOK + INV_MSG

    return msg_to_client

#************** commands handling functions **********************

def place_item(item_type):
    # generate random coordinates
    x = random.randint(0, 4)
    y = random.randint(0, 4)
    coordinate = "(" + str(x)+", "+str(y)+")"
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
    return ("\n" + OK + LOCATION_OK + "\n" + "\n".join([x for x in find_data(MAP, player_name).split(";")][1:]))

def attack_player(attacker, attacked):  # receives attacking player and attacked player
    return "attack ok"

def player_eat(player_name):
    # receives player , sees player position and tries to eat if location not empty
    player_line = find_data(PLAY, player_name)
    
    # splits "COORDINATES: (x,y)" and (x,y) is at index 1
    coordinates = eval(((player_line.split(";"))[COORDINATES].split(":"))[VALUE_INDEX])

    location_line = find_data(MAP, coordinates)
    
    line = location_line.split(";")
    food = eval((line[FOOD].split(":"))[VALUE_INDEX])
    # splits "FOOD: x" , and x is at index 1

    if (food > 0):
        if ("ENRGY: 10" not in player_line):
            food -= 1
            replace_data(MAP, location_line,
                            location_line.replace(line[FOOD], (" FOOD: " + str(food))))
            line = player_line.split(";")
            # obtains food quantity
            energy = eval((line[ENRGY].split(":"))[VALUE_INDEX])
            energy += 1

            replace_data(PLAY, player_line, player_line.replace(line[ENRGY], (" ENRGY: " + str(energy))))
        
            return OK + player_name + EAT_OK

        return NOK + player_name + EAT_NOK + " [player's energy full]"

    return NOK + player_name + EAT_NOK + " [location has no food available]"

def player_practice(player_name, option):
    # receives player tries to train (option: 1 - attack, 2 - defense) if location has center
    location_line = find_data(MAP, player_name)
    if (location_line.find("CENTER: True;") != -1):
        player_line = find_data(PLAY, player_name)
        line = player_line.split(";")
        energy = eval((line[ENRGY].split(":"))[VALUE_INDEX])
        if (energy > 0):
            energy -= 1
            if (option == "1"):
                replace_data(PLAY, player_line, player_line.replace(
                    line[ENRGY], (" ENRGY: " + str(energy)))) # looses 1 energy point
                player_line = find_data(PLAY, player_name) # gets new replaced line
                line = player_line.split(";")
                # obtains attack quantity and increases
                attack = eval((line[ATTACK].split(":"))[VALUE_INDEX])
                attack += 1
                replace_data(PLAY, player_line, player_line.replace(
                    line[ATTACK], (" ATT: " + str(attack))))
                return OK + player_name + PRACT_OK
            elif (option == "2"):
                replace_data(PLAY, player_line, player_line.replace(
                    line[ENRGY], (" ENRGY: " + str(energy))))  # looses 1 energy point
                player_line = find_data(PLAY, player_name)
                line = player_line.split(";")
                # obtains defense quantity and increases
                defense = eval((line[DEF].split(":"))[VALUE_INDEX])
                defense += 1
                replace_data(PLAY, player_line, player_line.replace(
                    line[DEF], (" DEF: " + str(defense))))
                return OK + player_name + PRACT_OK
            else:
                return NOK + INV_MSG
        else:
            NOK + player_name + PRACT_NOK + " [player has no energy left]"
    else:
        return NOK + player_name + PRACT_NOK + " [location has no training center]"

def player_trap(player_name):
    # receives player , sees player position and tries to trap him if location not empty
    location_line = find_data(MAP, player_name)
    if (location_line.find("TRAP: True;") != -1):
        player_line = find_data(PLAY, player_name)
        line = player_line.split(";")
        energy = eval((line[ENRGY].split(":"))[VALUE_INDEX])
        if (energy > 0):
            energy -= 1
            replace_data(PLAY, player_line, player_line.replace(
                line[ENRGY], (" ENRGY: " + str(energy))))  # looses 1 energy point
            player_line = find_data(PLAY, player_name) # gets new replaced line
            line = player_line.split(";")
            # obtains experience quantity and increases
            experience = eval((line[EXP].split(":"))[VALUE_INDEX])
            experience += 1
            replace_data(PLAY, player_line, player_line.replace(
                line[EXP], (" EXP: " + str(experience))))
            return OK + player_name + TRAP_OK
        else:
            return OK + player_name + TRAP_OK + " [player is dead]" # player server should remove player
    else:
        return NOK + player_name + TRAP_NOK + " [location has no trap]"

def add_player(player_name, att, defense):
    if (player_name != "" and (eval(att) +  eval(defense)) <= 50):
        x = random.randint(0, 4)
        y = random.randint(0, 4)
        coordinate = "(" + str(x)+", "+str(y)+")"
        

        replace_data(PLAY, "", player_name + " ; ATT: " + att + " ; DEF: " +
                     defense + "; EXP: 1; ENRGY: 10; COORDINATES: " + 
                     coordinate + "; WON: 0; LOST: 0\n") # adds new player line to players.save
        
        location_line = find_data(MAP, coordinate)
        if ("PLAYERS: NULL;" in location_line):
            new_line = location_line.replace("PLAYERS: NULL;", "PLAYERS: " + player_name + ";")
        else:
            new_line = location_line.replace("PLAYERS: ", "PLAYERS: " + player_name + ", ")
        
        replace_data(MAP, location_line, new_line) # adds player_name to map.save
        return OK + ADD_OK
    else:
        return NOK + ADD_NOK

#******************* main code **********************

#sockets initiation
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# the SO_REUSEADDR flag reuses a local socket in TIME_WAIT state, without waiting for its natural timeout to expire.
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((bind_ip, bind_port))
server.listen(5)  # max backlog of connections

active_users = []
threads = []
signal.signal(signal.SIGINT, signal_handler) # receive and handle sigint (ctrl+c)
rw = ReadWriteLock()  # lock for one writer and many readers of a file
generate_save() # creates required files

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
    threads.append(client_handler)

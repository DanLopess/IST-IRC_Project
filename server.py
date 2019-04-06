import socket
import threading
import random
import fileinput

# ***************** NOTES ******************
#   map lines structure: "(0,0) ; PLAYERS: NULL; FOOD: 0; TRAP: False; CENTER: False;\n"
#   players lines structure: "Player_name ; Ataque: 25 ; Defesa: 25; Experiencia: 25; Energia: 25; Coordinates: (x,y)\n"
#   
# ******************************************

#constants definition
NULL = ''
COMMAND = 0
FOOD = 1
TRAP = 2
CENTER = 3
IP = 0 # for identifying the ip address in address vector 
PORT = 1  # for identifying the port in address vector
PLAYERS = "saves/players.save"
MAP = "saves/map.save"
TRP = 'TRAP'
FOO = 'FOOD'
CTR = 'CENTER'

#position in saves

#socket communication parameters
bind_ip = '127.0.0.1'
bind_port = 12345
MSG_SIZE = 1024

#possible messages
LOG = 'LOGIN'
PLACE_FOOD = 'PLACEF'
PLACE_TRAP = 'PLACET'
PLACE_CENTER = 'PLACEC'
ADD_PLAYER = 'ADDP' # add new player to map
MOVE_PLAYER = 'MOVP' # receives this command from player, and checks whether moving is possible 
SHOW_LOC = 'SHOW_LOCATION'
ATT = 'ATTACK'
EAT = 'EAT'
PRACT = 'PRACTICE'
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
TRAP_OK = 'fell into trap'
ADD_OK = 'added successfully'
MOV_OK = 'moved successfully' # if fell into trap, then player_name + TRAP_OK is also sent

LOG_NOK  = 'failed to login'
LOCATION_NOK = 'location empty'
PLACE_NOK = 'could not be placed'
ATT_NOK = 'attack failed'
EAT_NOK = 'could not eat'
PRACT_NOK = 'could not practice'
TRAP_NOK = 'could not be trapped'
INV_MSG     = 'invalid message type'
INV_PLAYER = 'no such player'
ADD_NOK = 'failed to add player'
MOV_NOK = 'failed to move player'

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
    return input_message.split(":") # Splits input message by its separation punctuation (:)

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
            msg_to_client = attack_player(message[1], message[2])

        elif (message[COMMAND] == EAT):  # receives command and player name
            msg_to_client = player_eat(message[1])

        elif (message[COMMAND] == PRACT):  # receives command and player name
            msg_to_client = player_practice(message[1])

        elif (message[COMMAND] == TRP):  # receives command and player name
            msg_to_client = player_trap(message[1])

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
    coordinate = "(" + str(x)+","+str(y)+")"
    location_line = find_data(MAP, coordinate)
   
    if (item_type == FOOD):
        if ("FOOD:" in location_line):
            line = location_line.split(";")
            food = eval((line[2].split(":"))[1]) #obtains food quantity
            food += 1
            replace_data(MAP, location_line,
                         location_line.replace(line[2], (" FOOD: " + str(food))))

            return OK + FOO + PLACE_OK
        return NOK + FOO + " " + PLACE_NOK

    elif (item_type == TRAP):
        if ("TRAP: False" in location_line):
            replace_data(MAP, location_line, location_line.replace(
                "TRAP: False", "TRAP: True"))
            return OK + TRP + PLACE_OK
        return NOK + TRP + " " + PLACE_NOK + " [location already has trap]"

    elif (item_type == CENTER):
        if ("CENTER: False" in location_line):
            replace_data(MAP, location_line, location_line.replace(
                "CENTER: False", "CENTER: True"))
            return OK + CTR + PLACE_OK
        return NOK + CTR + " " + PLACE_NOK + " [location already has training center]"
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
    # get coordinates from player's line
    coordinates = ((player_line.split(";"))[-1].split(":"))[1]
    location_line = find_data(MAP, coordinates)

    line = location_line.split(";")
    food = eval((line[2].split(":"))[1])  # obtains food quantity

    if (food > 0):
        food -= 1
        replace_data(MAP, location_line,
                        location_line.replace(line[2], (" FOOD: " + str(food))))
        if ("Energy: 10" not in player_line):
            line = player_line.split(";")
            energy = eval((line[4].split(":"))[1])  # obtains food quantity
            energy += 1
            replace_data(PLAYERS, player_line,
                        player_line.replace(line[4], (" Energy: " + str(energy))))
        
            return OK + player_name + " " + EAT_OK

        return NOK + player_name + " " + EAT_NOK + " [player's energy full]"

    return NOK + player_name + " " + EAT_NOK


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

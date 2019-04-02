import socket
import sys
import select


import socket

TCP_IP = 'localhost'
TCP_PORT = 9001
BUFFER_SIZE = 1024

client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_sock.connect((TCP_IP, TCP_PORT))

# -----------------------

# o select quer ficar a espera de ler o socket e ler do stdin (consola)
inputs = [client_sock, sys.stdin]


while True:
  print('Input message to server: ')
  ins, outs, exs = select.select(inputs,[],[])
  #select devolve para a lista ins quem esta a espera de ler
  for i in ins:
    # i == sys.stdin - alguem escreveu na consola, vamos ler e enviar
    if i == sys.stdin:
        user_msg = sys.stdin.readline()
        client_msg = user_msg.encode()
        client_sock.sendto(client_msg,(SERVER_IP,SERVER_PORT))
    # i == sock - o servidor enviou uma mensagem para o socket
    elif i == client_sock:
        (server_msg,addr) = client_sock.recvfrom(MSG_SIZE)
        server_request = server_msg.decode()
        print("Message received from server:", server_request)

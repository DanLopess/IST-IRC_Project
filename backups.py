#NOTES::::
- agora o cliente do gamemaster efetua o comando ataque, mas quando juntos, esse comando vem do cliente player
- e o servidor calcula e envia os resultados para os dois jogadores

    while True:
    (client_msg, client_addr) = server_sock.recvfrom(MSG_SIZE)
    msg_request = client_msg.decode().split()
    request_type = msg_request[TYPE]

    if (request_type in messages):

        if(request_type == "IAM"):
            server_msg = register_client(
                msg_request, client_addr, active_users)

        elif(request_type == "HELLO"):
            server_msg = reply_hello(client_addr, active_users)

        elif(request_type == "HELLOTO"):
            (server_msg, client_addr) = forward_hello(
                msg_request, client_addr, active_users)

        elif(request_type == "KILLSERVER"):
            break

        else:
            server_msg = invalid_msg(msg_request)

    server_sock.sendto(server_msg, client_addr)
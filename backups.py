#NOTES::::
#- agora o cliente do gamemaster efetua o comando ataque, mas quando juntos, esse comando vem do cliente player
#- e o servidor calcula e envia os resultados para os dois jogadores


def find_coordinates(player_name):  # maybe implement in needed function?

    #function receives player_name and returns its current position (reads from players.save)
    # returns either tuple or int 0 (error)
    player_line = find_data(PLAYERS, player_name)

    if (player_line != ""):
        coordinates = eval(player_line[-6:-2])  # evaluates a tuple
        return coordinates
    else:
        # no such player
        # indicates that no coordinates were found because player nonexistant
        return (False, False)


#esta funcao e para encontrar a coordenada dum jogador, mas se apenas for preciso no show_location, n e necessaria uma funcao
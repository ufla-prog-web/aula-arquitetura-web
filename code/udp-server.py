# udp-server.py

import socket                                       # Importa o módulo socket

HOST = "127.0.0.1"                                  # Endereço de interface de loopback padrão (localhost). Use "0.0.0.0" para comunicação entre dois computadores diferentes
PORT = 65433                                        # Porta para escutar (portas não privilegiadas são > 1023)

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as servidor: # Cria um socket UDP/IP
    servidor.bind((HOST, PORT))                     # Liga o socket a um endereço e porta
    print("Servidor UDP: Aguardando mensagens ...")
    while True:                                     # Entra em um loop infinito para receber dados do cliente
        dados, endereco = servidor.recvfrom(1024)   # Recebe dados do cliente
        sdata = str(dados)                          # Converte os bytes recebidos em string
        expressao = sdata.split(": ")[1][:-1]       # Isola a informação da expressão (PROTOCOLO)
        respexp = eval(expressao)                   # Avalia o resultado da expressão matemática
        resp = "Servidor>Resposta: " + str(respexp) # Mensagem com a resposta
        servidor.sendto(resp.encode("utf-8"), endereco)
        print("Recebido de", endereco, ":", sdata)  # Imprime a mensagem recebida do cliente
        print(resp)                                 # Imprime a mensagem de resposta ao cliente

print("Conexão Fechada")
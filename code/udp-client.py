# udp-client.py

import socket                                              # Importa o módulo socket

HOST = "127.0.0.1"                                         # O endereço IP do servidor ou nome (host) do servidor
PORT = 65433                                               # A porta usada pelo servidor

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as cliente: # Cria um socket UDP/IP
    protocolo = "Cliente>Requisicao: "
    expressao = "(4+3)*3"                          # Expressão matemática a ser enviada para o servidor
    pergunta = protocolo + str(expressao)                  # Mensagem com a pergunta    
    cliente.sendto(pergunta.encode("utf-8"), (HOST, PORT)) # Envia os bytes da mensagem da requisição
    resposta, _ = cliente.recvfrom(1024)                   # Recebe os dados do servidor
    print("Pergunta: ", pergunta)                          # Imprime a mensagem da pergunta
    print("Resposta: ", resposta.decode("utf-8"))          # Imprime a mensagem recebida pelo servidor

print("Conexão Fechada")
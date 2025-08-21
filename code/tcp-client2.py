# tcp-client2.py

import socket                                         # Importa o módulo socket

HOST = "127.0.0.1"                                    # O endereço IP do servidor ou nome (host) do servidor
PORT = 65432                                          # A porta usada pelo servidor

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s: # Cria um socket TCP/IP
    s.connect((HOST, PORT))                           # Conecta ao servidor
    print(f"Conectado: {(HOST, PORT)}")               # Imprime uma mensagem
    protocolo = "Cliente>Requisicao: "
    expressao = input()                               # Lê uma expressão matemática ou a palavra "fim"
    while expressao != "fim":                         # Loop para ler várias expressões matemáticas
        msg = protocolo + expressao                   # Concatena o protocolo com a expressão
        s.sendall(msg.encode('utf-8'))                # Envia os bytes da mensagem da requisição
        data = s.recv(1024)                           # Aguarda receber os dados do servidor
        print(msg)                                    # Imprime uma mensagem
        print(data.decode('utf-8'))                   # Imprime a mensagem recebida pelo servidor
        expressao = input()                           # Lê uma expressão matemática ou a palavra "fim"

print("Conexão Fechada")
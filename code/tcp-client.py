# tcp-client.py

import socket                    # Importa o módulo socket

HOST = "127.0.0.1"               # O endereço IP do servidor ou nome (host) do servidor
PORT = 65432                     # A porta usada pelo servidor

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s: # Cria um socket TCP/IP
    s.connect((HOST, PORT))                     # Conecta ao servidor
    print(f"Conectado: {(HOST, PORT)}")         # Imprime uma mensagem
    print("Cliente>Requisicao: (5+3)*2-4/2+100")      # Imprime uma mensagem
    s.sendall(b"Cliente>Requisicao: (5+3)*2-4/2+100") # Envia os bytes da mensagem da requisição
    data = s.recv(1024)          # Aguarda receber os dados do servidor
    print(data)                  # Imprime a mensagem recebida pelo servidor

print("Conexão Fechada")
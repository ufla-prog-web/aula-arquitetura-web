# tcp-server.py

import socket                          # Importa o módulo socket

HOST = "127.0.0.1"                     # Endereço de interface de loopback padrão (localhost). Use "0.0.0.0" para comunicação entre dois computadores diferentes
PORT = 65432                           # Porta para escutar (portas não privilegiadas são > 1023)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s: # Cria um socket TCP/IP
    s.bind((HOST, PORT))               # Liga o socket a um endereço e porta
    print("Servidor: Aguardando conexões ...")
    s.listen()                         # Coloca o servidor no modo de escuta para aguardar conexões de clientes
    conn, addr = s.accept()            # Aceita conexões de clientes
    with conn:
        print(f"Conectado: {addr}")    # Imprime uma mensagem
        while True:                    # Entra em um loop infinito para receber dados do cliente
            data = conn.recv(1024)     # Recebe dados do cliente
            if not data:               # Fecha a conexão com o cliente quando não houver mais dados recebidos
                break
            sdata = str(data)          # Converte os bytes recebidos em string
            expressao = sdata.split(": ")[1][:-1] # Isola a informação da expressão (PROTOCOLO)
            respexp = eval(expressao)  # Avalia o resultado da expressão matemática
            resp = "Servidor>Resposta: " + str(respexp) # Mensagem com a resposta
            conn.sendall(bytes(resp, 'utf-8'))    # Envia a mensagem de resposta de volta para o cliente
            print(sdata)               # Imprime a mensagem recebida do cliente
            print(resp)                # Imprime a mensagem de resposta ao cliente

print("Conexão Fechada")
"""
Chat TCP - SERVIDOR
====================
Exercício 2 - Redes de Computadores
Universidade Presbiteriana Mackenzie

Integrantes:
    - Murillo Henrique Sakamoto  (RA 10426242)
    - Daniel Monteiro Malacarne  (RA 10420454)
    - Hugo Rafael Weng           (RA 10417866)

Descrição:
    Servidor de chat simples sobre TCP.
    Aguarda a conexão de um cliente, exibe as mensagens recebidas
    e permite que o operador responda pelo terminal. A conversa
    encerra quando qualquer um dos lados enviar o comando QUIT.

Uso:
    python servidor.py
    (execute ANTES do cliente.py)
"""

import socket

TCP_IP = '127.0.0.1'
TCP_PORTA = 10426          # Primeiros 5 dígitos do TIA (Murillo)
TAMANHO_BUFFER = 1024

servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
servidor.bind((TCP_IP, TCP_PORTA))
servidor.listen(1)

print(f"Servidor disponível na porta {TCP_PORTA} e escutando...")

conn, addr = servidor.accept()
print(f"Endereço conectado: {addr}")
print("Digite QUIT para encerrar a conexão.\n")

while True:
    # --- Recebe mensagem do cliente ---
    data = conn.recv(TAMANHO_BUFFER)
    if not data:
        print("Cliente desconectou.")
        break

    mensagem_cliente = data.decode('UTF-8')
    print(f"[Cliente]: {mensagem_cliente}")

    if mensagem_cliente.strip().upper() == "QUIT":
        print("Cliente enviou QUIT. Encerrando conexão.")
        conn.send("QUIT".encode('UTF-8'))
        break

    # --- Servidor digita sua resposta ---
    resposta = input("[Servidor]: ")
    conn.send(resposta.encode('UTF-8'))

    if resposta.strip().upper() == "QUIT":
        print("Servidor enviou QUIT. Encerrando conexão.")
        break

conn.close()
servidor.close()
print("Conexão encerrada.")
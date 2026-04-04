"""
Chat TCP - CLIENTE
====================
Exercício 2 - Redes de Computadores
Universidade Presbiteriana Mackenzie

Integrantes:
    - Murillo Henrique Sakamoto  (RA 10426242)
    - Daniel Monteiro Malacarne  (RA 10420454)
    - Hugo Rafael Weng           (RA 10417866)

Descrição:
    Cliente de chat simples sobre TCP.
    Conecta ao servidor, envia mensagens digitadas pelo usuário
    e exibe as respostas. A conversa encerra quando qualquer um
    dos lados enviar o comando QUIT.

Uso:
    python cliente.py
"""

import socket

TCP_IP = '127.0.0.1'
TCP_PORTA = 10426          # Primeiros 5 dígitos do TIA (Murillo)
TAMANHO_BUFFER = 1024

cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
cliente.connect((TCP_IP, TCP_PORTA))

print(f"Conectado ao servidor {TCP_IP}:{TCP_PORTA}")
print("Digite QUIT para encerrar a conexão.\n")

while True:
    # --- Cliente digita sua mensagem ---
    mensagem = input("[Cliente]: ")
    cliente.send(mensagem.encode('UTF-8'))

    if mensagem.strip().upper() == "QUIT":
        print("Você enviou QUIT. Encerrando conexão.")
        break

    # --- Recebe resposta do servidor ---
    data = cliente.recv(TAMANHO_BUFFER)
    if not data:
        print("Servidor desconectou.")
        break

    resposta_servidor = data.decode('UTF-8')
    print(f"[Servidor]: {resposta_servidor}")

    if resposta_servidor.strip().upper() == "QUIT":
        print("Servidor enviou QUIT. Encerrando conexão.")
        break

cliente.close()
print("Conexão encerrada.")
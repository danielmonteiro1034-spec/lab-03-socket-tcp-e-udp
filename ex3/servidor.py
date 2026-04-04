"""
Quadro Branco Colaborativo - SERVIDOR
======================================
Exercício 3 - Redes de Computadores
Universidade Presbiteriana Mackenzie

Integrantes:
    - Murillo Henrique Sakamoto  (RA 10426242)
    - Daniel Monteiro Malacarne  (RA 10420454)
    - Hugo Rafael Weng           (RA 10417866)

Descrição:
    Servidor TCP multi-cliente para o Quadro Branco Colaborativo.
    Cada cliente conectado recebe uma thread dedicada. O servidor
    repassa (broadcast) todos os eventos de desenho para os demais
    clientes, permitindo colaboração em tempo real.

    Protocolo de framing:
        [4 bytes big-endian = tamanho da mensagem] + [payload JSON]

Uso:
    python servidor.py
    (execute ANTES dos clientes)
"""

import socket
import threading

HOST = '0.0.0.0'
PORT = 10420

# Lista de clientes conectados e lock para acesso thread-safe
clients: list[tuple] = []
clients_lock = threading.Lock()


def broadcast(data: bytes, sender_conn=None):
    """Envia dados para todos os clientes, exceto o remetente."""
    with clients_lock:
        disconnected = []
        for conn, addr in clients:
            if conn is sender_conn:
                continue
            try:
                length = len(data).to_bytes(4, byteorder='big')
                conn.sendall(length + data)
            except Exception:
                disconnected.append((conn, addr))

        for item in disconnected:
            clients.remove(item)
            print(f"[SERVIDOR] Cliente {item[1]} removido (broadcast falhou).")


def recv_exact(conn: socket.socket, n: int) -> bytes | None:
    """Recebe exatamente n bytes do socket, ou None se a conexão fechar."""
    buf = b''
    while len(buf) < n:
        chunk = conn.recv(n - len(buf))
        if not chunk:
            return None
        buf += chunk
    return buf


def handle_client(conn: socket.socket, addr):
    """Thread dedicada a um cliente. Lê eventos e faz broadcast."""
    print(f"[SERVIDOR] Cliente conectado: {addr}")
    with clients_lock:
        clients.append((conn, addr))

    try:
        while True:
            raw_len = recv_exact(conn, 4)
            if raw_len is None:
                break
            msg_len = int.from_bytes(raw_len, byteorder='big')

            raw_msg = recv_exact(conn, msg_len)
            if raw_msg is None:
                break

            broadcast(raw_msg, sender_conn=conn)

    except Exception as e:
        print(f"[SERVIDOR] Erro com {addr}: {e}")
    finally:
        with clients_lock:
            clients[:] = [(c, a) for c, a in clients if c is not conn]
        conn.close()
        print(f"[SERVIDOR] Cliente desconectado: {addr}")


def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen()
    print(f"[SERVIDOR] Quadro Branco escutando em {HOST}:{PORT}")
    print("[SERVIDOR] Aguardando clientes... (Ctrl+C para encerrar)\n")

    try:
        while True:
            conn, addr = server.accept()
            t = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
            t.start()
            print(f"[SERVIDOR] Threads ativas: {threading.active_count() - 1} cliente(s)")
    except KeyboardInterrupt:
        print("\n[SERVIDOR] Encerrando servidor.")
    finally:
        server.close()


if __name__ == '__main__':
    main()
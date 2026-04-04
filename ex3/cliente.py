"""
Quadro Branco Colaborativo - CLIENTE
======================================
Exercício 3 - Redes de Computadores
Universidade Presbiteriana Mackenzie

Integrantes:
    - Murillo Henrique Sakamoto  (RA 10426242)
    - Daniel Monteiro Malacarne  (RA 10420454)
    - Hugo Rafael Weng           (RA 10417866)

Descrição:
    Cliente TCP com interface gráfica (tkinter) para o Quadro Branco
    Colaborativo. Conecta ao servidor, envia eventos de desenho (traços,
    limpeza) codificados em JSON e recebe os eventos dos demais usuários
    em uma thread paralela, atualizando o canvas em tempo real.

    Funcionalidades:
        • Paleta de cores com 10 cores rápidas + seletor personalizado
        • 5 tamanhos de pincel
        • Borracha
        • Limpar quadro (sincroniza para todos os usuários)
        • Nome de usuário configurável na inicialização

    Protocolo de framing:
        [4 bytes big-endian = tamanho da mensagem] + [payload JSON]

Uso:
    python cliente.py
"""

import socket
import threading
import json
import tkinter as tk
from tkinter import colorchooser, messagebox, simpledialog

HOST = '127.0.0.1'
PORT = 10420

PALETTE = [
    '#FFFFFF', '#000000', '#EF4444', '#F97316', '#EAB308',
    '#22C55E', '#3B82F6', '#8B5CF6', '#EC4899', '#14B8A6',
]

BRUSH_SIZES = [2, 5, 10, 18, 28]


# ─── Protocolo de framing ────────────────────────────────────────────────────

def send_msg(sock: socket.socket, data: bytes):
    length = len(data).to_bytes(4, byteorder='big')
    sock.sendall(length + data)


def recv_exact(sock: socket.socket, n: int) -> bytes | None:
    buf = b''
    while len(buf) < n:
        chunk = sock.recv(n - len(buf))
        if not chunk:
            return None
        buf += chunk
    return buf


# ─── Aplicação principal ─────────────────────────────────────────────────────

class WhiteboardApp:
    def __init__(self, root: tk.Tk, sock: socket.socket, username: str):
        self.root = root
        self.sock = sock
        self.username = username
        self.color = '#000000'
        self.brush_size = 5
        self.last_x = None
        self.last_y = None
        self.drawing = False

        self._build_ui()
        self._start_receiver()

    # ── Interface ─────────────────────────────────────────────────────────────

    def _build_ui(self):
        self.root.title(f"Quadro Branco Colaborativo  •  {self.username}")
        self.root.configure(bg='#1E1E2E')
        self.root.resizable(False, False)

        toolbar = tk.Frame(self.root, bg='#2A2A3E', pady=8, padx=10)
        toolbar.pack(fill='x', side='top')

        tk.Label(toolbar, text="🎨 Quadro Branco", bg='#2A2A3E',
                 fg='#CDD6F4', font=('Helvetica', 13, 'bold')).pack(side='left', padx=(0, 20))

        tk.Label(toolbar, text="Cor:", bg='#2A2A3E',
                 fg='#BAC2DE', font=('Helvetica', 10)).pack(side='left')

        self.color_btn = tk.Button(
            toolbar, bg=self.color, width=3, relief='flat',
            command=self._choose_color, cursor='hand2'
        )
        self.color_btn.pack(side='left', padx=4)

        for c in PALETTE:
            tk.Button(
                toolbar, bg=c, width=2, relief='flat', cursor='hand2',
                command=lambda col=c: self._set_color(col)
            ).pack(side='left', padx=1)

        tk.Label(toolbar, text="  |  ", bg='#2A2A3E', fg='#45475A').pack(side='left')

        tk.Label(toolbar, text="Pincel:", bg='#2A2A3E',
                 fg='#BAC2DE', font=('Helvetica', 10)).pack(side='left')

        self.size_var = tk.IntVar(value=self.brush_size)
        for s in BRUSH_SIZES:
            tk.Radiobutton(
                toolbar, variable=self.size_var, value=s,
                text=str(s), bg='#2A2A3E', fg='#CDD6F4',
                selectcolor='#45475A', activebackground='#2A2A3E',
                font=('Helvetica', 9), command=lambda sz=s: self._set_size(sz),
                cursor='hand2'
            ).pack(side='left', padx=2)

        tk.Label(toolbar, text="  |  ", bg='#2A2A3E', fg='#45475A').pack(side='left')

        tk.Button(
            toolbar, text="⬜ Borracha", bg='#313244', fg='#CDD6F4',
            relief='flat', padx=8, cursor='hand2',
            command=self._use_eraser
        ).pack(side='left', padx=4)

        tk.Button(
            toolbar, text="🗑 Limpar", bg='#F38BA8', fg='#1E1E2E',
            relief='flat', padx=8, cursor='hand2', font=('Helvetica', 9, 'bold'),
            command=self._clear_canvas
        ).pack(side='left', padx=4)

        tk.Label(toolbar, text=f"👤 {self.username}", bg='#2A2A3E',
                 fg='#A6E3A1', font=('Helvetica', 10)).pack(side='right', padx=10)

        canvas_frame = tk.Frame(self.root, bg='#1E1E2E', padx=10, pady=10)
        canvas_frame.pack(fill='both', expand=True)

        self.canvas = tk.Canvas(
            canvas_frame, width=960, height=600,
            bg='#FFFFFF', cursor='crosshair',
            highlightthickness=2, highlightbackground='#45475A'
        )
        self.canvas.pack()

        self.canvas.bind('<ButtonPress-1>', self._on_press)
        self.canvas.bind('<B1-Motion>', self._on_drag)
        self.canvas.bind('<ButtonRelease-1>', self._on_release)

        self.status_var = tk.StringVar(value=f"✅ Conectado ao servidor {HOST}:{PORT}")
        tk.Label(
            self.root, textvariable=self.status_var,
            bg='#181825', fg='#6C7086',
            font=('Helvetica', 9), anchor='w', padx=10, pady=4
        ).pack(fill='x', side='bottom')

    # ── Eventos de mouse ──────────────────────────────────────────────────────

    def _on_press(self, event):
        self.drawing = True
        self.last_x, self.last_y = event.x, event.y

    def _on_drag(self, event):
        if not self.drawing or self.last_x is None:
            return
        x, y = event.x, event.y
        self._draw_line(self.last_x, self.last_y, x, y, self.color, self.brush_size)
        self._send_stroke(self.last_x, self.last_y, x, y, self.color, self.brush_size)
        self.last_x, self.last_y = x, y

    def _on_release(self, _event):
        self.drawing = False
        self.last_x = self.last_y = None

    def _draw_line(self, x1, y1, x2, y2, color, size):
        self.canvas.create_line(
            x1, y1, x2, y2,
            fill=color, width=size,
            capstyle=tk.ROUND, smooth=True
        )

    # ── Envio / recepção ──────────────────────────────────────────────────────

    def _send_stroke(self, x1, y1, x2, y2, color, size):
        event = {
            'type': 'stroke',
            'x1': x1, 'y1': y1,
            'x2': x2, 'y2': y2,
            'color': color,
            'size': size,
            'user': self.username,
        }
        try:
            send_msg(self.sock, json.dumps(event).encode())
        except Exception:
            self._disconnect("Conexão perdida com o servidor.")

    def _send_clear(self):
        event = {'type': 'clear', 'user': self.username}
        try:
            send_msg(self.sock, json.dumps(event).encode())
        except Exception:
            self._disconnect("Conexão perdida com o servidor.")

    def _start_receiver(self):
        threading.Thread(target=self._receiver_loop, daemon=True).start()

    def _receiver_loop(self):
        try:
            while True:
                raw_len = recv_exact(self.sock, 4)
                if raw_len is None:
                    break
                msg_len = int.from_bytes(raw_len, byteorder='big')
                raw_msg = recv_exact(self.sock, msg_len)
                if raw_msg is None:
                    break
                event = json.loads(raw_msg.decode())
                self.root.after(0, self._handle_remote_event, event)
        except Exception:
            pass
        self.root.after(0, self._disconnect, "Servidor desconectado.")

    def _handle_remote_event(self, event):
        if event['type'] == 'stroke':
            self._draw_line(
                event['x1'], event['y1'],
                event['x2'], event['y2'],
                event['color'], event['size']
            )
            self.status_var.set(f"✏️  {event['user']} está desenhando...")
        elif event['type'] == 'clear':
            self.canvas.delete('all')
            self.status_var.set(f"🗑  {event['user']} limpou o quadro.")

    # ── Controles ─────────────────────────────────────────────────────────────

    def _set_color(self, color):
        self.color = color
        self.color_btn.configure(bg=color)

    def _choose_color(self):
        result = colorchooser.askcolor(color=self.color, title="Escolha uma cor")
        if result and result[1]:
            self._set_color(result[1])

    def _set_size(self, size):
        self.brush_size = size
        self.size_var.set(size)

    def _use_eraser(self):
        self._set_color('#FFFFFF')

    def _clear_canvas(self):
        if messagebox.askyesno("Limpar", "Limpar o quadro para todos?"):
            self.canvas.delete('all')
            self._send_clear()

    def _disconnect(self, msg=''):
        self.status_var.set(f"❌ {msg}")
        try:
            self.sock.close()
        except Exception:
            pass


# ─── Ponto de entrada ─────────────────────────────────────────────────────────

def main():
    root = tk.Tk()
    root.withdraw()

    username = simpledialog.askstring(
        "Quadro Branco", "Digite seu nome de usuário:", parent=root
    )
    if not username or not username.strip():
        username = "Anônimo"

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((HOST, PORT))
    except ConnectionRefusedError:
        messagebox.showerror(
            "Erro de Conexão",
            f"Não foi possível conectar ao servidor em {HOST}:{PORT}.\n"
            "Verifique se o servidor está rodando."
        )
        root.destroy()
        sys.exit(1)

    root.deiconify()
    app = WhiteboardApp(root, sock, username.strip())
    root.mainloop()

    try:
        sock.close()
    except Exception:
        pass


if __name__ == '__main__':
    main()
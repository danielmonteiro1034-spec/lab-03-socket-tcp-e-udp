# Redes de Computadores — Lab 03: Sockets UDP e TCP

**Universidade Presbiteriana Mackenzie**  

## Integrantes

| Nome | RA |
|---|---|
| Murillo Henrique Sakamoto | 10426242 |
| Daniel Monteiro Malacarne | 10420454 |
| Hugo Rafael Weng | 10417866 |

---

## Vídeos de demonstração

| Vídeo | Conteúdo | Link |
|---|---|---|
| Vídeo 1 | Questões 1 e 2 — Chat TCP | https://youtu.be/_CBbQIiQOGk |
| Vídeo 2 | Questão 3 — Quadro Branco Colaborativo | https://youtu.be/28DTG2YCkjU |

---

## Pré-requisitos

- Python **3.10+** (as anotações de tipo `X | Y` requerem 3.10)
- Biblioteca padrão apenas — nenhuma instalação de pacotes externos necessária
- `tkinter` incluso na instalação padrão do Python (Windows/macOS). No Ubuntu/Debian:

```bash
sudo apt install python3-tk
```

---

## Exercício 2 — Chat TCP

Chat bidirecional entre cliente e servidor via TCP. A conversa encerra quando qualquer lado envia `QUIT`.

**Porta usada:** `10426` (primeiros 5 dígitos do TIA do Murillo Sakamoto)

### Como executar

> Abra **dois terminais** na pasta `ex2/`.

**Terminal 1 — servidor (execute primeiro):**
```bash
cd ex2
python servidor.py
```

**Terminal 2 — cliente:**
```bash
cd ex2
python cliente.py
```

### Fluxo de uso

1. O servidor exibe `"Servidor disponível na porta 10426 e escutando..."` e aguarda.
2. O cliente conecta e exibe `"Conectado ao servidor 127.0.0.1:10426"`.
3. O cliente digita uma mensagem → o servidor exibe e responde → e assim sucessivamente.
4. Qualquer lado digita `QUIT` para encerrar a sessão.

---

## Exercício 3 — Quadro Branco Colaborativo (TCP + Threads)

Aplicação multi-cliente onde vários usuários desenham juntos em tempo real em um canvas compartilhado. O servidor usa **uma thread por cliente** para tratar conexões simultâneas e faz **broadcast** dos eventos de desenho para todos os outros participantes.

**Porta usada:** `10420` (primeiros 5 dígitos do TIA do Daniel Monteiro)

### Como executar

> Abra **um terminal para o servidor** e **um terminal por cliente**.

**Terminal 1 — servidor (execute primeiro):**
```bash
cd ex3
python servidor.py
```

**Terminais 2, 3, … — clientes (um por usuário):**
```bash
cd ex3
python cliente.py                   # conecta em localhost:10420
```

Ao iniciar, cada cliente é solicitado a digitar um **nome de usuário** que aparece no quadro.

### Funcionalidades

- Paleta com 10 cores de acesso rápido + seletor de cor personalizado
- 5 tamanhos de pincel (2, 5, 10, 18, 28 px)
- Borracha
- Botão "Limpar" — apaga o quadro para **todos** os usuários conectados
- Identificação do usuário que está desenhando na barra de status

### Protocolo de comunicação

Todas as mensagens seguem um **framing fixo**:

```
[ 4 bytes big-endian: tamanho do payload ] + [ payload JSON ]
```

Tipos de evento:

```json
// Traço de desenho
{ "type": "stroke", "x1": 100, "y1": 200, "x2": 105, "y2": 205,
  "color": "#EF4444", "size": 5, "user": "Murillo" }

// Limpar quadro
{ "type": "clear", "user": "Daniel" }
```

### Arquitetura

```
Cliente A ──┐
Cliente B ──┼──► Servidor (broadcast) ──► Clientes A, B, C (exceto remetente)
Cliente C ──┘
```

---

## Estrutura do repositório

```
├── README.md
├── ex2/
│   ├── cliente.py   # Cliente do chat TCP
│   └── servidor.py  # Servidor do chat TCP
└── ex3/
    ├── cliente.py   # Cliente gráfico do Quadro Branco (tkinter)
    └── servidor.py  # Servidor multi-thread do Quadro Branco
```

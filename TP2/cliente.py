from flask import Flask, request
from websocket import WebSocketApp
import threading

# Crear aplicación Flask
app = Flask(__name__)

# WebSocket global
ws = None
ws_url = "ws://localhost:8080"  # URL del servidor WebSocket

# -------- FUNCIONES PARA MANEJAR EVENTOS WEBSOCKET -------- #

def on_message(ws, message):
    print(f"[Mensaje del servidor] {message}")

def on_error(ws, error):
    print(f"[Error de WebSocket] {error}")

def on_close(ws, close_status_code, close_msg):
    print("[WebSocket cerrado]")

def on_open(ws):
    print("[WebSocket abierto]")
    ws.send("Hola desde Flask WebSocket Client")

# -------- FUNCIONES PARA INICIAR WEBSOCKET -------- #

def start_websocket():
    global ws
    ws = WebSocketApp(
        ws_url,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close,
        on_open=on_open
    )
    # Este método bloquea, por eso lo ponemos en un hilo
    ws.run_forever(ping_interval=20, ping_timeout=10)

# -------- RUTAS FLASK -------- #

@app.route('/')
def index():
    return '''
        <h1>Enviar mensaje al servidor WebSocket</h1>
        <form action="/send" method="post">
            <input type="text" name="message" placeholder="Escribe tu mensaje">
            <input type="submit" value="Enviar">
        </form>
    '''

@app.route('/send', methods=['POST'])
def send():
    message = request.form['message']
    if ws and ws.sock and ws.sock.connected:
        ws.send(message)
        return f"Mensaje enviado: {message}<br><a href='/'>Enviar otro</a>"
    else:
        return "Error: WebSocket no está conectado.<br><a href='/'>Reintentar</a>"

# -------- MAIN -------- #

if __name__ == '__main__':
    # Lanzar WebSocket en hilo aparte
    websocket_thread = threading.Thread(target=start_websocket)
    websocket_thread.daemon = True
    websocket_thread.start()

    # Lanzar Flask
    app.run(port=5000)

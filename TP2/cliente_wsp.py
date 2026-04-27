from flask import Flask

app = Flask(__name__)

@app.route("/")
def index():
    return """
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Cliente WebSocket Visual</title>

<style>
body {
    font-family: Arial, sans-serif;
    background: #eef2f7;
    margin: 0;
    padding: 20px;
}

h1 {
    text-align: center;
}

.container {
    display: flex;
    gap: 20px;
}

.panel {
    background: white;
    border-radius: 12px;
    box-shadow: 0 0 12px rgba(0,0,0,0.15);
    padding: 20px;
}

.left {
    width: 55%;
}

.right {
    width: 45%;
}

#estado {
    padding: 12px;
    border-radius: 8px;
    background: #ddd;
    font-weight: bold;
    margin-bottom: 15px;
}

.conectado {
    background: #c8f7c5 !important;
    color: #176b16;
}

.desconectado {
    background: #ffd2d2 !important;
    color: #8a0000;
}

input {
    width: 70%;
    padding: 10px;
    font-size: 16px;
}

button {
    padding: 11px 18px;
    font-size: 16px;
    cursor: pointer;
}

#log, #proto {
    background: #111827;
    color: #e5e7eb;
    height: 380px;
    overflow-y: auto;
    padding: 12px;
    font-family: monospace;
    border-radius: 8px;
    margin-top: 15px;
}

.tx {
    color: #93c5fd;
}

.rx {
    color: #86efac;
}

.sys {
    color: #facc15;
}

.err {
    color: #fca5a5;
}
</style>
</head>

<body>

<h1>Cliente WebSocket desde Navegador</h1>

<div class="container">

    <div class="panel left">
        <h2>Mensajes WebSocket</h2>

        <div id="estado" class="desconectado">
            Estado: desconectado
        </div>

        <input id="mensaje" type="text" placeholder="Escriba un mensaje">
        <button onclick="enviar()">Enviar</button>

        <div id="log"></div>
    </div>

    <div class="panel right">
        <h2>Monitor de Protocolo</h2>
        <div id="proto"></div>
    </div>

</div>

<script>
const estado = document.getElementById("estado");
const log = document.getElementById("log");
const proto = document.getElementById("proto");
const input = document.getElementById("mensaje");

let ws = null;

function addLog(texto, clase) {
    const linea = document.createElement("div");
    linea.className = clase;
    linea.textContent = texto;
    log.appendChild(linea);
    log.scrollTop = log.scrollHeight;
}

function addProto(texto, clase) {
    const linea = document.createElement("div");
    linea.className = clase;
    linea.textContent = texto;
    proto.appendChild(linea);
    proto.scrollTop = proto.scrollHeight;
}

function conectarWebSocket() {
    addProto("HTTP GET /  → Flask entrega esta página HTML", "sys");
    addProto("HTTP 200 OK → HTML recibido por el navegador", "sys");
    addProto("JavaScript ejecuta: new WebSocket('ws://localhost:8080')", "sys");
    addProto("Solicitando HTTP Upgrade a WebSocket...", "sys");

    ws = new WebSocket("ws://localhost:8080");

    ws.onopen = function() {
        estado.textContent = "Estado: conectado a ws://localhost:8080";
        estado.className = "conectado";

        addProto("GET / HTTP/1.1", "sys");
        addProto("Host: localhost:8080", "sys");
        addProto("Upgrade: websocket", "sys");
        addProto("Connection: Upgrade", "sys");
        addProto("HTTP/1.1 101 Switching Protocols", "sys");
        addProto("[WS OPEN] canal WebSocket full-duplex activo", "sys");

        addLog("[SISTEMA] WebSocket abierto", "sys");

        ws.send("Hola desde el navegador");
        addLog("[CLIENTE] Hola desde el navegador", "tx");
        addProto("[TX FRAME] Hola desde el navegador", "tx");
    };

    ws.onmessage = function(event) {
        addLog("[SERVIDOR] " + event.data, "rx");
        addProto("[RX FRAME] " + event.data, "rx");
    };

    ws.onerror = function() {
        addLog("[ERROR] Error en WebSocket", "err");
        addProto("[ERROR] Falló la conexión WebSocket", "err");
    };

    ws.onclose = function() {
        estado.textContent = "Estado: WebSocket cerrado";
        estado.className = "desconectado";

        addLog("[SISTEMA] WebSocket cerrado", "sys");
        addProto("[WS CLOSED] conexión cerrada", "sys");
    };
}

function enviar() {
    const mensaje = input.value.trim();

    if (mensaje === "") {
        return;
    }

    if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(mensaje);
        addLog("[CLIENTE] " + mensaje, "tx");
        addProto("[TX FRAME] " + mensaje, "tx");
        input.value = "";
    } else {
        addLog("[ERROR] WebSocket no está conectado", "err");
        addProto("[ERROR] No se puede enviar: WebSocket cerrado", "err");
    }
}

input.addEventListener("keydown", function(event) {
    if (event.key === "Enter") {
        enviar();
    }
});

conectarWebSocket();
</script>

</body>
</html>
"""

if __name__ == "__main__":
    app.run(port=5011, debug=False)
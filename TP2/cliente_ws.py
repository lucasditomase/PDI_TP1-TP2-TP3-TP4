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
    background: #f2f4f8;
    margin: 0;
    padding: 30px;
}

.card {
    max-width: 800px;
    margin: auto;
    background: white;
    border-radius: 12px;
    padding: 25px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.15);
}

h1 {
    margin-top: 0;
}

#estado {
    padding: 10px;
    border-radius: 8px;
    font-weight: bold;
    margin-bottom: 20px;
    background: #ddd;
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

#log {
    margin-top: 20px;
    background: #111827;
    color: #e5e7eb;
    height: 350px;
    overflow-y: auto;
    padding: 15px;
    border-radius: 8px;
    font-family: monospace;
}

.enviado {
    color: #93c5fd;
}

.recibido {
    color: #86efac;
}

.sistema {
    color: #facc15;
}
</style>
</head>

<body>

<div class="card">
    <h1>Cliente WebSocket Visual</h1>

    <div id="estado" class="desconectado">
        Estado: desconectado
    </div>

    <input id="mensaje" type="text" placeholder="Escriba un mensaje">
    <button onclick="enviar()">Enviar</button>

    <div id="log"></div>
</div>

<script>
const estado = document.getElementById("estado");
const log = document.getElementById("log");
const input = document.getElementById("mensaje");

const ws = new WebSocket("ws://localhost:8080");

function agregarLog(texto, clase) {
    const linea = document.createElement("div");
    linea.className = clase;
    linea.textContent = texto;
    log.appendChild(linea);
    log.scrollTop = log.scrollHeight;
}

ws.onopen = function() {
    estado.textContent = "Estado: conectado a ws://localhost:8080";
    estado.className = "conectado";
    agregarLog("[SISTEMA] WebSocket abierto", "sistema");

    ws.send("Hola desde el navegador");
    agregarLog("[CLIENTE] Hola desde el navegador", "enviado");
};

ws.onmessage = function(event) {
    agregarLog("[SERVIDOR] " + event.data, "recibido");
};

ws.onerror = function() {
    agregarLog("[ERROR] Error en la conexión WebSocket", "sistema");
};

ws.onclose = function() {
    estado.textContent = "Estado: WebSocket cerrado";
    estado.className = "desconectado";
    agregarLog("[SISTEMA] WebSocket cerrado", "sistema");
};

function enviar() {
    const mensaje = input.value.trim();

    if (mensaje === "") return;

    if (ws.readyState === WebSocket.OPEN) {
        ws.send(mensaje);
        agregarLog("[CLIENTE] " + mensaje, "enviado");
        input.value = "";
    } else {
        agregarLog("[ERROR] WebSocket no está conectado", "sistema");
    }
}

input.addEventListener("keydown", function(event) {
    if (event.key === "Enter") {
        enviar();
    }
});
</script>

</body>
</html>
"""

if __name__ == "__main__":
    app.run(port=5000, debug=False)
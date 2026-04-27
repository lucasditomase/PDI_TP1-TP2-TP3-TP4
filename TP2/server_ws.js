const WebSocket = require('ws');

const wss = new WebSocket.Server({ port: 8080 });

console.log("Servidor WebSocket en ws://localhost:8080");

wss.on('connection', function connection(ws) {
  console.log('Cliente web conectado');

  ws.send('Bienvenido desde server.js');

  ws.on('message', function incoming(message) {
    console.log('Recibido:', message.toString());
    ws.send('Servidor recibió: ' + message.toString());
  });
});
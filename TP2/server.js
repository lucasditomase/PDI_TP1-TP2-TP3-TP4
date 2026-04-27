const WebSocket = require('ws');

// Creamos un servidor WebSocket en el puerto 8080

const wss = new WebSocket.Server({ port: 8080 });

console.log("Servidor WebSocket escuchando en ws://localhost:8080");

wss.on('connection', function connection(ws) {
  console.log('Cliente conectado.');
       
  // Cuando recibe un mensaje de un cliente
  ws.on('message', function incoming(message) {
    console.log('Recibido: %s', message);

    // Responder al cliente
    ws.send(`Servidor recibió: ${message}`);
  });

  // Enviar un mensaje al cliente apenas conecta
  ws.send('Bienvenido al chat WebSocket!');
});

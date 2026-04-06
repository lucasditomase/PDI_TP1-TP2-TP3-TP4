#!/bin/bash
echo "=== DEMOSTRACIÓN TAREA 3: Cliente TP1 → Sniffer ==="
echo "Este script ejecutará el sniffer continuo y enviará"
echo "un paquete ICMP personalizado desde el cliente."
echo ""

echo "Paso 1: Ejecutando sniffer continuo en background..."
sudo ./raw_sockets_sniffer_continuo &
SNIFFER_PID=$!

echo "Paso 2: Esperando que el sniffer inicie..."
sleep 2

echo "Paso 3: Enviando paquete ICMP personalizado desde cliente..."
sudo ./cliente_icmp_personalizado 127.0.0.1

echo "Paso 4: Esperando que el sniffer procese el paquete..."
sleep 3

echo "Paso 5: Deteniendo sniffer..."
kill $SNIFFER_PID 2>/dev/null

echo ""
echo "✓ Demostración TAREA 3 completada"
echo "El cliente ICMP envió un paquete personalizado que fue"
echo "capturado y analizado por el sniffer continuo."
#!/bin/bash
echo "=== DEMOSTRACIÓN: Sniffer ICMP Continuo ==="
echo "Este script ejecutará el sniffer continuo por 10 segundos"
echo "y generará tráfico ICMP para mostrar cómo funciona."
echo ""

echo "Ejecutando sniffer continuo en background..."
sudo ./raw_sockets_sniffer_continuo &
SNIFFER_PID=$!

echo "Esperando 2 segundos para que el sniffer inicie..."
sleep 2

echo "Generando tráfico ICMP con ping..."
ping -c 3 127.0.0.1 > /dev/null 2>&1

echo "Esperando que el sniffer procese los paquetes..."
sleep 3

echo "Deteniendo sniffer..."
kill $SNIFFER_PID 2>/dev/null

echo ""
echo "✓ Demostración completada"
echo "El sniffer continuo muestra todos los paquetes ICMP que llegan,"
echo "con timestamp, contador, y detalles completos de cada paquete."
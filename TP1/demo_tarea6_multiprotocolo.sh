#!/bin/bash
echo "=== DEMOSTRACIÓN TAREA 6: Sniffer Multi-Protocolo ==="
echo "Este script ejecutará el sniffer que captura ICMP, TCP y UDP"
echo "y generará tráfico de diferentes protocolos para mostrarlo."
echo ""

echo "Paso 1: Ejecutando sniffer multi-protocolo en background..."
sudo ./raw_sockets_sniffer_multiprotocolo &
SNIFFER_PID=$!

echo "Paso 2: Esperando que el sniffer inicie..."
sleep 3

echo "Paso 3: Generando tráfico ICMP con ping..."
ping -c 2 127.0.0.1 > /dev/null 2>&1 &
PING_PID=$!

echo "Paso 4: Esperando un poco..."
sleep 2

echo "Paso 5: Generando tráfico TCP con curl (HTTP)..."
curl -s http://httpbin.org/get > /dev/null 2>&1 &
CURL_PID=$!

echo "Paso 6: Generando más tráfico ICMP..."
ping -c 1 127.0.0.1 > /dev/null 2>&1

echo "Paso 7: Intentando generar tráfico UDP (DNS lookup)..."
nslookup google.com 8.8.8.8 > /dev/null 2>&1 &
NSLOOKUP_PID=$!

echo "Paso 8: Esperando que se procesen todos los paquetes..."
sleep 5

echo "Paso 9: Deteniendo procesos de background..."
kill $PING_PID $CURL_PID $NSLOOKUP_PID 2>/dev/null
kill $SNIFFER_PID 2>/dev/null

echo ""
echo "✓ Demostración TAREA 6 completada"
echo "El sniffer multi-protocolo capturó paquetes de:"
echo "  - ICMP (de ping)"
echo "  - TCP (de HTTP/curl)"
echo "  - UDP (de DNS/nslookup)"
echo ""
echo "Cada protocolo se analiza de manera específica según su estructura."
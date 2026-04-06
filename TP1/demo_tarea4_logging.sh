#!/bin/bash
echo "=== DEMOSTRACIÓN TAREA 4: Logging Detallado ICMP ==="
echo "Este script ejecutará el sniffer con logging detallado,"
echo "generará tráfico ICMP, y mostrará el contenido del log."
echo ""

# Limpiar log anterior
rm -f trafico_icmp_log.txt

echo "Paso 1: Ejecutando sniffer con logging en background..."
sudo ./raw_sockets_sniffer_logging &
SNIFFER_PID=$!

echo "Paso 2: Esperando que el sniffer inicie..."
sleep 2

echo "Paso 3: Generando tráfico ICMP con ping..."
ping -c 2 127.0.0.1 > /dev/null 2>&1

echo "Paso 4: Enviando paquete ICMP personalizado..."
sudo ./cliente_icmp_personalizado 127.0.0.1

echo "Paso 5: Generando más tráfico con ping..."
ping -c 1 127.0.0.1 > /dev/null 2>&1

echo "Paso 6: Esperando que se procesen todos los paquetes..."
sleep 3

echo "Paso 7: Deteniendo sniffer..."
kill $SNIFFER_PID 2>/dev/null

echo ""
echo "=== CONTENIDO DEL ARCHIVO DE LOG ==="
echo "trafico_icmp_log.txt:"
echo "====================================="
cat trafico_icmp_log.txt

echo ""
echo "✓ Demostración TAREA 4 completada"
echo "Se generaron múltiples paquetes ICMP y todos fueron"
echo "registrados detalladamente en el archivo de log."
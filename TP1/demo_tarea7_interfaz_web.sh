#!/bin/bash
echo "=== DEMOSTRACIÓN TAREA 7: Interfaz Web del Sniffer ==="
echo "Este script iniciará la interfaz web del sniffer TP 1B."
echo "Acceda a http://localhost:5000 en su navegador."
echo ""

# Verificar que Flask esté instalado
if ! python3 -c "import flask" 2>/dev/null; then
    echo "Instalando Flask..."
    pip install flask
fi

echo "Iniciando servidor web..."
echo "Abra http://localhost:5000 en su navegador para ver la interfaz"
echo ""
echo "Características de la interfaz:"
echo "  Estado del sniffer (ACTIVO/DETENIDO)"
echo "  Botones para iniciar/detener/clear"
echo "  Lista de paquetes capturados en tiempo real"
echo "  Detalles de cada paquete (protocolo, IPs, tamaño, etc.)"
echo "  Colores diferentes por protocolo (ICMP=verde, TCP=azul, UDP=amarillo)"
echo ""
echo "Para probar:"
echo "  1. Haga clic en 'Iniciar Sniffer'"
echo "  2. En otra terminal, ejecute: ping -c 3 127.0.0.1"
echo "  3. Vea cómo aparecen los paquetes ICMP en la interfaz"
echo "  4. Pruebe con curl o nslookup para TCP/UDP"
echo ""

python3 interfaz_web_sniffer.py
from flask import Flask, render_template_string, jsonify
import subprocess
import threading
import time
import signal
import os

app = Flask(__name__)

# Variable global para almacenar paquetes capturados
captured_packets = []
sniffer_process = None

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>TP 1B - Sniffer Web Interface</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #333; text-align: center; }
        .status { padding: 10px; margin: 10px 0; border-radius: 4px; }
        .status.running { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .status.stopped { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
        .packet { background: #f8f9fa; border: 1px solid #dee2e6; padding: 15px; margin: 10px 0; border-radius: 4px; }
        .packet-header { font-weight: bold; color: #495057; margin-bottom: 5px; }
        .packet-details { font-family: monospace; font-size: 12px; color: #6c757d; }
        .protocol-ICMP { border-left: 4px solid #28a745; }
        .protocol-TCP { border-left: 4px solid #007bff; }
        .protocol-UDP { border-left: 4px solid #ffc107; }
        .controls { text-align: center; margin: 20px 0; }
        button { padding: 10px 20px; margin: 0 10px; border: none; border-radius: 4px; cursor: pointer; }
        .start-btn { background: #28a745; color: white; }
        .stop-btn { background: #dc3545; color: white; }
        .clear-btn { background: #6c757d; color: white; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🕵️ TP 1B - Raw Sockets Sniffer Web Interface</h1>

        <div class="status {{ 'running' if sniffer_running else 'stopped' }}">
            Estado del Sniffer: {{ 'ACTIVO' if sniffer_running else 'DETENIDO' }}
        </div>

        <div class="controls">
            <button class="start-btn" onclick="startSniffer()">▶️ Iniciar Sniffer</button>
            <button class="stop-btn" onclick="stopSniffer()">⏹️ Detener Sniffer</button>
            <button class="clear-btn" onclick="clearPackets()">🗑️ Limpiar</button>
        </div>

        <h2>Paquetes Capturados: <span id="packetCount">{{ packets|length }}</span></h2>

        <div id="packets">
            {% for packet in packets %}
            <div class="packet protocol-{{ packet.protocol }}">
                <div class="packet-header">
                    📦 Paquete #{{ packet.id }} - {{ packet.timestamp }}
                </div>
                <div class="packet-details">
                    <strong>Protocolo:</strong> {{ packet.protocol }} ({{ packet.protocol_num }}) |
                    <strong>Tamaño:</strong> {{ packet.size }} bytes<br>
                    <strong>Origen:</strong> {{ packet.src_ip }} → <strong>Destino:</strong> {{ packet.dst_ip }}<br>
                    <strong>TTL:</strong> {{ packet.ttl }} | <strong>ID:</strong> {{ packet.ip_id }}<br>
                    {% if packet.details %}
                    <strong>Detalles:</strong> {{ packet.details }}
                    {% endif %}
                </div>
            </div>
            {% endfor %}
        </div>
    </div>

    <script>
        function updatePackets() {
            fetch('/api/packets')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('packetCount').textContent = data.length;
                    document.getElementById('packets').innerHTML = data.map(packet => `
                        <div class="packet protocol-${packet.protocol}">
                            <div class="packet-header">
                                📦 Paquete #${packet.id} - ${packet.timestamp}
                            </div>
                            <div class="packet-details">
                                <strong>Protocolo:</strong> ${packet.protocol} (${packet.protocol_num}) |
                                <strong>Tamaño:</strong> ${packet.size} bytes<br>
                                <strong>Origen:</strong> ${packet.src_ip} → <strong>Destino:</strong> ${packet.dst_ip}<br>
                                <strong>TTL:</strong> ${packet.ttl} | <strong>ID:</strong> ${packet.ip_id}<br>
                                ${packet.details ? '<strong>Detalles:</strong> ' + packet.details : ''}
                            </div>
                        </div>
                    `).join('');
                });
        }

        function startSniffer() {
            fetch('/api/start', { method: 'POST' })
                .then(() => {
                    document.querySelector('.status').className = 'status running';
                    document.querySelector('.status').textContent = 'Estado del Sniffer: ACTIVO';
                    setInterval(updatePackets, 1000);
                });
        }

        function stopSniffer() {
            fetch('/api/stop', { method: 'POST' })
                .then(() => {
                    document.querySelector('.status').className = 'status stopped';
                    document.querySelector('.status').textContent = 'Estado del Sniffer: DETENIDO';
                });
        }

        function clearPackets() {
            fetch('/api/clear', { method: 'POST' })
                .then(() => updatePackets());
        }

        // Actualizar cada segundo si está corriendo
        setInterval(() => {
            if (document.querySelector('.status').classList.contains('running')) {
                updatePackets();
            }
        }, 1000);
    </script>
</body>
</html>
"""

def run_sniffer():
    """Ejecuta el sniffer multi-protocolo y captura su output"""
    global sniffer_process, captured_packets

    try:
        # Ejecutar el sniffer multi-protocolo
        sniffer_process = subprocess.Popen(
            ['sudo', './raw_sockets_sniffer_multiprotocolo'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True
        )

        packet_id = 0
        while True:
            if sniffer_process.poll() is not None:
                break

            # Leer línea por línea
            line = sniffer_process.stdout.readline()
            if not line:
                break

            # Parsear líneas que contienen información de paquetes
            if "=== PAQUETE #" in line and "[" in line:
                packet_id += 1
                # Leer las siguientes líneas para obtener detalles completos
                lines = [line.strip()]
                for _ in range(5):  # Leer hasta 5 líneas siguientes
                    next_line = sniffer_process.stdout.readline()
                    if next_line:
                        lines.append(next_line.strip())
                    else:
                        break

                # Parsear el paquete
                packet_info = parse_packet_info(lines)
                if packet_info:
                    packet_info['id'] = packet_id
                    captured_packets.append(packet_info)

                    # Mantener solo los últimos 50 paquetes
                    if len(captured_packets) > 50:
                        captured_packets.pop(0)

    except Exception as e:
        print(f"Error ejecutando sniffer: {e}")

def parse_packet_info(lines):
    """Parsea la información del paquete desde las líneas del output"""
    try:
        packet = {
            'timestamp': '00:00:00',
            'protocol': 'UNKNOWN',
            'protocol_num': 0,
            'size': 0,
            'src_ip': '0.0.0.0',
            'dst_ip': '0.0.0.0',
            'ttl': 0,
            'ip_id': 0,
            'details': ''
        }

        for line in lines:
            if "=== PAQUETE #" in line and "[" in line:
                # Extraer timestamp
                start = line.find('[')
                end = line.find(']')
                if start != -1 and end != -1:
                    packet['timestamp'] = line[start+1:end]

            elif "📦 Tamaño:" in line:
                # Extraer tamaño y protocolo
                parts = line.split('|')
                if len(parts) >= 2:
                    size_part = parts[0].split(':')[1].strip().split()[0]
                    packet['size'] = int(size_part)

                    proto_part = parts[1].strip()
                    if 'ICMP' in proto_part:
                        packet['protocol'] = 'ICMP'
                        packet['protocol_num'] = 1
                    elif 'TCP' in proto_part:
                        packet['protocol'] = 'TCP'
                        packet['protocol_num'] = 6
                    elif 'UDP' in proto_part:
                        packet['protocol'] = 'UDP'
                        packet['protocol_num'] = 17

            elif "📍" in line and "→" in line:
                # Extraer IPs
                parts = line.split('📍')[1].split('→')
                if len(parts) == 2:
                    packet['src_ip'] = parts[0].strip()
                    packet['dst_ip'] = parts[1].strip()

            elif "📊 TTL:" in line:
                # Extraer TTL e ID
                parts = line.split('|')
                if len(parts) >= 2:
                    ttl_part = parts[0].split(':')[1].strip()
                    id_part = parts[1].split(':')[1].strip()
                    packet['ttl'] = int(ttl_part)
                    packet['ip_id'] = int(id_part)

            elif "🔍" in line:
                # Extraer detalles específicos del protocolo
                packet['details'] = line.split('🔍')[1].strip()

        return packet
    except:
        return None

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE,
                                packets=captured_packets,
                                sniffer_running=sniffer_process is not None and sniffer_process.poll() is None)

@app.route('/api/packets')
def get_packets():
    return jsonify(captured_packets)

@app.route('/api/start', methods=['POST'])
def start_sniffer_api():
    global sniffer_process
    if sniffer_process is None or sniffer_process.poll() is not None:
        thread = threading.Thread(target=run_sniffer)
        thread.daemon = True
        thread.start()
    return {'status': 'started'}

@app.route('/api/stop', methods=['POST'])
def stop_sniffer_api():
    global sniffer_process
    if sniffer_process and sniffer_process.poll() is None:
        sniffer_process.terminate()
        sniffer_process.wait()
    return {'status': 'stopped'}

@app.route('/api/clear', methods=['POST'])
def clear_packets_api():
    global captured_packets
    captured_packets.clear()
    return {'status': 'cleared'}

if __name__ == '__main__':
    print("=== INTERFAZ WEB DEL SNIFFER TP 1B ===")
    print("Acceda a http://localhost:5000 para ver la interfaz")
    print("Presione Ctrl+C para detener el servidor web")
    app.run(debug=True, host='0.0.0.0', port=5000)
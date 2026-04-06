#!/usr/bin/env python3
# servidor_select_archivos.py
# Servidor con select() que envía archivos y muestra información de clientes

import socket
import select
import time
import os
import queue
import threading
from datetime import datetime

HOST = '127.0.0.1'
PORT = 6669
ARCHIVO_PRUEBA = 'archivo_prueba.txt'

# Diccionario para almacenar información de clientes
clientes_info = {}
clientes_lock = threading.Lock()

def mostrar_clientes():
    """Muestra información de clientes conectados"""
    while True:
        time.sleep(10)  # Mostrar cada 10 segundos
        with clientes_lock:
            if clientes_info:
                print("\n=== CLIENTES CONECTADOS (SELECT) ===")
                for cliente_id, info in clientes_info.items():
                    estado = "ACTIVO" if info['activo'] else "DESCONECTADO"
                    tiempo_conexion = info['tiempo_conexion'].strftime('%H:%M:%S')
                    print(f"  {cliente_id} - Conectado: {tiempo_conexion} - Estado: {estado}")
                print("=" * 45)

def main():
    # Crear socket del servidor
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    servidor.bind((HOST, PORT))
    servidor.listen(5)
    servidor.setblocking(0)  # No bloqueante
    
    print(f"Servidor select iniciado en {HOST}:{PORT}")
    print("Presione Ctrl+C para detener el servidor")
    
    # Listas para select()
    entradas = [servidor]  # Sockets para leer
    salidas = []           # Sockets para escribir
    mensajes_salida = {}   # Cola de mensajes por socket
    
    # Información de clientes
    clientes_tiempos = {}  # socket -> tiempo_conexion
    
    # Iniciar hilo para mostrar clientes
    import threading
    threading.Thread(target=mostrar_clientes, daemon=True).start()
    
    try:
        while entradas:
            # Usar select() para esperar actividad
            readable, writable, exceptional = select.select(entradas, salidas, entradas, 1.0)
            
            # Procesar sockets legibles
            for s in readable:
                if s is servidor:
                    # Nueva conexión
                    conn, addr = s.accept()
                    conn.setblocking(0)
                    cliente_id = f"{addr[0]}:{addr[1]}"
                    
                    entradas.append(conn)
                    clientes_tiempos[conn] = datetime.now()
                    
                    with clientes_lock:
                        clientes_info[cliente_id] = {
                            'ip': addr[0],
                            'puerto': addr[1],
                            'tiempo_conexion': datetime.now(),
                            'activo': True
                        }
                    
                    print(f"Nueva conexión: {cliente_id}")
                    
                    # Agregar a diccionario de clientes
                    with clientes_lock:
                        clientes_info[cliente_id] = {
                            'conexion': datetime.now(),
                            'estado': 'ACTIVO',
                            'activo': True
                        }
                    
                    # Inicializar cola de mensajes para este cliente
                    mensajes_salida[conn] = queue.Queue()
                    
                    # Cliente listo, no enviar nada aún - esperar confirmación
                    
                else:
                    # Datos de cliente existente
                    try:
                        data = s.recv(1024)
                        if data:
                            cliente_id = f"{s.getpeername()[0]}:{s.getpeername()[1]}"
                            print(f"Datos de {cliente_id}: {data.decode('utf-8', errors='ignore')[:50]}...")
                            
                            # Si es confirmación, enviar archivo
                            if "listo para recibir" in data.decode('utf-8', errors='ignore').lower():
                                if os.path.exists(ARCHIVO_PRUEBA):
                                    with open(ARCHIVO_PRUEBA, 'rb') as f:
                                        datos_archivo = f.read()
                                    
                                    # Enviar tamaño primero
                                    tamano = str(len(datos_archivo))
                                    mensajes_salida[s].put(tamano.encode('utf-8'))
                                    if s not in salidas:
                                        salidas.append(s)
                                else:
                                    mensajes_salida[s].put(b"ERROR: Archivo no encontrado")
                                    if s not in salidas:
                                        salidas.append(s)
                            elif "OK" in data.decode('utf-8', errors='ignore'):
                                # Cliente confirmó recepción del tamaño, enviar archivo
                                if os.path.exists(ARCHIVO_PRUEBA):
                                    with open(ARCHIVO_PRUEBA, 'rb') as f:
                                        datos_archivo = f.read()
                                    mensajes_salida[s].put(datos_archivo)
                                    if s not in salidas:
                                        salidas.append(s)
                            elif "recibido correctamente" in data.decode('utf-8', errors='ignore').lower():
                                print(f"Archivo enviado exitosamente a {cliente_id}")
                                # Comenzar envío de tiempo conectado periódicamente
                                tiempo_conexion = clientes_tiempos.get(s, datetime.now())
                                tiempo_actual = datetime.now()
                                tiempo_conectado = tiempo_actual - tiempo_conexion
                                tiempo_msg = f"Tiempo conectado: {str(tiempo_conectado).split('.')[0]}"
                                mensajes_salida[s].put(tiempo_msg.encode('utf-8'))
                                if s not in salidas:
                                    salidas.append(s)
                            elif "PING" in data.decode('utf-8', errors='ignore'):
                                # Responder heartbeat y enviar tiempo actualizado
                                tiempo_conexion = clientes_tiempos.get(s, datetime.now())
                                tiempo_actual = datetime.now()
                                tiempo_conectado = tiempo_actual - tiempo_conexion
                                tiempo_msg = f"Tiempo conectado: {str(tiempo_conectado).split('.')[0]}"
                                mensajes_salida[s].put("OK".encode('utf-8'))
                                # Programar próximo envío de tiempo
                                time.sleep(0.1)  # Pequeño delay
                                mensajes_salida[s].put(tiempo_msg.encode('utf-8'))
                                if s not in salidas:
                                    salidas.append(s)
                                    
                        else:
                            # Conexión cerrada
                            cliente_id = f"{s.getpeername()[0]}:{s.getpeername()[1]}"
                            print(f"Cliente desconectado: {cliente_id}")
                            
                            with clientes_lock:
                                if cliente_id in clientes_info:
                                    clientes_info[cliente_id]['activo'] = False
                            
                            if s in salidas:
                                salidas.remove(s)
                            entradas.remove(s)
                            s.close()
                            
                            if s in mensajes_salida:
                                del mensajes_salida[s]
                            if s in clientes_tiempos:
                                del clientes_tiempos[s]
                                
                    except Exception as e:
                        print(f"Error leyendo de socket: {e}")
                        if s in entradas:
                            entradas.remove(s)
                        if s in salidas:
                            salidas.remove(s)
                        s.close()
                        
            # Procesar sockets escribibles
            for s in writable:
                try:
                    if s in mensajes_salida and not mensajes_salida[s].empty():
                        next_msg = mensajes_salida[s].get_nowait()
                        s.send(next_msg)
                    else:
                        salidas.remove(s)
                except Exception as e:
                    print(f"Error escribiendo a socket: {e}")
                    if s in salidas:
                        salidas.remove(s)
                        
            # Procesar excepciones
            for s in exceptional:
                print(f"Excepción en socket: {s}")
                entradas.remove(s)
                if s in salidas:
                    salidas.remove(s)
                s.close()
                
    except KeyboardInterrupt:
        print("\nDeteniendo servidor select...")
    finally:
        for s in entradas:
            if s != servidor:
                s.close()
        servidor.close()
        print("Servidor select detenido.")

if __name__ == "__main__":
    main()

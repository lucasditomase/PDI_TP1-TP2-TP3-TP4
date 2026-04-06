#!/usr/bin/env python3
# servidor_concurrente_archivos.py
# Servidor concurrente que envía archivos y muestra información de clientes

import socket
import threading
import time
import os
from datetime import datetime

HOST = '127.0.0.1'
PORT = 6668
ARCHIVO_PRUEBA = 'archivo_prueba.txt'

# Diccionario para almacenar información de clientes
clientes_info = {}
clientes_lock = threading.Lock()

def manejar_cliente(conn, addr):
    """Maneja la conexión con un cliente"""
    cliente_id = f"{addr[0]}:{addr[1]}"
    tiempo_conexion = datetime.now()
    
    with clientes_lock:
        clientes_info[cliente_id] = {
            'ip': addr[0],
            'puerto': addr[1],
            'tiempo_conexion': tiempo_conexion,
            'activo': True
        }
    
    try:
        print(f"Cliente conectado: {cliente_id}")
        
        # Enviar información de conexión al cliente
        info_conexion = f"Conectado el {tiempo_conexion.strftime('%Y-%m-%d %H:%M:%S')}"
        conn.send(info_conexion.encode('utf-8'))
        
        # Esperar confirmación del cliente
        confirmacion = conn.recv(1024).decode('utf-8')
        print(f"Cliente {cliente_id}: {confirmacion}")
        
        # Enviar archivo
        if os.path.exists(ARCHIVO_PRUEBA):
            with open(ARCHIVO_PRUEBA, 'rb') as f:
                datos_archivo = f.read()
            
            # Enviar tamaño del archivo primero
            tamano = len(datos_archivo)
            conn.send(str(tamano).encode('utf-8'))
            
            # Esperar confirmación
            conn.recv(1024)
            
            # Enviar archivo
            conn.sendall(datos_archivo)
            print(f"Archivo enviado a {cliente_id} ({tamano} bytes)")
            
            # Recibir confirmación de recepción
            respuesta = conn.recv(1024).decode('utf-8')
            print(f"Cliente {cliente_id}: {respuesta}")
        else:
            conn.send("ERROR: Archivo no encontrado".encode('utf-8'))
        
        # Mantener conexión para mostrar tiempo
        while True:
            try:
                # Calcular tiempo conectado
                tiempo_actual = datetime.now()
                tiempo_conectado = tiempo_actual - tiempo_conexion
                
                # Enviar tiempo conectado cada 5 segundos
                tiempo_msg = f"Tiempo conectado: {str(tiempo_conectado).split('.')[0]}"
                conn.send(tiempo_msg.encode('utf-8'))
                
                time.sleep(5)
                
                # Verificar si cliente sigue activo
                conn.settimeout(1.0)
                try:
                    heartbeat = conn.recv(1024)
                    if heartbeat:
                        conn.send("OK".encode('utf-8'))
                except socket.timeout:
                    continue
                    
            except (ConnectionResetError, BrokenPipeError):
                print(f"Cliente {cliente_id} desconectado")
                break
                
    except Exception as e:
        print(f"Error con cliente {cliente_id}: {e}")
    finally:
        with clientes_lock:
            if cliente_id in clientes_info:
                clientes_info[cliente_id]['activo'] = False
        conn.close()

def mostrar_clientes():
    """Muestra información de clientes conectados"""
    while True:
        time.sleep(10)  # Mostrar cada 10 segundos
        with clientes_lock:
            if clientes_info:
                print("\n=== CLIENTES CONECTADOS ===")
                for cliente_id, info in clientes_info.items():
                    estado = "ACTIVO" if info['activo'] else "DESCONECTADO"
                    tiempo_conexion = info['tiempo_conexion'].strftime('%H:%M:%S')
                    print(f"  {cliente_id} - Conectado: {tiempo_conexion} - Estado: {estado}")
                print("=" * 40)

def main():
    # Crear socket del servidor
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    servidor.bind((HOST, PORT))
    servidor.listen(5)
    
    print(f"Servidor concurrente iniciado en {HOST}:{PORT}")
    print("Presione Ctrl+C para detener el servidor")
    
    # Iniciar hilo para mostrar clientes
    threading.Thread(target=mostrar_clientes, daemon=True).start()
    
    try:
        while True:
            conn, addr = servidor.accept()
            # Crear hilo para cada cliente
            hilo_cliente = threading.Thread(target=manejar_cliente, args=(conn, addr))
            hilo_cliente.daemon = True
            hilo_cliente.start()
            
    except KeyboardInterrupt:
        print("\nDeteniendo servidor...")
    finally:
        servidor.close()
        print("Servidor detenido.")

if __name__ == "__main__":
    main()

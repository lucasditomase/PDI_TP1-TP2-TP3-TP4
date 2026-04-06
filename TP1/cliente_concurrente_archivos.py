#!/usr/bin/env python3
# cliente_concurrente_archivos.py
# Cliente que recibe archivos y muestra información de conexión

import socket
import time
import os
from datetime import datetime

HOST = '127.0.0.1'
PORT = 6668

def main():
    try:
        # Crear socket del cliente
        cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        cliente.connect((HOST, PORT))
        
        print(f"Conectado al servidor {HOST}:{PORT}")
        
        # Recibir información de conexión
        info_conexion = cliente.recv(1024).decode('utf-8')
        print(f"Servidor: {info_conexion}")
        
        # Enviar confirmación
        cliente.send("Cliente listo para recibir archivo".encode('utf-8'))
        
        # Recibir tamaño del archivo
        tamano_str = cliente.recv(1024).decode('utf-8')
        try:
            tamano = int(tamano_str)
            print(f"Tamaño del archivo a recibir: {tamano} bytes")
        except ValueError:
            print(f"Error: Tamaño inválido recibido: {tamano_str}")
            return
        
        # Confirmar recepción del tamaño
        cliente.send("OK".encode('utf-8'))
        
        # Recibir archivo
        datos_recibidos = b""
        while len(datos_recibidos) < tamano:
            chunk = cliente.recv(4096)
            if not chunk:
                break
            datos_recibidos += chunk
        
        if len(datos_recibidos) == tamano:
            # Guardar archivo recibido
            archivo_recibido = f"archivo_recibido_{int(time.time())}.txt"
            with open(archivo_recibido, 'wb') as f:
                f.write(datos_recibidos)
            
            print(f"Archivo recibido y guardado como: {archivo_recibido}")
            print("Contenido del archivo:")
            print(datos_recibidos.decode('utf-8', errors='ignore'))
            
            # Enviar confirmación
            cliente.send("Archivo recibido correctamente".encode('utf-8'))
        else:
            print(f"Error: Se esperaban {tamano} bytes pero se recibieron {len(datos_recibidos)}")
            cliente.send("Error en recepción del archivo".encode('utf-8'))
            return
        
        # Mantener conexión para recibir tiempo conectado
        print("\nMonitoreando tiempo de conexión (presione Ctrl+C para salir):")
        try:
            while True:
                # Recibir tiempo conectado
                tiempo_msg = cliente.recv(1024).decode('utf-8')
                if tiempo_msg:
                    print(f"Servidor: {tiempo_msg}")
                
                # Enviar heartbeat
                cliente.send("PING".encode('utf-8'))
                
                # Esperar respuesta
                respuesta = cliente.recv(1024).decode('utf-8')
                
                time.sleep(5)
                
        except KeyboardInterrupt:
            print("\nCliente finalizando...")
        except Exception as e:
            print(f"Error en comunicación: {e}")
            
    except Exception as e:
        print(f"Error de conexión: {e}")
    finally:
        cliente.close()
        print("Cliente desconectado.")

if __name__ == "__main__":
    main()

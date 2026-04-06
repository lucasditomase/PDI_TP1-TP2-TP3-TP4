#!/usr/bin/env python3
# cliente_select_archivos.py
# Cliente que recibe archivos usando select() y muestra información de conexión

import socket
import select
import time
import os
from datetime import datetime

HOST = '127.0.0.1'
PORT = 6669

def main():
    try:
        # Crear socket del cliente
        cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        cliente.connect((HOST, PORT))
        cliente.setblocking(0)  # No bloqueante para usar select()
        
        print(f"Conectado al servidor select {HOST}:{PORT}")
        
        # Listas para select()
        entradas = [cliente]
        salidas = []
        mensajes_salida = queue.Queue()
        
        # Estado de la comunicación
        esperando_tamano = True
        esperando_archivo = False
        tamano_esperado = 0
        datos_recibidos = b""
        archivo_recibido = False
        
        # Enviar mensaje inicial
        mensajes_salida.put("Cliente listo para recibir archivo".encode('utf-8'))
        salidas.append(cliente)
        
        try:
            while True:
                readable, writable, exceptional = select.select(entradas, salidas, entradas, 1.0)
                
                # Procesar datos para leer
                for s in readable:
                    if s is cliente:
                        data = s.recv(4096)
                        if data:
                            if esperando_tamano:
                                # Recibir tamaño del archivo
                                try:
                                    tamano_esperado = int(data.decode('utf-8'))
                                    print(f"Tamaño del archivo a recibir: {tamano_esperado} bytes")
                                    esperando_tamano = False
                                    esperando_archivo = True
                                    
                                    # Confirmar recepción del tamaño
                                    mensajes_salida.put("OK".encode('utf-8'))
                                    if cliente not in salidas:
                                        salidas.append(cliente)
                                        
                                except ValueError:
                                    if "ERROR" in data.decode('utf-8'):
                                        print(f"Servidor: {data.decode('utf-8')}")
                                        return
                                    elif "Conectado el" in data.decode('utf-8'):
                                        print(f"Servidor: {data.decode('utf-8')}")
                            
                            elif esperando_archivo:
                                # Recibir datos del archivo
                                datos_recibidos += data
                                
                                if len(datos_recibidos) >= tamano_esperado:
                                    # Archivo completo recibido
                                    archivo_recibido = f"archivo_recibido_select_{int(time.time())}.txt"
                                    with open(archivo_recibido, 'wb') as f:
                                        f.write(datos_recibidos)
                                    
                                    print(f"Archivo recibido y guardado como: {archivo_recibido}")
                                    print("Contenido del archivo:")
                                    print(datos_recibidos.decode('utf-8', errors='ignore'))
                                    
                                    # Enviar confirmación
                                    mensajes_salida.put("Archivo recibido correctamente".encode('utf-8'))
                                    if cliente not in salidas:
                                        salidas.append(cliente)
                                    
                                    esperando_archivo = False
                                    archivo_recibido = True
                            
                            elif archivo_recibido:
                                # Recibir tiempo conectado
                                mensaje = data.decode('utf-8', errors='ignore')
                                if "Tiempo conectado" in mensaje:
                                    print(f"Servidor: {mensaje}")
                                    
                                    # Enviar heartbeat
                                    mensajes_salida.put("PING".encode('utf-8'))
                                    if cliente not in salidas:
                                        salidas.append(cliente)
                                elif mensaje == "OK":
                                    pass  # Respuesta al heartbeat
                                    
                        else:
                            # Conexión cerrada
                            print("Servidor cerró la conexión")
                            return
                
                # Procesar datos para escribir
                for s in writable:
                    if s is cliente and not mensajes_salida.empty():
                        try:
                            next_msg = mensajes_salida.get_nowait()
                            s.send(next_msg)
                        except:
                            pass
                        finally:
                            if mensajes_salida.empty():
                                salidas.remove(s)
                
                # Procesar excepciones
                for s in exceptional:
                    print(f"Excepción en socket: {s}")
                    return
                    
                # Pequeña pausa para no consumir CPU
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            print("\nCliente select finalizando...")
            
    except Exception as e:
        print(f"Error de conexión: {e}")
    finally:
        cliente.close()
        print("Cliente select desconectado.")

if __name__ == "__main__":
    import queue  # Importar aquí para evitar error de importación circular
    main()

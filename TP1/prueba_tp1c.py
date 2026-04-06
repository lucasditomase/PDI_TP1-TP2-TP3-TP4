#!/usr/bin/env python3
# prueba_tp1c.py
# Script para probar las implementaciones del TP1C

import subprocess
import time
import signal
import sys
import os

def ejecutar_comando(cmd, descripcion, background=False):
    """Ejecuta un comando y maneja errores"""
    print(f"\n=== {descripcion} ===")
    print(f"Comando: {' '.join(cmd)}")
    
    if background:
        proceso = subprocess.Popen(cmd)
        time.sleep(2)  # Dar tiempo para que inicie
        return proceso
    else:
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                print("✓ Comando ejecutado exitosamente")
                if result.stdout:
                    print("Output:", result.stdout[:500] + "..." if len(result.stdout) > 500 else result.stdout)
            else:
                print(f"✗ Error (código {result.returncode})")
                if result.stderr:
                    print("Error:", result.stderr[:500] + "..." if len(result.stderr) > 500 else result.stderr)
            return result.returncode == 0
        except subprocess.TimeoutExpired:
            print("⏰ Comando timeout")
            return False
        except Exception as e:
            print(f"✗ Error ejecutando comando: {e}")
            return False

def menu():
    """Muestra el menú de opciones"""
    print("\n" + "="*60)
    print("          PRUEBA TP1C - SOCKETS PYTHON")
    print("="*60)
    print("1. Probar servidor concurrente (threads) + cliente")
    print("2. Probar servidor select + cliente") 
    print("3. Ver archivos implementados")
    print("4. Ver contenido del archivo de prueba")
    print("5. Limpiar archivos generados")
    print("0. Salir")
    print("="*60)

def probar_concurrente():
    """Prueba la versión concurrente"""
    print("\n--- PRUEBA SERVIDOR CONCURRENTE (THREADS) ---")
    
    # Iniciar servidor en background
    servidor = ejecutar_comando(
        [sys.executable, "servidor_concurrente_archivos.py"],
        "Iniciando servidor concurrente",
        background=True
    )
    
    if servidor:
        try:
            time.sleep(3)  # Esperar que servidor inicie
            
            # Ejecutar cliente
            ejecutar_comando(
                [sys.executable, "cliente_concurrente_archivos.py"],
                "Ejecutando cliente concurrente"
            )
            
            time.sleep(15)  # Dar tiempo para ver la comunicación
            
        finally:
            # Detener servidor
            print("\nDeteniendo servidor...")
            servidor.terminate()
            servidor.wait()
            print("✓ Servidor detenido")

def probar_select():
    """Prueba la versión con select"""
    print("\n--- PRUEBA SERVIDOR SELECT ---")
    
    # Iniciar servidor en background
    servidor = ejecutar_comando(
        [sys.executable, "servidor_select_archivos.py"],
        "Iniciando servidor select",
        background=True
    )
    
    if servidor:
        try:
            time.sleep(3)  # Esperar que servidor inicie
            
            # Ejecutar cliente
            ejecutar_comando(
                [sys.executable, "cliente_select_archivos.py"],
                "Ejecutando cliente select"
            )
            
            time.sleep(15)  # Dar tiempo para ver la comunicación
            
        finally:
            # Detener servidor
            print("\nDeteniendo servidor...")
            servidor.terminate()
            servidor.wait()
            print("✓ Servidor detenido")

def ver_archivos():
    """Muestra los archivos implementados"""
    print("\n--- ARCHIVOS IMPLEMENTADOS ---")
    archivos = [
        "servidor_concurrente_archivos.py",
        "cliente_concurrente_archivos.py", 
        "servidor_select_archivos.py",
        "cliente_select_archivos.py",
        "archivo_prueba.txt"
    ]
    
    for archivo in archivos:
        if os.path.exists(archivo):
            size = os.path.getsize(archivo)
            print(f"✓ {archivo} ({size} bytes)")
        else:
            print(f"✗ {archivo} - NO ENCONTRADO")

def ver_contenido_archivo():
    """Muestra el contenido del archivo de prueba"""
    archivo = "archivo_prueba.txt"
    if os.path.exists(archivo):
        print(f"\n--- CONTENIDO DE {archivo} ---")
        with open(archivo, 'r') as f:
            contenido = f.read()
            print(contenido)
    else:
        print(f"Archivo {archivo} no encontrado")

def limpiar_archivos():
    """Limpia archivos generados durante las pruebas"""
    print("\n--- LIMPIANDO ARCHIVOS GENERADOS ---")
    archivos_limpiar = []
    
    # Buscar archivos recibidos
    for archivo in os.listdir('.'):
        if archivo.startswith('archivo_recibido'):
            archivos_limpiar.append(archivo)
    
    if archivos_limpiar:
        for archivo in archivos_limpiar:
            try:
                os.remove(archivo)
                print(f"✓ Eliminado: {archivo}")
            except Exception as e:
                print(f"✗ Error eliminando {archivo}: {e}")
    else:
        print("No hay archivos para limpiar")

def main():
    while True:
        menu()
        try:
            opcion = input("Seleccione una opción: ").strip()
            
            if opcion == "1":
                probar_concurrente()
            elif opcion == "2":
                probar_select()
            elif opcion == "3":
                ver_archivos()
            elif opcion == "4":
                ver_contenido_archivo()
            elif opcion == "5":
                limpiar_archivos()
            elif opcion == "0":
                print("¡Hasta luego!")
                break
            else:
                print("Opción inválida")
                
        except KeyboardInterrupt:
            print("\n\nInterrupción detectada. Saliendo...")
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()

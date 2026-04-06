# TP1C - Sockets en Python

## Descripción
Implementación de aplicaciones cliente-servidor en Python que transfieren archivos pequeños, muestran información de conexión de clientes y retornan timestamps de conexión y duración.

## Implementaciones

### 1. Versión Concurrente (Threading)
- **Servidor**: `servidor_concurrente_archivos.py`
- **Cliente**: `cliente_concurrente_archivos.py`
- **Características**:
  - Usa `threading` para concurrencia real
  - Cada cliente se maneja en un hilo separado
  - Muestra información de clientes conectados cada 10 segundos
  - Transfiere archivos binarios
  - Registra tiempos de conexión y desconexión

### 2. Versión Select (Concurrencia Aparente)
- **Servidor**: `servidor_select_archivos.py`
- **Cliente**: `cliente_select_archivos.py`
- **Características**:
  - Usa `select()` para multiplexación I/O
  - Concurrencia aparente (un solo hilo)
  - Manejo de sockets no-bloqueantes
  - Cola de mensajes para comunicación
  - Monitoreo de tiempos de conexión

## Archivos Incluidos
- `servidor_concurrente_archivos.py` - Servidor con threading
- `cliente_concurrente_archivos.py` - Cliente para servidor concurrente
- `servidor_select_archivos.py` - Servidor con select
- `cliente_select_archivos.py` - Cliente para servidor select
- `archivo_prueba.txt` - Archivo de prueba para transferencias
- `prueba_tp1c.py` - Script de prueba interactivo

## Cómo Usar

### Opción 1: Script de Prueba Interactivo
```bash
python3 prueba_tp1c.py
```
El script ofrece un menú para:
- Probar servidor concurrente + cliente
- Probar servidor select + cliente
- Ver archivos implementados
- Ver contenido del archivo de prueba
- Limpiar archivos generados

### Opción 2: Ejecución Manual

#### Versión Concurrente:
```bash
# Terminal 1 - Servidor
python3 servidor_concurrente_archivos.py

# Terminal 2 - Cliente
python3 cliente_concurrente_archivos.py
```

#### Versión Select:
```bash
# Terminal 1 - Servidor
python3 servidor_select_archivos.py

# Terminal 2 - Cliente
python3 cliente_select_archivos.py
```

## Funcionalidades Implementadas

### ✅ Transferencia de Archivos
- Envío de archivos binarios
- Negociación de tamaño de archivo
- Verificación de integridad

### ✅ Información de Clientes
- IP y puerto del cliente
- Timestamp de conexión
- Duración de la conexión
- Estado de la conexión

### ✅ Monitoreo de Tiempos
- Hora de conexión inicial
- Duración total de la sesión
- Estadísticas de conexión

### ✅ Manejo de Recursos
- Limpieza de sockets
- Terminación ordenada
- Manejo de señales de interrupción

## Protocolo de Comunicación

### Handshake Inicial:
1. Cliente se conecta
2. Servidor envía timestamp de conexión
3. Cliente confirma recepción

### Transferencia de Archivo:
1. Cliente solicita archivo
2. Servidor envía tamaño del archivo
3. Cliente confirma tamaño
4. Servidor envía datos binarios
5. Cliente verifica recepción

### Monitoreo Continuo:
- Heartbeat cada 5 segundos
- Servidor muestra estado cada 10 segundos
- Registro de desconexiones

## Consideraciones Técnicas

### Threading vs Select
- **Threading**: Concurrencia real, mejor para CPU-bound tasks
- **Select**: Concurrencia aparente, mejor para I/O-bound tasks

### Manejo de Conexiones
- Sockets TCP/IP
- Puerto 8080 (configurable)
- Timeout de 30 segundos
- Reconexión automática

### Archivos de Prueba
- `archivo_prueba.txt`: Texto de prueba
- Archivos generados: `archivo_recibido_*.txt`

## Troubleshooting

### Errores Comunes:
1. **Puerto ocupado**: Cambiar puerto en el código
2. **Archivo no encontrado**: Verificar existencia de `archivo_prueba.txt`
3. **Conexión rechazada**: Verificar que el servidor esté ejecutándose

### Logs y Debugging:
- Ambos programas muestran información detallada
- Mensajes de error incluyen códigos y descripciones
- Estadísticas de conexión en tiempo real

## Resultados Esperados

Al ejecutar las pruebas, deberías ver:
- ✅ Conexión exitosa cliente-servidor
- ✅ Transferencia completa del archivo
- ✅ Información de IP/puerto del cliente
- ✅ Timestamps de conexión y duración
- ✅ Estadísticas de la sesión
- ✅ Terminación ordenada de programas

## Notas del Desarrollo

Esta implementación cumple con todos los requerimientos del TP1C:
- Transferencia de archivos pequeños
- Información de conexión de clientes
- Timestamps y duración de conexiones
- Ambas aproximaciones de concurrencia (threading y select)
- Manejo adecuado de recursos y limpieza

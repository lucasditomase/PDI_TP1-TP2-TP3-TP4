## COMPARACIÓN: Versiones del Sniffer ICMP

### 1. **Sniffer Original** (`raw_sockets_sniffer.c`)
- **Comportamiento**: Captura solo 1 paquete ICMP y termina
- **Salida**: Mínima información (solo direcciones IP)
- **Propósito**: Demostración básica de captura de paquetes

### 2. **Sniffer Educativo** (`raw_sockets_sniffer_explicado.c`) - TAREA 1
- **Comportamiento**: Captura solo 1 paquete ICMP y termina
- **Salida**: 7 pasos detallados explicando cada operación
- **Propósito**: Enseñar cómo funciona el análisis de paquetes ICMP
- **Características nuevas**:
  - Explicaciones paso a paso
  - Muestra estructura de headers IP e ICMP
  - Guarda paquete en archivo con comentarios

### 3. **Sniffer Continuo** (`raw_sockets_sniffer_continuo.c`) - TAREA 2
- **Comportamiento**: Captura TODOS los paquetes ICMP indefinidamente
- **Salida**: Información detallada de cada paquete con timestamp
- **Propósito**: Monitoreo continuo del tráfico ICMP
- **Características nuevas**:
  - Bucle infinito (while(1))
  - Contador de paquetes
  - Timestamp de recepción
  - Análisis completo de headers IP e ICMP
  - No termina automáticamente

### **Diferencias Clave:**
| Aspecto | Original | Educativo | Continuo |
|---------|----------|-----------|----------|
| **Paquetes capturados** | 1 solo | 1 solo | Todos |
| **Explicaciones** | Ninguna | Detalladas | Mínimas |
| **Timestamp** | No | No | Sí |
| **Contador** | No | No | Sí |
| **Archivo** | Sí | Sí | No |
| **Bucle** | No | No | Infinito |

### **Próximas Tareas TP 1B:**
- **TAREA 3**: Enviar tráfico desde cliente TP1 al sniffer
- **TAREA 4**: Logging detallado del tráfico ICMP
- **TAREA 5**: Explicar estructuras de datos utilizadas
- **TAREA 6**: Soporte para múltiples protocolos
- **TAREA 7**: Mostrar resultados en interfaz web
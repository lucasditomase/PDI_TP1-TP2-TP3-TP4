# TP 1B - TAREA 5: ESTRUCTURAS DE DATOS UTILIZADAS

## 📋 ESTRUCTURAS PRINCIPALES EN RAW SOCKETS

### 1. Estructura `struct iphdr` - Header IP

Esta estructura representa el header de un paquete IPv4 (Internet Protocol version 4).
Se define en `<netinet/ip.h>` y contiene todos los campos del header IP.

```c
struct iphdr {
    unsigned int ihl:4;           // Internet Header Length - Longitud del header IP (en palabras de 32 bits)
    unsigned int version:4;       // Version - Versión del protocolo IP (siempre 4 para IPv4)
    uint8_t tos;                  // Type of Service - Tipo de servicio (prioridad, QoS)
    uint16_t tot_len;             // Total Length - Longitud total del paquete IP (header + datos)
    uint16_t id;                  // Identification - Identificador único del paquete
    uint16_t frag_off;            // Fragment Offset - Offset para fragmentación
    uint8_t ttl;                  // Time to Live - Tiempo de vida (saltos máximo)
    uint8_t protocol;             // Protocol - Protocolo de la capa superior (1=ICMP, 6=TCP, 17=UDP)
    uint16_t check;               // Header Checksum - Checksum del header IP
    uint32_t saddr;               // Source Address - Dirección IP origen
    uint32_t daddr;               // Destination Address - Dirección IP destino
};
```

#### Campos principales explicados:

| Campo | Tamaño | Descripción | Valores típicos |
|-------|--------|-------------|-----------------|
| `ihl` | 4 bits | Longitud del header IP en palabras de 32 bits | 5 (20 bytes) |
| `version` | 4 bits | Versión del protocolo IP | 4 (IPv4) |
| `tos` | 8 bits | Tipo de servicio (prioridad) | 0 (normal) |
| `tot_len` | 16 bits | Longitud total del paquete | 20-65535 bytes |
| `id` | 16 bits | Identificador único del paquete | Número incremental |
| `frag_off` | 16 bits | Información de fragmentación | 0 (no fragmentado) |
| `ttl` | 8 bits | Tiempo de vida (saltos) | 64, 128, 255 |
| `protocol` | 8 bits | Protocolo de capa superior | 1=ICMP, 6=TCP, 17=UDP |
| `check` | 16 bits | Checksum del header | Calculado automáticamente |
| `saddr` | 32 bits | IP origen | ej: 127.0.0.1 |
| `daddr` | 32 bits | IP destino | ej: 192.168.1.1 |

### 2. Estructura `struct icmphdr` - Header ICMP

Esta estructura representa el header de un paquete ICMP (Internet Control Message Protocol).
Se define en `<netinet/ip_icmp.h>` y es específica para mensajes de control y error.

```c
struct icmphdr {
    uint8_t type;                 // Type - Tipo de mensaje ICMP
    uint8_t code;                 // Code - Código específico del tipo
    uint16_t checksum;            // Checksum - Checksum del mensaje ICMP
    union {
        struct {
            uint16_t id;          // Identifier - Identificador (para Echo)
            uint16_t sequence;    // Sequence Number - Número de secuencia
        } echo;
        uint32_t gateway;          // Gateway - Dirección gateway (para redirects)
        struct {
            uint16_t unused;      // Unused - No usado
            uint16_t mtu;         // MTU - Maximum Transmission Unit
        } frag;
    } un;
};
```

#### Tipos ICMP más comunes:

| Tipo | Nombre | Descripción | Código típico |
|------|--------|-------------|---------------|
| 0 | Echo Reply | Respuesta a ping | 0 |
| 3 | Destination Unreachable | Destino inalcanzable | 0-15 |
| 5 | Redirect | Redirección de ruta | 0-3 |
| 8 | Echo Request | Solicitud de ping | 0 |
| 11 | Time Exceeded | Tiempo excedido (TTL=0) | 0-1 |

#### Campos principales explicados:

| Campo | Tamaño | Descripción | Uso |
|-------|--------|-------------|-----|
| `type` | 8 bits | Tipo de mensaje ICMP | Define el propósito del mensaje |
| `code` | 8 bits | Código específico | Proporciona detalles adicionales |
| `checksum` | 16 bits | Checksum del mensaje | Verificación de integridad |
| `un.echo.id` | 16 bits | Identificador | Para parear request/reply |
| `un.echo.sequence` | 16 bits | Número de secuencia | Para ordenar paquetes |

## 🔍 CÓMO SE USAN EN EL CÓDIGO

### Parsing de paquetes recibidos:

```c
// Recibir paquete RAW
char buffer[65536];
int bytes = recvfrom(sockfd, buffer, sizeof(buffer), 0, ...);

// Parsear header IP
struct iphdr *ip_header = (struct iphdr *)buffer;

// Calcular posición del header ICMP (después del header IP)
int ip_header_len = ip_header->ihl * 4;  // ihl está en palabras de 32 bits
struct icmphdr *icmp_header = (struct icmphdr *)(buffer + ip_header_len);

// Acceder a campos
printf("IP Origen: %s\n", inet_ntoa(*(struct in_addr*)&ip_header->saddr));
printf("Tipo ICMP: %d\n", icmp_header->type);
printf("Código ICMP: %d\n", icmp_header->code);
```

### Construcción de paquetes enviados:

```c
// Crear buffer para el paquete
char packet[1024];
struct iphdr *ip = (struct iphdr *)packet;
struct icmphdr *icmp = (struct icmphdr *)(packet + 20);  // Después de 20 bytes IP

// Llenar header IP
ip->version = 4;
ip->ihl = 5;
ip->protocol = IPPROTO_ICMP;
ip->saddr = inet_addr("127.0.0.1");
// ...

// Llenar header ICMP
icmp->type = ICMP_ECHO;  // 8
icmp->code = 0;
icmp->un.echo.id = 1234;
icmp->un.echo.sequence = 1;
// ...
```

## 📊 RELACIÓN ENTRE ESTRUCTURAS

```
[ PAQUETE RAW RECIBIDO ]
├── struct iphdr (20 bytes)     ← Header IP
│   ├── version, ihl, tos, ...
│   ├── saddr, daddr
│   └── protocol = 1 (ICMP)
└── struct icmphdr (+ datos)    ← Header ICMP
    ├── type, code, checksum
    ├── id, sequence (para echo)
    └── datos del payload
```

## ⚠️ CONSIDERACIONES IMPORTANTES

1. **Orden de bytes**: Los campos de 16/32 bits están en network byte order (big-endian)
   - Usar `ntohs()` para convertir a host byte order al leer
   - Usar `htons()` para convertir a network byte order al escribir

2. **Longitud variable**: El header IP puede tener opciones (ihl > 5)
   - Siempre calcular la posición del header ICMP: `buffer + (ip->ihl * 4)`

3. **Checksum**: Debe calcularse correctamente para que el paquete sea válido
   - Para IP: checksum del header IP
   - Para ICMP: checksum del header ICMP + datos

4. **Unión en ICMP**: El campo `un` es una unión que se interpreta diferente según el tipo ICMP
   - Para Echo: `un.echo.id` y `un.echo.sequence`
   - Para otros tipos: campos diferentes

## 🧪 EJEMPLO PRÁCTICO

Ver el código en `raw_sockets_sniffer_explicado.c` para ver cómo se parsean estas estructuras en la práctica, o `cliente_icmp_personalizado.c` para ver cómo se construyen.
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <netinet/ip.h>
#include <netinet/ip_icmp.h>

int main() {
    int sockfd;
    char buffer[65536];
    struct sockaddr saddr;
    socklen_t saddr_len = sizeof(saddr);

    printf("=== PASO 1: Creación del socket RAW ===\n");
    printf("Creando socket RAW para capturar paquetes ICMP...\n");

    // Crear raw socket
    sockfd = socket(AF_INET, SOCK_RAW, IPPROTO_ICMP);
    if (sockfd < 0) {
        perror("ERROR en socket(): No se pudo crear el socket RAW");
        printf("Posibles causas: Sin permisos de root, o socket ya en uso\n");
        return 1;
    }
    printf("✓ Socket RAW creado exitosamente (sockfd = %d)\n", sockfd);
    printf("  - Familia: AF_INET (IPv4)\n");
    printf("  - Tipo: SOCK_RAW (acceso directo a paquetes)\n");
    printf("  - Protocolo: IPPROTO_ICMP (solo paquetes ICMP)\n\n");

    printf("=== PASO 2: Inicio del bucle de captura ===\n");
    printf("Sniffer ICMP iniciado... Esperando paquetes (Ctrl+C para detener)\n\n");

    while (1) {
        printf("=== PASO 3: Esperando recepción de paquetes ===\n");
        printf("Llamando a recvfrom() para recibir el siguiente paquete...\n");

        ssize_t packet_size = recvfrom(sockfd, buffer, sizeof(buffer), 0, &saddr, &saddr_len);
        if (packet_size < 0) {
            perror("ERROR en recvfrom(): Problema al recibir paquete");
            printf("Continuando con el siguiente paquete...\n\n");
            continue;
        }
        printf("✓ Paquete recibido exitosamente\n");
        printf("  - Tamaño del paquete: %zd bytes\n", packet_size);
        printf("  - Dirección del remitente guardada en saddr\n\n");

        printf("=== PASO 4: Análisis del header IP ===\n");
        struct iphdr *ip = (struct iphdr*) buffer;
        printf("Analizando header IP del paquete...\n");
        printf("  - Puntero al header IP: %p\n", (void*)ip);
        printf("  - Versión IP: %d\n", ip->version);
        printf("  - Longitud del header IP: %d bytes (%d palabras de 32 bits)\n", ip->ihl * 4, ip->ihl);
        printf("  - Protocolo del paquete: %d", ip->protocol);

        if (ip->protocol == IPPROTO_ICMP) {
            printf(" (ICMP - correcto!)\n\n");
        } else {
            printf(" (NO es ICMP, ignorando paquete)\n\n");
            continue;
        }

        printf("=== PASO 5: Análisis del header ICMP ===\n");
        struct icmphdr *icmp = (struct icmphdr*)(buffer + ip->ihl * 4);
        printf("Analizando header ICMP...\n");
        printf("  - Puntero al header ICMP: %p (después del header IP)\n", (void*)icmp);
        printf("  - Tipo ICMP: %d", icmp->type);

        switch(icmp->type) {
            case ICMP_ECHO: printf(" (Echo Request - ping enviado)\n"); break;
            case ICMP_ECHOREPLY: printf(" (Echo Reply - respuesta a ping)\n"); break;
            default: printf(" (Otro tipo ICMP)\n"); break;
        }

        printf("  - Código ICMP: %d\n", icmp->code);
        printf("  - ID del echo: %d\n", ntohs(icmp->un.echo.id));
        printf("  - Número de secuencia: %d\n", ntohs(icmp->un.echo.sequence));
        printf("✓ Información ICMP extraída exitosamente\n\n");

        printf("=== PASO 6: Guardado del paquete en archivo ===\n");
        printf("Guardando paquete completo en archivo icmp_packet.bin...\n");

        FILE *f = fopen("icmp_packet.bin", "wb");
        if (f) {
            size_t written = fwrite(buffer, 1, packet_size, f);
            fclose(f);
            printf("✓ Paquete guardado exitosamente\n");
            printf("  - Archivo: icmp_packet.bin\n");
            printf("  - Bytes escritos: %zu\n", written);
            printf("  - Tamaño del archivo: %zd bytes\n", packet_size);
            printf("✓ Primer paquete ICMP capturado y guardado\n\n");
            break; // solo capturamos uno para el ejemplo
        } else {
            printf("❌ ERROR: No se pudo abrir el archivo icmp_packet.bin\n");
            printf("Continuando con la captura...\n\n");
        }
    }

    printf("=== PASO 7: Cierre del programa ===\n");
    printf("Cerrando socket RAW...\n");
    close(sockfd);
    printf("✓ Socket cerrado exitosamente\n");
    printf("✓ Programa finalizado\n");

    return 0;
}
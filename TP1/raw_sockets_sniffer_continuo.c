#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <netinet/ip.h>
#include <netinet/ip_icmp.h>
#include <time.h>

int main() {
    int sockfd;
    char buffer[65536];
    struct sockaddr saddr;
    socklen_t saddr_len = sizeof(saddr);
    int packet_count = 0;

    printf("=== SNIFFER ICMP - MODO CONTINUO ===\n");
    printf("Mostrando TODO el tráfico ICMP que llega...\n");
    printf("Presione Ctrl+C para detener\n\n");

    // Crear raw socket
    sockfd = socket(AF_INET, SOCK_RAW, IPPROTO_ICMP);
    if (sockfd < 0) {
        perror("ERROR: No se pudo crear socket RAW");
        return 1;
    }
    printf("✓ Socket RAW creado para capturar ICMP\n\n");

    while (1) {
        packet_count++;

        // Obtener timestamp
        time_t now = time(NULL);
        struct tm *t = localtime(&now);
        char timestamp[20];
        strftime(timestamp, sizeof(timestamp), "%H:%M:%S", t);

        printf("=== PAQUETE ICMP #%d [%s] ===\n", packet_count, timestamp);

        ssize_t packet_size = recvfrom(sockfd, buffer, sizeof(buffer), 0, &saddr, &saddr_len);
        if (packet_size < 0) {
            printf("❌ Error al recibir paquete #%d\n", packet_count);
            continue;
        }

        // Analizar header IP
        struct iphdr *ip = (struct iphdr*) buffer;
        printf("📦 Tamaño: %zd bytes | Versión IP: %d | Protocolo: %d",
               packet_size, ip->version, ip->protocol);

        if (ip->protocol == IPPROTO_ICMP) {
            printf(" (ICMP ✓)\n");
        } else {
            printf(" (NO ICMP, ignorando)\n\n");
            continue;
        }

        // Analizar header ICMP
        struct icmphdr *icmp = (struct icmphdr*)(buffer + ip->ihl * 4);
        printf("🔍 ICMP Tipo: %d", icmp->type);

        switch(icmp->type) {
            case ICMP_ECHO: printf(" (Echo Request - Ping enviado)"); break;
            case ICMP_ECHOREPLY: printf(" (Echo Reply - Respuesta a ping)"); break;
            case ICMP_DEST_UNREACH: printf(" (Destination Unreachable)"); break;
            case ICMP_TIME_EXCEEDED: printf(" (Time Exceeded)"); break;
            default: printf(" (Tipo desconocido)"); break;
        }

        printf(" | Código: %d", icmp->code);

        if (icmp->type == ICMP_ECHO || icmp->type == ICMP_ECHOREPLY) {
            printf(" | ID: %d | Seq: %d", ntohs(icmp->un.echo.id), ntohs(icmp->un.echo.sequence));
        }

        printf("\n");

        // Mostrar direcciones IP
        struct sockaddr_in *src = (struct sockaddr_in*)&saddr;
        printf("📍 Origen: %s", inet_ntoa(src->sin_addr));
        printf(" → Destino: %s\n", inet_ntoa(*(struct in_addr*)&ip->daddr));

        // Información adicional del header IP
        printf("📊 TTL: %d | Checksum IP: 0x%04x | ID: %d\n",
               ip->ttl, ntohs(ip->check), ntohs(ip->id));

        printf("✓ Paquete ICMP #%d procesado\n\n", packet_count);

        // Pequeña pausa para no saturar la salida
        usleep(100000); // 0.1 segundos
    }

    close(sockfd);
    return 0;
}
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/ip.h>
#include <netinet/ip_icmp.h>
#include <arpa/inet.h>
#include <time.h>

#define MAX_BUFFER_SIZE 65536

// Función para obtener timestamp formateado
void get_timestamp(char *buffer, size_t size) {
    time_t now = time(NULL);
    struct tm *t = localtime(&now);
    strftime(buffer, size, "%Y-%m-%d %H:%M:%S", t);
}

int main() {
    int sockfd;
    char buffer[MAX_BUFFER_SIZE];
    struct sockaddr_in addr;
    socklen_t addr_len = sizeof(addr);
    FILE *log_file;

    // Abrir archivo de log
    log_file = fopen("trafico_icmp_log.txt", "a");
    if (log_file == NULL) {
        perror("Error abriendo archivo de log");
        return 1;
    }

    // Crear socket RAW para ICMP
    sockfd = socket(AF_INET, SOCK_RAW, IPPROTO_ICMP);
    if (sockfd < 0) {
        perror("Error creando socket RAW");
        fclose(log_file);
        return 1;
    }

    printf("=== SNIFFER ICMP - MODO LOGGING DETALLADO ===\n");
    printf("Guardando TODO el tráfico ICMP en 'trafico_icmp_log.txt'\n");
    printf("Presione Ctrl+C para detener\n\n");

    // Escribir header del log
    fprintf(log_file, "=== LOG DE TRÁFICO ICMP - INICIO: ");
    char timestamp[20];
    get_timestamp(timestamp, sizeof(timestamp));
    fprintf(log_file, "%s ===\n\n", timestamp);

    int packet_count = 0;

    while (1) {
        // Recibir paquete
        int bytes_received = recvfrom(sockfd, buffer, MAX_BUFFER_SIZE, 0,
                                    (struct sockaddr *)&addr, &addr_len);

        if (bytes_received < 0) {
            perror("Error recibiendo paquete");
            continue;
        }

        packet_count++;
        get_timestamp(timestamp, sizeof(timestamp));

        // Parsear headers IP e ICMP
        struct iphdr *ip_header = (struct iphdr *)buffer;
        struct icmphdr *icmp_header = (struct icmphdr *)(buffer + (ip_header->ihl * 4));

        // Información básica del paquete
        char src_ip[INET_ADDRSTRLEN], dst_ip[INET_ADDRSTRLEN];
        inet_ntop(AF_INET, &(ip_header->saddr), src_ip, INET_ADDRSTRLEN);
        inet_ntop(AF_INET, &(ip_header->daddr), dst_ip, INET_ADDRSTRLEN);

        // Mostrar en pantalla (resumen)
        printf("=== PAQUETE ICMP #%d [%s] ===\n", packet_count, timestamp);
        printf("📦 Tamaño: %d bytes | Origen: %s → Destino: %s\n",
               bytes_received, src_ip, dst_ip);
        printf("🔍 ICMP Tipo: %d | Código: %d\n", icmp_header->type, icmp_header->code);

        // Guardar log detallado en archivo
        fprintf(log_file, "=== PAQUETE ICMP #%d - %s ===\n", packet_count, timestamp);
        fprintf(log_file, "TIMESTAMP: %s\n", timestamp);
        fprintf(log_file, "TAMAÑO TOTAL: %d bytes\n", bytes_received);
        fprintf(log_file, "DIRECCIÓN ORIGEN: %s\n", src_ip);
        fprintf(log_file, "DIRECCIÓN DESTINO: %s\n", dst_ip);
        fprintf(log_file, "PROTOCOLO: %d (ICMP)\n", ip_header->protocol);
        fprintf(log_file, "TTL: %d\n", ip_header->ttl);
        fprintf(log_file, "CHECKSUM IP: 0x%04x\n", ntohs(ip_header->check));
        fprintf(log_file, "ID PAQUETE IP: %d\n", ntohs(ip_header->id));
        fprintf(log_file, "TIPO ICMP: %d", icmp_header->type);

        // Interpretar tipo ICMP
        switch (icmp_header->type) {
            case ICMP_ECHO: fprintf(log_file, " (Echo Request - Ping enviado)"); break;
            case ICMP_ECHOREPLY: fprintf(log_file, " (Echo Reply - Respuesta a ping)"); break;
            case ICMP_DEST_UNREACH: fprintf(log_file, " (Destination Unreachable)"); break;
            case ICMP_TIME_EXCEEDED: fprintf(log_file, " (Time Exceeded)"); break;
            default: fprintf(log_file, " (Tipo desconocido)");
        }
        fprintf(log_file, "\nCÓDIGO ICMP: %d\n", icmp_header->code);
        fprintf(log_file, "CHECKSUM ICMP: 0x%04x\n", ntohs(icmp_header->checksum));

        // Información específica según tipo ICMP
        if (icmp_header->type == ICMP_ECHO || icmp_header->type == ICMP_ECHOREPLY) {
            fprintf(log_file, "ID ECHO: %d\n", ntohs(icmp_header->un.echo.id));
            fprintf(log_file, "SECUENCIA ECHO: %d\n", ntohs(icmp_header->un.echo.sequence));
        }

        // Calcular tamaño del payload ICMP
        int ip_header_len = ip_header->ihl * 4;
        int icmp_header_len = sizeof(struct icmphdr);
        int payload_len = bytes_received - ip_header_len - icmp_header_len;

        fprintf(log_file, "TAMAÑO PAYLOAD ICMP: %d bytes\n", payload_len);

        if (payload_len > 0) {
            fprintf(log_file, "PAYLOAD (hex): ");
            unsigned char *payload = (unsigned char *)buffer + ip_header_len + icmp_header_len;
            for (int i = 0; i < payload_len && i < 20; i++) { // Mostrar máximo 20 bytes
                fprintf(log_file, "%02x ", payload[i]);
            }
            if (payload_len > 20) fprintf(log_file, "...");
            fprintf(log_file, "\n");

            // Intentar mostrar como texto si es imprimible
            fprintf(log_file, "PAYLOAD (texto): ");
            int printable = 1;
            for (int i = 0; i < payload_len && i < 50; i++) {
                if (payload[i] < 32 || payload[i] > 126) {
                    printable = 0;
                    break;
                }
            }
            if (printable) {
                for (int i = 0; i < payload_len && i < 50; i++) {
                    fprintf(log_file, "%c", payload[i]);
                }
            } else {
                fprintf(log_file, "[datos binarios]");
            }
            fprintf(log_file, "\n");
        }

        fprintf(log_file, "----------------------------------------\n\n");
        fflush(log_file); // Forzar escritura inmediata

        printf("✓ Log detallado guardado en archivo\n\n");
    }

    fclose(log_file);
    close(sockfd);
    return 0;
}
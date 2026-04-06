#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/ip.h>
#include <netinet/ip_icmp.h>
#include <netinet/tcp.h>
#include <netinet/udp.h>
#include <arpa/inet.h>
#include <time.h>
#include <poll.h>

#define MAX_BUFFER_SIZE 65536
#define NUM_PROTOCOLS 3

// Estructura para manejar múltiples sockets
typedef struct {
    int sockfd;
    int protocol;
    char *name;
} protocol_socket_t;

// Función para obtener timestamp
void get_timestamp(char *buffer, size_t size) {
    time_t now = time(NULL);
    struct tm *t = localtime(&now);
    strftime(buffer, size, "%H:%M:%S", t);
}

// Función para analizar paquete ICMP
void analyze_icmp_packet(char *buffer, int bytes_received, struct iphdr *ip_header) {
    struct icmphdr *icmp_header = (struct icmphdr *)(buffer + (ip_header->ihl * 4));

    printf("🔍 ICMP Tipo: %d", icmp_header->type);
    switch (icmp_header->type) {
        case ICMP_ECHO: printf(" (Echo Request)"); break;
        case ICMP_ECHOREPLY: printf(" (Echo Reply)"); break;
        case ICMP_DEST_UNREACH: printf(" (Destination Unreachable)"); break;
        case ICMP_TIME_EXCEEDED: printf(" (Time Exceeded)"); break;
        default: printf(" (Tipo %d)", icmp_header->type);
    }
    printf(" | Código: %d", icmp_header->code);

    if (icmp_header->type == ICMP_ECHO || icmp_header->type == ICMP_ECHOREPLY) {
        printf(" | ID: %d | Seq: %d", ntohs(icmp_header->un.echo.id), ntohs(icmp_header->un.echo.sequence));
    }
    printf("\n");
}

// Función para analizar paquete TCP
void analyze_tcp_packet(char *buffer, int bytes_received, struct iphdr *ip_header) {
    struct tcphdr *tcp_header = (struct tcphdr *)(buffer + (ip_header->ihl * 4));

    printf("🔍 TCP Puerto Origen: %d → Puerto Destino: %d\n",
           ntohs(tcp_header->source), ntohs(tcp_header->dest));

    printf("   Flags: ");
    if (tcp_header->syn) printf("SYN ");
    if (tcp_header->ack) printf("ACK ");
    if (tcp_header->fin) printf("FIN ");
    if (tcp_header->rst) printf("RST ");
    if (tcp_header->psh) printf("PSH ");
    if (tcp_header->urg) printf("URG ");
    printf("\n");

    // Calcular tamaño del payload TCP
    int tcp_header_len = tcp_header->doff * 4;
    int payload_len = bytes_received - (ip_header->ihl * 4) - tcp_header_len;
    printf("   Payload TCP: %d bytes\n", payload_len);
}

// Función para analizar paquete UDP
void analyze_udp_packet(char *buffer, int bytes_received, struct iphdr *ip_header) {
    struct udphdr *udp_header = (struct udphdr *)(buffer + (ip_header->ihl * 4));

    printf("🔍 UDP Puerto Origen: %d → Puerto Destino: %d\n",
           ntohs(udp_header->source), ntohs(udp_header->dest));

    printf("   Longitud UDP: %d bytes | Checksum: 0x%04x\n",
           ntohs(udp_header->len), ntohs(udp_header->check));

    // Calcular tamaño del payload UDP
    int payload_len = bytes_received - (ip_header->ihl * 4) - sizeof(struct udphdr);
    printf("   Payload UDP: %d bytes\n", payload_len);
}

int main() {
    protocol_socket_t protocols[NUM_PROTOCOLS] = {
        {-1, IPPROTO_ICMP, "ICMP"},
        {-1, IPPROTO_TCP,  "TCP"},
        {-1, IPPROTO_UDP,  "UDP"}
    };

    struct pollfd fds[NUM_PROTOCOLS];
    int active_sockets = 0;

    printf("=== SNIFFER MULTI-PROTOCOLO ===\n");
    printf("Capturando paquetes ICMP, TCP y UDP simultáneamente\n");
    printf("Presione Ctrl+C para detener\n\n");

    // Crear sockets para cada protocolo
    for (int i = 0; i < NUM_PROTOCOLS; i++) {
        protocols[i].sockfd = socket(AF_INET, SOCK_RAW, protocols[i].protocol);
        if (protocols[i].sockfd < 0) {
            perror("Error creando socket");
            printf("No se pudo crear socket para %s\n", protocols[i].name);
            continue;
        }

        fds[active_sockets].fd = protocols[i].sockfd;
        fds[active_sockets].events = POLLIN;
        active_sockets++;

        printf("✓ Socket creado para %s (protocolo %d)\n", protocols[i].name, protocols[i].protocol);
    }

    if (active_sockets == 0) {
        printf("Error: No se pudo crear ningún socket\n");
        return 1;
    }

    printf("\nEsperando paquetes...\n\n");

    int packet_count = 0;

    while (1) {
        // Usar poll para esperar datos en cualquier socket
        int ret = poll(fds, active_sockets, -1);  // Esperar indefinidamente

        if (ret < 0) {
            perror("Error en poll");
            continue;
        }

        // Verificar cuál socket tiene datos
        for (int i = 0; i < active_sockets; i++) {
            if (fds[i].events & POLLIN) {
                char buffer[MAX_BUFFER_SIZE];
                struct sockaddr_in addr;
                socklen_t addr_len = sizeof(addr);

                // Recibir paquete
                int bytes_received = recvfrom(fds[i].fd, buffer, MAX_BUFFER_SIZE, 0,
                                            (struct sockaddr *)&addr, &addr_len);

                if (bytes_received < 0) {
                    perror("Error recibiendo paquete");
                    continue;
                }

                packet_count++;
                char timestamp[20];
                get_timestamp(timestamp, sizeof(timestamp));

                // Parsear header IP
                struct iphdr *ip_header = (struct iphdr *)buffer;

                // Obtener direcciones IP
                char src_ip[INET_ADDRSTRLEN], dst_ip[INET_ADDRSTRLEN];
                inet_ntop(AF_INET, &(ip_header->saddr), src_ip, INET_ADDRSTRLEN);
                inet_ntop(AF_INET, &(ip_header->daddr), dst_ip, INET_ADDRSTRLEN);

                // Determinar protocolo por el socket que recibió
                const char *protocol_name = "DESCONOCIDO";
                for (int j = 0; j < NUM_PROTOCOLS; j++) {
                    if (fds[i].fd == protocols[j].sockfd) {
                        protocol_name = protocols[j].name;
                        break;
                    }
                }

                // Mostrar información del paquete
                printf("=== PAQUETE #%d [%s] ===\n", packet_count, timestamp);
                printf("📦 Tamaño: %d bytes | Protocolo: %s (%d)\n",
                       bytes_received, protocol_name, ip_header->protocol);
                printf("📍 %s → %s\n", src_ip, dst_ip);
                printf("📊 TTL: %d | ID: %d\n", ip_header->ttl, ntohs(ip_header->id));

                // Análisis específico según protocolo
                if (strcmp(protocol_name, "ICMP") == 0) {
                    analyze_icmp_packet(buffer, bytes_received, ip_header);
                } else if (strcmp(protocol_name, "TCP") == 0) {
                    analyze_tcp_packet(buffer, bytes_received, ip_header);
                } else if (strcmp(protocol_name, "UDP") == 0) {
                    analyze_udp_packet(buffer, bytes_received, ip_header);
                }

                printf("\n");
            }
        }
    }

    // Cerrar sockets
    for (int i = 0; i < NUM_PROTOCOLS; i++) {
        if (protocols[i].sockfd >= 0) {
            close(protocols[i].sockfd);
        }
    }

    return 0;
}
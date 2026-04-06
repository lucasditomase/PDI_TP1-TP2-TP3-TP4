#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/ip.h>
#include <netinet/ip_icmp.h>
#include <arpa/inet.h>

// Función para calcular checksum ICMP
unsigned short checksum(void *b, int len) {
    unsigned short *buf = b;
    unsigned int sum = 0;
    unsigned short result;

    for (sum = 0; len > 1; len -= 2)
        sum += *buf++;
    if (len == 1)
        sum += *(unsigned char*)buf;
    sum = (sum >> 16) + (sum & 0xFFFF);
    sum += (sum >> 16);
    result = ~sum;
    return result;
}

int main(int argc, char *argv[]) {
    if (argc != 2) {
        printf("Uso: %s <direccion_IP>\n", argv[0]);
        printf("Ejemplo: %s 127.0.0.1\n", argv[0]);
        return 1;
    }

    char *dest_ip = argv[1];
    int sockfd;
    struct sockaddr_in dest_addr;
    char packet[1024];
    struct iphdr *ip_header = (struct iphdr *)packet;
    struct icmphdr *icmp_header = (struct icmphdr *)(packet + sizeof(struct iphdr));

    // Crear socket RAW
    if ((sockfd = socket(AF_INET, SOCK_RAW, IPPROTO_ICMP)) < 0) {
        perror("Error creando socket");
        return 1;
    }

    // Configurar dirección destino
    memset(&dest_addr, 0, sizeof(dest_addr));
    dest_addr.sin_family = AF_INET;
    dest_addr.sin_addr.s_addr = inet_addr(dest_ip);

    // Construir header IP
    ip_header->ihl = 5;
    ip_header->version = 4;
    ip_header->tos = 0;
    ip_header->tot_len = sizeof(struct iphdr) + sizeof(struct icmphdr) + 4; // + datos
    ip_header->id = htonl(54321);
    ip_header->frag_off = 0;
    ip_header->ttl = 255;
    ip_header->protocol = IPPROTO_ICMP;
    ip_header->check = 0;
    ip_header->saddr = inet_addr("127.0.0.1"); // IP origen
    ip_header->daddr = dest_addr.sin_addr.s_addr;

    // Calcular checksum IP
    ip_header->check = checksum((unsigned short *)ip_header, sizeof(struct iphdr));

    // Construir header ICMP (Echo Request)
    icmp_header->type = ICMP_ECHO;
    icmp_header->code = 0;
    icmp_header->un.echo.id = 1234;
    icmp_header->un.echo.sequence = 1;
    icmp_header->checksum = 0;

    // Agregar datos al paquete ICMP
    char *data = packet + sizeof(struct iphdr) + sizeof(struct icmphdr);
    strcpy(data, "Hola desde cliente ICMP!");

    // Calcular checksum ICMP
    icmp_header->checksum = checksum((unsigned short *)icmp_header,
                                   sizeof(struct icmphdr) + strlen(data) + 1);

    // Activar IP_HDRINCL para incluir header IP personalizado
    int one = 1;
    if (setsockopt(sockfd, IPPROTO_IP, IP_HDRINCL, &one, sizeof(one)) < 0) {
        perror("Error en setsockopt");
        close(sockfd);
        return 1;
    }

    printf("=== CLIENTE ICMP - Enviando paquete ICMP personalizado ===\n");
    printf("Destino: %s\n", dest_ip);
    printf("Tipo ICMP: Echo Request (8)\n");
    printf("Datos: %s\n", data);
    printf("Enviando paquete...\n");

    // Enviar paquete
    if (sendto(sockfd, packet, ip_header->tot_len, 0,
               (struct sockaddr *)&dest_addr, sizeof(dest_addr)) < 0) {
        perror("Error enviando paquete");
        close(sockfd);
        return 1;
    }

    printf("✓ Paquete ICMP enviado exitosamente!\n");
    printf("El sniffer continuo debería capturarlo y mostrarlo.\n");

    close(sockfd);
    return 0;
}
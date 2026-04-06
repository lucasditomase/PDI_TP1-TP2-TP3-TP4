#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <sys/socket.h>
#include <sys/select.h>

#define PORT 12345
#define BUFFER_SIZE 1024

int main() {
    int sock;
    struct sockaddr_in server_addr;
    char buffer[BUFFER_SIZE];
    fd_set read_fds;

    // Crear socket
    sock = socket(AF_INET, SOCK_STREAM, 0);
    if (sock < 0) {
        perror("socket");
        exit(EXIT_FAILURE);
    }

    // Configurar dirección del servidor
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(PORT);
    inet_pton(AF_INET, "127.0.0.1", &server_addr.sin_addr);

    // Conectarse al servidor
    if (connect(sock, (struct sockaddr *)&server_addr, sizeof(server_addr)) < 0) {
        perror("connect");
        exit(EXIT_FAILURE);
    }

    printf("Conectado al servidor. Puedes escribir mensajes:\n");

    while (1) {
        FD_ZERO(&read_fds);
        FD_SET(0, &read_fds);      // Entrada estándar
        FD_SET(sock, &read_fds);   // Socket

        if (select(sock + 1, &read_fds, NULL, NULL, NULL) < 0) {
            perror("select");
            exit(EXIT_FAILURE);
        }

        // Entrada del usuario
        if (FD_ISSET(0, &read_fds)) {
            fgets(buffer, BUFFER_SIZE, stdin);
            send(sock, buffer, strlen(buffer), 0);
        }

        // Mensaje del servidor
        if (FD_ISSET(sock, &read_fds)) {
            int valread = read(sock, buffer, BUFFER_SIZE - 1);
            if (valread <= 0) {
                printf("Desconectado del servidor.\n");
                break;
            }
            buffer[valread] = '\0';
            printf("Mensaje: %s", buffer);
        }
    }

    close(sock);
    return 0;
}
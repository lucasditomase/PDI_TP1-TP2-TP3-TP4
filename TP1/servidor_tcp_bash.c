#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <netinet/in.h>
#include <arpa/inet.h>

#define MAX 1024
#define PORT 8080

int main() {
    int server_fd, client_fd;
    struct sockaddr_in server_addr, client_addr;
    char buffer[MAX];
    char client_name[50];

    // Crear socket
    server_fd = socket(AF_INET, SOCK_STREAM, 0);
    if (server_fd == -1) {
        perror("Socket no pudo abrirse ... error ...");
        exit(1);
    }

    // Configurar estructura
    server_addr.sin_family = AF_INET;
    server_addr.sin_addr.s_addr = INADDR_ANY;
    server_addr.sin_port = htons(PORT);
    memset(&(server_addr.sin_zero), 0, 8);

    // Asociar dirección y puerto
    if (bind(server_fd, (struct sockaddr*)&server_addr, sizeof(server_addr)) != 0) {
        perror("Bind falló");
        exit(1);
    }

    // Escuchar conexiones
    if (listen(server_fd, 1) != 0) {
        perror("Listen con error...");
        exit(1);
    }

    printf("Servidor esperando conexión en el puerto %d...\n", PORT);
    socklen_t addr_size = sizeof(client_addr);
    client_fd = accept(server_fd, (struct sockaddr*)&client_addr, &addr_size);
    if (client_fd < 0) {
        perror("Falló al aceptar conexión");
        exit(1);
    }

    // Recibir nombre del cliente
    recv(client_fd, client_name, sizeof(client_name), 0);
    printf("Cliente conectado: %s\n", client_name);

    while (1) {
        // Recibir mensaje del cliente
        memset(buffer, 0, MAX);
        int bytes = recv(client_fd, buffer, MAX, 0);
        if (bytes <= 0) {
            printf("Cliente desconectado.\n");
            break;
        }

        if (strncmp(buffer, "FIN", 3) == 0) {
            printf("%s ha finalizado la conexión.\n", client_name);
            break;
        }

        printf("%s: %s", client_name, buffer);

        // Enviar respuesta
        printf("Servidor: ");
        memset(buffer, 0, MAX);
        fgets(buffer, MAX, stdin);
        send(client_fd, buffer, strlen(buffer), 0);

        if (strncmp(buffer, "FIN", 3) == 0) {
            printf("Servidor finaliza la conexión.\n");
            break;
        }
    }

    close(client_fd);
    close(server_fd);
    return 0;
}
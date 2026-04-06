#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <netinet/in.h>
#include <arpa/inet.h>

#define MAX 1024
#define PORT 8080

int main() {
    int sockfd;
    struct sockaddr_in server_addr;
    char buffer[MAX];
    char name[50];

    // Crear socket
    sockfd = socket(AF_INET, SOCK_STREAM, 0);
    if (sockfd == -1) {
        perror("Socket falló");
        exit(1);
    }

    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(PORT);
    inet_pton(AF_INET, "127.0.0.1", &server_addr.sin_addr);
    memset(&(server_addr.sin_zero), 0, 8);

    // Conectar al servidor
    if (connect(sockfd, (struct sockaddr*)&server_addr, sizeof(server_addr)) != 0) {
        perror("Conexión falló");
        exit(1);
    }

    // Enviar nombre
    printf("Ingresar nombre: ");
    fgets(name, sizeof(name), stdin);
    name[strcspn(name, "\n")] = 0; // Eliminar salto de línea
    send(sockfd, name, strlen(name), 0);

    while (1) {
        // Enviar mensaje
        printf("%s: ", name);
        memset(buffer, 0, MAX);
        fgets(buffer, MAX, stdin);
        send(sockfd, buffer, strlen(buffer), 0);

        if (strncmp(buffer, "FIN", 3) == 0) {
            printf("Terminando la conexión...\n");
            break;
        }

        // Recibir respuesta
        memset(buffer, 0, MAX);
        int bytes = recv(sockfd, buffer, MAX, 0);
        if (bytes <= 0 || strncmp(buffer, "FIN", 3) == 0) {
            printf("Servidor finalizó la conexión.\n");
            break;
        }

        printf("Servidor: %s", buffer);
    }

    close(sockfd);
    return 0;
}
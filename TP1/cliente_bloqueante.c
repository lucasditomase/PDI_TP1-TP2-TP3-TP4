#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>

#define PORT 12345
#define BUFFER_SIZE 1024

int main() {
    int sock;
    struct sockaddr_in server_addr;
    char buffer[BUFFER_SIZE];

    // 1. Crear socket
    sock = socket(AF_INET, SOCK_STREAM, 0);
    if (sock == -1) {
        perror("Error al abrir el socket ...");
        exit(EXIT_FAILURE);
    }

    // 2. Configurar dirección del servidor
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(PORT);
    server_addr.sin_addr.s_addr = inet_addr("127.0.0.1");

    // 3. Conectar al servidor
    if (connect(sock, (struct sockaddr *)&server_addr, sizeof(server_addr)) < 0) {
        perror("Error al conectar");
        exit(EXIT_FAILURE);
    }

    printf("Conectado al servidor. Escribe mensajes y presiona Enter.\n");

    // 4. Bucle principal bloqueante
    while (1) {
        printf("> ");
        fgets(buffer, BUFFER_SIZE, stdin);  // BLOQUEA esperando entrada
        send(sock, buffer, strlen(buffer), 0);

        // Leer respuesta del servidor
        int valread = read(sock, buffer, BUFFER_SIZE - 1);
        if (valread <= 0) {
            printf("Conexión cerrada por el servidor.\n");
            break;
        }

        buffer[valread] = '\0';
        printf("Servidor: %s", buffer);
    }

    close(sock);
    return 0;
}
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <signal.h>

#define MAX 1024
#define PORT 8080

void handle_client(int client_fd, struct sockaddr_in client_addr) {
    char buffer[MAX];
    char name[50] = "Cliente";
    char client_ip[INET_ADDRSTRLEN];
    char response[MAX + 100];
    pid_t pid = getpid();

    inet_ntop(AF_INET, &(client_addr.sin_addr), client_ip, INET_ADDRSTRLEN);
    int client_port = ntohs(client_addr.sin_port);

    printf("[PID %d] Conexión desde %s:%d\n", pid, client_ip, client_port);

    // Recibir nombre del cliente
    recv(client_fd, name, sizeof(name), 0);
    printf("[PID %d] Cliente: %s\n", pid, name);

    while (1) {
        memset(buffer, 0, MAX);
        int bytes = recv(client_fd, buffer, MAX, 0);
        if (bytes <= 0) {
            printf("[PID %d] %s se desconectó.\n", pid, name);
            break;
        }

        // Verificar si cliente quiere finalizar
        if (strncmp(buffer, "FIN", 3) == 0) {
            printf("[PID %d] %s finalizó la conexión.\n", pid, name);
            break;
        }

        printf("[%s | PID %d]: %s", name, pid, buffer);

        // Preparar respuesta automática
        snprintf(response, sizeof(response),
                 "Este es el mensaje recibido por el servidor: %s", buffer);
        send(client_fd, response, strlen(response), 0);
    }

    close(client_fd);
    printf("[PID %d] Proceso hijo termina.\n", pid);
    exit(0);
}

int main() {
    int server_fd, client_fd;
    struct sockaddr_in server_addr, client_addr;

    signal(SIGCHLD, SIG_IGN); // Evita procesos zombies

    server_fd = socket(AF_INET, SOCK_STREAM, 0);
    if (server_fd == -1) {
        perror("Error al crear socket");
        exit(1);
    }

    server_addr.sin_family = AF_INET;
    server_addr.sin_addr.s_addr = INADDR_ANY;
    server_addr.sin_port = htons(PORT);
    memset(&(server_addr.sin_zero), 0, 8);

    if (bind(server_fd, (struct sockaddr*)&server_addr, sizeof(server_addr)) != 0) {
        perror("Error en bind");
        exit(1);
    }

    if (listen(server_fd, 5) != 0) {
        perror("Error en listen");
        exit(1);
    }

    printf("Servidor concurrente activo en puerto %d...\n", PORT);

    socklen_t len = sizeof(client_addr);
    while (1) {
        client_fd = accept(server_fd, (struct sockaddr*)&client_addr, &len);
        if (client_fd < 0) {
            perror("Fallo en accept");
            continue;
        }

        pid_t pid = fork();
        if (pid == 0) {
            close(server_fd);
            handle_client(client_fd, client_addr);
        } else if (pid > 0) {
            printf("[PID %d] Cliente conectado. Proceso hijo PID %d\n", getpid(), pid);
            close(client_fd);
        } else {
            perror("Error en fork");
            close(client_fd);
        }
    }

    close(server_fd);
    return 0;
}
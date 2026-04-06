#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <arpa/inet.h>
#include <netinet/in.h>
#include <sys/select.h>

#define PORT 12345
#define MAX_CLIENTS 10
#define BUFFER_SIZE 1024

int main() {
    int server_fd, new_socket, client_sockets[MAX_CLIENTS];
    struct sockaddr_in address;
    fd_set read_fds;
    int max_sd, sd, activity, valread;
    char buffer[BUFFER_SIZE];
    
    // CAMBIO 1: Declarar addrlen al inicio de la función main
    socklen_t addrlen; 
    
    // Inicializar todos los clientes a 0
    for (int i = 0; i < MAX_CLIENTS; i++) {
        client_sockets[i] = 0;
    }

    // Crear socket
    if ((server_fd = socket(AF_INET, SOCK_STREAM, 0)) == 0) {
        perror("socket falló");
        exit(EXIT_FAILURE);
    }

    // Configurar dirección del servidor
    address.sin_family = AF_INET;
    address.sin_addr.s_addr = INADDR_ANY;
    address.sin_port = htons(PORT);

    // Enlazar socket al puerto
    if (bind(server_fd, (struct sockaddr *)&address, sizeof(address)) < 0) {
        perror("bind falló");
        exit(EXIT_FAILURE);
    }

    // Escuchar conexiones entrantes
    if (listen(server_fd, 3) < 0) {
        perror("listen");
        exit(EXIT_FAILURE);
    }

    printf("Servidor escuchando en puerto %d...\n", PORT);

    while (1) {
        // Limpiar conjunto de descriptores
        FD_ZERO(&read_fds);
        FD_SET(server_fd, &read_fds);
        max_sd = server_fd;

        // Agregar sockets de clientes al conjunto
        for (int i = 0; i < MAX_CLIENTS; i++) {
            sd = client_sockets[i];
            if (sd > 0) FD_SET(sd, &read_fds);
            if (sd > max_sd) max_sd = sd;
        }

        // Esperar actividad
        activity = select(max_sd + 1, &read_fds, NULL, NULL, NULL);

        if ((activity < 0) && (errno != EINTR)) {
            printf("Error en select\n");
        }

        // Nueva conexión
        if (FD_ISSET(server_fd, &read_fds)) {
            
            // CAMBIO 2: Solo asignamos el valor, ya no declaramos la variable
            addrlen = sizeof(address); 
            
            if ((new_socket = accept(server_fd, (struct sockaddr *)&address, &addrlen)) < 0) {
                perror("accept");
                exit(EXIT_FAILURE);
            }

            printf("Nueva conexión: socket fd %d, IP %s, puerto %d\n",
                   new_socket, inet_ntoa(address.sin_addr), ntohs(address.sin_port));

            // Agregar a la lista de clientes
            for (int i = 0; i < MAX_CLIENTS; i++) {
                if (client_sockets[i] == 0) {
                    client_sockets[i] = new_socket;
                    break;
                }
            }
        }

        // Revisar mensajes de clientes
        for (int i = 0; i < MAX_CLIENTS; i++) {
            sd = client_sockets[i];

            if (FD_ISSET(sd, &read_fds)) {
                if ((valread = read(sd, buffer, BUFFER_SIZE)) == 0) {
                    // Desconexión
                    
                    // CAMBIO 3: Asignamos el tamaño y usamos la variable correctamente (ya no hace falta el casteo a socklen_t*)
                    addrlen = sizeof(address); 
                    getpeername(sd, (struct sockaddr*)&address, &addrlen);
                    
                    printf("Cliente desconectado: IP %s, puerto %d\n",
                           inet_ntoa(address.sin_addr), ntohs(address.sin_port));
                    close(sd);
                    client_sockets[i] = 0;
                } else {
                    buffer[valread] = '\0';
                    printf("Mensaje recibido: %s", buffer);

                    // Reenviar mensaje a otros clientes
                    for (int j = 0; j < MAX_CLIENTS; j++) {
                        if (client_sockets[j] != 0 && client_sockets[j] != sd) {
                            send(client_sockets[j], buffer, strlen(buffer), 0);
                        }
                    }
                }
            }
        }
    }

    return 0;
}
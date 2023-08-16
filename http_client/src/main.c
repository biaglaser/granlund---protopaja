#include <zephyr/net/net_core.h>
#include <zephyr/net/net_ip.h>
#include <zephyr/net/socket.h>
#include <zephyr/net/http_client.h>

#define SERVER_HOST  "granlund.protopaja.aalto.fi"
#define SERVER_PORT  80
#define SERVER_URL   "https://granlund.protopaja.aalto.fi"
#define POST_DATA    "key1=value1&key2=value2"


void main(void)
{
    struct sockaddr_in server_addr;
    static struct http_request req;
    static char response[1024];

    /* Initialize the server address struct */
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(SERVER_PORT);
    inet_pton(AF_INET, SERVER_HOST, &server_addr.sin_addr);

    /* Prepare HTTP request */
    req.method = HTTP_POST;
    req.url = SERVER_URL;
    req.protocol = "HTTP/1.1";
    req.host = SERVER_HOST;
    req.header_fields = NULL;
    req.content = POST_DATA;
    req.content_len = strlen(POST_DATA);
    req.response = response;
    req.response_len = sizeof(response);

    /* Send HTTP POST request */
    int client_fd = socket(AF_INET, SOCK_STREAM, 0);
    connect(client_fd, (struct sockaddr *)&server_addr, sizeof(server_addr));
    http_client_req(client_fd, &req, K_FOREVER, NULL);

    /* Log the response */
    printk("HTTP Response: %s\n", response);

    /* Close socket */
    close(client_fd);
}

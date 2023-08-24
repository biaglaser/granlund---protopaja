/*
 * Copyright (c) 2020 Nordic Semiconductor ASA
 *
 * SPDX-License-Identifier: LicenseRef-Nordic-5-Clause
 */

#include <string.h>
#include <zephyr/kernel.h>
#include <stdlib.h>
#include <zephyr/net/socket.h>
#include <modem/nrf_modem_lib.h>
#include <zephyr/net/tls_credentials.h>
#include <modem/lte_lc.h>
#include <modem/modem_key_mgmt.h>
#include <zephyr/device.h>
#include <zephyr/drivers/uart.h>
#define HTTPS_PORT 443

#define HTTPS_HOSTNAME "granlund.protopaja.aalto.fi"

#define HTTP_HEADERS_TEMPLATE "POST /akbar HTTP/1.1\r\nHost: granlund.protopaja.aalto.fi\r\nContent-Length: %u\r\nConnection: close\r\n\r\n"

#define RECV_BUF_SIZE 2048
#define TLS_SEC_TAG 42


#define UART_DEVICE_NODE DT_CHOSEN(zephyr_shell_uart)
#define UART_DEVICE_NODE2 DT_NODELABEL(uart1)
#define MSG_SIZE 32

/* queue to store up to 10 messages (aligned to 4-byte boundary) */
K_MSGQ_DEFINE(uart_msgq, MSG_SIZE, 10, 4);
K_MSGQ_DEFINE(uart_msgq2, MSG_SIZE, 10, 4);

static const struct device *const uart_dev = DEVICE_DT_GET(UART_DEVICE_NODE);
static const struct device *const uart_dev2 = DEVICE_DT_GET(UART_DEVICE_NODE2);

/* receive buffer used in UART ISR callback */
static char rx_buf[MSG_SIZE];
static int rx_buf_pos;
static char rx_buf2[MSG_SIZE];
static int rx_buf_pos2;





char send_buf[1024]={0};
static char recv_buf[RECV_BUF_SIZE];

/* Certificate for `example.com` */
static const char cert[] = {
	#include "../cert/isrgrootx1.pem"
};

BUILD_ASSERT(sizeof(cert) < KB(4), "Certificate too large");

/* Provision certificate to modem */
int cert_provision(void)
{
	int err;
	bool exists;
	int mismatch;

	/* It may be sufficient for you application to check whether the correct
	 * certificate is provisioned with a given tag directly using modem_key_mgmt_cmp().
	 * Here, for the sake of the completeness, we check that a certificate exists
	 * before comparing it with what we expect it to be.
	 */
	err = modem_key_mgmt_exists(TLS_SEC_TAG, MODEM_KEY_MGMT_CRED_TYPE_CA_CHAIN, &exists);
	if (err) {
		printk("Failed to check for certificates err %d\n", err);
		return err;
	}

	if (exists) {
		mismatch = modem_key_mgmt_cmp(TLS_SEC_TAG,
					      MODEM_KEY_MGMT_CRED_TYPE_CA_CHAIN,
					      cert, strlen(cert));
		if (!mismatch) {
			printk("Certificate match\n");
			return 0;
		}

		printk("Certificate mismatch\n");
		err = modem_key_mgmt_delete(TLS_SEC_TAG, MODEM_KEY_MGMT_CRED_TYPE_CA_CHAIN);
		if (err) {
			printk("Failed to delete existing certificate, err %d\n", err);
		}
	}

	printk("Provisioning certificate\n");

	/*  Provision certificate to the modem */
	err = modem_key_mgmt_write(TLS_SEC_TAG,
				   MODEM_KEY_MGMT_CRED_TYPE_CA_CHAIN,
				   cert, sizeof(cert) - 1);
	if (err) {
		printk("Failed to provision certificate, err %d\n", err);
		return err;
	}

	return 0;
}

/* Setup TLS options on a given socket */
int tls_setup(int fd)
{
	int err;
	int verify;

	/* Security tag that we have provisioned the certificate with */
	const sec_tag_t tls_sec_tag[] = {
		TLS_SEC_TAG,
	};

#if defined(CONFIG_SAMPLE_TFM_MBEDTLS)
	err = tls_credential_add(tls_sec_tag[0], TLS_CREDENTIAL_CA_CERTIFICATE, cert, sizeof(cert));
	if (err) {
		return err;
	}
#endif

	/* Set up TLS peer verification */
	enum {
		NONE = 0,
		OPTIONAL = 1,
		REQUIRED = 2,
	};

	verify = REQUIRED;

	err = setsockopt(fd, SOL_TLS, TLS_PEER_VERIFY, &verify, sizeof(verify));
	if (err) {
		printk("Failed to setup peer verification, err %d\n", errno);
		return err;
	}

	/* Associate the socket with the security tag
	 * we have provisioned the certificate with.
	 */
	err = setsockopt(fd, SOL_TLS, TLS_SEC_TAG_LIST, tls_sec_tag,
			 sizeof(tls_sec_tag));
	if (err) {
		printk("Failed to setup TLS sec tag, err %d\n", errno);
		return err;
	}

	err = setsockopt(fd, SOL_TLS, TLS_HOSTNAME, HTTPS_HOSTNAME, sizeof(HTTPS_HOSTNAME) - 1);
	if (err) {
		printk("Failed to setup TLS hostname, err %d\n", errno);
		return err;
	}
	return 0;
}
/*
 * Read characters from UART until line end is detected. Afterwards push the
 * data to the message queue.
 */
void serial_cb(const struct device *dev, void *user_data)
{
	uint8_t c;

	if (!uart_irq_update(uart_dev)) {
		return;
	}

	while (uart_irq_rx_ready(uart_dev)) {

		uart_fifo_read(uart_dev, &c, 1);

		if ((c == '\n' || c == '\r') && rx_buf_pos > 0) {
			/* terminate string */
			rx_buf[rx_buf_pos] = '\0';

			/* if queue is full, message is silently dropped */
			k_msgq_put(&uart_msgq, &rx_buf, K_NO_WAIT);

			/* reset the buffer (it was copied to the msgq) */
			rx_buf_pos = 0;
		} else if (rx_buf_pos < (sizeof(rx_buf) - 1)) {
			rx_buf[rx_buf_pos++] = c;
		}
		/* else: characters beyond buffer size are dropped */
	}
}

void serial_cb2(const struct device *dev, void *user_data)
{
	uint8_t c;

	if (!uart_irq_update(uart_dev2)) {
		return;
	}

	while (uart_irq_rx_ready(uart_dev2)) {

		uart_fifo_read(uart_dev2, &c, 1);

		if ((c == '\n' || c == '\r') && rx_buf_pos2 > 0) {
			/* terminate string */
			rx_buf2[rx_buf_pos2] = '\0';

			/* if queue is full, message is silently dropped */
			k_msgq_put(&uart_msgq2, &rx_buf2, K_NO_WAIT);

			/* reset the buffer (it was copied to the msgq) */
			rx_buf_pos2 = 0;
		} else if (rx_buf_pos2 < (sizeof(rx_buf2) - 1)) {
			rx_buf2[rx_buf_pos2++] = c;
		}
		/* else: characters beyond buffer size are dropped */
	}
}

/*
 * Print a null-terminated string character by character to the UART interface
 */
void print_uart(char *buf)
{
	int msg_len = strlen(buf);

	for (int i = 0; i < msg_len; i++) {
		uart_poll_out(uart_dev, buf[i]);
	}
}

void print_uart2(char *buf)
{
	int msg_len = strlen(buf);

	for (int i = 0; i < msg_len; i++) {
		uart_poll_out(uart_dev2, buf[i]);
	}
}

void http_post_payload(char *payload) {
    int fd;
    char *p;
    int bytes;
    size_t off;
    struct addrinfo *res;
    struct addrinfo hints = {
        .ai_family = AF_INET,
        .ai_socktype = SOCK_STREAM,
    };
    
    /* Prepare the HTTP request using the payload */
    int payload_len = strlen(payload);
    int headers_len = snprintf(send_buf, sizeof(send_buf), HTTP_HEADERS_TEMPLATE, payload_len);
    memcpy(send_buf + headers_len, payload, payload_len);
    int total_len = headers_len + payload_len;

    int err = getaddrinfo(HTTPS_HOSTNAME, NULL, &hints, &res);
    if (err) {
        printk("getaddrinfo() failed, err %d\n", errno);
        return;
    }

	((struct sockaddr_in *)res->ai_addr)->sin_port = htons(HTTPS_PORT);

	if (IS_ENABLED(CONFIG_SAMPLE_TFM_MBEDTLS)) {
		fd = socket(AF_INET, SOCK_STREAM | SOCK_NATIVE_TLS, IPPROTO_TLS_1_2);
	} else {
		fd = socket(AF_INET, SOCK_STREAM, IPPROTO_TLS_1_2);
	}
	if (fd == -1) {
		printk("Failed to open socket!\n");
		goto clean_up;
	}

	/* Setup TLS socket options */
    err = tls_setup(fd);
    if (err) {
        goto clean_up;
    }

    printk("Connecting to %s\n", HTTPS_HOSTNAME);
    err = connect(fd, res->ai_addr, sizeof(struct sockaddr_in));
    if (err) {
        printk("connect() failed, err: %d\n", errno);
        goto clean_up;
    }

    off = 0;
    do {
        bytes = send(fd, &send_buf[off], total_len - off, 0);
        if (bytes < 0) {
            printk("send() failed, err %d\n", errno);
            goto clean_up;
        }
        off += bytes;
    } while (off < total_len);

    printk("Sent %d bytes\n", off);

    off = 0;
    do {
        bytes = recv(fd, &recv_buf[off], RECV_BUF_SIZE - off, 0);
        if (bytes < 0) {
            printk("recv() failed, err %d\n", errno);
            goto clean_up;
        }
        off += bytes;
    } while (bytes != 0);

    printk("Received %d bytes\n", off);
		/* Make sure recv_buf is NULL terminated (for safe use with strstr) */
	if (off < sizeof(recv_buf)) {
		recv_buf[off] = '\0';
	} else {
		recv_buf[sizeof(recv_buf) - 1] = '\0';
	}
	/* Print HTTP response */
    p = strstr(recv_buf, "\r\n");
    if (p) {
        off = p - recv_buf;
        recv_buf[off + 1] = '\0';
        printk("\n>\t %s\n\n", recv_buf);
    }

    printk("Finished, closing socket.\n");

clean_up:
    freeaddrinfo(res);
    (void)close(fd);
}


void main(void)
{
	int err;
	int fd;
	char *p;
	int bytes;
	size_t off;
	struct addrinfo *res;
	struct addrinfo hints = {
		.ai_family = AF_INET,
		.ai_socktype = SOCK_STREAM,
	};
	char tx_buf[MSG_SIZE];
	char tx_buf2[MSG_SIZE];

	if (!device_is_ready(uart_dev)) {
		printk("UART device not found!");
		return;
	}
	if (!device_is_ready(uart_dev2)) {
		printk("UART device not found!");
		return;
	}

	/* configure interrupt and callback to receive data */
	uart_irq_callback_user_data_set(uart_dev, serial_cb, NULL);
	uart_irq_rx_enable(uart_dev);
	uart_irq_callback_user_data_set(uart_dev2, serial_cb2, NULL);
	uart_irq_rx_enable(uart_dev2);
	printk("HTTPS client sample started\n\r");

#if !defined(CONFIG_SAMPLE_TFM_MBEDTLS)
	/* Provision certificates before connecting to the LTE network */
	err = cert_provision();
	if (err) {
		return;
	}
#endif

	printk("Waiting for network.. ");
	err = lte_lc_init_and_connect();
	if (err) {
		printk("Failed to connect to the LTE network, err %d\n", err);
		return;
	}
	printk("OK\n");

	while(1)
	{
		if (k_msgq_get(&uart_msgq, &tx_buf, K_NO_WAIT) == 0) {
			print_uart("Echo: ");
			print_uart(tx_buf);
			print_uart("\r\n");
		}
		if(k_msgq_get(&uart_msgq2, &tx_buf2, K_NO_WAIT) == 0) {
			print_uart("Echo: ");
			print_uart(tx_buf2);
			print_uart("\r\n");
			print_uart2("Echo: ");
			print_uart2(tx_buf2);
			print_uart2("\r\n");
			http_post_payload(tx_buf2);
		}
	}	
}

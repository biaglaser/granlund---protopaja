/*
 * Copyright (c) 2022 Libre Solar Technologies GmbH
 *
 * SPDX-License-Identifier: Apache-2.0
 */

#include <zephyr/kernel.h>
#include <zephyr/device.h>
#include <zephyr/drivers/uart.h>

#include <string.h>

/* change this to any other UART peripheral if desired */
#define UART_DEVICE_NODE DT_CHOSEN(zephyr_shell_uart)

#define MSG_SIZE 32

/* queue to store up to 10 messages (aligned to 4-byte boundary) */
K_MSGQ_DEFINE(uart_msgq, MSG_SIZE, 10, 4);

static const struct device *const uart_dev = DEVICE_DT_GET(UART_DEVICE_NODE);

/* receive buffer used in UART ISR callback */
static char rx_buf[MSG_SIZE];
static int rx_buf_pos;

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

// receiver
void main(void)
{
    if (!device_is_ready(uart_dev)) {
        printk("UART device not found!\n");
        return;
    }


    uart_irq_callback_user_data_set(uart_dev, serial_cb, NULL);
    uart_irq_rx_enable(uart_dev);

    char rx_buf[MSG_SIZE];

    while (k_msgq_get(&uart_msgq, &rx_buf, K_FOREVER) == 0) {
        print_uart("Echo: ");
        print_uart(rx_buf);
        print_uart("\r\n");
    }
}


/** sender
void main(void)
{
    if (!device_is_ready(uart_dev)) {
        printk("UART device not found!\n");
        return;
    }

    while (1) {
        print_uart("Message from Board 1\r\n");
        k_sleep(K_SECONDS(5));
    }
}

*/
 
/** receiver
void main(void)
{
    if (!device_is_ready(uart_dev)) {
        printk("UART device not found!\n");
        return;
    }


    uart_irq_callback_user_data_set(uart_dev, serial_cb, NULL);
    uart_irq_rx_enable(uart_dev);

    char rx_buf[MSG_SIZE];

    while (k_msgq_get(&uart_msgq, &rx_buf, K_FOREVER) == 0) {
        print_uart("Echo: ");
        print_uart(rx_buf);
        print_uart("\r\n");
    }
}

*/
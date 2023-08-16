#include <zephyr/drivers/uart.h>
#include <zephyr/sys/printk.h>
#include <zephyr/bluetooth/bluetooth.h>
#include <zephyr/bluetooth/hci.h>

#define NAME_LEN 30
struct device *uart_dev;

void uart_send(const char *data) {
    for (size_t i = 0; i < strlen(data); i++) {
        uart_poll_out(uart_dev, data[i]);
    }
}

static void scan_cb(const bt_addr_le_t *addr, int8_t rssi, uint8_t adv_type,
                    struct net_buf_simple *buf)
{
    char addr_str[BT_ADDR_LE_STR_LEN];
    char message[512];

    bt_addr_le_to_str(addr, addr_str, sizeof(addr_str));
    snprintf(message, sizeof(message), "Device found: %s (RSSI %d)\n", addr_str, rssi);
    printk("%s", message);
    uart_send(message);

    /* Sending payload over UART */
    char payload_str[3];
    for (int i = 0; i < buf->len; i++) {
        snprintf(payload_str, sizeof(payload_str), "%02x", buf->data[i]);
        uart_send(payload_str);
        uart_send(" ");  // Space delimiter
    }
    uart_send("\n");
}


void main(void)
{
    int err;

    printk("Starting Bluetooth Observer...\n");

    err = bt_enable(NULL);
    if (err) {
        printk("Bluetooth init failed (err %d)\n", err);
        return;
    }

    printk("Bluetooth initialized\n");

    struct bt_le_scan_param scan_params = {
        .type       = BT_HCI_LE_SCAN_PASSIVE,
        .options    = BT_LE_SCAN_OPT_NONE,
        .interval   = BT_GAP_SCAN_FAST_INTERVAL,
        .window     = BT_GAP_SCAN_FAST_WINDOW,
    };

    err = bt_le_scan_start(&scan_params, scan_cb);
    if (err) {
        printk("Starting scanning failed (err %d)\n", err);
        return;
    }

    printk("Scanning started\n");

	uart_dev = device_get_binding("UART_0");
    if (!uart_dev) {
        printk("Cannot find UART_0!\n");
        return;
    }
}
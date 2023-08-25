#include <bluefruit.h>

// Number of target devices
#define NUM_TARGET_DEVICES 2

// Target MAC addresses in little-endian format
const uint8_t target_mac[NUM_TARGET_DEVICES][6] = {
  {0x03, 0xF5, 0x9F, 0x3E, 0xA4, 0xF6},  // Address for F6:4:3E:9F:F5:03
  {0x31, 0x17, 0x28, 0x2B, 0xB0, 0xE3}   // Address for E3:B0:2B:28:17:31
};

void setup() 
{
  Serial.begin(115200);
  while ( !Serial ) delay(10);   // for nrf52840 with native usb

  Serial.println("Bluefruit52 Central Scan Example");
  Serial.println("--------------------------------\n");

  Bluefruit.begin(0, 1);
  Bluefruit.setTxPower(4);
  Bluefruit.setName("Bluefruit52");

  Bluefruit.setConnLedInterval(250);
  Bluefruit.Scanner.setRxCallback(scan_callback);
  Bluefruit.Scanner.start(0);

  Serial.println("Scanning ...");
}

void scan_callback(ble_gap_evt_adv_report_t* report)
{
  for (int i = 0; i < NUM_TARGET_DEVICES; i++)
  {
    if (memcmp(report->peer_addr.addr, target_mac[i], 6) == 0)
    {
      Serial.println("Timestamp Addr              Rssi Data");

      Serial.printf("%09d ", millis());

      // MAC is in little endian --> print reverse
      Serial.printBufferReverse(report->peer_addr.addr, 6, ':');
      Serial.print(" ");

      Serial.print(report->rssi);
      Serial.print("  ");

      Serial.printBuffer(report->data.p_data, report->data.len, '-');
      Serial.println();
      Serial.println();

      // Once a match is found, no need to check other MAC addresses for this report
      break;
    }
  }

  // Continue scanning
  Bluefruit.Scanner.resume();
}

void loop() 
{
  // nothing to do
}

#include <bluefruit.h>

void setup() 
{
  Serial.begin(115200);
  while ( !Serial ) delay(10);   // for nrf52840 with native usb

  Serial.println("Bluefruit52 Central Scan Example");
  Serial.println("--------------------------------\n");

  // Initialize Bluefruit with maximum connections as Peripheral = 0, Central = 1
  // SRAM usage required by SoftDevice will increase dramatically with number of connections
  Bluefruit.begin(0, 1);
  Bluefruit.setTxPower(4);    // Check bluefruit.h for supported values
  Bluefruit.setName("Bluefruit52");

  // Start Central Scan
  Bluefruit.setConnLedInterval(250);
  Bluefruit.Scanner.setRxCallback(scan_callback);
  Bluefruit.Scanner.start(0);

  Serial.println("Scanning ...");
}

void scan_callback(ble_gap_evt_adv_report_t* report)
{
  // Print timestamp
  Serial.printf("%09d ", millis());
  
  // Print MAC Address (in reverse order)
  Serial.printBufferReverse(report->peer_addr.addr, 6, ':');

  // Print data
  Serial.print("  ");
  Serial.printBuffer(report->data.p_data, report->data.len, '-');

  // Add a newline
  Serial.println();

  // Resume scanning (required for Softdevice v6)
  Bluefruit.Scanner.resume();
}

void loop() 
{
  // nothing to do
}

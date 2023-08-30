#include <bluefruit.h>

uint64_t getTime(void) {
  static uint64_t combinedTime=0;
  static uint32_t previousTime=0;
  uint32_t currentTime=micros();
  combinedTime+=currentTime-previousTime;
  previousTime=currentTime;
  return(combinedTime);
}
void scan_callback(ble_gap_evt_adv_report_t* report)
{
  Serial.printf("%lu ", getTime());
  for (int i = 0; i < 6; ++i) {
    Serial.printf("%02x", report->peer_addr.addr[i]);
  }
  Serial.print(" ");
  for (int i = 0; i < report->data.len; ++i) {
    Serial.printf("%02x", report->data.p_data[i]);
  }

  Serial.print("\n"); /**
  // Print timestamp
  Serial.printf("%d ", millis());
  
  // Print MAC Address (in reverse order)
  Serial.printBufferReverse(report->peer_addr.addr, 6, '');

  // Print data
  Serial.print(" ");
  Serial.printBuffer(report->data.p_data, report->data.len, '-');

  // Add a newline
  Serial.println();
*/
  // Resume scanning (required for Softdevice v6)
  Bluefruit.Scanner.resume();
}

void setup() 
{
  Serial.begin(115200);
  while ( !Serial ) delay(10);   // for nrf52840 with native usb
  // Initialize Bluefruit with maximum connections as Peripheral = 0, Central = 1
  // SRAM usage required by SoftDevice will increase dramatically with number of connections
  Bluefruit.begin(0, 1);
  Bluefruit.setTxPower(4);    // Check bluefruit.h for supported values
  Bluefruit.setName("Bluefruit52");

  // Start Central Scan
  Bluefruit.setConnLedInterval(250);
  Bluefruit.Scanner.setRxCallback(scan_callback);
  Bluefruit.Scanner.start(0);
}



void loop() 
{
  // nothing to do
}

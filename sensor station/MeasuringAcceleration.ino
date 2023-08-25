#include <bluefruit.h>
#include "ADXL335.h"

ADXL335 accelerometer;

void setup() 
{
  Serial.begin(115200);
  Bluefruit.begin();

  // Turn off Blue LED for lowest power consumption
  Bluefruit.autoConnLed(false);
  Bluefruit.setTxPower(0);    // Check bluefruit.h for supported values
  
  accelerometer.begin();

  // Setup the initial advertising packet
  startAdv();

  Serial.println("Broadcasting beacon with accelerometer data");
}

void startAdv(void)
{  
  uint8_t customData[6]; // 2 bytes for each axis
  updateCustomData(customData);

  // Add/Update the data
  Bluefruit.Advertising.addData(BLE_GAP_AD_TYPE_MANUFACTURER_SPECIFIC_DATA, customData, sizeof(customData));

  // Secondary Scan Response packet (optional)
  Bluefruit.ScanResponse.addName();
  
  // Setup advertising parameters
  Bluefruit.Advertising.restartOnDisconnect(true);
  Bluefruit.Advertising.setInterval(160, 160);    // in unit of 0.625 ms
  Bluefruit.Advertising.setFastTimeout(30);       // number of seconds in fast mode
  Bluefruit.Advertising.start(0);                 // 0 = Don't stop advertising after n seconds  
}

void loop() 
{
  // Refresh advertising data every 500 ms
  delay(500);
  updateAdvData();
}

void updateAdvData() 
{
  uint8_t customData[6]; // 2 bytes for each axis
  updateCustomData(customData);

  // Update the data
  Bluefruit.Advertising.addData(BLE_GAP_AD_TYPE_MANUFACTURER_SPECIFIC_DATA, customData, sizeof(customData));
}

void updateCustomData(uint8_t* customData)
{
  int16_t x, y, z;
  accelerometer.getXYZ(&x, &y, &z);

  customData[0] = (uint8_t)(x >> 8);  // X High byte
  customData[1] = (uint8_t)x;         // X Low byte
  customData[2] = (uint8_t)(y >> 8);  // Y High byte
  customData[3] = (uint8_t)y;         // Y Low byte
  customData[4] = (uint8_t)(z >> 8);  // Z High byte
  customData[5] = (uint8_t)z;         // Z Low byte
}

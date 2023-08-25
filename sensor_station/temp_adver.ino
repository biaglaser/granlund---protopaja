#include <Adafruit_Sensor.h>
#include <DHT.h>
#include <DHT_U.h>
#include <bluefruit.h>

#define DHTPIN 2
#define DHTTYPE DHT22
DHT_Unified dht(DHTPIN, DHTTYPE);
uint32_t delayMS;

void setup() {
  Serial.begin(115200);

  // DHT initialization
  dht.begin();
  sensor_t sensor;
  dht.temperature().getSensor(&sensor);
  delayMS = sensor.min_delay / 1000;

  // Bluetooth initialization
  Bluefruit.begin();
  Bluefruit.autoConnLed(false);
  Bluefruit.setTxPower(0);  
  startAdv();
}

void startAdv(void) {  
  Bluefruit.Advertising.clearData();
  Bluefruit.ScanResponse.clearData();

  uint8_t customData[2]; // 2 bytes for temperature
  updateCustomData(customData);

  Bluefruit.Advertising.addData(BLE_GAP_AD_TYPE_MANUFACTURER_SPECIFIC_DATA, customData, sizeof(customData));
  Bluefruit.ScanResponse.addName();
  
  Bluefruit.Advertising.restartOnDisconnect(true);
  Bluefruit.Advertising.setInterval(160, 160);
  Bluefruit.Advertising.setFastTimeout(30);       
  Bluefruit.Advertising.start(0);                 
}

void loop() {
  delay(500);
  Bluefruit.Advertising.stop();
  delay(10);
  startAdv();
}

void updateCustomData(uint8_t* customData) {
  // Get temperature data
  sensors_event_t tempEvent;
  dht.temperature().getEvent(&tempEvent);
  int16_t temp = (int16_t)(tempEvent.temperature * 100);  // Convert float to int with 2 decimal precision
  customData[0] = (uint8_t)(temp >> 8);
  customData[1] = (uint8_t)temp;
}

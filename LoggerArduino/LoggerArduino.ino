// Include the libraries we need
#include <OneWire.h>
#include <DallasTemperature.h>

#define ONE_WIRE_BUS 2
#define TEMPERATURE_PRECISION 12
#define SENSORS_NUMBER 6
#define ERROR_CODE 9999
#define CYCLE_TIME 1000
#define CONVERSION_DELAY 750/ (1 << (12-TEMPERATURE_PRECISION))
#define SEPARATOR " "
#define BAUD_RATE 9600



OneWire oneWire(ONE_WIRE_BUS);

DallasTemperature sensors(&oneWire);

DeviceAddress sensorsAddress[SENSORS_NUMBER] = {
   
{0x10, 0xD8, 0x25, 0x96, 0x03, 0x08, 0x00, 0xCE},
{0x10, 0xEF, 0x7D, 0x8B, 0x03, 0x08, 0x00, 0xA8},
{0x10, 0xAC, 0x47, 0x8B, 0x03, 0x08, 0x00, 0xBD},
{0x10, 0xA2, 0xAA, 0x8B, 0x03, 0x08, 0x00, 0x98},
{0x10, 0xA1, 0x23, 0x8C, 0x03, 0x08, 0x00, 0x7F}, 
{0x10, 0x70, 0x45, 0x8C, 0x03, 0x08, 0x00, 0x01}
  
}; 

bool activeSensorsFlag[SENSORS_NUMBER] = {false};



void setup(void)
{
  Serial.begin(BAUD_RATE);
  delay(300);
  Serial.println("Dallas Temperature IC Control Library Demo");

  sensors.begin();

  Serial.print("Locating devices...");
  Serial.print("Found ");
  Serial.print(sensors.getDeviceCount(), DEC);
  Serial.println(" devices");

  Serial.print("Parasite power is: ");
  if (sensors.isParasitePowerMode()) Serial.println("ON");
  else Serial.println("OFF");

  for(int i=0; i<SENSORS_NUMBER; i++){
    if (!sensors.isConnected(sensorsAddress[i])){
      Serial.print("Unable to find address for Device ");
      Serial.println(i);
    }
    else{
      activeSensorsFlag[i] = true;
      
      Serial.print("Device ");
      Serial.print(i);
      Serial.print(" Address: ");
      printAddress(sensorsAddress[i]);
      Serial.println();
      sensors.setResolution(sensorsAddress[i], TEMPERATURE_PRECISION);
      Serial.print("Device ");
      Serial.print(i);
      Serial.print(" Resolution: ");
      Serial.print(sensors.getResolution(sensorsAddress[i]), DEC);
      Serial.println();
    }
  }

  sensors.setWaitForConversion(false); 
  Serial.println();

}


void loop(void)
{

  unsigned long time = millis();

  while(millis() < time - 200 + CYCLE_TIME - CONVERSION_DELAY){ delay(10); } 
  sensors.requestTemperatures();
  while(millis() < time + CYCLE_TIME){ delay(5); } 
  
  for(int i=0; i<SENSORS_NUMBER; i++) {
    float temp = sensors.getTempC(sensorsAddress[i]);
    if(activeSensorsFlag[i] && temp != DEVICE_DISCONNECTED_C) Serial.print(temp);
    else Serial.print(ERROR_CODE);
    Serial.print(SEPARATOR);
  }
  Serial.println();

}

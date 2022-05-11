
// Arduino UNO has 5.0 volt with a max ADC value of 1023 steps
// ACS712 5A  uses 185 mV per A
// ACS712 20A uses 100 mV per A
// ACS712 30A uses  66 mV per A
//A0 AC curr
//A1 AC VOLT
//A2 DC curr
//A3 DC VOLT
// include the library code:

#include "ACS712.h"

#include <Wire.h>

ACS712 ACS(A0, 4.47, 1023, 66);
ACS712 ACS_2(A2, 4.47, 1023, 66);
byte cmd;

//digital read
int ac_curr_dig = 0; //save the digital conversion of current
int ac_volt_dig = 0; //save the digital conversion of voltage

int ac_curr_dig_2 = 0; //save the digital conversion of current
int ac_volt_dig_2 = 0; //save the digital conversion of voltage

unsigned int sample = 1;     //number of samples to take before sending to lcd


const int led = 13;
const int rele = 12;
int led_state = LOW;

void setup()
{
  // set up the LCD's number of columns and rows:
  Serial.begin(9600);
  pinMode(led, OUTPUT);
  pinMode(rele, OUTPUT);
  ACS.autoMidPoint();
  ACS_2.autoMidPoint();

  Wire.begin(0x20);
  Wire.onReceive(receiveEvent);
  Wire.onRequest(sendEvent);

  Serial.println(__FILE__);
  digitalWrite(led, led_state);
  digitalWrite(rele, LOW); //disabled
}

void loop()
{
  //CURRENTS AC AND DC
  int dig_mA = 0;
  int dig_mA_2 = 0;
  int temp_1 = 0;
  int temp_2 = 0;
  for (int i = 0; i < sample; i++)
  {

    dig_mA += ACS.mA_AC(60);

    dig_mA_2 +=analogRead(A2); //currenct DC
  }

  ac_curr_dig = (dig_mA / sample);
  ac_curr_dig_2 = (dig_mA_2 / sample);


  //testing Dc current other way
  
  float voltage_dc_panel =(analogRead(A2)+0.5) * (4.47 / 1024.0);
  Serial.print("voltage ACS panel");
  Serial.println(voltage_dc_panel);
  float dc_v_acs=((voltage_dc_panel)-2.22  )/0.066;
  Serial.print("Current ACS Panel");
  Serial.println(dc_v_acs);

  //

  //VOLTAGES AC AND DC
  int dig_volt = 0;
  int dig_volt_2 = 0;
  for (int i = 0; i < sample; i++)
  {
    dig_volt += analogRead(A1);
    dig_volt_2 += analogRead(A3);
  }
  ac_volt_dig = (dig_volt / sample);
  ac_volt_dig_2 = (dig_volt_2 / sample);

  cmd = Wire.read(); //read the received byte
  switch (cmd)
  {
  case 0x0A:
    Serial.print("received: ");
    Serial.println(cmd, HEX);
    break;
  case 0x0B:
    digitalWrite(rele, HIGH); //disabled
    Serial.print("received: ");
    Serial.println(cmd, HEX);
    break;
  case 0x0C:
    digitalWrite(rele, LOW); //disabled
    Serial.print("received: ");
    Serial.println(cmd, HEX);
    break;
  default:
    break;
  }
  cmd = 0;
}

void receiveEvent(int hoeMny)
{


}

void sendEvent()
{
  //Serial.println("entre en sendEvent");
  if (led_state == 1)
    led_state = 0;
  else
    led_state = 1;

  digitalWrite(led, led_state);
  Wire.write(ac_curr_dig >> 8 & 0xff);   //byte 1
  Wire.write(ac_curr_dig);               //byte 2
  Wire.write(ac_volt_dig >> 8 & 0xff);   //byte 3
  Wire.write(ac_volt_dig);               //byte 4
  Wire.write(ac_curr_dig_2 >> 8 & 0xff); //byte 5
  Wire.write(ac_curr_dig_2);             //byte 6
  Wire.write(ac_volt_dig_2 >> 8 & 0xff); //byte 7
  Wire.write(ac_volt_dig_2);             //byte 8
}

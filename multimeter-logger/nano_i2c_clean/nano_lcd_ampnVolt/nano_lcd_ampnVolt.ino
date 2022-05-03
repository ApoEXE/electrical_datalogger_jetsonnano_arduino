
// Arduino UNO has 5.0 volt with a max ADC value of 1023 steps
// ACS712 5A  uses 185 mV per A
// ACS712 20A uses 100 mV per A
// ACS712 30A uses  66 mV per A

// include the library code:

#include "ACS712.h"

#include<Wire.h>

ACS712  ACS(A0, 5.0, 1023, 66);
ACS712  ACS_2(A2, 5.0, 1023, 66);

//digital read
int ac_curr_dig = 0;//save the digital conversion of current
int ac_volt_dig = 0;//save the digital conversion of voltage
unsigned int sample = 50;//number of samples to take before sending to lcd
volatile bool flag1 = false; //send on received command from jetson


void setup() {
  // set up the LCD's number of columns and rows:
  Serial.begin(9600);
  pinMode(13, OUTPUT);
  pinMode(11, OUTPUT);
  ACS.autoMidPoint();
  ACS_2.autoMidPoint();
  //ACS.setNoisemV(70);
  Wire.begin(0x20);
  Wire.onReceive(receiveEvent);
  Wire.onRequest(sendEvent);

  Serial.print("sin miedo al exito");
  digitalWrite(13, HIGH);
}

void loop() {


  if (flag1 == true)
  {
    Serial.println("Code recived. sending status");
    flag1 = false;

  }
 
  double dig_mA = 0;
  for(int i = 0; i< sample; i++)
      dig_mA += ACS.mA_AC(60);
  int mA = (dig_mA/sample);
  ac_curr_dig = mA;
  float AC_amp = mA/1000.0;
  if(AC_amp < 0.07){
    AC_amp = 0;
    ac_curr_dig=0;
  }
  //Serial.print("AC_amp ");
  //Serial.print(AC_amp);
  //Serial.print(" ");

  double dig_volt = 0;
  for(int i = 0; i< sample; i++){
      dig_volt += analogRead(A1);
  }
  int anaVolt = (dig_volt/sample);
  ac_volt_dig = anaVolt;
  
  //float volt_div = anaVolt * 5.1/1023.0;
  //float volt_in = volt_div*(1000+880000)/1000;
  //float volt_ac = (volt_in/sqrt(2)) + 5;
  //Serial.print("AC_volt ");
  //Serial.println(volt_ac);
  //Serial.print(" ");
 
}

void receiveEvent(int hoeMny)
{
  byte cmd = Wire.read();  //read the received byte
  if (cmd == 0x0A)    //be sure that 0x0A is coming from MEGA
  {
    flag1  = true;
    
  }
}

void sendEvent()
{
  Serial.println("entre en sendEvent");

  Wire.write(ac_curr_dig>>8&0xff);
  Wire.write(ac_curr_dig);
  Wire.write(ac_volt_dig>>8&0xff);
  Wire.write(ac_volt_dig);
}

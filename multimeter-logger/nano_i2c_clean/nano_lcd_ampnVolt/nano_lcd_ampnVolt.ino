
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

#include<Wire.h>

ACS712  ACS(A0, 5.0, 1023, 66);
ACS712  ACS_2(A2, 5.0, 1023, 66);

//digital read
int ac_curr_dig = 0;//save the digital conversion of current
int ac_volt_dig = 0;//save the digital conversion of voltage

int ac_curr_dig_2 = 0;//save the digital conversion of current
int ac_volt_dig_2 = 0;//save the digital conversion of voltage

unsigned int sample = 1;//number of samples to take before sending to lcd
volatile bool flag1 = false; //send on received command from jetson

const int led = 13;
int flag2  = 0;
int led_state = LOW;

void setup() {
  // set up the LCD's number of columns and rows:
  Serial.begin(9600);
  pinMode(led, OUTPUT);
  pinMode(A6, OUTPUT);
  ACS.autoMidPoint();
  ACS_2.autoMidPoint();

  //ACS.setNoisemV(70);
  Wire.begin(0x20);
  Wire.onReceive(receiveEvent);
  Wire.onRequest(sendEvent);

  Serial.println(__FILE__);
  digitalWrite(led, led_state);
}

void loop() {


  if (flag1 == true)
  {
    Serial.println("Code recived. sending status");
    flag1 = false;

  }
 
  double dig_mA = 0;
  double dig_mA_2 = 0;
  for(int i = 0; i< sample; i++)
      dig_mA += ACS.mA_AC(60);
      dig_mA_2 += ACS_2.mA_DC();
  int mA = (dig_mA/sample);
  int mA_2 = (dig_mA_2/sample);
  ac_curr_dig = mA;
  ac_curr_dig_2 = mA_2;
  float AC_amp = mA/1000.0;
  if(AC_amp < 0.07){
    AC_amp = 0;
    ac_curr_dig=0;
  }
  float AC_amp_2 = mA_2/1000.0;
    if(AC_amp_2  < 0.07){
    AC_amp_2  = 0;
    ac_curr_dig_2=0;
  }
  //Serial.print("AC_amp ");
  //Serial.print(AC_amp);
  //Serial.print(" ");

  double dig_volt = 0;
  double dig_volt_2 = 0;
  for(int i = 0; i< sample; i++){
      dig_volt += analogRead(A1);
      dig_volt_2 += analogRead(A3);
  }
  int anaVolt = (dig_volt/sample);
  ac_volt_dig = anaVolt;
  int anaVolt_2 = (dig_volt_2/sample);
  ac_volt_dig_2 = anaVolt_2;
  //float volt_div = anaVolt * 5.1/1023.0;
  //float volt_in = volt_div*(1000+880000)/1000;
  //float volt_ac = (volt_in/sqrt(2)) + 5;
  //Serial.print("AC_volt ");
  //Serial.println(volt_ac);
  //Serial.print(" ");
 
}

void receiveEvent(int hoeMny)
{
  if(led_state == 1){
  led_state = 0;
  }
  else
  led_state = 1;
  digitalWrite(led, led_state);

  byte cmd = Wire.read();  //read the received byte
  if (cmd == 0x0A)    //be sure that 0x0A is coming from MEGA
  {
    flag1  = true;
    
  }
  if (cmd == 0x0B)    //relay toggle
  {
    if(flag2==1){
    flag2  = 0;
    
    }
    else{
    flag2  = 1;
    }
    digitalWrite(A6, flag2);
    
  }
}

void sendEvent()
{
  Serial.println("entre en sendEvent");
  Wire.write(ac_curr_dig>>8&0xff);//byte 1
  Wire.write(ac_curr_dig);//byte 2
  Wire.write(ac_volt_dig>>8&0xff);//byte 3
  Wire.write(ac_volt_dig);//byte 4
  Wire.write(ac_curr_dig_2>>8&0xff);//byte 5
  Wire.write(ac_curr_dig_2);//byte 6
  Wire.write(ac_volt_dig_2>>8&0xff);//byte 7
  Wire.write(ac_volt_dig_2);//byte 8
}

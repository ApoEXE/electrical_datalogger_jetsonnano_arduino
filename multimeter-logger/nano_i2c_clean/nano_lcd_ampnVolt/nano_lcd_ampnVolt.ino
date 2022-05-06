
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
int flag2  = 1;
int led_state = LOW;

void setup() {
  // set up the LCD's number of columns and rows:
  Serial.begin(9600);
  pinMode(led, OUTPUT);
  pinMode(A6, OUTPUT);
  ACS.autoMidPoint();
  ACS_2.autoMidPoint();

  Wire.begin(0x20);
  Wire.onReceive(receiveEvent);
  Wire.onRequest(sendEvent);

  Serial.println(__FILE__);
  digitalWrite(led, led_state);
  digitalWrite(A6, HIGH);
}

void loop() {


  if (flag1 == true)
  {
    Serial.println("flag 1");
    flag1 = false;

  }


  digitalWrite(led, led_state);
  
  int dig_mA = 0;
  int dig_mA_2 = 0;
  int temp_1 = 0;
  int temp_2 = 0;
  for(int i = 0; i< sample; i++)
      
      temp_1 = ACS.mA_AC(60);
      if(temp_1 > 70)
          dig_mA += temp_1;
      temp_2 = ACS_2.mA_AC(60);
      if(temp_2 > 70)
          dig_mA_2 += temp_2;
   
  int mA = (dig_mA/sample);
  int mA_2 = (dig_mA_2/sample);
  ac_curr_dig = mA;
  ac_curr_dig_2 = mA_2;
  float ac_curr =(ac_curr_dig/1000);

  Serial.print("AC_amp ");
  Serial.print(ac_curr);
  Serial.print(" ");

  float ac_curr_panel =(ac_curr_dig_2/1000);

  Serial.print("panel_amp ");
  Serial.print(ac_curr_panel);
  Serial.println("");
  
  int dig_volt = 0;
  int dig_volt_2 = 0;
  for(int i = 0; i< sample; i++){
      dig_volt += analogRead(A1);
      dig_volt_2 += analogRead(A3);
  }
  int anaVolt = (dig_volt/sample);
  ac_volt_dig = anaVolt;
  int anaVolt_2 = (dig_volt_2/sample);
  ac_volt_dig_2 = anaVolt_2;

  
  float volt_div = (anaVolt+0.5) * (4.9/1024.0);
  float volt_in = volt_div*(1000+880000)/1000;
  float volt_ac = (volt_in/sqrt(2));
  Serial.print("AC_volt ");
  Serial.println(volt_ac);
  Serial.print(" ");

  float panel_volt_div = (anaVolt_2+0.5) * (4.9/1024.0);
  float panel_volt_in = panel_volt_div*(28200+10000)/10000;
  float panel_volt_ac = (panel_volt_in/sqrt(2));
  Serial.print("Panel_volt ");
  Serial.println(panel_volt_ac);
  Serial.print(" ");

  if(panel_volt_ac < 12.0){
      digitalWrite(A6, LOW);
    }
    else
      digitalWrite(A6, HIGH);
 
}

void receiveEvent(int hoeMny)
{

  
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
  }
   if(led_state == 1){
  led_state = 0;
  }
  else
  led_state = 1;
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

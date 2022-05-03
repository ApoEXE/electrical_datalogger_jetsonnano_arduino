/*
  LiquidCrystal Library - Hello World

 Demonstrates the use a 16x2 LCD display.  The LiquidCrystal
 library works with all LCD displays that are compatible with the
 Hitachi HD44780 driver. There are many of them out there, and you
 can usually tell them by the 16-pin interface.

 This sketch prints "Hello World!" to the LCD
 and shows the time.

  The circuit:
 * LCD RS pin to digital pin 12
 * LCD Enable pin to digital pin 11
 * LCD D4 pin to digital pin 5
 * LCD D5 pin to digital pin 4
 * LCD D6 pin to digital pin 3
 * LCD D7 pin to digital pin 2
 * LCD R/W pin to ground
 * LCD VSS pin to ground
 * LCD VCC pin to 5V
 * 10K resistor:
 * ends to +5V and ground
 * wiper to LCD VO pin (pin 3)

 Library originally added 18 Apr 2008
 by David A. Mellis
 library modified 5 Jul 2009
 by Limor Fried (http://www.ladyada.net)
 example added 9 Jul 2009
 by Tom Igoe
 modified 22 Nov 2010
 by Tom Igoe
 modified 7 Nov 2016
 by Arturo Guadalupi

 This example code is in the public domain.

 http://www.arduino.cc/en/Tutorial/LiquidCrystalHelloWorld

*/
// Arduino UNO has 5.0 volt with a max ADC value of 1023 steps
// ACS712 5A  uses 185 mV per A
// ACS712 20A uses 100 mV per A
// ACS712 30A uses  66 mV per A

// include the library code:

#include <LiquidCrystal.h>
#include "ACS712.h"

#include<Wire.h>

// initialize the library by associating any needed LCD interface pin
// with the arduino pin number it is connected to
const int rs = 12, en = 11, d4 = 5, d5 = 4, d6 = 3, d7 = 2;
LiquidCrystal lcd(rs, en, d4, d5, d6, d7);
ACS712  ACS(A0, 5.0, 1023, 66);
static char outstr[15];

//digital read
int ac_curr_dig = 0;//save the digital conversion of current
int ac_volt_dig = 0;//save the digital conversion of voltage
unsigned int sample = 50;//number of samples to take before sending to lcd
volatile bool flag1 = false; //send on received command from jetson


void setup() {
  // set up the LCD's number of columns and rows:
  Serial.begin(9600);
  lcd.begin(16, 2);
  // Print a message to the LCD.
  //lcd.print("Electrical Log");
  ACS.autoMidPoint();
  //ACS.setNoisemV(70);
  lcd.clear();
  Wire.begin(0x20);
  Wire.onReceive(receiveEvent);
  Wire.onRequest(sendEvent);

  Serial.print("sin miedo al exito");

}

void loop() {

// put your main code here, to run repeatedly:
  if (flag1 == true)
  {
    Serial.println("Code recived. sending status");
    flag1 = false;

  }

  // set the cursor to column 0, line 1
  // (note: line 1 is the second row, since counting begins with 0):
  lcd.setCursor(0, 1);
  double dig_mA = 0;
  for(int i = 0; i< sample; i++)
      dig_mA += ACS.mA_AC(60);
  int mA = (dig_mA/sample);
  ac_curr_dig = mA;
  float AC_amp = mA/1000.0;
  if(AC_amp < 0.07)
    AC_amp = 0;
  //Serial.print("AC_amp ");
  //Serial.print(AC_amp);
  //Serial.print(" ");
  lcd.print("Amp: ");
  lcd.setCursor(4, 1);
  dtostrf(AC_amp,7, 3, outstr);
  lcd.print(outstr);

  double dig_volt = 0;
  int conversion = 0;
  for(int i = 0; i< sample; i++){
    conversion = analogRead(A1);
      dig_volt += conversion;
      Serial.println(conversion);
  }
  int anaVolt = (dig_volt/sample);
  
  ac_volt_dig = anaVolt;
  float volt_div = anaVolt * 5.1/1023.0;

  float volt_in = volt_div*(1000+880000)/1000;

  float volt_ac = (volt_in/sqrt(2)) + 5;
  //Serial.print("AC_volt ");
  //Serial.println(volt_ac);
  //Serial.print(" ");
  
  lcd.setCursor(0, 0);
  lcd.print("Volt: ");
  dtostrf(volt_ac,7, 3, outstr);
  lcd.print(outstr);
 
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

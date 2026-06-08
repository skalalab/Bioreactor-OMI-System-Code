#include <Servo.h>
const int ledPin = 13;
// speed is the speed at which the pump will run
// values can range from 0 - 225. This can be changed
int speed;
// the pin that the arduino is connected to.
// the pin should be a PWM pin, see https://docs.arduino.cc/tutorials/uno-r4-minima/cheat-sheet/
int pin = 9;
int clampPin = 3;
Servo pump;

// runs when the board is powered on or resets
void setup() {
  Serial.begin(9600);
  //analogWriteResolution(8); //built in default is 8
  //Serial.setTimeout(50000); //how long in ms to wait for serial input. When using python should be small value, 
                          // when using serial monitor should be how long it should wait before shutting off/ larger value
                          // find a way to change this without having to upload every time
  delay(200);
  pinMode(ledPin, OUTPUT);
  pump.attach(pin);
  pinMode(clampPin, OUTPUT);
  // sets pin 9 to output signal
  }

void loop() {
  
  //stops the pump from running when given an input
  if (!Serial.available()) {
    return;
  } else{
  // returns the number of bytes available from serial

    
    
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();
    //int serialVal = cmd.parseInt();
    if(cmd == "0"){
      delay(50);
      //Serial.print("Serial value is ");
      //Serial.println(serialVal);
      Serial.println("Stopping pump ");
      pump.write(90);
      speed = 90;
      digitalWrite(clampPin, LOW);
      digitalWrite(ledPin, LOW);

    } else if (cmd != "0"){
      //input is validated in python program
      //Serial.print("Serial value is ");
      //Serial.println(serialVal);
      digitalWrite(clampPin, HIGH);
      digitalWrite(ledPin, HIGH);
      Serial.println("Setting speed to MAX");
      //Serial.println(serialVal);
      //speed = serialVal;
      speed = 0;
      // runs the pump at speed
      pump.write(speed);
    }
  }

}

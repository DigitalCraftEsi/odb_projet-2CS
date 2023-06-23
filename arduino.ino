#include <Stepper.h>
#include <OneWire.h>
#include <DallasTemperature.h>
#include <Servo.h>
#include <Ultrasonic.h>

struct Statistics {
  float coffee;
  float milk;
  float water;
  float sugar;
};
Servo servo;  
// Data wire is plugged into digital pin 2 on the Arduino
#define ONE_WIRE_BUS 2
const int CLPin = 50; 
const int MLPin = 6;
Ultrasonic Coffelevel(CLPin);
Ultrasonic Milklevel(MLPin);

// Setup a oneWire instance to communicate with any OneWire device
OneWire oneWire(ONE_WIRE_BUS);

// Pass oneWire reference to DallasTemperature library
DallasTemperature sensors(&oneWire);
const int DoorLock = 3;
const int SugarPin = 12;
const int pumpPin = 10;
const int heaterPin = 48;
const int CoffePin = 32;
bool milkStock = false;
bool coffeeStock = false;
bool pumpRunning = false;
bool heating=false;
const int moteur = 5;
double stepsPerRevolution = 2024;
Stepper myStepper2(stepsPerRevolution, 22, 23, 24, 25);
void setup() {
  myStepper2.setSpeed(5);
  pinMode(pumpPin, OUTPUT);
  digitalWrite(pumpPin, LOW);
  pinMode(heaterPin, OUTPUT);
  digitalWrite(heaterPin, LOW);
  sensors.begin();  // Start up the library
  Serial.begin(9600);
  pinMode(moteur,OUTPUT);
  digitalWrite(moteur, LOW);
  servo.attach(11);
  servo.write(85);
  pinMode(CoffePin,OUTPUT);
  digitalWrite(CoffePin, LOW);
  pinMode(SugarPin,OUTPUT);
  digitalWrite(SugarPin, HIGH);
  pinMode(DoorLock,OUTPUT);
  digitalWrite(DoorLock, HIGH);
}
void loop() {
   
  if (Serial.available() > 0) {
    String data = Serial.readStringUntil('\n');
    Serial.println(data);
    if(data == "water"){
      Serial.println("Preparing water");
      Serial.println("Heating water");
      bool temp = false ;
      float   temperature ;
      digitalWrite(heaterPin,HIGH);
      while(!temp){
        sensors.requestTemperatures();
        temperature = sensors.getTempCByIndex(0);
        if(temperature >= 60){
          digitalWrite(heaterPin,LOW);
          temp = true;
        }
      }
      digitalWrite(pumpPin, HIGH);
      delay(3000);
      digitalWrite(pumpPin,LOW);
      // Send the level of water to raspberry 
      Serial.println("Height");
      Serial.println("30");
      // Inform the raspberry that preparing water is done
      Serial.println("water Prepared");
    }else if(data == "coffee"){
      Serial.println("Preparing coffee");
      digitalWrite(CoffePin,HIGH);
      delay(300); // Keep the pump running for 2 seconds
      digitalWrite(CoffePin,LOW);
      float distanceC = Coffelevel.read();
      Serial.println("Height");
      Serial.println(distanceC);
      Serial.println("coffee Prepared");
    }else if(data == "milk"){
      Serial.println("Preparing milk");
      myStepper2.step(stepsPerRevolution);
      float distanceM = Milklevel.read();
      Serial.println("Height");
      Serial.println(distanceM);
      Serial.println("milk Prepared");      
    }else if(data == "sugar"){
      Serial.println("Preparing sugar");
      digitalWrite(SugarPin,LOW);
      delay(3000); // Keep the pump running for 2 seconds
      digitalWrite(SugarPin,HIGH);
      Serial.println("Height");
      Serial.println("50");
      Serial.println("sugar Prepared");
    }else if(data == "mix"){
      Serial.println("Mixing the ingredients");
      for (int angle = 85; angle <= 170; angle ++) {
        servo.write(angle);       // Définissez l'angle du servo
        delay(10);    
      }
      delay(1000);
      digitalWrite(moteur,HIGH);
      delay(2000);//normalement 5sec
      digitalWrite(moteur,LOW);
      delay(1000);
      for (int angle = 160; angle >= 85; angle --) {
        servo.write(angle);       // Définissez l'angle du servo
        delay(15);                // Attendez 15 millisecondes pour que le servo atteigne la position
      }
      Serial.println("Mixing done");
    }else if(data=="unlock"){
      Serial.println("Unlocking");
      // unlock the door of despenser
      digitalWrite(DoorLock,LOW);
      Serial.println("unlocked");
    }else if(data=="lock"){
      Serial.println("locking");
      // lock the electric lock      
      digitalWrite(DoorLock,HIGH);
      Serial.println("locked");
    }else if(data=="statistics"){
      Serial.println("statistics");
      Statistics stats;
      stats.coffee = Coffelevel.read();
      stats.milk = Milklevel.read();
      stats.water = 5.0;
      stats.sugar = 2.0;
      // prepare statistics in string to send it to raspberry
      String objString = "{\"coffee\":" + String(stats.coffee) + ",\"milk\":" + String(stats.milk) + ",\"water\":" + String(stats.water) + ",\"sugar\":" + String(stats.sugar) + "}";    // Print the string representation of the object
      Serial.println("statistics are");
      // send statistics
      Serial.println(objString);    
      Serial.println("Statistics done");
    }
  }
}

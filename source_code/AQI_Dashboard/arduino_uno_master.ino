#include "DHT.h"
#include <Wire.h> 
#include <LiquidCrystal_I2C.h>

#define DHTPIN 6
#define DHTTYPE DHT11
#define MQ135_PIN A1
#define DUST_LED_PIN 7
#define DUST_MEASURE_PIN A2

unsigned long lastSendTime = 0;
const long sendInterval = 10000; // Gửi mỗi 10 giây (test mode)

DHT dht(DHTPIN, DHTTYPE);
LiquidCrystal_I2C lcd(0x27, 16, 2);

void setup() {
  Serial.begin(9600);
  
  dht.begin();
  pinMode(DUST_LED_PIN, OUTPUT);
  
  lcd.init();      
  lcd.backlight();
  lcd.setCursor(0,0);
  lcd.print("System Ready!");
  
  delay(2000);
  
  // TEST: Gửi thử 1 dòng ngay khi khởi động
  Serial.println("{\"temperature\":25.0,\"humidity\":60.0,\"gas_level\":100.0,\"dust_density\":50.0}");
  lcd.clear();
  lcd.print("Test data sent!");
  delay(2000);
}

void loop() {
  unsigned long currentTime = millis();
  
  static unsigned long lastUiUpdate = 0;
  static unsigned long lastPageSwitch = 0;
  static int lcdPage = 0;
  
  static float temperature = 0;
  static float humidity = 0;
  static int gasRaw = 0;
  static float gasPPM = 0;
  static float dustVoltage = 0;
  static float dustDensityMg = 0;
  static float dustDensityUg = 0;

  if (currentTime - lastUiUpdate >= 1000) {
    lastUiUpdate = currentTime;

    temperature = dht.readTemperature();
    humidity = dht.readHumidity();
    
    gasRaw = analogRead(MQ135_PIN);
    gasPPM = (gasRaw * (5.0 / 1023.0)) * 100; 
    
    digitalWrite(DUST_LED_PIN, LOW);
    delayMicroseconds(280);
    int dustRaw = analogRead(DUST_MEASURE_PIN);
    delayMicroseconds(40);
    digitalWrite(DUST_LED_PIN, HIGH);
    delayMicroseconds(9680);
    
    dustVoltage = dustRaw * (5.0 / 1023.0);
    dustDensityMg = (dustVoltage - 0.1) / 0.17;
    if (dustDensityMg < 0) dustDensityMg = 0;
    dustDensityUg = dustDensityMg * 1000;

    if (currentTime - lastPageSwitch >= 3000) {
      lastPageSwitch = currentTime;
      lcdPage = (lcdPage + 1) % 3;
      lcd.clear();
    }

    if (lcdPage == 0) {
      lcd.setCursor(0, 0);
      lcd.print("Nhiet do:"); 
      lcd.print(temperature, 2); 
      lcd.print("*C");
      
      lcd.setCursor(0, 1);
      lcd.print("Do am:   "); 
      lcd.print(humidity, 2); 
      lcd.print("%");
    } 
    else if (lcdPage == 1) {
      lcd.setCursor(0, 0);
      lcd.print("Gas MQ135:  ");
      lcd.print(gasRaw);
      
      lcd.setCursor(0, 1);
      lcd.print("(Analog)");
    }
    else if (lcdPage == 2) {
      lcd.setCursor(0, 0);
      lcd.print("V_Bui:"); 
      lcd.print(dustVoltage, 2); 
      lcd.print("V");
      
      lcd.setCursor(0, 1);
      lcd.print("Bui:"); 
      lcd.print(dustDensityMg, 2); 
      lcd.print("mg/m3");
    }
  }
  
  if (currentTime - lastSendTime >= sendInterval) {
    lastSendTime = currentTime;
    
    if (isnan(temperature) || isnan(humidity)) {
      temperature = 25.0;
      humidity = 60.0;
    }
    
    sendDataToESP32(temperature, humidity, gasPPM, dustDensityUg);
  }
}

void sendDataToESP32(float temp, float hum, float gas, float dust) {
  // Debug: Hiển thị trên LCD
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Sending ESP32...");
  
  Serial.print("{\"temperature\":");
  Serial.print(temp, 1);
  Serial.print(",\"humidity\":");
  Serial.print(hum, 1);
  Serial.print(",\"gas_level\":");
  Serial.print(gas, 1);
  Serial.print(",\"dust_density\":");
  Serial.print(dust, 1);
  Serial.println("}");
  
  // Debug: Xác nhận đã gửi
  delay(500);
  lcd.setCursor(0, 1);
  lcd.print("Sent!");
  delay(1500);
}

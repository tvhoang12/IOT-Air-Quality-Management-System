"""
Code mẫu cho ESP32 để kết nối với hệ thống IoT Dashboard
"""

#include <WiFi.h>
#include <HTTPClient.h>
#include <DHT.h>
#include <ArduinoJson.h>

// WiFi Configuration
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";

// Server Configuration
const char* serverUrl = "http://YOUR_SERVER_IP:8000/devices/api/webhook/";
const char* apiKey = "YOUR_API_KEY";  // Lấy từ trang "Thêm thiết bị"

// DHT11 Configuration
#define DHTPIN 4
#define DHTTYPE DHT11
DHT dht(DHTPIN, DHTTYPE);

// MQ-135 Gas Sensor
#define MQ135_PIN 34

// GP2Y10 Dust Sensor
#define DUST_LED_PIN 2
#define DUST_MEASURE_PIN 35

// Timing
unsigned long lastSendTime = 0;
const long sendInterval = 5000; // Gửi dữ liệu mỗi 5 giây

void setup() {
  Serial.begin(115200);
  
  // Initialize sensors
  dht.begin();
  pinMode(DUST_LED_PIN, OUTPUT);
  
  // Connect to WiFi
  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");
  
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  
  Serial.println();
  Serial.println("WiFi connected!");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
}

void loop() {
  unsigned long currentTime = millis();
  
  if (currentTime - lastSendTime >= sendInterval) {
    lastSendTime = currentTime;
    
    // Read sensor data
    float temperature = dht.readTemperature();
    float humidity = dht.readHumidity();
    float gasLevel = readGasSensor();
    float dustDensity = readDustSensor();
    
    // Check if readings are valid
    if (isnan(temperature) || isnan(humidity)) {
      Serial.println("Failed to read from DHT sensor!");
      return;
    }
    
    // Send data to server
    sendDataToServer(temperature, humidity, gasLevel, dustDensity);
  }
}

float readGasSensor() {
  int rawValue = analogRead(MQ135_PIN);
  // Convert to ppm (simplified)
  float voltage = rawValue * (3.3 / 4095.0);
  float ppm = voltage * 100; // Đơn giản hóa, cần calibrate thực tế
  return ppm;
}

float readDustSensor() {
  digitalWrite(DUST_LED_PIN, LOW);
  delayMicroseconds(280);
  
  int dustValue = analogRead(DUST_MEASURE_PIN);
  
  delayMicroseconds(40);
  digitalWrite(DUST_LED_PIN, HIGH);
  delayMicroseconds(9680);
  
  // Convert to µg/m³
  float voltage = dustValue * (3.3 / 4095.0);
  float dustDensity = 0.17 * voltage - 0.1;
  
  if (dustDensity < 0) dustDensity = 0;
  
  return dustDensity * 1000; // Convert to µg/m³
}

void sendDataToServer(float temp, float hum, float gas, float dust) {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    
    http.begin(serverUrl);
    http.addHeader("Content-Type", "application/json");
    http.addHeader("X-API-Key", apiKey);
    
    // Create JSON payload
    StaticJsonDocument<256> doc;
    doc["temperature"] = temp;
    doc["humidity"] = hum;
    doc["gas_level"] = gas;
    doc["dust_density"] = dust;
    doc["ip_address"] = WiFi.localIP().toString();
    
    String jsonString;
    serializeJson(doc, jsonString);
    
    // Send POST request
    int httpResponseCode = http.POST(jsonString);
    
    if (httpResponseCode > 0) {
      String response = http.getString();
      Serial.println("HTTP Response code: " + String(httpResponseCode));
      Serial.println("Response: " + response);
      
      // Print sensor values
      Serial.println("--- Sensor Data ---");
      Serial.print("Temperature: "); Serial.print(temp); Serial.println(" °C");
      Serial.print("Humidity: "); Serial.print(hum); Serial.println(" %");
      Serial.print("Gas Level: "); Serial.print(gas); Serial.println(" ppm");
      Serial.print("Dust Density: "); Serial.print(dust); Serial.println(" µg/m³");
      Serial.println("------------------");
    } else {
      Serial.print("Error code: ");
      Serial.println(httpResponseCode);
    }
    
    http.end();
  } else {
    Serial.println("WiFi Disconnected");
  }
}

/*
 * Hướng dẫn kết nối phần cứng:
 * 
 * DHT11:
 * - VCC -> 3.3V
 * - GND -> GND
 * - DATA -> GPIO 4
 * 
 * MQ-135 Gas Sensor:
 * - VCC -> 5V
 * - GND -> GND
 * - AOUT -> GPIO 34 (ADC1)
 * 
 * GP2Y10 Dust Sensor:
 * - V-LED -> 5V
 * - LED -> GPIO 2
 * - GND -> GND
 * - Vo -> GPIO 35 (ADC1)
 * 
 * Thư viện cần cài đặt:
 * - DHT sensor library by Adafruit
 * - ArduinoJson by Benoit Blanchon
 * - HTTPClient (built-in)
 * 
 * Cách sử dụng:
 * 1. Cài đặt các thư viện cần thiết trong Arduino IDE
 * 2. Thay thế các giá trị YOUR_* bằng thông tin thực tế
 * 3. Upload code lên ESP32
 * 4. Mở Serial Monitor để xem log
 */

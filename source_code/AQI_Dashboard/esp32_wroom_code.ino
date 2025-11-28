/*
 * Code ESP32 WROOM gửi dữ liệu sensor đến Django Server
 * Hỗ trợ: DHT11, MQ-135, GP2Y10
 */

#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <DHT.h>

// ============ WIFI CONFIGURATION ============
const char* ssid = "YOUR_WIFI_SSID";           // Tên WiFi
const char* password = "YOUR_WIFI_PASSWORD";   // Mật khẩu WiFi

// ============ SERVER CONFIGURATION ============
const char* serverUrl = "http://192.168.1.100:8000/devices/api/webhook/";
const char* apiKey = "YOUR_API_KEY";  // Lấy từ trang "Thêm thiết bị"

// ============ SENSOR PINS ============
#define DHTPIN 4           // DHT11 data pin
#define DHTTYPE DHT11      // DHT sensor type
#define MQ135_PIN 34       // MQ-135 analog pin (ADC1)
#define DUST_LED_PIN 2     // GP2Y10 LED control
#define DUST_MEASURE_PIN 35 // GP2Y10 analog pin (ADC1)

// ============ TIMING ============
unsigned long lastSendTime = 0;
const long sendInterval = 5000; // Gửi dữ liệu mỗi 5 giây

// ============ SENSOR OBJECTS ============
DHT dht(DHTPIN, DHTTYPE);

// ============ SETUP ============
void setup() {
  Serial.begin(115200);
  delay(1000);
  
  Serial.println("\n\n========================================");
  Serial.println("ESP32 IoT Air Quality Monitor");
  Serial.println("========================================");
  
  // Initialize sensors
  dht.begin();
  pinMode(DUST_LED_PIN, OUTPUT);
  
  Serial.println("✓ Sensors initialized");
  
  // Connect to WiFi
  connectToWiFi();
}

// ============ MAIN LOOP ============
void loop() {
  // Kiểm tra kết nối WiFi
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("✗ WiFi disconnected! Reconnecting...");
    connectToWiFi();
  }
  
  unsigned long currentTime = millis();
  
  // Gửi dữ liệu theo interval
  if (currentTime - lastSendTime >= sendInterval) {
    lastSendTime = currentTime;
    
    // Đọc dữ liệu từ sensors
    float temperature = readTemperature();
    float humidity = readHumidity();
    float gasLevel = readGasSensor();
    float dustDensity = readDustSensor();
    
    // Kiểm tra dữ liệu hợp lệ
    if (isnan(temperature) || isnan(humidity)) {
      Serial.println("✗ Failed to read from DHT sensor!");
      return;
    }
    
    // Gửi dữ liệu lên server
    sendDataToServer(temperature, humidity, gasLevel, dustDensity);
  }
}

// ============ WIFI FUNCTIONS ============
void connectToWiFi() {
  Serial.print("\nConnecting to WiFi: ");
  Serial.println(ssid);
  
  WiFi.begin(ssid, password);
  
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 20) {
    delay(500);
    Serial.print(".");
    attempts++;
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\n✓ WiFi connected!");
    Serial.print("  IP address: ");
    Serial.println(WiFi.localIP());
    Serial.print("  Signal strength: ");
    Serial.print(WiFi.RSSI());
    Serial.println(" dBm");
  } else {
    Serial.println("\n✗ WiFi connection failed!");
  }
}

// ============ SENSOR READING FUNCTIONS ============
float readTemperature() {
  float temp = dht.readTemperature();
  return temp;
}

float readHumidity() {
  float hum = dht.readHumidity();
  return hum;
}

float readGasSensor() {
  // Đọc giá trị analog từ MQ-135
  int rawValue = analogRead(MQ135_PIN);
  
  // Convert sang voltage (ESP32: 0-4095 = 0-3.3V)
  float voltage = rawValue * (3.3 / 4095.0);
  
  // Convert sang ppm (công thức đơn giản hóa, cần calibrate cho chính xác)
  // Trong thực tế cần calibrate với khí chuẩn
  float ppm = voltage * 100;
  
  return ppm;
}

float readDustSensor() {
  // GP2Y10 dust sensor protocol
  digitalWrite(DUST_LED_PIN, LOW);
  delayMicroseconds(280);
  
  int dustValue = analogRead(DUST_MEASURE_PIN);
  
  delayMicroseconds(40);
  digitalWrite(DUST_LED_PIN, HIGH);
  delayMicroseconds(9680);
  
  // Convert sang voltage
  float voltage = dustValue * (3.3 / 4095.0);
  
  // Convert sang µg/m³ (theo datasheet GP2Y10)
  // V = 0.17 * Dust Density (mg/m³) + 0.1
  float dustDensity = (voltage - 0.1) / 0.17;
  
  if (dustDensity < 0) dustDensity = 0;
  
  return dustDensity * 1000; // Convert mg/m³ to µg/m³
}

// ============ SERVER COMMUNICATION ============
void sendDataToServer(float temp, float hum, float gas, float dust) {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("✗ WiFi not connected!");
    return;
  }
  
  HTTPClient http;
  
  // Begin connection
  http.begin(serverUrl);
  http.addHeader("Content-Type", "application/json");
  http.addHeader("X-API-Key", apiKey);
  http.setTimeout(10000); // 10 second timeout
  
  // Create JSON payload
  StaticJsonDocument<256> doc;
  doc["temperature"] = round(temp * 10) / 10.0;  // 1 chữ số thập phân
  doc["humidity"] = round(hum * 10) / 10.0;
  doc["gas_level"] = round(gas * 10) / 10.0;
  doc["dust_density"] = round(dust * 10) / 10.0;
  doc["ip_address"] = WiFi.localIP().toString();
  
  String jsonString;
  serializeJson(doc, jsonString);
  
  // Send POST request
  Serial.println("\n--- Sending Data ---");
  Serial.print("Server: ");
  Serial.println(serverUrl);
  Serial.print("Payload: ");
  Serial.println(jsonString);
  
  int httpResponseCode = http.POST(jsonString);
  
  // Handle response
  if (httpResponseCode > 0) {
    String response = http.getString();
    
    Serial.print("✓ Response code: ");
    Serial.println(httpResponseCode);
    Serial.print("  Response: ");
    Serial.println(response);
    
    // Print sensor values
    Serial.println("\n--- Sensor Readings ---");
    Serial.print("  Temperature: ");
    Serial.print(temp, 1);
    Serial.println(" °C");
    
    Serial.print("  Humidity: ");
    Serial.print(hum, 1);
    Serial.println(" %");
    
    Serial.print("  Gas Level: ");
    Serial.print(gas, 1);
    Serial.println(" ppm");
    
    Serial.print("  Dust Density: ");
    Serial.print(dust, 1);
    Serial.println(" µg/m³");
    Serial.println("---------------------");
    
  } else {
    Serial.print("✗ Error code: ");
    Serial.println(httpResponseCode);
    Serial.println("  Check server URL and API key!");
  }
  
  http.end();
}

/*
 * ============================================
 * HƯỚNG DẪN KẾT NỐI PHẦN CỨNG
 * ============================================
 * 
 * ESP32 WROOM Pinout:
 * 
 * DHT11 (Temperature & Humidity):
 *   VCC  -> 3.3V
 *   GND  -> GND
 *   DATA -> GPIO 4
 * 
 * MQ-135 (Gas Sensor):
 *   VCC  -> 5V (hoặc VIN)
 *   GND  -> GND
 *   AOUT -> GPIO 34 (ADC1_CH6)
 * 
 * GP2Y10 (Dust Sensor):
 *   V-LED -> 150Ω resistor -> 5V
 *   LED   -> GPIO 2
 *   GND   -> GND
 *   Vo    -> GPIO 35 (ADC1_CH7)
 *   
 * Lưu ý:
 * - Dùng ADC1 (GPIO 32-39) vì ADC2 conflict với WiFi
 * - MQ-135 cần thời gian preheat ~24h để ổn định
 * - GP2Y10 cần capacitor 220µF giữa V-LED và GND
 * 
 * ============================================
 * THƯ VIỆN CẦN CÀI ĐẶT (Arduino IDE)
 * ============================================
 * 
 * 1. DHT sensor library by Adafruit
 *    Tools -> Manage Libraries -> Search "DHT sensor"
 * 
 * 2. ArduinoJson by Benoit Blanchon
 *    Tools -> Manage Libraries -> Search "ArduinoJson"
 * 
 * 3. HTTPClient (Built-in với ESP32)
 * 
 * ============================================
 * CÁCH SỬ DỤNG
 * ============================================
 * 
 * 1. Cài đặt ESP32 board:
 *    File -> Preferences -> Additional Board URLs:
 *    https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
 * 
 * 2. Chọn board:
 *    Tools -> Board -> ESP32 Arduino -> ESP32 Dev Module
 * 
 * 3. Cấu hình:
 *    - Thay YOUR_WIFI_SSID, YOUR_WIFI_PASSWORD
 *    - Thay YOUR_API_KEY (lấy từ trang thêm thiết bị)
 *    - Thay IP server (nếu khác localhost)
 * 
 * 4. Upload code lên ESP32
 * 
 * 5. Mở Serial Monitor (115200 baud) để xem log
 * 
 * ============================================
 */

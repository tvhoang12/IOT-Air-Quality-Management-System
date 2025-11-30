/*
 * ESP32 Slave - Nhận dữ liệu từ Arduino Uno Master
 * 
 * Arduino Uno đọc cảm biến → Gửi qua Serial → ESP32 nhận → Gửi lên Website
 * 
 * KẾT NỐI PHẦN CỨNG:
 * ==========================================
 * Arduino Uno        →    ESP32 WROOM
 * ──────────────────────────────────────────
 * TX (Pin 1)         →    GPIO 16 (RX2)
 * RX (Pin 0)         →    GPIO 17 (TX2)
 * 5V                 →    VIN
 * GND                →    GND
 * ==========================================
 */
#include <WiFi.h>
#include <HTTPClient.h>
#include "ArduinoJson.h"
// ============ WIFI CONFIGURATION ============
const char* ssid = "PTIT_B5"; // Thay bằng tên WiFi của bạn
const char* password = ""; // Để trống nếu WiFi không có mật khẩu
// ============ SERVER CONFIGURATION ============
const char* serverUrl = "http://172.17.6.8:8000/devices/api/webhook/";
const char* apiKey = "sAwDq4ZWCq1nnXxc9QDPczVp2pAM2qvrpIbDRnEE2x8";
// const char* SECRET_KEY = "4cac78ad23e6e5bd41a4eb86f58c0e820a9c03eb5255b2a2bfec19baa7ec0077"
// ============ SERIAL PINS (ESP32 ↔ Arduino Uno) ============
#define RXD2 16  // ESP32 GPIO16 ← Arduino TX
#define TXD2 17  // ESP32 GPIO17 → Arduino RX
// ============ VARIABLES ============
String receivedData = "";
bool newData = false;
void setup() {
  // Serial cho debug (USB)
  Serial.begin(115200);
  delay(1000);
  
  Serial.println("\n========================================");
  Serial.println("ESP32 - Arduino Uno Bridge");
  Serial.println("========================================");
  
  // Serial2 giao tiếp với Arduino Uno
  Serial2.begin(9600, SERIAL_8N1, RXD2, TXD2);
  Serial.println("✓ Serial2: RX=GPIO16, TX=GPIO17, Baud=9600");
  
  // Kết nối WiFi
  connectWiFi();
  
  Serial.println("\n✓ Waiting for Arduino data...\n");
}
void loop() {
  // Kiểm tra WiFi
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("✗ WiFi lost! Reconnecting...");
    connectWiFi();
  }
  
  // Đọc dữ liệu từ Arduino Uno
  while (Serial2.available()) {
    char c = Serial2.read();
    
    if (c == '\n') {
      newData = true;
    } else {
      receivedData += c;
    }
  }
  
  // Xử lý dữ liệu khi nhận đủ 1 dòng
  if (newData && receivedData.length() > 0) {
    Serial.println("--- Data from Arduino ---");
    Serial.println(receivedData);
    
    parseAndSend(receivedData);
    
    receivedData = "";
    newData = false;
    Serial.println("-------------------------\n");
  }
}
void connectWiFi() {
  Serial.print("Connecting WiFi: ");
  Serial.println(ssid);
  
  WiFi.begin(ssid, password);
  
  int count = 0;
  while (WiFi.status() != WL_CONNECTED && count < 20) {
    delay(500);
    Serial.print(".");
    count++;
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\n✓ WiFi OK!");
    Serial.print("  IP: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("\n✗ WiFi Failed!");
  }
}
void parseAndSend(String jsonStr) {
  // Parse JSON từ Arduino
  StaticJsonDocument<256> doc;
  DeserializationError err = deserializeJson(doc, jsonStr);
  
  if (err) {
    Serial.print("✗ JSON Error: ");
    Serial.println(err.c_str());
    return;
  }
  
  // Lấy dữ liệu
  float temp = doc["temperature"] | 0.0;
  float hum = doc["humidity"] | 0.0;
  float gas = doc["gas_level"] | 0.0;
  float dust = doc["dust_density"] | 0.0;
  
  Serial.println("--- Sensor Values ---");
  Serial.printf("  Temp: %.1f°C\n", temp);
  Serial.printf("  Humidity: %.1f%%\n", hum);
  Serial.printf("  Gas: %.1f ppm\n", gas);
  Serial.printf("  Dust: %.1f µg/m³\n", dust);
  Serial.println("---------------------");
  
  // Gửi lên server
  sendToServer(temp, hum, gas, dust);
}
void sendToServer(float t, float h, float g, float d) {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("✗ No WiFi!");
    return;
  }
  
  HTTPClient http;
  http.begin(serverUrl);
  http.addHeader("Content-Type", "application/json");
  http.addHeader("X-API-Key", apiKey);
  http.setTimeout(10000);
  
  // Tạo JSON payload
  StaticJsonDocument<256> doc;
  doc["temperature"] = round(t * 10) / 10.0;
  doc["humidity"] = round(h * 10) / 10.0;
  doc["gas_level"] = round(g * 10) / 10.0;
  doc["dust_density"] = round(d * 10) / 10.0;
  doc["ip_address"] = WiFi.localIP().toString();
  
  String json;
  serializeJson(doc, json);
  
  Serial.println("--- Sending to Server ---");
  Serial.println(json);
  
  int code = http.POST(json);
  
  if (code > 0) {
    Serial.printf("✓ Response: %d\n", code);
    Serial.println(http.getString());
  } else {
    Serial.printf("✗ Error: %d\n", code);
  }
  
  http.end();
  Serial.println("-------------------------\n");
}
/*
 * ============================================
 * ARDUINO UNO PHẢI GỬI DỮ LIỆU DẠNG JSON:
 * ============================================
 * 
 * Ví dụ:
 * {"temperature":25.5,"humidity":60.0,"gas_level":150.0,"dust_density":35.0}
 * 
 * Code Arduino Uno (mẫu):
 * -----------------------
 * #include <DHT.h>
 * #define DHTPIN 2
 * #define DHTTYPE DHT11
 * DHT dht(DHTPIN, DHTTYPE);
 * 
 * void setup() {
 *   Serial.begin(9600);
 *   dht.begin();
 * }
 * 
 * void loop() {
 *   float t = dht.readTemperature();
 *   float h = dht.readHumidity();
 *   float g = analogRead(A0) * 0.5;  // MQ-135
 *   float d = analogRead(A1) * 0.17; // GP2Y10
 *   
 *   Serial.print("{\"temperature\":");
 *   Serial.print(t);
 *   Serial.print(",\"humidity\":");
 *   Serial.print(h);
 *   Serial.print(",\"gas_level\":");
 *   Serial.print(g);
 *   Serial.print(",\"dust_density\":");
 *   Serial.print(d);
 *   Serial.println("}");
 *   
 *   delay(60000); // 1 phút
 * }
 * 
 * ============================================
 * CÁCH SỬ DỤNG:
 * ============================================
 * 
 * 1. Nạp code này vào ESP32
 * 2. Nạp code đọc sensor vào Arduino Uno
 * 3. Kết nối:
 *    Arduino TX  → ESP32 GPIO16
 *    Arduino RX  → ESP32 GPIO17  
 *    Arduino 5V  → ESP32 VIN
 *    Arduino GND → ESP32 GND
 * 4. Thay WiFi SSID/Password và API Key
 * 5. Mở Serial Monitor (115200) để xem log
 * 
 * ============================================
 */

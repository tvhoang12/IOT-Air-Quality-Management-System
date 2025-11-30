#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

// ============ WIFI CONFIGURATION ============
const char* ssid = "PTIT_B5";
// const char* password = "123456788";

// ============ SERVER CONFIGURATION ============
const char* serverUrl = "http://172.17.9.139:8000/devices/api/webhook/";
const char* apiKey = "eX4fOrsMMMyGwWrfI0CnLAYqRV_-p4rsLIz3Znr0ZfY";
const char* secretKey = "e35da08fb9a8209efa9733d35dab2ec1bd0960aa00db83cb251861c8b76ca0b6";

// ============ SERIAL PINS (ESP32 ↔ Arduino Uno) ============
// Arduino D0 (RX) → ESP32 D17 (TX2)
// Arduino D1 (TX) → ESP32 D16 (RX2)
#define RXD2 16  // ESP32 GPIO16 ← Arduino D1 (TX)
#define TXD2 17  // ESP32 GPIO17 → Arduino D0 (RX)

// ============ VARIABLES ============
String receivedData = "";
bool newData = false;
unsigned long byteCount = 0;
unsigned long lastDebug = 0;

void setup() {
  // Serial cho debug (USB)
  Serial.begin(115200);
  delay(1000);
  
  Serial.println("\n========================================");
  Serial.println("ESP32 - Arduino Uno Bridge Receiver");
  Serial.println("========================================");
  
  // Serial2 để nhận dữ liệu từ Arduino Uno
  // RX2=GPIO16 nhận từ Arduino D1 (TX)
  // TX2=GPIO17 gửi đến Arduino D0 (RX)
  Serial2.begin(9600, SERIAL_8N1, RXD2, TXD2);
  Serial.println("✓ Serial2: RX=GPIO16, TX=GPIO17, Baud=9600");
  Serial.println("  Arduino D1 → ESP32 D16");
  Serial.println("  Arduino D0 ← ESP32 D17");
  
  // Kết nối WiFi
  connectWiFi();
  
  Serial.println("\n✓ Waiting for Arduino data...\n");
}

void loop() {
  unsigned long currentTime = millis();
  
  // Debug mỗi 5 giây
  if (currentTime - lastDebug >= 5000) {
    lastDebug = currentTime;
    Serial.printf("[DEBUG] Bytes received: %lu | Buffer: %d chars\n", 
                  byteCount, receivedData.length());
    if (byteCount == 0) {
      Serial.println("⚠️ Still waiting for Arduino data...");
    }
  }
  
  // Kiểm tra WiFi
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("✗ WiFi lost! Reconnecting...");
    connectWiFi();
  }
  
  // Đọc dữ liệu từ Arduino Uno qua Serial2
  while (Serial2.available()) {
    char c = Serial2.read();
    byteCount++;
    
    if (c == '\n') {
      // Kết thúc 1 dòng JSON
      newData = true;
    } else {
      receivedData += c;
    }
  }
  
  // Xử lý dữ liệu khi nhận đủ 1 dòng JSON
  if (newData && receivedData.length() > 0) {
    Serial.println("\n--- Data from Arduino ---");
    Serial.println(receivedData);
    
    // Parse JSON và gửi lên server
    parseAndSend(receivedData);
    
    // Reset để nhận dữ liệu mới
    receivedData = "";
    newData = false;
    Serial.println("-------------------------\n");
  }
}

void parseAndSend(String jsonStr) {
  // Parse JSON nhận từ Arduino
  StaticJsonDocument<256> doc;
  DeserializationError err = deserializeJson(doc, jsonStr);
  
  if (err) {
    Serial.print("✗ JSON Parse Error: ");
    Serial.println(err.c_str());
    return;
  }
  
  // Lấy dữ liệu từ JSON
  float temp = doc["temperature"] | 0.0;
  float hum = doc["humidity"] | 0.0;
  float gas = doc["gas_level"] | 0.0;
  float dust = doc["dust_density"] | 0.0;
  
  Serial.println("--- Parsed Sensor Values ---");
  Serial.printf("  Temperature: %.1f°C\n", temp);
  Serial.printf("  Humidity: %.1f%%\n", hum);
  Serial.printf("  Gas Level: %.1f ppm\n", gas);
  Serial.printf("  Dust Density: %.1f µg/m³\n", dust);
  Serial.println("----------------------------");
  
  // Gửi lên server
  sendToServer(temp, hum, gas, dust);
}

void connectWiFi() {
  Serial.print("Connecting WiFi: ");
  Serial.println(ssid);
  
  WiFi.begin(ssid);
  
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

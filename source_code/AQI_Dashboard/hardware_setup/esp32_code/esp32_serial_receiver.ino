/*
 * ESP32 SLAVE - WiFi Gateway nhận dữ liệu từ Arduino Uno Master
 * 
 * Mô hình: Arduino Uno (Master) → Serial → ESP32 (Slave) → WiFi → Server
 * 
 * Kết nối:
 * - Arduino TX (D1) → ESP32 RX2 (GPIO16)
 * - Arduino RX (D0) → ESP32 TX2 (GPIO17)
 * - Arduino GND → ESP32 GND
 * 
 * Chức năng:
 * - Nhận JSON từ Arduino qua Serial2
 * - Gửi lên Django server qua WiFi
 * - LED GPIO2 báo trạng thái
 */

#include <WiFi.h>
#include <HTTPClient.h>
#include <WiFiClientSecure.h>
#include <ArduinoJson.h>

// ===== CẤU HÌNH WIFI =====
const char* ssid = "YOUR_WIFI_SSID";      // ← Thay tên WiFi của bạn
const char* password = "YOUR_WIFI_PASS";  // ← Thay mật khẩu WiFi

// ===== CẤU HÌNH SERVER =====
// Lấy IP máy tính: ip addr show | grep "inet " | grep -v 127.0.0.1
// Ví dụ: inet 192.168.1.100/24 → Dùng 192.168.1.100

const char* serverUrl = "http://192.168.1.100:8000/api/sensor-data/";
// Hoặc dùng ngrok: "https://your-url.ngrok-free.dev/api/sensor-data/"

const char* deviceId = "UNO_MASTER_ESP32_SLAVE";

// ===== CẤU HÌNH HARDWARE =====
#define LED_PIN 2
#define RX2_PIN 16  // Nhận từ Arduino TX
#define TX2_PIN 17  // Gửi cho Arduino RX (không dùng)

// Serial2 để giao tiếp với Arduino
HardwareSerial ArduinoSerial(2);

// ===== HÀM GỬI DỮ LIỆU =====
bool sendDataToServer(String jsonData) {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("❌ WiFi không kết nối!");
    return false;
  }
  
  WiFiClientSecure *client = new WiFiClientSecure;
  if (!client) {
    Serial.println("❌ Không thể tạo WiFiClientSecure!");
    return false;
  }
  
  client->setInsecure();
  
  HTTPClient http;
  http.begin(*client, serverUrl);
  http.addHeader("Content-Type", "application/json");
  http.addHeader("ngrok-skip-browser-warning", "true");
  http.addHeader("User-Agent", "ESP32-UNO-AQI");
  http.setTimeout(15000);
  
  // Thêm device_id vào JSON
  StaticJsonDocument<256> doc;
  DeserializationError error = deserializeJson(doc, jsonData);
  
  if (error) {
    Serial.println("❌ JSON parse error!");
    delete client;
    return false;
  }
  
  doc["device_id"] = deviceId;
  
  String payload;
  serializeJson(doc, payload);
  
  Serial.println("\n📤 Gửi dữ liệu...");
  Serial.println("Payload: " + payload);
  
  int httpResponseCode = http.POST(payload);
  
  bool success = false;
  if (httpResponseCode > 0) {
    String response = http.getString();
    Serial.printf("✅ Response Code: %d\n", httpResponseCode);
    
    if (httpResponseCode == 201) {
      success = true;
      
      StaticJsonDocument<512> responseDoc;
      DeserializationError err = deserializeJson(responseDoc, response);
      
      if (!err) {
        bool savedToDb = responseDoc["saved_to_database"] | false;
        if (savedToDb) {
          Serial.println("💾 [SAVED TO DATABASE]");
        } else {
          Serial.println("⚡ [CACHED ONLY]");
        }
      }
    }
  } else {
    Serial.printf("❌ Lỗi HTTP: %d\n", httpResponseCode);
  }
  
  http.end();
  delete client;
  return success;
}

// ===== NHÁY LED =====
void blinkLED(int times, int delayMs) {
  for (int i = 0; i < times; i++) {
    digitalWrite(LED_PIN, HIGH);
    delay(delayMs);
    digitalWrite(LED_PIN, LOW);
    delay(delayMs);
  }
}

// ===== SETUP =====
void setup() {
  Serial.begin(115200);  // Serial Monitor
  ArduinoSerial.begin(115200, SERIAL_8N1, RX2_PIN, TX2_PIN);  // Serial2 cho Arduino
  
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);
  
  Serial.println("\n======================================================================");
  Serial.println("  ESP32 SLAVE - WIFI GATEWAY FOR ARDUINO UNO MASTER");
  Serial.println("======================================================================");
  Serial.println("Role: WiFi Gateway (Slave)");
  Serial.println("Master: Arduino Uno + DHT22");
  Serial.println("Device ID: " + String(deviceId));
  Serial.println("Server URL: " + String(serverUrl));
  Serial.println("Serial2: RX2=GPIO16, TX2=GPIO17, Baud=115200");
  Serial.println("======================================================================\n");
  
  // Kết nối WiFi
  Serial.print("🔌 Đang kết nối WiFi");
  WiFi.begin(ssid, password);
  
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 20) {
    delay(500);
    Serial.print(".");
    attempts++;
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\n✅ WiFi đã kết nối!");
    Serial.println("IP Address: " + WiFi.localIP().toString());
    blinkLED(3, 200);
  } else {
    Serial.println("\n❌ Không thể kết nối WiFi!");
  }
  
  Serial.println("\n📡 Chờ dữ liệu từ Arduino Uno Master (Serial2)...\n");
  Serial.println("Tip: Mở Serial Monitor của Arduino để debug!");
  Serial.println("");
}

// ===== LOOP =====
void loop() {
  // Đọc dữ liệu từ Arduino qua Serial2
  if (ArduinoSerial.available()) {
    String jsonData = ArduinoSerial.readStringUntil('\n');
    jsonData.trim();
    
    if (jsonData.length() > 0) {
      Serial.println("\n" + String('=') + String('=') + String('=') + String('=') + String('='));
      Serial.println("📥 Nhận từ Arduino Master: " + jsonData);
      
      // Parse để hiển thị thông tin
      StaticJsonDocument<256> previewDoc;
      DeserializationError err = deserializeJson(previewDoc, jsonData);
      if (!err) {
        float temp = previewDoc["temperature"] | 0.0;
        float hum = previewDoc["humidity"] | 0.0;
        int aqi = previewDoc["aqi"] | 0;
        String status = previewDoc["air_quality_status"] | "UNKNOWN";
        int count = previewDoc["count"] | 0;
        Serial.printf("   #%d | Temp: %.1f°C | Hum: %.1f%% | AQI: %d (%s)\n", 
                      count, temp, hum, aqi, status.c_str());
      }
      
      // Gửi lên server
      bool success = sendDataToServer(jsonData);
      
      if (success) {
        blinkLED(1, 100);
      } else {
        blinkLED(3, 50);
      }
    }
  }
  
  delay(100);
}

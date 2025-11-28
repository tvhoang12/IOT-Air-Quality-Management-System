/*
 * ESP32 Air Quality Monitor - Wokwi Simulator
 * Gửi dữ liệu về Django server qua HTTP POST
 * 
 * Hardware:
 * - ESP32 DevKit V1
 * - LED Status (GPIO2)
 * 
 * Chức năng:
 * - Tạo dữ liệu cảm biến ngẫu nhiên
 * - Gửi về server mỗi 5 giây
 * - LED nháy khi gửi thành công
 */

#include <WiFi.h>
#include <HTTPClient.h>
#include <WiFiClientSecure.h>
#include <ArduinoJson.h>

// ===== CẤU HÌNH WIFI =====
const char* ssid = "Wokwi-GUEST";
const char* password = "";

// ===== CẤU HÌNH SERVER =====
// Sử dụng ngrok để kết nối từ Wokwi đến localhost
// URL ngrok: https://inequilateral-youlanda-hypermagical.ngrok-free.dev
const char* serverUrl = "https://inequilateral-youlanda-hypermagical.ngrok-free.dev/api/sensor-data/";
const char* deviceId = "ESP32_WOKWI_SIMULATOR";

// ===== CẤU HÌNH PHẦN CỨNG =====
const int LED_PIN = 2;  // GPIO2 - LED trạng thái

// ===== CẤU HÌNH THỜI GIAN =====
const unsigned long SEND_INTERVAL = 5000;  // 5 giây
unsigned long lastSendTime = 0;
int sendCount = 0;

// ===== HÀM TẠO DỮ LIỆU NGẪU NHIÊN =====
struct SensorData {
  float temperature;
  float humidity;
  float gas_level;
  float dust_density;
  int aqi;
  String air_quality_status;
};

SensorData generateRandomData() {
  SensorData data;
  
  // Nhiệt độ: 22-32°C
  data.temperature = random(220, 321) / 10.0;
  
  // Độ ẩm: 50-80%
  data.humidity = random(500, 801) / 10.0;
  
  // Khí gas: 100-300 ppm
  data.gas_level = random(1000, 3001) / 10.0;
  
  // Bụi: 30-150 µg/m³
  data.dust_density = random(300, 1501) / 10.0;
  
  // AQI: 50-180
  data.aqi = random(50, 181);
  
  // Trạng thái không khí dựa trên AQI
  if (data.aqi <= 50) {
    data.air_quality_status = "GOOD";
  } else if (data.aqi <= 100) {
    data.air_quality_status = "MODERATE";
  } else if (data.aqi <= 150) {
    data.air_quality_status = "UNHEALTHY";
  } else {
    data.air_quality_status = "VERY_UNHEALTHY";
  }
  
  return data;
}

// ===== HÀM GỬI DỮ LIỆU =====
bool sendDataToServer(SensorData data) {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("❌ WiFi không kết nối!");
    return false;
  }
  
  // Tạo WiFiClientSecure cho HTTPS (ngrok)
  WiFiClientSecure *client = new WiFiClientSecure;
  if (!client) {
    Serial.println("❌ Không thể tạo WiFiClientSecure!");
    return false;
  }
  
  // Skip SSL certificate verification cho ngrok
  client->setInsecure();
  
  HTTPClient http;
  http.begin(*client, serverUrl);
  http.addHeader("Content-Type", "application/json");
  http.addHeader("ngrok-skip-browser-warning", "true");  // Bypass ngrok warning page
  http.addHeader("User-Agent", "ESP32-AQI-Monitor");
  http.setTimeout(15000);  // Timeout 15 giây
  
  // Tạo JSON payload
  StaticJsonDocument<256> doc;
  doc["temperature"] = data.temperature;
  doc["humidity"] = data.humidity;
  doc["gas_level"] = data.gas_level;
  doc["dust_density"] = data.dust_density;
  doc["aqi"] = data.aqi;
  doc["air_quality_status"] = data.air_quality_status;
  doc["device_id"] = deviceId;
  
  String jsonPayload;
  serializeJson(doc, jsonPayload);
  
  // Gửi POST request
  Serial.println("\n📤 Gửi dữ liệu...");
  Serial.println("Payload: " + jsonPayload);
  
  int httpResponseCode = http.POST(jsonPayload);
  
  bool success = false;
  if (httpResponseCode > 0) {
    String response = http.getString();
    Serial.printf("✅ Response Code: %d\n", httpResponseCode);
    Serial.println("Response: " + response);
    
    if (httpResponseCode == 201) {
      success = true;
      
      // Parse response để kiểm tra trạng thái lưu
      StaticJsonDocument<512> responseDoc;
      DeserializationError error = deserializeJson(responseDoc, response);
      
      if (!error) {
        bool savedToDb = responseDoc["saved_to_database"] | false;
        if (savedToDb) {
          Serial.println("💾 [SAVED TO DATABASE]");
        } else {
          Serial.println("⚡ [CACHED ONLY - Real-time display]");
        }
      }
    }
  } else {
    Serial.printf("❌ Lỗi HTTP: %d - %s\n", httpResponseCode, http.errorToString(httpResponseCode).c_str());
    Serial.println("💡 Kiểm tra: Django server đang chạy? Ngrok đang chạy? URL đúng?");
  }
  
  http.end();
  delete client;
  return success;
}

// ===== HÀM TẠO CHUỖI LẶP =====
String repeatChar(char c, int count) {
  String result = "";
  for (int i = 0; i < count; i++) {
    result += c;
  }
  return result;
}

// ===== HÀM NHÁY LED =====
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
  Serial.begin(115200);
  delay(1000);
  
  // Khởi tạo LED
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);
  
  Serial.println("\n" + repeatChar('=', 70));
  Serial.println("  ESP32 AIR QUALITY MONITOR - WOKWI SIMULATOR");
  Serial.println(repeatChar('=', 70));
  Serial.println("Device ID: " + String(deviceId));
  Serial.println("Server URL: " + String(serverUrl));
  Serial.println("Send Interval: " + String(SEND_INTERVAL / 1000) + " giây");
  Serial.println(repeatChar('=', 70) + "\n");
  
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
    blinkLED(3, 200);  // Nháy 3 lần báo hiệu kết nối thành công
  } else {
    Serial.println("\n❌ Không thể kết nối WiFi!");
    Serial.println("⚠️  Vui lòng kiểm tra cấu hình Private Gateway trong Wokwi");
  }
  
  Serial.println("\n📡 Bắt đầu gửi dữ liệu...\n");
}

// ===== LOOP =====
void loop() {
  unsigned long currentTime = millis();
  
  // Gửi dữ liệu mỗi SEND_INTERVAL giây
  if (currentTime - lastSendTime >= SEND_INTERVAL) {
    lastSendTime = currentTime;
    sendCount++;
    
    // Tạo dữ liệu ngẫu nhiên
    SensorData data = generateRandomData();
    
    // Hiển thị thông tin
    Serial.println("┌" + repeatChar('─', 68) + "┐");
    Serial.printf("│ #%-3d | Temp: %.1f°C | Hum: %.1f%% | Gas: %.1f ppm | Dust: %.1f µg/m³ │\n",
                  sendCount, data.temperature, data.humidity, data.gas_level, data.dust_density);
    Serial.printf("│      | AQI: %-3d | Status: %-20s                 │\n",
                  data.aqi, data.air_quality_status.c_str());
    Serial.println("└" + repeatChar('─', 68) + "┘");
    
    // Gửi dữ liệu
    bool success = sendDataToServer(data);
    
    if (success) {
      // Nháy LED 1 lần khi gửi thành công
      blinkLED(1, 100);
    } else {
      // Nháy LED nhanh 3 lần khi lỗi
      blinkLED(3, 50);
    }
  }
  
  delay(100);  // Delay ngắn để không block CPU
}

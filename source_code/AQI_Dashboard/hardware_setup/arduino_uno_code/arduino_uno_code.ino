/*
 * Arduino Uno MASTER - Đọc DHT22 và gửi qua Serial cho ESP32
 * 
 * Mô hình: Uno (Master) → Serial → ESP32 (Slave WiFi Gateway)
 * 
 * Hardware:
 * - DHT22: Nhiệt độ & Độ ẩm (D2)
 * - LED Status (D13 - built-in)
 * 
 * Kết nối ESP32:
 * - Arduino TX (D1) → ESP32 RX2 (GPIO16)
 * - Arduino RX (D0) → ESP32 TX2 (GPIO17)
 * - GND → GND chung
 */

#include <DHT.h>

// ===== CẤU HÌNH DHT22 =====
#define DHTPIN 2
#define DHTTYPE DHT22
DHT dht(DHTPIN, DHTTYPE);

// ===== CẤU HÌNH LED =====
#define LED_PIN 13  // Built-in LED

// ===== CẤU HÌNH THỜI GIAN =====
const unsigned long SEND_INTERVAL = 5000;  // 5 giây
unsigned long lastSendTime = 0;
int sendCount = 0;

void setup() {
  // Serial để gửi cho ESP32 (TX/RX)
  Serial.begin(115200);
  
  // Khởi động DHT22
  dht.begin();
  
  // LED status
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);
  
  // Chờ Serial ổn định
  delay(2000);
  
  Serial.println("Arduino Uno MASTER ready!");
  Serial.println("Reading DHT22 sensor...");
  
  // Nháy LED 3 lần báo sẵn sàng
  for (int i = 0; i < 3; i++) {
    digitalWrite(LED_PIN, HIGH);
    delay(200);
    digitalWrite(LED_PIN, LOW);
    delay(200);
  }
}

void loop() {
  unsigned long currentTime = millis();
  
  if (currentTime - lastSendTime >= SEND_INTERVAL) {
    lastSendTime = currentTime;
    sendCount++;
    
    // Bật LED khi đọc cảm biến
    digitalWrite(LED_PIN, HIGH);
    
    // Đọc DHT22
    float temperature = dht.readTemperature();
    float humidity = dht.readHumidity();
    
    // Kiểm tra lỗi đọc DHT22
    bool dht_error = false;
    if (isnan(temperature) || isnan(humidity)) {
      dht_error = true;
      // Dùng giá trị ngẫu nhiên khi DHT22 lỗi
      temperature = random(220, 321) / 10.0;
      humidity = random(500, 801) / 10.0;
    }
    
    // Tạo dữ liệu mô phỏng cho gas và dust (vì chưa có cảm biến)
    float gas_level = random(1000, 3001) / 10.0;      // 100-300 ppm
    float dust_density = random(300, 1501) / 10.0;    // 30-150 µg/m³
    
    // Tính AQI dựa trên nhiệt độ, độ ẩm, gas, dust
    // Công thức đơn giản: AQI = f(temp, humidity, gas, dust)
    int aqi = (int)((gas_level * 0.4) + (dust_density * 0.4) + 
                    ((temperature - 20) * 0.5) + ((humidity - 50) * 0.2));
    
    // Giới hạn AQI 50-180
    if (aqi < 50) aqi = random(50, 70);
    if (aqi > 180) aqi = random(150, 180);
    
    // Xác định trạng thái không khí
    String status;
    if (aqi <= 50) {
      status = "GOOD";
    } else if (aqi <= 100) {
      status = "MODERATE";
    } else if (aqi <= 150) {
      status = "UNHEALTHY";
    } else {
      status = "VERY_UNHEALTHY";
    }
    
    // Gửi JSON qua Serial cho ESP32
    Serial.print("{");
    Serial.print("\"temperature\":");
    Serial.print(temperature, 1);
    Serial.print(",\"humidity\":");
    Serial.print(humidity, 1);
    Serial.print(",\"gas_level\":");
    Serial.print(gas_level, 1);
    Serial.print(",\"dust_density\":");
    Serial.print(dust_density, 1);
    Serial.print(",\"aqi\":");
    Serial.print(aqi);
    Serial.print(",\"air_quality_status\":\"");
    Serial.print(status);
    Serial.print("\",\"sensor_status\":\"");
    Serial.print(dht_error ? "DHT22_ERROR" : "OK");
    Serial.print("\",\"count\":");
    Serial.print(sendCount);
    Serial.println("}");
    
    // Tắt LED
    digitalWrite(LED_PIN, LOW);
    
    // Nháy LED nhanh nếu DHT22 lỗi
    if (dht_error) {
      for (int i = 0; i < 3; i++) {
        digitalWrite(LED_PIN, HIGH);
        delay(50);
        digitalWrite(LED_PIN, LOW);
        delay(50);
      }
    }
  }
}

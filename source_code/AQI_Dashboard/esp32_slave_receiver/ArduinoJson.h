/*
 * Arduino Uno Master - Đọc cảm biến và gửi cho ESP32
 * 
 * Cảm biến → Arduino Uno đọc → Gửi JSON qua Serial → ESP32 nhận
 * 
 * KẾT NỐI CẢM BIẾN:
 * ==========================================
 * DHT11 (Temperature & Humidity):
 *   VCC  → 5V
 *   GND  → GND
 *   DATA → Pin 2
 * 
 * MQ-135 (Gas Sensor):
 *   VCC  → 5V
 *   GND  → GND
 *   AOUT → A0
 * 
 * GP2Y10 (Dust Sensor):
 *   V-LED → 5V (qua điện trở 150Ω)
 *   LED   → Pin 3
 *   GND   → GND
 *   Vo    → A1
 * 
 * KẾT NỐI VỚI ESP32:
 * ==========================================
 *   TX (Pin 1)  → ESP32 GPIO16
 *   RX (Pin 0)  → ESP32 GPIO17
 *   5V          → ESP32 VIN
 *   GND         → ESP32 GND
 * ==========================================
 */
#include <DHT.h>
#include <Wire.h> 
#include <LiquidCrystal_I2C.h>
// ============ CẢM BIẾN PINS ============
#define DHTPIN 6           // DHT11 data pin (User wiring: D6)
#define DHTTYPE DHT11      // DHT sensor type
#define MQ135_PIN A1       // MQ-135 analog pin (User wiring: A1)
#define DUST_LED_PIN 7     // GP2Y10 LED control (User wiring: D7)
#define DUST_MEASURE_PIN A2 // GP2Y10 analog pin (User wiring: A2)
// ============ TIMING ============
unsigned long lastSendTime = 0;
const long sendInterval = 60000; // Gửi mỗi 1 phút (60000ms)
// ============ SENSOR OBJECTS ============
DHT dht(DHTPIN, DHTTYPE);
LiquidCrystal_I2C lcd(0x27, 16, 2); // Nếu lỗi hãy đổi 0x27 thành 0x3F
void setup() {
  // Serial để gửi dữ liệu cho ESP32
  Serial.begin(9600);
  
  // Khởi tạo cảm biến
  dht.begin();
  pinMode(DUST_LED_PIN, OUTPUT);
  
  // Khởi tạo LCD
  lcd.init();      
  lcd.backlight();
  lcd.setCursor(0,0);
  lcd.print("System Ready!");
  
  // Chờ ổn định
  delay(2000);
}
void loop() {
  unsigned long currentTime = millis();
  
  // Đọc dữ liệu liên tục để hiển thị LCD
  float temperature = readTemperature();
  float humidity = readHumidity();
  float gasLevel = readGasSensor();
  float dustDensity = readDustSensor();
  // Hiển thị LCD (Mỗi 2 giây chuyển trang hoặc cập nhật)
  // Ở đây hiển thị đơn giản luân phiên
  static unsigned long lastLcdUpdate = 0;
  static int lcdPage = 0;
  
  if (currentTime - lastLcdUpdate >= 2000) {
    lastLcdUpdate = currentTime;
    lcdPage = !lcdPage; // Đảo trang
    
    lcd.clear();
    if (isnan(temperature) || isnan(humidity)) {
       lcd.print("Loi DHT11 !");
    } else {
      if (lcdPage == 0) {
        // Trang 1: Temp & Humi
        lcd.setCursor(0, 0);
        lcd.print("Temp: "); lcd.print((int)temperature); lcd.print("C");
        lcd.setCursor(0, 1);
        lcd.print("Humi: "); lcd.print((int)humidity); lcd.print("%");
      } else {
        // Trang 2: Gas & Dust
        lcd.setCursor(0, 0);
        lcd.print("Gas: "); lcd.print((int)gasLevel);
        lcd.setCursor(0, 1);
        lcd.print("Dust: "); lcd.print((int)dustDensity); lcd.print("ug");
      }
    }
  }
  
  // Gửi dữ liệu mỗi 1 phút
  if (currentTime - lastSendTime >= sendInterval) {
    lastSendTime = currentTime;
    
    // Kiểm tra dữ liệu hợp lệ trước khi gửi
    if (isnan(temperature) || isnan(humidity)) {
      temperature = 25.0;
      humidity = 60.0;
    }
    
    // Gửi dữ liệu dạng JSON qua Serial
    sendDataToESP32(temperature, humidity, gasLevel, dustDensity);
  }
}
// ============ ĐỌC CẢM BIẾN ============
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
  
  // Convert sang voltage (Arduino: 0-1023 = 0-5V)
  float voltage = rawValue * (5.0 / 1023.0);
  
  // Convert sang ppm (công thức đơn giản hóa)
  // Lưu ý: Cần calibrate cho chính xác
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
  float voltage = dustValue * (5.0 / 1023.0);
  
  // Convert sang µg/m³ (theo datasheet GP2Y10)
  // V = 0.17 * Dust Density (mg/m³) + 0.1
  float dustDensity = (voltage - 0.1) / 0.17;
  
  if (dustDensity < 0) dustDensity = 0;
  
  return dustDensity * 1000; // Convert mg/m³ to µg/m³
}
// ============ GỬI DỮ LIỆU ============
void sendDataToESP32(float temp, float hum, float gas, float dust) {
  // Tạo JSON string
  // Format: {"temperature":25.5,"humidity":60.0,"gas_level":150.0,"dust_density":35.0}
  
  Serial.print("{\"temperature\":");
  Serial.print(temp, 1);
  Serial.print(",\"humidity\":");
  Serial.print(hum, 1);
  Serial.print(",\"gas_level\":");
  Serial.print(gas, 1);
  Serial.print(",\"dust_density\":");
  Serial.print(dust, 1);
  Serial.println("}");
  
  // Debug (có thể bỏ comment nếu muốn test riêng Arduino)
  // Lưu ý: Khi kết nối với ESP32, chỉ nên gửi JSON thuần
  /*
  Serial.print("DEBUG - T:");
  Serial.print(temp);
  Serial.print(" H:");
  Serial.print(hum);
  Serial.print(" G:");
  Serial.print(gas);
  Serial.print(" D:");
  Serial.println(dust);
  */
}
/*
 * ============================================
 * THƯ VIỆN CẦN CÀI (Arduino IDE)
 * ============================================
 * 
 * 1. DHT sensor library by Adafruit
 *    Tools → Manage Libraries → "DHT sensor"
 * 
 * ============================================
 * CÁCH SỬ DỤNG
 * ============================================
 * 
 * 1. Kết nối cảm biến theo sơ đồ trên
 * 2. Cài thư viện DHT sensor
 * 3. Nạp code này vào Arduino Uno
 * 4. Kết nối với ESP32:
 *    - Arduino TX → ESP32 GPIO16
 *    - Arduino RX → ESP32 GPIO17
 *    - 5V → VIN, GND → GND
 * 5. Nạp code esp32_slave_receiver.ino vào ESP32
 * 6. Cấp nguồn cho Arduino (qua USB hoặc adapter)
 * 
 * ============================================
 * TROUBLESHOOTING
 * ============================================
 * 
 * Nếu DHT11 đọc NaN:
 * - Kiểm tra kết nối VCC, GND, DATA
 * - Thử thêm điện trở pull-up 10kΩ giữa DATA và VCC
 * - Đợi 2 giây sau khi khởi động
 * 
 * Nếu ESP32 không nhận dữ liệu:
 * - Kiểm tra TX/RX có đúng không (có thể bị ngược)
 * - Kiểm tra baud rate: 9600
 * - Mở Serial Monitor Arduino để xem có gửi không
 * - GND phải chung giữa Arduino và ESP32
 * 
 * ============================================
 * TEST RIÊNG ARDUINO (KHÔNG KẾT NỐI ESP32)
 * ============================================
 * 
 * Mở Serial Monitor với 9600 baud, sẽ thấy:
 * {"temperature":25.5,"humidity":60.0,"gas_level":150.0,"dust_density":35.0}
 * 
 * Mỗi 1 phút sẽ có 1 dòng JSON mới
 * 
 * ============================================
 */
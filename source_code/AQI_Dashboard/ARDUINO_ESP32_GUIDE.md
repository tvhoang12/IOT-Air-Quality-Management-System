# Hướng dẫn kết nối Arduino Uno + ESP32 + Cảm biến

## 📋 Tổng quan hệ thống

```
Cảm biến → Arduino Uno (Master) → ESP32 (Slave) → Website Django
```

- **Arduino Uno**: Đọc dữ liệu từ các cảm biến, gửi JSON qua Serial
- **ESP32**: Nhận dữ liệu từ Arduino, kết nối WiFi, gửi lên server

---

## 🔌 Sơ đồ kết nối

### 1. Arduino Uno ↔ Cảm biến

#### DHT11 (Nhiệt độ & Độ ẩm)
```
DHT11        Arduino Uno
VCC     →    5V
GND     →    GND
DATA    →    Pin 2
```

#### MQ-135 (Gas Sensor)
```
MQ-135       Arduino Uno
VCC     →    5V
GND     →    GND
AOUT    →    A0
```

#### GP2Y10 (Dust Sensor)
```
GP2Y10       Arduino Uno
V-LED   →    5V (qua điện trở 150Ω)
LED     →    Pin 3
GND     →    GND
Vo      →    A1
```

**Lưu ý**: GP2Y10 cần thêm capacitor 220µF giữa V-LED và GND để ổn định

---

### 2. Arduino Uno ↔ ESP32

```
Arduino Uno       ESP32 WROOM
────────────────────────────────
TX (Pin 1)    →   GPIO 16 (RX2)
RX (Pin 0)    →   GPIO 17 (TX2)
5V            →   VIN
GND           →   GND
```

**Quan trọng**:
- ✅ TX Arduino → RX ESP32 (GPIO16)
- ✅ RX Arduino → TX ESP32 (GPIO17)
- ✅ GND phải chung giữa 2 board
- ✅ ESP32 lấy nguồn từ Arduino qua VIN (5V)

---

## 💻 Code cần nạp

### 1. Arduino Uno
**File**: `arduino_uno_master.ino`

**Chức năng**:
- Đọc DHT11 (nhiệt độ, độ ẩm)
- Đọc MQ-135 (gas level)
- Đọc GP2Y10 (dust density)
- Gửi JSON qua Serial mỗi 1 phút

**Thư viện cần cài**:
- DHT sensor library by Adafruit

**Baud rate**: 9600

---

### 2. ESP32 WROOM
**File**: `esp32_slave_receiver.ino`

**Chức năng**:
- Nhận JSON từ Arduino Uno qua Serial2
- Parse JSON
- Kết nối WiFi
- Gửi dữ liệu lên website Django

**Thư viện cần cài**:
- ArduinoJson by Benoit Blanchon

**Cấu hình cần thay đổi**:
```cpp
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";
const char* serverUrl = "http://192.168.1.100:8000/devices/api/webhook/";
const char* apiKey = "YOUR_API_KEY";
```

**Baud rate**: 
- Serial (USB debug): 115200
- Serial2 (Arduino): 9600

---

## 📝 Định dạng dữ liệu

### Arduino Uno gửi (qua Serial TX):
```json
{"temperature":25.5,"humidity":60.0,"gas_level":150.0,"dust_density":35.0}
```

### ESP32 gửi lên server (HTTP POST):
```json
{
  "temperature": 25.5,
  "humidity": 60.0,
  "gas_level": 150.0,
  "dust_density": 35.0,
  "ip_address": "192.168.1.100"
}
```

**Headers**:
```
Content-Type: application/json
X-API-Key: your_api_key_here
```

---

## 🚀 Cách nạp code

### Bước 1: Nạp Arduino Uno
1. Mở Arduino IDE
2. Chọn Board: **Arduino Uno**
3. Chọn Port (VD: COM3, /dev/ttyUSB0)
4. Mở file `arduino_uno_master.ino`
5. Cài thư viện DHT sensor
6. Upload code

### Bước 2: Nạp ESP32
1. Mở Arduino IDE (hoặc IDE khác)
2. Chọn Board: **ESP32 Dev Module**
3. Chọn Port
4. Mở file `esp32_slave_receiver.ino`
5. Cài thư viện ArduinoJson
6. **Thay đổi WiFi SSID, Password, API Key**
7. Upload code

### Bước 3: Kết nối phần cứng
1. **Ngắt kết nối USB** khỏi cả 2 board
2. Kết nối dây theo sơ đồ:
   - TX Arduino → GPIO16 ESP32
   - RX Arduino → GPIO17 ESP32
   - 5V → VIN
   - GND → GND
3. Cấp nguồn cho Arduino Uno (qua USB hoặc adapter)
4. ESP32 sẽ được cấp nguồn từ Arduino qua VIN

---

## 🔍 Kiểm tra hoạt động

### Test Arduino Uno (riêng lẻ)
1. Ngắt kết nối với ESP32
2. Kết nối USB Arduino với máy tính
3. Mở Serial Monitor (9600 baud)
4. Sẽ thấy JSON mỗi 1 phút:
```
{"temperature":25.5,"humidity":60.0,"gas_level":150.0,"dust_density":35.0}
```

### Test ESP32 (kết nối với Arduino)
1. Kết nối cả 2 board theo sơ đồ
2. Kết nối USB ESP32 với máy tính
3. Mở Serial Monitor (115200 baud)
4. Sẽ thấy:
```
ESP32 - Arduino Uno Bridge
✓ Serial2: RX=GPIO16, TX=GPIO17
✓ WiFi OK!
--- Data from Arduino ---
{"temperature":25.5,...}
--- Sensor Values ---
  Temp: 25.5°C
  ...
✓ Response: 200
```

---

## ⚠️ Troubleshooting

### ESP32 không nhận được dữ liệu từ Arduino
**Nguyên nhân**:
- Dây TX/RX bị ngược
- Baud rate không khớp
- GND không chung

**Giải pháp**:
1. Kiểm tra lại kết nối:
   - Arduino TX (Pin 1) → ESP32 GPIO16
   - Arduino RX (Pin 0) → ESP32 GPIO17
2. Thử đổi GPIO16 ↔ GPIO17 nếu vẫn không được
3. Đảm bảo GND được nối chung
4. Kiểm tra baud rate: Arduino và ESP32 đều dùng 9600

### DHT11 đọc NaN (Not a Number)
**Nguyên nhân**:
- Kết nối lỏng
- Thiếu điện trở pull-up
- Chưa đợi đủ thời gian khởi động

**Giải pháp**:
1. Kiểm tra kết nối VCC, GND, DATA
2. Thêm điện trở 10kΩ giữa DATA và VCC
3. Thêm `delay(2000)` trong `setup()`

### ESP32 không kết nối WiFi
**Giải pháp**:
1. Kiểm tra SSID và Password
2. Đảm bảo ESP32 trong phạm vi WiFi
3. Kiểm tra router có bật DHCP không

### Server trả về lỗi 401 (Unauthorized)
**Nguyên nhân**: API Key sai

**Giải pháp**:
1. Đăng nhập website: http://127.0.0.1:8000
2. Vào "Thêm thiết bị"
3. Copy API Key mới
4. Thay vào ESP32 code
5. Nạp lại ESP32

---

## 📊 Luồng dữ liệu

```
1. Arduino đọc cảm biến (mỗi 1 phút)
   ↓
2. Arduino gửi JSON qua Serial TX
   ↓
3. ESP32 nhận JSON qua Serial2 RX (GPIO16)
   ↓
4. ESP32 parse JSON
   ↓
5. ESP32 gửi HTTP POST lên server
   ↓
6. Django server nhận, tính AQI, lưu vào database
   ↓
7. Dashboard hiển thị real-time
```

---

## 🎯 Lưu ý quan trọng

1. **Nguồn điện**:
   - Arduino cần nguồn ổn định (USB hoặc adapter 7-12V)
   - ESP32 lấy nguồn từ Arduino qua VIN (5V)
   - Nếu dùng nhiều cảm biến, cân nhắc nguồn riêng

2. **Baud rate**:
   - Arduino Serial: 9600
   - ESP32 Serial2: 9600
   - ESP32 Serial (debug): 115200

3. **Timing**:
   - Arduino gửi dữ liệu mỗi 1 phút
   - Server lưu vào database ngay lập tức

4. **API Key**:
   - Lấy từ website sau khi tạo thiết bị
   - Không chia sẻ API Key
   - Mỗi thiết bị có 1 API Key riêng

---

## 📁 File code trong project

- `arduino_uno_master.ino` - Code cho Arduino Uno
- `esp32_slave_receiver.ino` - Code cho ESP32
- `demo_esp32_virtual.py` - Script Python test (không cần phần cứng)

---

**Chúc bạn thành công!** 🎉

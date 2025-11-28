# Arduino Uno + ESP32 - Kết nối qua Serial

## 📦 Linh kiện

1. **Arduino Uno**
2. **ESP32 DevKit V1**
3. **Cảm biến** (DHT22, MQ-135, GP2Y10)
4. **Breadboard & dây nối**
5. **2 cáp USB**

## 🔌 Sơ đồ kết nối

### Mô hình tổng thể:

```
Cảm biến → Arduino Uno → (Serial) → ESP32 → WiFi → Server
```

### Kết nối chi tiết:

```
Arduino Uno          ESP32
-----------          -----
TX (D1)      ----->  RX2 (GPIO16)
RX (D0)      <-----  TX2 (GPIO17)
GND          ----->  GND
5V           ----->  VIN (nếu ESP32 không có USB riêng)
```

### Cảm biến → Arduino Uno:

```
DHT22:
  VCC   → 5V (Uno)
  DATA  → D2 (Uno)
  GND   → GND (Uno)

MQ-135:
  VCC   → 5V (Uno)
  AOUT  → A0 (Uno)
  GND   → GND (Uno)

GP2Y10:
  VCC   → 5V (Uno)
  AOUT  → A1 (Uno)
  GND   → GND (Uno)
```

## 💻 Hướng dẫn upload code

### Bước 1: Upload code cho Arduino Uno

1. Mở Arduino IDE
2. Tools → Board → Arduino Uno
3. Tools → Port → Chọn port Arduino (vd: `/dev/ttyACM0`)
4. Mở file `arduino_uno_code/arduino_uno_code.ino`
5. Cài thư viện DHT:
   - Sketch → Include Library → Manage Libraries
   - Tìm "DHT sensor library" by Adafruit
   - Install
6. Upload code (Ctrl+U)

### Bước 2: Upload code cho ESP32

1. **Ngắt kết nối TX/RX** giữa Arduino và ESP32 (quan trọng!)
2. Tools → Board → ESP32 Dev Module
3. Tools → Port → Chọn port ESP32 (vd: `/dev/ttyUSB0`)
4. Mở file `esp32_code/esp32_serial_receiver.ino`
5. **Sửa WiFi & Server URL**:
   ```cpp
   const char* ssid = "TEN_WIFI_CUA_BAN";
   const char* password = "MAT_KHAU_WIFI";
   const char* serverUrl = "http://192.168.1.XXX:8000/api/sensor-data/";
   ```
6. Upload code (Ctrl+U)

### Bước 3: Kết nối lại TX/RX

Sau khi upload xong, kết nối lại:
```
Arduino TX (D1) → ESP32 RX2 (GPIO16)
Arduino RX (D0) → ESP32 TX2 (GPIO17)
Arduino GND     → ESP32 GND
```

### Bước 4: Chạy Django server

```bash
cd "/media/hoang/HDD_Code/Tài liệu học tập/Kỳ 1 năm 4/IOT/source_code/AQI_Dashboard"
python manage.py runserver 8000
```

### Bước 5: Lấy IP máy tính

```bash
ip addr show | grep "inet " | grep -v 127.0.0.1
```

Ví dụ: `inet 192.168.1.100/24` → Dùng `192.168.1.100`

### Bước 6: Test

1. Mở Serial Monitor của ESP32 (115200 baud)
2. Xem output:
   ```
   ✅ WiFi đã kết nối!
   IP Address: 192.168.1.150
   📡 Chờ dữ liệu từ Arduino Uno...
   
   📥 Nhận từ Arduino: {"temperature":28.5,"humidity":65.0,...}
   📤 Gửi dữ liệu...
   ✅ Response Code: 201
   ⚡ [CACHED ONLY]
   ```

3. Mở dashboard: http://localhost:8000

## 🎯 Cách hoạt động

1. **Arduino Uno**: Đọc cảm biến mỗi 5 giây → Gửi JSON qua Serial
2. **ESP32**: Nhận JSON từ Serial2 → Gửi lên server qua WiFi
3. **Server**: Nhận data → Cache (5s) hoặc lưu DB (5 phút)
4. **Dashboard**: Hiển thị real-time mỗi 5 giây

## 🐛 Troubleshooting

### Arduino không gửi dữ liệu
```
# Mở Serial Monitor của Arduino (115200 baud)
# Phải thấy JSON output mỗi 5 giây
```

### ESP32 không nhận được
```
📡 Chờ dữ liệu từ Arduino Uno...
(không có gì)
```
- Kiểm tra kết nối TX/RX
- Kiểm tra GND chung
- Kiểm tra baud rate = 115200 (cả 2 bên)

### ESP32 không kết nối WiFi
- Kiểm tra SSID/password
- WiFi phải là 2.4GHz (không phải 5GHz)

### Không gửi được lên server
- Kiểm tra Django server đang chạy
- Kiểm tra IP đúng
- Ping thử: `ping 192.168.1.XXX`
- Dùng ngrok nếu không cùng mạng

## 📊 Kiểm tra dữ liệu

```bash
# Xem dữ liệu mới nhất
curl http://localhost:8000/api/latest/

# Xem Firebase
# https://console.firebase.google.com/project/aqi-iot-db/database
```

## 💡 Tips

- **Debug**: Mở cả 2 Serial Monitor (Arduino + ESP32)
- **Nguồn**: Nếu ESP32 không đủ nguồn từ Arduino, cắm USB riêng
- **Cảm biến lỗi**: Code Arduino sẽ tự động dùng random data
- **WiFi xa**: Dùng ngrok thay vì IP local



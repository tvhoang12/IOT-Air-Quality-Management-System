# ESP32 Standalone - Kết nối trực tiếp

## 📦 Linh kiện cần thiết

1. **ESP32 DevKit V1** (hoặc tương tự)
2. **Cáp USB Type-C** (hoặc Micro-USB tùy board)
3. **LED + Resistor 220Ω** (optional - để debug)
4. **Breadboard** (optional)

## 🔌 Kết nối phần cứng

### Kết nối đơn giản (chỉ có LED status):

```
ESP32          LED Circuit
------         -----------
GPIO2    ----> Resistor 220Ω ----> LED Anode (+)
GND      ----> LED Cathode (-)
```

### Nếu có cảm biến thật:

```
ESP32          DHT22 (Nhiệt độ & Độ ẩm)
------         ---------------------------
3V3      ----> VCC
GPIO4    ----> DATA
GND      ----> GND

ESP32          MQ-135 (Khí gas)
------         ----------------
3V3      ----> VCC
GPIO34   ----> AOUT (Analog)
GND      ----> GND

ESP32          GP2Y10 (Bụi)
------         -------------
5V       ----> VCC
GPIO35   ----> AOUT
GND      ----> GND
```

## 💻 Cài đặt phần mềm

### Bước 1: Cài Arduino IDE

```bash
# Download từ: https://www.arduino.cc/en/software
# Hoặc dùng snap (Ubuntu):
sudo snap install arduino
```

### Bước 2: Cài ESP32 Board

1. Mở Arduino IDE
2. File → Preferences
3. Thêm URL vào "Additional Board Manager URLs":
   ```
   https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
   ```
4. Tools → Board → Boards Manager
5. Tìm "ESP32" và cài đặt

### Bước 3: Chọn board

1. Tools → Board → ESP32 Arduino → **ESP32 Dev Module**
2. Tools → Port → Chọn `/dev/ttyUSB0` (hoặc tương tự)

## 📝 Upload code

### Bước 1: Mở file sketch

```bash
# Copy file sketch.ino vào thư mục mới
mkdir -p ~/Arduino/ESP32_AQI_Monitor
cp "/media/hoang/HDD_Code/Tài liệu học tập/Kỳ 1 năm 4/IOT/source_code/AQI_Dashboard/wokwi_esp32/sketch.ino" ~/Arduino/ESP32_AQI_Monitor/ESP32_AQI_Monitor.ino
```

### Bước 2: Cấu hình WiFi

Sửa file `ESP32_AQI_Monitor.ino` dòng 20-21:

```cpp
const char* ssid = "TEN_WIFI_CUA_BAN";
const char* password = "MAT_KHAU_WIFI";
```

### Bước 3: Cấu hình server URL

**Option A: Dùng IP local (nếu ESP32 và máy tính cùng WiFi)**

```cpp
const char* serverUrl = "http://192.168.1.XXX:8000/api/sensor-data/";
```

Lấy IP máy tính:
```bash
ip addr show | grep "inet " | grep -v 127.0.0.1
```

**Option B: Dùng ngrok/localtunnel**

```cpp
const char* serverUrl = "https://your-ngrok-url.ngrok-free.dev/api/sensor-data/";
```

### Bước 4: Upload

1. Kết nối ESP32 qua USB
2. Arduino IDE: Sketch → Upload
3. Chờ upload hoàn tất (~30 giây)
4. Tools → Serial Monitor (115200 baud)

## 🎯 Kiểm tra hoạt động

### Serial Monitor sẽ hiển thị:

```
======================================================================
  ESP32 AIR QUALITY MONITOR - WOKWI SIMULATOR
======================================================================
Device ID: ESP32_WOKWI_SIMULATOR
Server URL: http://192.168.1.100:8000/api/sensor-data/
Send Interval: 5 giây
======================================================================

🔌 Đang kết nối WiFi.....
✅ WiFi đã kết nối!
IP Address: 192.168.1.150

📡 Bắt đầu gửi dữ liệu...

┌────────────────────────────────────────────────────────────────────┐
│ #1   | Temp: 28.5°C | Hum: 65.0% | Gas: 180.0 ppm | Dust: 75.0 µg/m³ │
│      | AQI: 120 | Status: MODERATE                                   │
└────────────────────────────────────────────────────────────────────┘
📤 Gửi dữ liệu...
✅ Response Code: 201
⚡ [CACHED ONLY - Real-time display]
```

### Dashboard: http://localhost:8000

Sẽ thấy dữ liệu cập nhật real-time mỗi 5 giây.

## 🐛 Troubleshooting

### ESP32 không kết nối WiFi
```
❌ Không thể kết nối WiFi!
```
- Kiểm tra SSID và password
- Kiểm tra WiFi 2.4GHz (ESP32 không hỗ trợ 5GHz)
- Restart ESP32

### Không gửi được data
```
❌ Lỗi HTTP: -1 - connection refused
```
- Kiểm tra Django server đang chạy
- Kiểm tra IP/URL đúng
- Ping thử: `ping 192.168.1.XXX`

### Port không nhận diện
```
Serial port not found
```
```bash
# Cài driver CH340/CP2102
# Ubuntu:
sudo apt install brltty
sudo systemctl stop brltty-udev.service
sudo systemctl disable brltty-udev.service

# Thêm user vào group dialout:
sudo usermod -a -G dialout $USER
# Logout và login lại
```

### Upload lỗi
```
Failed to connect to ESP32
```
- Giữ nút BOOT trên ESP32 khi upload
- Chọn đúng port
- Tốc độ upload: 115200

## 📊 Test với cảm biến thật

Nếu có cảm biến DHT22, MQ-135, GP2Y10, xem file:
`ESP32_WITH_REAL_SENSORS.ino`

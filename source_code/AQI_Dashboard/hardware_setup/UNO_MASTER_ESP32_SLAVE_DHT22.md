# 🎯 MÔ HÌNH: ARDUINO UNO (MASTER) + ESP32 (SLAVE) + DHT22

## 📋 Tổng quan kiến trúc

```
DHT22 → Arduino Uno (MASTER) → Serial → ESP32 (SLAVE) → WiFi → Django Server
        [Đọc cảm biến]          [TX/RX]   [WiFi Gateway]        [Firebase DB]
```

**Vai trò:**
- **Arduino Uno**: Master - Đọc cảm biến DHT22, tính toán AQI, gửi JSON qua Serial
- **ESP32**: Slave - WiFi Gateway nhận JSON từ Uno, forward lên server

## 🔌 Sơ đồ kết nối phần cứng

### Kết nối DHT22 → Arduino Uno:

```
DHT22               Arduino Uno
-----               -----------
VCC (Pin 1)   ---->  5V
DATA (Pin 2)  ---->  D2 (Digital Pin 2)
GND (Pin 4)   ---->  GND

Lưu ý: Nếu DHT22 không có điện trở pull-up tích hợp,
       thêm điện trở 10kΩ giữa VCC và DATA
```

### Kết nối Arduino Uno ↔ ESP32:

```
Arduino Uno          ESP32 DevKit V1
-----------          ---------------
TX (D1)       ---->  RX2 (GPIO16)
RX (D0)       <----  TX2 (GPIO17)
GND           ---->  GND

Lưu ý: KHÔNG nối VCC/5V giữa Uno và ESP32!
       Mỗi board có USB riêng hoặc ESP32 dùng VIN từ Uno.
```

### Sơ đồ tổng thể:

```
                    ┌─────────────────┐
                    │     DHT22       │
                    │  Nhiệt độ & ẩm  │
                    └────────┬────────┘
                             │ (D2)
                             │
                    ┌────────▼────────┐
                    │  Arduino Uno    │
                    │    (MASTER)     │
                    │  - Đọc DHT22    │
                    │  - Tính AQI     │
                    │  - Tạo JSON     │
                    └────────┬────────┘
                             │ TX/RX (Serial)
                             │
                    ┌────────▼────────┐
                    │     ESP32       │
                    │    (SLAVE)      │
                    │  - Nhận JSON    │
                    │  - Gửi WiFi     │
                    └────────┬────────┘
                             │ WiFi
                             │
                    ┌────────▼────────┐
                    │ Django Server   │
                    │   + Firebase    │
                    └─────────────────┘
```

## 📦 Linh kiện cần thiết

- [ ] **Arduino Uno R3** (hoặc tương tự)
- [ ] **ESP32 DevKit V1** (hoặc tương tự)
- [ ] **DHT22** (AM2302) - Cảm biến nhiệt độ & độ ẩm
- [ ] **Điện trở 10kΩ** (nếu DHT22 không có pull-up)
- [ ] **Breadboard** (khuyến nghị 830 points)
- [ ] **Dây nối** (Male-Male, Male-Female)
- [ ] **2 cáp USB** (cho Uno: Type-B, cho ESP32: Micro-USB hoặc Type-C)

## 💻 Hướng dẫn upload code từng bước

### Bước 1️⃣: Lắp ráp phần cứng

1. **Kết nối DHT22 vào Arduino Uno:**
   ```
   DHT22 VCC  → Uno 5V
   DHT22 DATA → Uno D2
   DHT22 GND  → Uno GND
   (Thêm R 10kΩ giữa VCC và DATA nếu cần)
   ```

2. **Kết nối Arduino Uno với ESP32:**
   ```
   Uno TX (D1)  → ESP32 GPIO16 (RX2)
   Uno RX (D0)  → ESP32 GPIO17 (TX2)
   Uno GND      → ESP32 GND
   ```

3. **Kiểm tra kết nối:**
   - Chắc chắn GND chung
   - KHÔNG nối 5V/VCC giữa 2 board
   - TX → RX, RX → TX (cross-over)

### Bước 2️⃣: Upload code cho Arduino Uno (Master)

1. **Mở Arduino IDE**

2. **Cài thư viện DHT22:**
   ```
   Sketch → Include Library → Manage Libraries
   Tìm: "DHT sensor library" by Adafruit
   Click Install
   Cũng cài: "Adafruit Unified Sensor"
   ```

3. **Chọn board và port:**
   ```
   Tools → Board → Arduino Uno
   Tools → Port → /dev/ttyACM0 (Linux) hoặc COM3 (Windows)
   ```

4. **Mở file code:**
   ```
   File → Open
   → hardware_setup/arduino_uno_code/arduino_uno_code.ino
   ```

5. **Upload code:**
   ```
   Sketch → Upload (hoặc Ctrl+U)
   Chờ "Done uploading"
   ```

6. **Kiểm tra Serial Monitor:**
   ```
   Tools → Serial Monitor
   Baud rate: 115200
   
   Sẽ thấy:
   Arduino Uno MASTER ready!
   Reading DHT22 sensor...
   {"temperature":28.5,"humidity":65.0,...}  ← JSON mỗi 5 giây
   ```

### Bước 3️⃣: Upload code cho ESP32 (Slave)

⚠️ **QUAN TRỌNG:** Ngắt kết nối TX/RX giữa Uno và ESP32 trước khi upload!

1. **Ngắt dây TX/RX** (để ESP32 có thể nhận code từ USB)

2. **Chọn board ESP32:**
   ```
   Tools → Board → ESP32 Arduino → ESP32 Dev Module
   Tools → Port → /dev/ttyUSB0 (Linux) hoặc COM5 (Windows)
   ```

3. **Mở file code:**
   ```
   File → Open
   → hardware_setup/esp32_code/esp32_serial_receiver.ino
   ```

4. **Cấu hình WiFi và Server:**
   
   Sửa dòng 20-21:
   ```cpp
   const char* ssid = "TenWiFiCuaBan";
   const char* password = "MatKhauWiFi";
   ```
   
   Lấy IP máy tính (cùng WiFi):
   ```bash
   # Linux/Mac:
   ip addr show | grep "inet " | grep -v 127.0.0.1
   # Hoặc: ifconfig | grep "inet "
   
   # Windows:
   ipconfig
   
   # Ví dụ kết quả: inet 192.168.1.100/24
   ```
   
   Sửa dòng 27:
   ```cpp
   const char* serverUrl = "http://192.168.1.100:8000/api/sensor-data/";
   //                              ↑ Thay IP của bạn
   ```

5. **Upload code:**
   ```
   Sketch → Upload (Ctrl+U)
   Nếu lỗi "Failed to connect", giữ nút BOOT trên ESP32 khi upload
   ```

6. **Kết nối lại TX/RX** sau khi upload xong

### Bước 4️⃣: Chạy Django Server

```bash
cd "/media/hoang/HDD_Code/Tài liệu học tập/Kỳ 1 năm 4/IOT/source_code/AQI_Dashboard"

# Chạy server
python manage.py runserver 8000
```

Sẽ thấy:
```
Django version 4.2.7, using settings 'AQI_Dashboard.settings'
Starting development server at http://0.0.0.0:8000/
```

### Bước 5️⃣: Test hệ thống

1. **Mở Serial Monitor ESP32:**
   ```
   Tools → Serial Monitor
   Baud: 115200
   
   Sẽ thấy:
   ======================================================================
     ESP32 SLAVE - WIFI GATEWAY FOR ARDUINO UNO MASTER
   ======================================================================
   Role: WiFi Gateway (Slave)
   Master: Arduino Uno + DHT22
   ...
   ✅ WiFi đã kết nối!
   IP Address: 192.168.1.150
   
   📡 Chờ dữ liệu từ Arduino Uno Master (Serial2)...
   
   =====
   📥 Nhận từ Arduino Master: {"temperature":28.5,...}
      #1 | Temp: 28.5°C | Hum: 65.0% | AQI: 120 (MODERATE)
   📤 Gửi dữ liệu...
   ✅ Response Code: 201
   ⚡ [CACHED ONLY]
   ```

2. **Xem Dashboard:**
   ```
   Mở browser: http://localhost:8000
   Sẽ thấy dữ liệu cập nhật real-time mỗi 5 giây
   ```

3. **Kiểm tra Firebase:**
   ```
   https://console.firebase.google.com/project/aqi-iot-db/database
   ```

## 📊 Luồng dữ liệu

```
1. DHT22 đo nhiệt độ & độ ẩm
        ↓
2. Arduino Uno đọc DHT22 mỗi 5 giây
        ↓
3. Uno tính AQI, tạo dữ liệu mô phỏng gas/dust
        ↓
4. Uno tạo JSON và gửi qua Serial TX
        ↓
5. ESP32 nhận JSON qua Serial2 RX
        ↓
6. ESP32 parse JSON, thêm device_id
        ↓
7. ESP32 gửi HTTP POST qua WiFi
        ↓
8. Django nhận, cache 5s hoặc lưu DB 5 phút
        ↓
9. Firebase lưu trữ dữ liệu
        ↓
10. Dashboard hiển thị real-time
```

## 🐛 Troubleshooting

### ❌ Arduino không đọc được DHT22

**Triệu chứng:**
```
Arduino Serial Monitor hiển thị giá trị ngẫu nhiên
hoặc temperature/humidity = NaN
```

**Giải pháp:**
- Kiểm tra kết nối DHT22: VCC → 5V, DATA → D2, GND → GND
- Thêm điện trở pull-up 10kΩ giữa VCC và DATA
- Đợi 2-3 giây sau khi bật nguồn (DHT22 cần thời gian khởi động)
- Thử đổi sang DHT11 nếu có

### ❌ ESP32 không nhận được data từ Arduino

**Triệu chứng:**
```
ESP32 Serial Monitor chỉ hiển thị:
📡 Chờ dữ liệu từ Arduino Uno Master...
(không có gì thêm)
```

**Giải pháp:**
- Kiểm tra TX/RX đúng chưa: Uno TX → ESP32 GPIO16
- Kiểm tra GND chung
- Kiểm tra baud rate = 115200 (cả 2 board)
- Mở Serial Monitor của Arduino xem có JSON không
- Thử swap TX/RX nếu vẫn không được

### ❌ ESP32 không kết nối WiFi

**Triệu chứng:**
```
❌ Không thể kết nối WiFi!
```

**Giải pháp:**
- Kiểm tra SSID và password đúng
- WiFi phải là 2.4GHz (ESP32 không hỗ trợ 5GHz)
- Tắt xác thực enterprise nếu có
- Thử dùng hotspot điện thoại để test

### ❌ ESP32 không gửi được lên server

**Triệu chứng:**
```
❌ Lỗi HTTP: -1 - connection refused
```

**Giải pháp:**
- Kiểm tra Django server đang chạy: `ps aux | grep "manage.py runserver"`
- Kiểm tra IP đúng: `ip addr show`
- Ping thử: `ping 192.168.1.100`
- Tắt firewall tạm: `sudo ufw disable`
- Dùng ngrok nếu không cùng mạng

### ❌ LED Arduino nháy nhanh (DHT22 error)

**Triệu chứng:**
```
LED built-in nháy nhanh 3 lần
```

**Giải pháp:**
- DHT22 lỗi đọc → hệ thống tự động dùng giá trị ngẫu nhiên
- Kiểm tra lại kết nối DHT22
- Code vẫn chạy bình thường (dùng random data)

## 💡 Tips quan trọng

1. **Debug đồng thời:** Mở 2 Serial Monitor (Arduino + ESP32) để debug
2. **Nguồn điện:** Nếu ESP32 yếu nguồn từ Arduino, cắm USB riêng cho mỗi board
3. **Upload code:** Nhớ ngắt TX/RX khi upload ESP32
4. **WiFi:** Đảm bảo ESP32 và máy tính cùng mạng (cùng WiFi)
5. **Thư viện:** Cài đúng "DHT sensor library" by Adafruit (không phải DHT library khác)

## 📈 Mở rộng

### Thêm cảm biến thật (sau này):

```cpp
// Trong arduino_uno_code.ino, thay random() bằng đọc cảm biến:

// MQ-135 (Gas) - Kết nối A0
int gasRaw = analogRead(A0);
float gas_level = map(gasRaw, 0, 1023, 100, 300);

// GP2Y10 (Dust) - Kết nối A1
int dustRaw = analogRead(A1);
float dust_density = map(dustRaw, 0, 1023, 30, 150);
```

### Dùng ngrok cho remote access:

```bash
# Terminal 1
python manage.py runserver 8000

# Terminal 2
ngrok http 8000

# Copy URL vào esp32_serial_receiver.ino:
const char* serverUrl = "https://abc123.ngrok-free.dev/api/sensor-data/";
```

## ✅ Checklist hoàn thành

- [ ] DHT22 kết nối đúng với Arduino Uno
- [ ] Arduino upload thành công, Serial Monitor hiển thị JSON
- [ ] ESP32 upload thành công (nhớ ngắt TX/RX trước)
- [ ] TX/RX kết nối lại sau upload
- [ ] GND chung giữa Uno và ESP32
- [ ] WiFi SSID/password đúng
- [ ] Server URL đúng (IP hoặc ngrok)
- [ ] Django server đang chạy
- [ ] ESP32 kết nối WiFi thành công
- [ ] ESP32 nhận được JSON từ Uno
- [ ] ESP32 gửi thành công lên server (Response 201)
- [ ] Dashboard hiển thị dữ liệu real-time

## 📞 Hỗ trợ thêm

Nếu cần trợ giúp:
1. Chụp ảnh sơ đồ kết nối thực tế
2. Copy toàn bộ Serial Monitor output (cả Arduino và ESP32)
3. Paste Django server logs
4. Kiểm tra lại từng bước trong checklist

---

**Chúc bạn lắp ráp thành công! 🚀**

# 🚀 HƯỚNG DẪN LẮP RÁP HARDWARE - HỆ THỐNG GIÁM SÁT CHẤT LƯỢNG KHÔNG KHÍ

Tài liệu này hướng dẫn cách lắp ráp và chạy code trực tiếp trên linh kiện.

## 📁 Cấu trúc thư mục

```
hardware_setup/
├── README.md                          # File này
├── ESP32_STANDALONE.md                # Hướng dẫn ESP32 standalone
├── ARDUINO_UNO_ESP32.md              # Hướng dẫn Arduino Uno + ESP32
├── arduino_uno_code/
│   └── arduino_uno_code.ino          # Code cho Arduino Uno
└── esp32_code/
    └── esp32_serial_receiver.ino     # Code cho ESP32 nhận Serial
```

## 🎯 Chọn phương án phù hợp

### ⭐ Phương án 1: ESP32 Standalone (KHUYẾN NGHỊ)

**Ưu điểm:**
- ✅ Đơn giản, ít dây nối
- ✅ ESP32 đã có WiFi tích hợp
- ✅ Không cần Arduino Uno
- ✅ Tiết kiệm chi phí

**Nhược điểm:**
- ❌ Cần cảm biến tương thích ESP32 (3.3V)

**Khi nào dùng:**
- Bạn CHƯA có Arduino Uno
- Bạn muốn hệ thống đơn giản
- Chỉ cần demo với dữ liệu ngẫu nhiên

👉 **Xem hướng dẫn:** `ESP32_STANDALONE.md`

---

### 📋 Phương án 2: Arduino Uno + ESP32

**Ưu điểm:**
- ✅ Tận dụng Arduino Uno sẵn có
- ✅ Dễ kết nối cảm biến 5V
- ✅ Phân tách rõ: Uno đọc sensor, ESP32 gửi WiFi

**Nhược điểm:**
- ❌ Phức tạp hơn (2 board, nhiều dây)
- ❌ Cần 2 cáp USB hoặc nguồn ngoài

**Khi nào dùng:**
- Bạn ĐÃ có Arduino Uno
- Bạn có cảm biến 5V (DHT22, MQ-135, GP2Y10)
- Muốn học cách giao tiếp Serial giữa 2 board

👉 **Xem hướng dẫn:** `ARDUINO_UNO_ESP32.md`

---

## 🛠️ Chuẩn bị chung

### Phần mềm cần cài:

1. **Arduino IDE**
   ```bash
   # Ubuntu:
   sudo snap install arduino
   
   # Hoặc download: https://www.arduino.cc/en/software
   ```

2. **ESP32 Board cho Arduino IDE**
   - Xem hướng dẫn trong `ESP32_STANDALONE.md`

3. **Driver USB** (nếu cần)
   ```bash
   # Ubuntu - CH340/CP2102 driver
   sudo apt install brltty
   sudo systemctl stop brltty-udev.service
   sudo usermod -a -G dialout $USER
   # Logout và login lại
   ```

### Phần cứng:

**Phương án 1 (ESP32 Standalone):**
- [ ] ESP32 DevKit V1
- [ ] Cáp USB (Type-C hoặc Micro-USB)
- [ ] LED + Resistor 220Ω (optional)

**Phương án 2 (Uno + ESP32):**
- [ ] Arduino Uno
- [ ] ESP32 DevKit V1
- [ ] DHT22 (Nhiệt độ & Độ ẩm)
- [ ] MQ-135 (Khí gas)
- [ ] GP2Y10 (Bụi mịn)
- [ ] Breadboard
- [ ] Dây nối
- [ ] 2 cáp USB

---

## 📖 Quy trình lắp ráp nhanh

### Cho ESP32 Standalone:

```bash
1. Kết nối ESP32 qua USB
2. Mở Arduino IDE
3. Chọn Board: ESP32 Dev Module
4. Chọn Port: /dev/ttyUSB0
5. Sửa WiFi SSID/password trong code
6. Upload code
7. Mở Serial Monitor (115200)
8. Xem dữ liệu gửi mỗi 5 giây
```

### Cho Arduino Uno + ESP32:

```bash
1. Kết nối cảm biến vào Arduino Uno
2. Upload code arduino_uno_code.ino
3. Kết nối Arduino TX → ESP32 RX2
4. Kết nối Arduino RX → ESP32 TX2
5. Kết nối GND chung
6. Upload code esp32_serial_receiver.ino
7. Mở Serial Monitor ESP32 (115200)
8. Kiểm tra nhận JSON từ Arduino
```

---

## 🌐 Cấu hình kết nối Server

### Option 1: IP Local (Cùng WiFi)

```cpp
// Lấy IP máy tính:
// $ ip addr show | grep "inet " | grep -v 127.0.0.1
// Kết quả: inet 192.168.1.100/24

const char* serverUrl = "http://192.168.1.100:8000/api/sensor-data/";
```

### Option 2: Ngrok (Khác WiFi hoặc từ xa)

```bash
# Terminal 1: Chạy Django
python manage.py runserver 8000

# Terminal 2: Chạy ngrok
ngrok http 8000

# Copy URL: https://abc123.ngrok-free.dev
```

```cpp
const char* serverUrl = "https://abc123.ngrok-free.dev/api/sensor-data/";
```

---

## ✅ Kiểm tra hoạt động

### 1. Serial Monitor ESP32

Phải thấy:
```
✅ WiFi đã kết nối!
IP Address: 192.168.1.150
📤 Gửi dữ liệu...
✅ Response Code: 201
⚡ [CACHED ONLY]
```

### 2. Django Server Logs

```
[23/Nov/2025 16:15:31] "POST /api/sensor-data/" 201
```

### 3. Dashboard

Mở http://localhost:8000 → Thấy dữ liệu cập nhật real-time

### 4. Firebase Console

https://console.firebase.google.com/project/aqi-iot-db/database

---

## 🐛 Troubleshooting Common Issues

| Vấn đề | Giải pháp |
|--------|-----------|
| ESP32 không nhận diện port | Cài driver CH340, thêm user vào group dialout |
| WiFi không kết nối | Kiểm tra SSID/password, dùng WiFi 2.4GHz |
| HTTP connection failed | Kiểm tra Django đang chạy, IP đúng |
| Serial Monitor không có gì | Kiểm tra baud rate = 115200 |
| Arduino không gửi data | Kiểm tra TX/RX kết nối đúng, GND chung |

---

## 📞 Hỗ trợ

Nếu gặp vấn đề:

1. Đọc kỹ file `.md` tương ứng
2. Kiểm tra Serial Monitor output
3. Kiểm tra Django server logs
4. Test bằng curl/Postman trước

---

## 📚 Tài liệu tham khảo

- ESP32 Pinout: https://randomnerdtutorials.com/esp32-pinout-reference-gpios/
- Arduino Uno Pinout: https://docs.arduino.cc/hardware/uno-rev3
- DHT22 Datasheet: https://www.sparkfun.com/datasheets/Sensors/Temperature/DHT22.pdf
- Django REST API: http://localhost:8000/api/

---

**Chúc bạn lắp ráp thành công! 🎉**

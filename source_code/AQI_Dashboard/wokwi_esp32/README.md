# ESP32 Air Quality Monitor - Wokwi Simulator

## 📋 Mô tả

Dự án mô phỏng ESP32 gửi dữ liệu chất lượng không khí về Django server trên Wokwi.

## 🔧 Cấu hình Hardware

- **ESP32 DevKit V1**
- **LED Status** (GPIO2) - Nháy khi gửi dữ liệu thành công

## 📊 Dữ liệu gửi

```json
{
  "temperature": 28.5,      // 22-32°C
  "humidity": 65.0,         // 50-80%
  "gas_level": 180.0,       // 100-300 ppm
  "dust_density": 75.0,     // 30-150 µg/m³
  "aqi": 120,               // 50-180
  "air_quality_status": "MODERATE",
  "device_id": "ESP32_WOKWI_SIMULATOR"
}
```

## 🚀 Cách sử dụng

### Bước 1: Cài đặt Wokwi Private Gateway

Để ESP32 trong Wokwi có thể kết nối localhost, bạn cần cài đặt **Wokwi Private Gateway**:

```bash
# Cài đặt wokwi-cli
npm install -g wokwi-cli

# Đăng nhập Wokwi (cần tài khoản Wokwi Club)
wokwi-cli login

# Chạy Private Gateway
wokwi-cli gateway start
```

**Lưu ý:** Bạn cần tài khoản [Wokwi Club](https://wokwi.com/club) để sử dụng Private Gateway.

### Bước 2: Chạy Django Server

```bash
cd "/media/hoang/HDD_Code/Tài liệu học tập/Kỳ 1 năm 4/IOT/source_code/AQI_Dashboard"
python manage.py runserver 8000
```

### Bước 3: Chạy Wokwi Simulator

1. Truy cập [Wokwi.com](https://wokwi.com)
2. Tạo project mới: **New Project → ESP32**
3. Copy nội dung các file:
   - `diagram.json` → Tab "diagram.json"
   - `sketch.ino` → Tab "sketch.ino"
   - `wokwi.toml` → Tab "wokwi.toml"
4. Nhấn **Start Simulation** (nút ▶️)

### Bước 4: Kiểm tra kết quả

**Serial Monitor sẽ hiển thị:**
```
======================================================================
  ESP32 AIR QUALITY MONITOR - WOKWI SIMULATOR
======================================================================
Device ID: ESP32_WOKWI_SIMULATOR
Server URL: http://localhost:8000/api/sensor-data/
Send Interval: 5 giây
======================================================================

🔌 Đang kết nối WiFi.....
✅ WiFi đã kết nối!
IP Address: 192.168.1.100

📡 Bắt đầu gửi dữ liệu...

┌────────────────────────────────────────────────────────────────────┐
│ #1   | Temp: 28.5°C | Hum: 65.0% | Gas: 180.0 ppm | Dust: 75.0 µg/m³ │
│      | AQI: 120 | Status: MODERATE                                   │
└────────────────────────────────────────────────────────────────────┘
📤 Gửi dữ liệu...
✅ Response Code: 201
⚡ [CACHED ONLY - Real-time display]
```

**Dashboard:** http://localhost:8000 sẽ cập nhật real-time.

## 🔄 Cơ chế hoạt động

### Gửi dữ liệu (ESP32)
- Mỗi **5 giây** gửi 1 lần
- LED nháy 1 lần khi thành công
- LED nháy nhanh 3 lần khi lỗi

### Lưu dữ liệu (Server)
- **Cache:** Cập nhật mỗi 5 giây → Dashboard real-time
- **Database:** Lưu mỗi 5 phút → Biểu đồ

### Trạng thái hiển thị
- `[CACHED ONLY]` - 59 lần đầu (chỉ cache)
- `[SAVED TO DATABASE]` - Lần thứ 60 (sau 5 phút)

## 📝 Giải pháp thay thế (Không cần Wokwi Club)

Nếu không có Wokwi Club, có thể dùng **ngrok** hoặc **localtunnel**:

### Sử dụng ngrok:

```bash
# Cài đặt ngrok
# Download từ: https://ngrok.com/download

# Chạy ngrok
ngrok http 8000

# Lấy URL public (vd: https://abc123.ngrok.io)
# Thay đổi trong sketch.ino:
# const char* serverUrl = "https://abc123.ngrok.io/api/sensor-data/";
```

### Sử dụng localtunnel:

```bash
# Cài đặt localtunnel
npm install -g localtunnel

# Chạy localtunnel
lt --port 8000

# Lấy URL public (vd: https://funny-cat-12.loca.lt)
# Thay đổi trong sketch.ino:
# const char* serverUrl = "https://funny-cat-12.loca.lt/api/sensor-data/";
```

## 🎯 Kiểm tra kết nối

**Xem dữ liệu mới nhất:**
```bash
curl http://localhost:8000/api/latest/
```

**Xem dữ liệu lịch sử:**
```bash
curl http://localhost:8000/api/historical/?hours=1
```

**Xem Firebase Console:**
https://console.firebase.google.com/project/aqi-iot-db/database/aqi-iot-db-default-rtdb/data

## 🛠️ Troubleshooting

### Lỗi WiFi không kết nối
- Kiểm tra Wokwi Private Gateway đã chạy chưa
- Restart simulation

### Lỗi HTTP Connection Failed
- Kiểm tra Django server đã chạy chưa
- Kiểm tra URL trong `sketch.ino`
- Thử dùng ngrok/localtunnel

### LED không nháy
- Kiểm tra kết nối trong `diagram.json`
- Kiểm tra GPIO2 đã đúng chưa

## 📚 Tài liệu tham khảo

- [Wokwi ESP32 Guide](https://docs.wokwi.com/guides/esp32)
- [Wokwi Private Gateway](https://docs.wokwi.com/guides/esp32-wifi#the-private-gateway)
- [ArduinoJson Documentation](https://arduinojson.org/)
- [ESP32 HTTPClient](https://github.com/espressif/arduino-esp32/tree/master/libraries/HTTPClient)

## 📞 Hỗ trợ

Nếu gặp vấn đề, kiểm tra:
1. Serial Monitor trong Wokwi
2. Django server logs
3. Firebase Console
4. Network tab trong browser (F12)

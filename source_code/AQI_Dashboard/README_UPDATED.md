# Hệ Thống Giám Sát Chất Lượng Không Khí IoT

Hệ thống IoT Dashboard quản lý và giám sát chất lượng không khí với nhiều thiết bị ESP32, hỗ trợ authentication Firebase và quản lý thiết bị theo người dùng.

## 🌟 Tính năng

### Authentication & User Management
- ✅ Đăng ký/Đăng nhập với Firebase Authentication
- ✅ Quản lý profile người dùng (email, username, phone, fullname)
- ✅ Bảo mật với Firebase ID Token
- ✅ Session management

### Device Management
- ✅ Thêm/Xóa/Cập nhật thiết bị IoT
- ✅ Mỗi người dùng quản lý nhiều thiết bị
- ✅ API Key & Secret Key cho mỗi thiết bị
- ✅ Theo dõi trạng thái online/offline
- ✅ Hiển thị thời gian kết nối cuối

### IoT Monitoring
- ✅ Giám sát nhiệt độ, độ ẩm (DHT11)
- ✅ Giám sát nồng độ khí độc (MQ-135)
- ✅ Giám sát mật độ bụi (GP2Y10)
- ✅ Tính toán chỉ số AQI tự động
- ✅ Biểu đồ thời gian thực
- ✅ Dashboard trực quan

### ESP32 Integration
- ✅ Webhook API để nhận dữ liệu từ ESP32
- ✅ Authentication bằng API Key
- ✅ Auto-update trạng thái thiết bị
- ✅ Code mẫu ESP32 đầy đủ

## 🏗️ Kiến trúc hệ thống

```
┌─────────────┐      WiFi/HTTP      ┌──────────────┐
│   ESP32     │ ─────────────────> │   Django     │
│  + Sensors  │                     │   Backend    │
└─────────────┘                     └──────────────┘
                                           │
                                           │
                                    ┌──────┴──────┐
                                    │   Firebase   │
                                    │     Auth     │
                                    └─────────────┘
                                           │
                                           ▼
                                    ┌──────────────┐
                                    │  Web Client  │
                                    │  (Browser)   │
                                    └──────────────┘
```

## 📋 Yêu cầu hệ thống

- Python 3.8+
- Django 4.2+
- Firebase Account
- ESP32 (nếu sử dụng thiết bị thật)

## 🚀 Cài đặt

### 1. Clone repository

```bash
cd AQI_Dashboard
```

### 2. Tạo virtual environment

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# hoặc
venv\Scripts\activate  # Windows
```

### 3. Cài đặt dependencies

```bash
pip install -r requirements.txt
```

### 4. Cấu hình Firebase

Xem file `FIREBASE_SETUP.md` để biết chi tiết cách cấu hình Firebase.

**Tóm tắt:**
1. Tạo Firebase project
2. Tải `firebase-service-account.json` 
3. Đặt file vào thư mục gốc
4. Cập nhật Firebase config trong HTML templates

### 5. Migration database

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Tạo superuser

```bash
python manage.py createsuperuser
```

### 7. Chạy server

```bash
python manage.py runserver 0.0.0.0:8000
```

## 📱 Sử dụng

### Đăng ký tài khoản

1. Truy cập: http://localhost:8000/users/register/
2. Điền thông tin: họ tên, email, số điện thoại, mật khẩu
3. Click "Đăng ký"

### Đăng nhập

1. Truy cập: http://localhost:8000/users/login/
2. Nhập email và mật khẩu
3. Click "Đăng nhập"

### Thêm thiết bị IoT

1. Sau khi đăng nhập, click "Thêm thiết bị mới"
2. Điền thông tin:
   - Tên thiết bị (VD: ESP32 Phòng khách)
   - Mã thiết bị (VD: ESP32_001)
   - Vị trí (optional)
   - Mô tả (optional)
3. Click "Thêm thiết bị"
4. **QUAN TRỌNG:** Lưu lại API Key và Secret Key hiển thị

### Cấu hình ESP32

1. Mở file `ESP32_CODE_SAMPLE.ino`
2. Cập nhật các thông tin:
   ```cpp
   const char* ssid = "YOUR_WIFI_SSID";
   const char* password = "YOUR_WIFI_PASSWORD";
   const char* serverUrl = "http://YOUR_SERVER_IP:8000/devices/api/webhook/";
   const char* apiKey = "YOUR_API_KEY";
   ```
3. Upload code lên ESP32
4. Kết nối các cảm biến theo sơ đồ trong file

### Xem dashboard

1. Truy cập danh sách thiết bị: http://localhost:8000/devices/
2. Click "Xem chi tiết" trên thiết bị muốn giám sát
3. Xem dữ liệu real-time và biểu đồ

## 🔌 API Documentation

### Authentication APIs

#### POST `/users/api/auth/`
Xác thực Firebase token và tạo/cập nhật user

**Request:**
```json
{
    "idToken": "firebase_id_token",
    "fullname": "Nguyễn Văn A",
    "phone": "0123456789"
}
```

**Response:**
```json
{
    "success": true,
    "user": {
        "id": 1,
        "email": "user@example.com",
        "username": "user",
        "fullname": "Nguyễn Văn A",
        "phone": "0123456789"
    }
}
```

### Device APIs

#### GET `/devices/`
Danh sách thiết bị của user (requires login)

#### POST `/devices/add/`
Thêm thiết bị mới (requires login)

**Form Data:**
- device_name: Tên thiết bị
- device_id: Mã thiết bị (unique)
- location: Vị trí (optional)
- description: Mô tả (optional)

**Response:**
```json
{
    "success": true,
    "device_id": 1,
    "api_key": "generated_api_key",
    "secret_key": "generated_secret_key",
    "message": "Thiết bị đã được thêm thành công"
}
```

### IoT Webhook API

#### POST `/devices/api/webhook/`
Nhận dữ liệu từ ESP32

**Headers:**
```
Content-Type: application/json
X-API-Key: your_device_api_key
```

**Request Body:**
```json
{
    "temperature": 25.5,
    "humidity": 60.0,
    "gas_level": 100.0,
    "dust_density": 50.0,
    "ip_address": "192.168.1.100"
}
```

**Response:**
```json
{
    "status": "success",
    "message": "Data received",
    "data_id": 123
}
```

## 🔧 Cấu trúc Project

```
AQI_Dashboard/
├── apps/
│   ├── users/              # User management & Firebase auth
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── firebase_config.py
│   │   └── middleware.py
│   └── devices/            # Device management
│       ├── models.py
│       └── views.py
├── monitor/                # IoT monitoring
│   ├── models.py
│   └── views.py
├── templates/
│   ├── auth/              # Login/Register pages
│   ├── devices/           # Device management pages
│   └── monitor/           # Dashboard
├── static/
│   ├── css/
│   └── js/
├── aqi_dashboard/         # Django settings
├── firebase-service-account.json  # Firebase credentials (not in git)
├── ESP32_CODE_SAMPLE.ino  # ESP32 sample code
├── FIREBASE_SETUP.md      # Firebase setup guide
├── DEPLOYMENT_GUIDE.md    # Deployment instructions
└── requirements.txt
```

## 🛠️ Tech Stack

### Backend
- **Django 4.2** - Web framework
- **Django REST Framework** - API
- **Firebase Admin SDK** - Authentication
- **SQLite/PostgreSQL** - Database

### Frontend
- **Bootstrap 5** - UI framework
- **Chart.js** - Data visualization
- **Firebase JS SDK** - Client authentication
- **Vanilla JavaScript** - Client logic

### IoT
- **ESP32** - Microcontroller
- **DHT11** - Temperature & Humidity sensor
- **MQ-135** - Gas sensor
- **GP2Y10** - Dust sensor

## 📊 Database Schema

### Users (CustomUser)
- id, username, email, password
- firebase_uid, phone, fullname
- created_at, updated_at

### Devices
- id, device_id, device_name
- owner (ForeignKey to User)
- location, description, status
- is_online, last_seen, ip_address
- firmware_version, created_at, updated_at

### DeviceKeys
- id, device (OneToOne)
- api_key, secret_key
- created_at

### SensorData
- id, device (ForeignKey)
- temperature, humidity
- gas_level, dust_density
- aqi, air_quality_status
- timestamp

## 🔐 Security

- Firebase Authentication cho user management
- API Key authentication cho ESP32
- CSRF protection
- CORS configuration
- Secure password hashing
- Environment variables cho sensitive data

## 📝 Troubleshooting

Xem file `DEPLOYMENT_GUIDE.md` section "Troubleshooting" để biết cách giải quyết các vấn đề thường gặp.

## 📄 License

MIT License

## 👨‍💻 Tác giả

Dự án IoT - Thiết kế và Thi công

## 🤝 Đóng góp

Mọi đóng góp đều được chào đón! Vui lòng tạo issue hoặc pull request.

## 📞 Hỗ trợ

Nếu gặp vấn đề, vui lòng:
1. Kiểm tra file `DEPLOYMENT_GUIDE.md`
2. Xem logs: `tail -f logs/django.log`
3. Mở issue trên GitHub

---

**Note:** Đây là dự án học tập. Trong production, cần thêm các tính năng bảo mật và tối ưu hóa.

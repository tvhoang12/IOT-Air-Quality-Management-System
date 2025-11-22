# Hệ Thống Giám Sát Chất Lượng Không Khí IoT

Dashboard Django để giám sát chất lượng không khí từ ESP32.

## Tính năng

- 📊 Dashboard real-time hiển thị dữ liệu cảm biến
- 📈 Biểu đồ AQI, nhiệt độ, độ ẩm theo thời gian
- 🌡️ Hiển thị nhiệt độ, độ ẩm (DHT11)
- 💨 Hiển thị mức Gas (MQ-135)
- 🌫️ Hiển thị mật độ bụi (GP2Y10)
- 🔴 Cảnh báo theo mức AQI
- 📱 Responsive design với Bootstrap 5
- 🔌 REST API để nhận dữ liệu từ ESP32

## Cài đặt

### 1. Clone hoặc tạo môi trường ảo

```bash
cd AQI_Dashboard
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# hoặc
venv\Scripts\activate  # Windows
```

### 2. Cài đặt dependencies

```bash
pip install -r requirements.txt
```

### 3. Tạo database và migrate

```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. Tạo superuser (tùy chọn)

```bash
python manage.py createsuperuser
```

### 5. Chạy server

```bash
python manage.py runserver 0.0.0.0:8000
```

Server sẽ chạy tại: `http://localhost:8000`

## API Endpoints

### 1. Gửi dữ liệu từ ESP32
**POST** `/api/sensor-data/`

Request body (JSON):
```json
{
    "temperature": 25.5,
    "humidity": 60.0,
    "gas_level": 150.0,
    "dust_density": 35.0,
    "aqi": 85,
    "air_quality_status": "MODERATE",
    "device_id": "ESP32_001"
}
```

### 2. Lấy dữ liệu mới nhất
**GET** `/api/latest/`

### 3. Lấy dữ liệu lịch sử
**GET** `/api/historical/?hours=24`

### 4. Lấy thống kê
**GET** `/api/statistics/?hours=24`

### 5. Trạng thái thiết bị
**GET** `/api/device-status/`

### 6. Dữ liệu biểu đồ
**GET** `/api/chart-data/?hours=6`

## Mức độ AQI

| AQI | Mức độ | Màu sắc |
|-----|--------|---------|
| 0-50 | Tốt | Xanh lá |
| 51-100 | Trung bình | Vàng |
| 101-150 | Không tốt cho nhóm nhạy cảm | Cam |
| 151-200 | Không tốt | Đỏ |
| 201-300 | Rất không tốt | Tím |
| 301-500 | Nguy hại | Nâu đỏ |

## Cấu trúc thư mục

```
AQI_Dashboard/
├── aqi_dashboard/          # Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── monitor/                # App chính
│   ├── models.py          # Database models
│   ├── views.py           # API views
│   ├── serializers.py     # REST serializers
│   ├── urls.py            # URL routing
│   └── admin.py           # Django admin
├── templates/
│   └── monitor/
│       └── dashboard.html # Dashboard UI
├── manage.py
└── requirements.txt
```

## Công nghệ sử dụng

- **Backend**: Django 4.2.7, Django REST Framework
- **Frontend**: Bootstrap 5, Chart.js
- **Database**: SQLite (có thể chuyển sang PostgreSQL/MySQL)
- **Icons**: Bootstrap Icons

## Lưu ý

- Thay đổi `SECRET_KEY` trong `settings.py` khi deploy production
- Cấu hình `ALLOWED_HOSTS` và `DEBUG = False` khi deploy
- Có thể thêm authentication cho API endpoints
- Sử dụng HTTPS khi deploy production

## Tác giả

Dự án IoT - Giám sát chất lượng không khí
Kỳ 1 năm 4 - Đại học

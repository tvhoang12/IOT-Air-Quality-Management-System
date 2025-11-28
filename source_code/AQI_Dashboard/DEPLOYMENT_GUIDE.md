# Hướng dẫn Migration và Deployment

## 1. Cài đặt Dependencies

```bash
pip install -r requirements.txt
```

## 2. Tạo Migrations

Sau khi thêm các apps mới, cần tạo migrations:

```bash
# Tạo migrations cho apps mới
python manage.py makemigrations users
python manage.py makemigrations devices
python manage.py makemigrations monitor

# Áp dụng migrations
python manage.py migrate
```

## 3. Tạo Superuser

```bash
python manage.py createsuperuser
```

Nhập thông tin:
- Username: admin
- Email: admin@example.com
- Password: (mật khẩu của bạn)

## 4. Cấu hình Firebase

Xem file `FIREBASE_SETUP.md` để biết chi tiết.

**Tóm tắt:**
1. Tạo project trên Firebase Console
2. Tải file `firebase-service-account.json`
3. Đặt file vào thư mục gốc project
4. Cập nhật Firebase config trong các file HTML

## 5. Chạy Server

```bash
python manage.py runserver 0.0.0.0:8000
```

## 6. Kiểm tra hệ thống

### Đăng ký tài khoản mới:
- Truy cập: http://localhost:8000/users/register/
- Điền thông tin và đăng ký

### Đăng nhập:
- Truy cập: http://localhost:8000/users/login/
- Đăng nhập với tài khoản vừa tạo

### Thêm thiết bị:
- Sau khi đăng nhập, click "Thêm thiết bị mới"
- Điền thông tin thiết bị
- Lưu lại API Key và Secret Key

### Cấu hình ESP32:
- Sử dụng file `ESP32_CODE_SAMPLE.ino`
- Thay thế các giá trị cấu hình
- Upload lên ESP32

## 7. API Endpoints

### Authentication:
- POST `/users/api/auth/` - Firebase authentication
- GET `/users/login/` - Trang đăng nhập
- GET `/users/register/` - Trang đăng ký
- GET `/users/logout/` - Đăng xuất

### Devices:
- GET `/devices/` - Danh sách thiết bị
- GET `/devices/add/` - Thêm thiết bị mới
- GET `/devices/<id>/` - Chi tiết thiết bị
- POST `/devices/<id>/delete/` - Xóa thiết bị
- POST `/devices/<id>/update/` - Cập nhật thiết bị

### Data Webhook (cho ESP32):
- POST `/devices/api/webhook/` - Nhận dữ liệu từ ESP32
  - Header: `X-API-Key: <your_api_key>`
  - Body: JSON với temperature, humidity, gas_level, dust_density

### Monitor APIs:
- GET `/monitor/api/latest/` - Dữ liệu mới nhất
- GET `/monitor/api/historical/?hours=24` - Dữ liệu lịch sử
- GET `/monitor/api/chart-data/?hours=6` - Dữ liệu cho biểu đồ

## 8. Testing với Postman

### Test Device Webhook:

```http
POST http://localhost:8000/devices/api/webhook/
Headers:
  Content-Type: application/json
  X-API-Key: YOUR_API_KEY
Body:
{
    "temperature": 25.5,
    "humidity": 60.0,
    "gas_level": 100.0,
    "dust_density": 50.0,
    "ip_address": "192.168.1.100"
}
```

## 9. Deployment trên Production

### Cấu hình cho Production:

1. Cập nhật `settings.py`:
```python
DEBUG = False
ALLOWED_HOSTS = ['your-domain.com', 'www.your-domain.com']
SECRET_KEY = 'your-secret-key-here'  # Đổi sang key mới
```

2. Cấu hình HTTPS:
```python
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

3. Static files:
```bash
python manage.py collectstatic
```

4. Sử dụng PostgreSQL thay vì SQLite:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'aqi_dashboard',
        'USER': 'your_user',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

## 10. Troubleshooting

### Lỗi Firebase Authentication:
- Kiểm tra file `firebase-service-account.json` có đúng không
- Xác nhận Firebase config trong HTML files đã được cập nhật

### Lỗi CORS:
- Kiểm tra `CORS_ALLOWED_ORIGINS` trong settings.py
- Thêm domain/IP của bạn vào danh sách

### ESP32 không kết nối được:
- Kiểm tra API Key có đúng không
- Xác nhận server URL đúng
- Kiểm tra WiFi connection
- Xem Serial Monitor để debug

### Database errors:
- Chạy lại migrations: `python manage.py migrate`
- Xóa database và tạo mới: `rm db.sqlite3 && python manage.py migrate`

## 11. Backup và Restore

### Backup database:
```bash
python manage.py dumpdata > backup.json
```

### Restore database:
```bash
python manage.py loaddata backup.json
```

## 12. Monitoring

### Xem logs:
```bash
tail -f logs/django.log
```

### Check device status:
Truy cập Django Admin: http://localhost:8000/admin/
- Username: admin
- Password: (mật khẩu đã tạo)

## 13. Security Best Practices

1. Đổi SECRET_KEY trước khi deploy
2. Enable HTTPS trong production
3. Giữ bí mật API keys và Firebase credentials
4. Sử dụng environment variables cho sensitive data
5. Thường xuyên update dependencies
6. Implement rate limiting cho API endpoints
7. Backup database định kỳ

## 14. Performance Optimization

1. Enable database indexing
2. Use caching (Redis/Memcached)
3. Optimize queries với select_related/prefetch_related
4. Compress static files
5. Use CDN cho static files
6. Enable gzip compression

# Deploy Django lên Railway (Free)

## Bước 1: Tạo file requirements.txt

cd "/media/hoang/HDD_Code/Tài liệu học tập/Kỳ 1 năm 4/IOT/source_code/AQI_Dashboard"
pip freeze > requirements.txt

## Bước 2: Tạo Procfile

echo "web: python manage.py runserver 0.0.0.0:\$PORT" > Procfile

## Bước 3: Cài Railway CLI

npm install -g @railway/cli

## Bước 4: Deploy

railway login
railway init
railway up

## Bước 5: Lấy URL

railway domain

## Bước 6: Cập nhật code ESP32

const char* serverUrl = "https://your-app.railway.app/api/sensor-data/";

## Bước 7: Test

curl https://your-app.railway.app/api/latest/

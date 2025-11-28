#!/bin/bash

echo "======================================================================"
echo "  HƯỚNG DẪN SỬ DỤNG LOCALTUNNEL (Thay thế ngrok)"
echo "======================================================================"
echo ""
echo "Localtunnel KHÔNG CÓ anti-bot protection như ngrok!"
echo ""
echo "Bước 1: Chạy Django server"
echo "  cd '/media/hoang/HDD_Code/Tài liệu học tập/Kỳ 1 năm 4/IOT/source_code/AQI_Dashboard'"
echo "  python manage.py runserver 8000"
echo ""
echo "Bước 2: Chạy localtunnel (terminal mới)"
echo "  lt --port 8000"
echo ""
echo "Bước 3: Copy URL từ output (vd: https://funny-cat-12.loca.lt)"
echo ""
echo "Bước 4: Sửa sketch.ino dòng 26:"
echo '  const char* serverUrl = "https://YOUR-URL.loca.lt/api/sensor-data/";'
echo ""
echo "Bước 5: Chạy Wokwi simulation"
echo ""
echo "======================================================================"
echo ""
echo "Chạy localtunnel ngay bây giờ? (y/n)"
read -p "> " answer

if [ "$answer" = "y" ] || [ "$answer" = "Y" ]; then
    echo ""
    echo "🚀 Đang chạy localtunnel..."
    lt --port 8000
else
    echo "Hủy."
fi

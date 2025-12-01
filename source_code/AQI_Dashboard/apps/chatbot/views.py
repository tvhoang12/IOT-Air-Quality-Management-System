from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import json
import google.generativeai as genai
import traceback

@csrf_exempt
def chat_api(request):
    # Manual POST check
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST method allowed'}, status=405)
    
    try:
        print("[CHATBOT] Received request")
        data = json.loads(request.body)
        user_message = data.get('message', '')
        print(f"[CHATBOT] User message: {user_message}")
        
        if not user_message:
            return JsonResponse({'error': 'Message is required'}, status=400)
        
        from monitor.models import SensorData
        latest_data = SensorData.objects.order_by('-timestamp').first()
        print(f"[CHATBOT] Latest data found: {latest_data is not None}")
        
        if not latest_data:
            context = "Hiện tại chưa có dữ liệu cảm biến nào trong hệ thống."
            print("[CHATBOT] No sensor data available")
        else:
            print(f"[CHATBOT] AQI: {latest_data.aqi}, Temp: {latest_data.temperature}")
            context = f"""
Bạn là AQI Assistant - Trợ lý ảo chuyên nghiệp về chất lượng không khí và môi trường.

VAI TRÒ CỦA BẠN:
- Chuyên gia phân tích chất lượng không khí với kiến thức sâu rộng
- Cung cấp thông tin chính xác, chi tiết dựa trên dữ liệu thực tế
- Tư vấn các biện pháp bảo vệ sức khỏe phù hợp với từng tình huống
- Giải thích các chỉ số một cách dễ hiểu, khoa học

DỮ LIỆU CẢM BIẾN HIỆN TẠI:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 Chỉ số AQI: {latest_data.aqi} - Mức độ: {latest_data.get_air_quality_status_display()}
🌡️ Nhiệt độ: {latest_data.temperature}°C
💧 Độ ẩm: {latest_data.humidity}%
☁️ Nồng độ khí Gas (CO, NH3, NOx): {latest_data.gas_level} ppm
🌫️ Mật độ bụi mịn PM2.5: {latest_data.dust_density} µg/m³
⏰ Thời gian đo: {latest_data.timestamp.strftime('%H:%M:%S - %d/%m/%Y')}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

NGUYÊN TẮC TRẢ LỜI:
✅ Trả lời CHI TIẾT, đầy đủ thông tin (5-8 câu, có cấu trúc rõ ràng)
✅ Phân tích SÂU về tình trạng không khí dựa trên TỪNG CHỈ SỐ cụ thể
✅ Giải thích ẢNH HƯỞNG của các yếu tố (nhiệt độ, độ ẩm, bụi, gas) đến sức khỏe
✅ Đưa ra KHUYẾN NGHỊ CỤ THỂ: Nên làm gì? Tránh làm gì? Cho ai?
✅ So sánh với NGƯỠNG AN TOÀN của WHO/EPA nếu có liên quan
✅ Sử dụng emoji phù hợp để dễ đọc (📊, ⚠️, ✅, ❌, 💡)
✅ Phân đoạn rõ ràng: Tình trạng → Nguyên nhân → Ảnh hưởng → Khuyến nghị

ĐẶC BIỆT LƯU Ý:
⚠️ Nếu AQI >= 100: NHẤN MẠNH rủi ro sức khỏe, đưa cảnh báo cụ thể
⚠️ Nếu PM2.5 > 35 µg/m³: Cảnh báo về bụi mịn nguy hiểm
⚠️ Nếu Gas > 50 ppm: Cảnh báo khí độc hại

PHONG CÁCH:
- Chuyên nghiệp nhưng thân thiện, dễ hiểu
- Dùng tiếng Việt tự nhiên, không dùng thuật ngữ khó hiểu
- Tập trung vào GIẢI PHÁP THỰC TẾ, không chỉ lý thuyết
"""
        
        print("[CHATBOT] Configuring Gemini API...")
        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel('models/gemini-2.5-flash')  # Working model
        
        print("[CHATBOT] Calling Gemini API...")
        response = model.generate_content(context + "\n\nCâu hỏi của người dùng: " + user_message)
        print(f"[CHATBOT] Response received: {len(response.text)} chars")
        
        return JsonResponse({
            'reply': response.text,
            'status': 'success'
        })
        
    except Exception as e:
        print(f"[CHATBOT ERROR] {str(e)}")
        print(f"[CHATBOT ERROR] Traceback:\n{traceback.format_exc()}")
        return JsonResponse({
            'error': str(e),
            'status': 'error'
        }, status=500)

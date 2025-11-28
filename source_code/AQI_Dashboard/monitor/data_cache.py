# Cache để lưu dữ liệu real-time tạm thời
from datetime import datetime, timedelta
import threading

class DataCache:
    """Cache lưu dữ liệu real-time và quản lý việc lưu vào database"""
    
    def __init__(self):
        self._lock = threading.Lock()
        self._latest_data = None  # Dữ liệu real-time mới nhất
        self._last_saved_time = None  # Thời gian lưu database lần cuối
        self.SAVE_INTERVAL_MINUTES = 5  # Lưu database mỗi 5 phút
    
    def update_latest(self, data):
        """Cập nhật dữ liệu real-time mới nhất"""
        with self._lock:
            # Thêm timestamp
            data['timestamp'] = datetime.now().isoformat()
            self._latest_data = data
    
    def get_latest(self):
        """Lấy dữ liệu real-time mới nhất"""
        with self._lock:
            return self._latest_data
    
    def should_save_to_db(self):
        """Kiểm tra xem có nên lưu vào database không (mỗi 5 phút)"""
        with self._lock:
            now = datetime.now()
            
            # Lần đầu tiên hoặc đã qua 5 phút
            if self._last_saved_time is None:
                return True
            
            time_diff = now - self._last_saved_time
            return time_diff >= timedelta(minutes=self.SAVE_INTERVAL_MINUTES)
    
    def mark_saved(self):
        """Đánh dấu đã lưu vào database"""
        with self._lock:
            self._last_saved_time = datetime.now()
    
    def get_last_saved_time(self):
        """Lấy thời gian lưu database lần cuối"""
        with self._lock:
            return self._last_saved_time

# Global cache instance
data_cache = DataCache()

# Firebase Configuration
# Download service account key from Firebase Console > Project Settings > Service Accounts
# Place the JSON file in the project root and update the path below

import firebase_admin
from firebase_admin import credentials, db
import os
from datetime import datetime

# Initialize Firebase Admin SDK
def initialize_firebase():
    """Initialize Firebase Admin SDK if not already initialized"""
    if not firebase_admin._apps:
        # Path to your service account key JSON file
        # Look in parent directory (project root)
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        cred_path = os.path.join(project_root, 'firebase-service-account.json')

        if os.path.exists(cred_path):
            print(f"✓ Firebase service account key found at: {cred_path}")
            cred = credentials.Certificate(cred_path)
            
            # Initialize with Realtime Database URL
            firebase_admin.initialize_app(cred, {
                'databaseURL': 'https://aqi-iot-db-default-rtdb.asia-southeast1.firebasedatabase.app/'
            })
            print("✓ Firebase Realtime Database initialized successfully!")
        else:
            print(f"⚠️  Firebase service account key not found at: {cred_path}")
            print("📥 Download from: https://console.firebase.google.com/project/YOUR_PROJECT/settings/serviceaccounts/adminsdk")
            print("💾 Save as: firebase-service-account.json in project root")
            return None

    return db.reference()

# Firebase service functions
class FirebaseService:
    def __init__(self):
        self.db = initialize_firebase()

    def add_sensor_data(self, data):
        """Add sensor data to Realtime Database"""
        if not self.db:
            return None

        try:
            # Reference to sensor_data collection
            ref = self.db.child('sensor_data')
            
            # Add timestamp
            data['timestamp'] = datetime.now().isoformat()
            
            # Push new data (auto-generates unique key)
            new_ref = ref.push(data)
            return new_ref.key
        except Exception as e:
            print(f"Error adding sensor data: {e}")
            return None

    def get_latest_data(self):
        """Get latest sensor data"""
        if not self.db:
            return None

        try:
            ref = self.db.child('sensor_data')
            
            # Query last record (ordered by key which is timestamp-based)
            latest = ref.order_by_key().limit_to_last(1).get()
            
            if latest:
                # Get the first (and only) item from dict
                for key, value in latest.items():
                    return value
            return None
        except Exception as e:
            print(f"Error getting latest data: {e}")
            return None

    def get_historical_data(self, hours=24):
        """Get historical data for the last N hours"""
        if not self.db:
            return []

        try:
            ref = self.db.child('sensor_data')
            
            # Get all data and filter by timestamp in Python
            all_data = ref.order_by_key().limit_to_last(100).get()
            
            if not all_data:
                return []
            
            # Convert to list
            data_list = []
            for key, value in all_data.items():
                data_list.append(value)
            
            # Sort by timestamp descending
            data_list.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
            
            return data_list
        except Exception as e:
            print(f"Error getting historical data: {e}")
            return []

    def get_chart_data(self, hours=6):
        """Get data for charts (simplified for performance)"""
        return self.get_historical_data(hours)

    def get_statistics(self):
        """Get basic statistics"""
        if not self.db:
            return {}

        try:
            ref = self.db.child('sensor_data')
            
            # Get last 100 records
            all_data = ref.order_by_key().limit_to_last(100).get()
            
            if not all_data:
                return {'total_records': 0}
            
            # Convert to list
            data = list(all_data.values())

            temperatures = [d.get('temperature', 0) for d in data]
            humidities = [d.get('humidity', 0) for d in data]
            aqis = [d.get('aqi', 0) for d in data]

            return {
                'total_records': len(data),
                'avg_temperature': round(sum(temperatures) / len(temperatures), 1) if temperatures else 0,
                'avg_humidity': round(sum(humidities) / len(humidities), 1) if humidities else 0,
                'avg_aqi': round(sum(aqis) / len(aqis), 1) if aqis else 0,
                'max_aqi': max(aqis) if aqis else 0,
                'min_aqi': min(aqis) if aqis else 0
            }
        except Exception as e:
            print(f"Error getting statistics: {e}")
            return {}

# Global Firebase service instance
firebase_service = FirebaseService()
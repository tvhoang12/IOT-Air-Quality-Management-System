# Firebase Service Account Configuration Template

Để hệ thống authentication hoạt động, bạn cần:

## 1. Tạo Firebase Project

1. Truy cập [Firebase Console](https://console.firebase.google.com/)
2. Tạo project mới hoặc chọn project hiện có
3. Vào **Project Settings** > **Service Accounts**
4. Click **Generate new private key**
5. Lưu file JSON vừa tải về thành `firebase-service-account.json` tại thư mục gốc project

## 2. Cấu hình Firebase Authentication

1. Trong Firebase Console, vào **Authentication**
2. Click **Get Started**
3. Enable **Email/Password** sign-in method
4. (Optional) Enable các phương thức đăng nhập khác nếu cần

## 3. Lấy Firebase Config cho Web

1. Vào **Project Settings** > **General**
2. Scroll xuống phần **Your apps**
3. Click icon **Web** (</>) để thêm app
4. Copy **Firebase configuration** object
5. Paste vào các file template:
   - `templates/auth/login.html`
   - `templates/auth/register.html`

Config sẽ có dạng:
```javascript
const firebaseConfig = {
    apiKey: "AIza...",
    authDomain: "your-project.firebaseapp.com",
    projectId: "your-project-id",
    storageBucket: "your-project.appspot.com",
    messagingSenderId: "123456789",
    appId: "1:123456789:web:abc..."
};
```

## 4. Cấu trúc file firebase-service-account.json

File này sẽ có dạng:
```json
{
  "type": "service_account",
  "project_id": "your-project-id",
  "private_key_id": "...",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
  "client_email": "firebase-adminsdk-...@your-project.iam.gserviceaccount.com",
  "client_id": "...",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "..."
}
```

## 5. Bảo mật

⚠️ **QUAN TRỌNG**: 
- KHÔNG commit file `firebase-service-account.json` lên Git
- File này đã được thêm vào `.gitignore`
- Giữ bí mật các thông tin authentication

# FitFinder Quick Reference

## 🚀 Essential Commands

```bash
# Setup
cd d:\PROJECTS\FITFINDER-
.venv\Scripts\activate
pip install -r requirements.txt

# Initialize Database (first time)
python init_db.py

# Start Server
python app.py

# Run Tests (in another terminal)
python tests/test_api.py

# Organize Project
python organize_project.py
```

---

## 🔌 Health Check

**Endpoint**: `GET /api/health`

```bash
curl http://localhost:5000/api/health
```

**Response**:
```json
{
  "status": "healthy",
  "api_key_loaded": true,
  "miragic": true
}
```

---

## 🔐 Authentication

### Register New User
```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"userid":"newuser","password":"Pass@123"}'
```

### Login (Get Token)
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"userid":"admin123","password":"Secret@123"}'
```

**Response** (save the `token`):
```json
{
  "success": true,
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "userid": "admin123",
    "userId": 1,
    "role": "ADMIN"
  }
}
```

### Logout (Blacklist Token)
```bash
curl -X POST http://localhost:5000/api/auth/logout \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Refresh Token
```bash
curl -X POST http://localhost:5000/api/auth/refresh \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 👤 Profile Management

### Get Profile
```bash
curl http://localhost:5000/api/profile \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Update Profile
```bash
curl -X PUT http://localhost:5000/api/profile/update \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "gender": "male",
    "preferredStyle": "casual",
    "preferredColor": "blue"
  }'
```

---

## 👗 Outfit Generation

```bash
curl -X POST http://localhost:5000/api/outfit/generate \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "style": "casual",
    "occasion": "daily",
    "gender": "female",
    "season": "spring",
    "colorPreference": "neutral"
  }'
```

---

## 🎭 Virtual Try-On

### Single Garment

**Using Python requests library**:
```python
import requests
from PIL import Image
import io

# Create a test image
img = Image.new('RGB', (100, 100), color='red')
img_bytes = io.BytesIO()
img.save(img_bytes, format='PNG')
img_bytes.seek(0)

# Upload
files = {
    'humanImage': ('person.png', img_bytes, 'image/png'),
    'clothImage': ('clothing.png', img_bytes, 'image/png')
}
data = {'garmentType': 'full_body'}
headers = {"Authorization": "Bearer YOUR_TOKEN"}

response = requests.post(
    'http://localhost:5000/api/tryon/single',
    files=files,
    data=data,
    headers=headers
)
print(response.json())
```

### Combo Try-On (Top + Bottom)

```python
files = {
    'humanImage': ('person.png', img_bytes, 'image/png'),
    'clothImage': ('top.png', img_bytes, 'image/png'),
    'bottomClothImage': ('bottom.png', img_bytes, 'image/png')
}

response = requests.post(
    'http://localhost:5000/api/tryon/combo',
    files=files,
    headers={"Authorization": "Bearer YOUR_TOKEN"}
)
```

### Check Job Status
```bash
curl http://localhost:5000/api/tryon/jobs/JOB_ID \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 🖼️ Gallery

### Get Saved Outfits
```bash
curl http://localhost:5000/api/gallery \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Save Outfit
```bash
curl -X POST http://localhost:5000/api/gallery/save \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "outfitName": "Summer Casual",
    "outfitDescription": "Perfect for summer",
    "style": "casual",
    "occasion": "everyday",
    "gender": "female",
    "imageUrl": "https://example.com/outfit.jpg"
  }'
```

---

## 📜 History

### Get Try-On History
```bash
curl http://localhost:5000/api/history \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Save Try-On Result
```bash
curl -X POST http://localhost:5000/api/history/save \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "humanImageUrl": "https://example.com/person.jpg",
    "clothingImageUrl": "https://example.com/clothing.jpg",
    "resultImageUrl": "https://example.com/result.jpg",
    "garmentType": "full_body",
    "description": "Summer try-on"
  }'
```

---

## 📧 Contact

```bash
curl -X POST http://localhost:5000/api/contact \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "message": "Great app!"
  }'
```

---

## 🧪 Testing

### Run Full Test Suite
```bash
python tests/test_api.py
```

### Test with Python
```python
import requests

# Test health
r = requests.get('http://localhost:5000/api/health')
print(r.json())

# Test login
r = requests.post('http://localhost:5000/api/auth/login',
  json={'userid': 'admin123', 'password': 'Secret@123'})
token = r.json()['data']['token']

# Test protected endpoint
r = requests.get('http://localhost:5000/api/profile',
  headers={'Authorization': f'Bearer {token}'})
print(r.json())
```

---

## 🔑 Default Admin Account

| Field | Value |
|-------|-------|
| UserID | `admin123` |
| Password | `Secret@123` |
| Role | `ADMIN` |

---

## 🌍 Environment Variables

Create `.env` in project root:

```env
# Flask
FLASK_ENV=development
SECRET_KEY=your-minimum-32-character-secret-key

# Database
DATABASE_URL=sqlite:///fitfinder.db

# API
MIRAGIC_API_KEY=your_api_key_here

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:5000
```

---

## 📂 Important Files

| File | Purpose |
|------|---------|
| `app.py` | Main Flask backend |
| `init_db.py` | Database initialization |
| `tests/test_api.py` | Test suite |
| `.env` | Environment config |
| `requirements.txt` | Dependencies |
| `README.md` | Project guide |
| `STRUCTURE.md` | Folder structure |
| `GETTING_STARTED.md` | Quick start |

---

## 🐛 Troubleshooting

### API doesn't start?
```bash
# Check version
python --version  # Should be 3.8+

# Try with explicit settings
set FLASK_ENV=development
python app.py
```

### Port 5000 in use?
```bash
# Use different port
python app.py --port=8000
```

### Can't login?
```bash
# Recreate database
python init_db.py

# Use default creds:
# userid: admin123
# password: Secret@123
```

### Tests failing?
```bash
# Make sure API is running:
python app.py  # In one terminal

# Then run tests in another:
python tests/test_api.py
```

---

## 📊 HTTP Status Codes

| Code | Meaning | Common Response |
|------|---------|-----------------|
| 200 | Success | `{"success": true}` |
| 400 | Bad Request | `{"error": "Invalid input"}` |
| 401 | Unauthorized | `{"error": "Token required"}` |
| 403 | Forbidden | `{"error": "Invalid token"}` |
| 404 | Not Found | `{"error": "Endpoint not found"}` |
| 413 | Payload Too Large | `{"error": "File too large (6MB max)"}` |
| 500 | Server Error | `{"error": "Internal error"}` |

---

## 🚀 Deployment

### Development
```bash
python app.py
```

### Production with Gunicorn
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Docker
```bash
docker build -t fitfinder .
docker run -e SECRET_KEY=key -p 5000:5000 fitfinder
```

### Railway.app
```bash
railway up
```

---

## 📚 All Endpoints Summary

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/health` | No | Health check |
| POST | `/api/auth/register` | No | Register user |
| POST | `/api/auth/login` | No | Login & get token |
| POST | `/api/auth/logout` | Yes | Logout & blacklist token |
| POST | `/api/auth/refresh` | Yes | Refresh token |
| GET | `/api/profile` | Yes | Get profile |
| PUT | `/api/profile/update` | Yes | Update profile |
| POST | `/api/outfit/generate` | Yes | Generate outfit |
| POST | `/api/tryon/single` | Yes | Single try-on |
| POST | `/api/tryon/combo` | Yes | Combo try-on |
| GET | `/api/tryon/jobs/:id` | Yes | Job status |
| GET | `/api/gallery` | Yes | Get gallery |
| POST | `/api/gallery/save` | Yes | Save to gallery |
| GET | `/api/history` | Yes | Get history |
| POST | `/api/history/save` | Yes | Save to history |
| POST | `/api/contact` | No | Contact form |

---

**Last Updated**: 2024
**Status**: ✅ Production Ready

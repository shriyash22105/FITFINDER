# FitFinder Java - Complete API Documentation

## 📍 Base URL
```
http://localhost:5000
```

## 🔐 Authentication
All protected endpoints require an active HTTP session with `user` attribute.

---

## 🔓 Authentication Endpoints

### 1. User Login

**Endpoint:**
```
POST /login
```

**Content-Type:**
```
application/x-www-form-urlencoded
```

**Request Body:**
```
userid=admin123&password=Secret@123
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Login successful"
}
```

**Response (401 Unauthorized):**
```json
{
  "success": false,
  "error": "Invalid credentials",
  "message": "User ID or password is incorrect"
}
```

**Example cURL:**
```bash
curl -X POST http://localhost:5000/login \
  -d "userid=admin123&password=Secret@123" \
  -c cookies.txt
```

---

### 2. User Logout

**Endpoint:**
```
GET /logout
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Logout successful"
}
```

**Example cURL:**
```bash
curl -X GET http://localhost:5000/logout \
  -b cookies.txt
```

---

### 3. Check Authentication Status

**Endpoint:**
```
GET /api/auth/status
```

**Response (200 OK - Authenticated):**
```json
{
  "authenticated": true,
  "userid": "admin123"
}
```

**Response (200 OK - Not Authenticated):**
```json
{
  "authenticated": false
}
```

**Example cURL:**
```bash
curl http://localhost:5000/api/auth/status -b cookies.txt
```

---

### 4. User Registration (Optional)

**Endpoint:**
```
POST /api/auth/register
```

**Content-Type:**
```
application/x-www-form-urlencoded
```

**Request Body:**
```
userid=newuser&password=NewPassword123
```

**Response (201 Created):**
```json
{
  "success": true,
  "data": "User registered successfully"
}
```

**Response (400 Bad Request):**
```json
{
  "success": false,
  "error": "Registration failed",
  "message": "User already exists: newuser"
}
```

**Example cURL:**
```bash
curl -X POST http://localhost:5000/api/auth/register \
  -d "userid=newuser&password=NewPassword123"
```

---

## 📸 Virtual Try-On Endpoints

### 5. Single Garment Try-On

**Endpoint:**
```
POST /api/tryon/single
```

**Content-Type:**
```
multipart/form-data
```

**Request Parameters:**
- `humanImage` (required): MultipartFile - Image of person wearing clothes
- `clothImage` (required): MultipartFile - Image of clothing item
- `garmentType` (optional): String - Type of garment (default: "full_body")

**Supported Garment Types:**
- `full_body` - Full body garment
- `top` - Upper body only
- `bottom` - Lower body only
- `dress` - Full dress

**Response (200 OK - With Miragic API):**
```json
{
  "success": true,
  "data": {
    "success": true,
    "data": {
      "status": "COMPLETED",
      "jobId": "abc123xyz",
      "resultUrl": "https://..."
    }
  }
}
```

**Response (200 OK - Local Fallback):**
```json
{
  "success": true,
  "note": "local_fallback",
  "data": {
    "success": true,
    "note": "local_fallback",
    "file": "virtual_tryon_fallback_1702345678901.png",
    "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAUA..."
  }
}
```

**Response (400 Bad Request):**
```json
{
  "success": false,
  "error": "humanImage and clothImage are required"
}
```

**Response (500 Internal Server Error):**
```json
{
  "success": false,
  "error": "Processing failed",
  "message": "Unable to process images"
}
```

**Example cURL:**
```bash
curl -X POST http://localhost:5000/api/tryon/single \
  -F "humanImage=@path/to/human.jpg" \
  -F "clothImage=@path/to/cloth.jpg" \
  -F "garmentType=full_body" \
  -b cookies.txt
```

**Example JavaScript (Fetch API):**
```javascript
const formData = new FormData();
formData.append('humanImage', document.getElementById('humanInput').files[0]);
formData.append('clothImage', document.getElementById('clothInput').files[0]);
formData.append('garmentType', 'full_body');

fetch('/api/tryon/single', {
  method: 'POST',
  body: formData,
  credentials: 'include'
})
.then(res => res.json())
.then(data => {
  if (data.success) {
    console.log('Try-on successful!', data.data);
  }
})
.catch(err => console.error(err));
```

---

### 6. Combo Garment Try-On (Top + Bottom)

**Endpoint:**
```
POST /api/tryon/combo
```

**Content-Type:**
```
multipart/form-data
```

**Request Parameters:**
- `humanImage` (required): MultipartFile - Image of person
- `clothImage` (required): MultipartFile - Top/shirt image
- `bottomClothImage` (required): MultipartFile - Bottom/pants image
- `garmentType` (optional): String - Type of combination (default: "comb")

**Response (200 OK):**
```json
{
  "success": true,
  "note": "local_fallback",
  "data": {
    "success": true,
    "note": "local_fallback",
    "file": "virtual_tryon_fallback_combo_1702345678901.png"
  }
}
```

**Response (400 Bad Request):**
```json
{
  "success": false,
  "error": "humanImage, clothImage, and bottomClothImage are required"
}
```

**Example cURL:**
```bash
curl -X POST http://localhost:5000/api/tryon/combo \
  -F "humanImage=@path/to/human.jpg" \
  -F "clothImage=@path/to/top.jpg" \
  -F "bottomClothImage=@path/to/bottom.jpg" \
  -F "garmentType=comb" \
  -b cookies.txt
```

---

## ❤️ System Endpoints

### 7. Health Check

**Endpoint:**
```
GET /api/health
```

**Response (200 OK):**
```json
{
  "status": "healthy",
  "miragic": true,
  "timestamp": 1702345678901
}
```

**Response Fields:**
- `status` (String): System status ("healthy" or "error")
- `miragic` (Boolean): Miragic API integration available
- `timestamp` (Long): Unix timestamp in milliseconds

**Example cURL:**
```bash
curl http://localhost:5000/api/health
```

**Example Monitoring Script:**
```bash
#!/bin/bash
while true; do
  response=$(curl -s http://localhost:5000/api/health)
  status=$(echo $response | jq -r '.status')
  
  if [ "$status" != "healthy" ]; then
    echo "Alert: Service is not healthy!"
    # Send alert/notification
  fi
  
  sleep 30
done
```

---

## 📋 HTTP Status Codes

| Status | Meaning | Example |
|--------|---------|---------|
| 200 | OK | Successful login, try-on completed |
| 201 | Created | User registered successfully |
| 400 | Bad Request | Missing required fields |
| 401 | Unauthorized | Invalid credentials |
| 500 | Internal Server Error | Processing failed |

---

## 🔄 Request/Response Examples

### Complete Try-On Flow

**Step 1: Login**
```bash
curl -X POST http://localhost:5000/login \
  -d "userid=admin123&password=Secret@123" \
  -c cookies.txt
```

**Step 2: Upload Images for Try-On**
```bash
curl -X POST http://localhost:5000/api/tryon/single \
  -F "humanImage=@person.jpg" \
  -F "clothImage=@shirt.jpg" \
  -F "garmentType=top" \
  -b cookies.txt \
  -o result.json
```

**Step 3: Process Response**
```bash
cat result.json | jq '.data.file'
# Output: virtual_tryon_fallback_1702345678901.png
```

**Step 4: Logout**
```bash
curl http://localhost:5000/logout -b cookies.txt
```

---

## 🧪 Testing with Postman

### Postman Collection JSON

```json
{
  "info": {
    "name": "FitFinder API",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Login",
      "request": {
        "method": "POST",
        "header": [],
        "body": {
          "mode": "urlencoded",
          "urlencoded": [
            {
              "key": "userid",
              "value": "admin123"
            },
            {
              "key": "password",
              "value": "Secret@123"
            }
          ]
        },
        "url": {
          "raw": "http://localhost:5000/login",
          "protocol": "http",
          "host": ["localhost"],
          "port": "5000",
          "path": ["login"]
        }
      }
    },
    {
      "name": "Single Try-On",
      "request": {
        "method": "POST",
        "header": [],
        "body": {
          "mode": "formdata",
          "formdata": [
            {
              "key": "humanImage",
              "type": "file",
              "src": "path/to/human.jpg"
            },
            {
              "key": "clothImage",
              "type": "file",
              "src": "path/to/cloth.jpg"
            },
            {
              "key": "garmentType",
              "value": "full_body",
              "type": "text"
            }
          ]
        },
        "url": {
          "raw": "http://localhost:5000/api/tryon/single",
          "protocol": "http",
          "host": ["localhost"],
          "port": "5000",
          "path": ["api", "tryon", "single"]
        }
      }
    }
  ]
}
```

---

## 📱 Frontend Integration Examples

### React.js Example

```javascript
import React, { useState } from 'react';

function VirtualTryOn() {
  const [humanImage, setHumanImage] = useState(null);
  const [clothImage, setClothImage] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleTryOn = async () => {
    const formData = new FormData();
    formData.append('humanImage', humanImage);
    formData.append('clothImage', clothImage);
    formData.append('garmentType', 'full_body');

    setLoading(true);
    try {
      const response = await fetch('/api/tryon/single', {
        method: 'POST',
        body: formData,
        credentials: 'include'
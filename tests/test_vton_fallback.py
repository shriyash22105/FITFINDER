import os
import time
import requests
from io import BytesIO
from PIL import Image

def generate_mock_image(color, size=(300, 300), format='JPEG'):
    img = Image.new('RGB', size, color=color)
    output = BytesIO()
    img.save(output, format=format)
    output.seek(0)
    return output

def test_vton_single_fallback():
    base_url = "http://127.0.0.1:5000/api"
    print(f"--- Authenticating and Testing VTON Fallback on {base_url} ---")
    
    # 1. Register
    uid = f"tester_{int(time.time())}"
    requests.post(f"{base_url}/auth/register", json={"userid": uid, "password": "password123"})
    
    # 2. Login
    login_resp = requests.post(f"{base_url}/auth/login", json={"userid": uid, "password": "password123"})
    token = login_resp.json().get('data', {}).get('token')
    if not token:
        print("❌ Login failed, no token!")
        return

    # 3. Upload images
    human_img = generate_mock_image('blue')
    cloth_img = generate_mock_image('red')
    
    files = {
        'humanImage': ('test_human.jpg', human_img, 'image/jpeg'),
        'clothImage': ('test_cloth.jpg', cloth_img, 'image/jpeg')
    }
    
    headers = {
        'Authorization': f'Bearer {token}'
    }

    print("[1] Firing multi-part upload to backend API...")
    start_time = time.time()
    try:
        response = requests.post(f"{base_url}/tryon/single", files=files, headers=headers, timeout=120)
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print(f"✅ SUCCESS in {elapsed:.2f}s!")
                print(f"   Route resolved to: {result.get('note', 'unknown strategy')}")
            else:
                print(f"❌ API logical failure: {result.get('error')} | details: {result.get('details')}")
        else:
            print(f"❌ HTTP Error {response.status_code}: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed completely: {e}")

if __name__ == "__main__":
    test_vton_single_fallback()

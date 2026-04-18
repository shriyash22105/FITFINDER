import requests
from PIL import Image
import io
import time

BASE_URL = 'http://localhost:5000'
TOKEN = None  # Will login first

class TryOnTester:
    def __init__(self):
        self.headers = {}
        self.login()
    
    def login(self):
        payload = {'userid': 'admin123', 'password': 'Secret@123'}
        resp = requests.post(f'{BASE_URL}/api/auth/login', json=payload)
        data = resp.json()
        self.TOKEN = data['data']['token']
        self.headers = {'Authorization': f'Bearer {self.TOKEN}'}
        print('Login token obtained')
    
    def create_image(self, color='red'):
        img = Image.new('RGB', (224, 224), color=color)
        buf = io.BytesIO()
        img.save(buf, 'JPEG')
        buf.seek(0)
        return buf
    
    def test_single_tryon(self):
        print('\\n=== SINGLE TRY-ON TEST ===')
        human = self.create_image('blue')
        cloth = self.create_image('green')
        
        files = {
            'humanImage': ('human.jpg', human, 'image/jpeg'),
            'clothImage': ('cloth.jpg', cloth, 'image/jpeg')
        }
        data = {'garmentType': 'full_body'}
        
        resp = requests.post(f'{BASE_URL}/api/tryon/single', files=files, data=data, headers=self.headers)
        print(f'Status: {resp.status_code}')
        print(resp.json())
        assert resp.status_code == 200
        assert resp.json()['success']
        print('✓ SINGLE TRY-ON PASS')
    
    def test_combo_tryon(self):
        print('\\n=== COMBO TRY-ON TEST ===')
        human = self.create_image('blue')
        top = self.create_image('yellow')
        bottom = self.create_image('purple')
        
        files = {
            'humanImage': ('human.jpg', human, 'image/jpeg'),
            'clothImage': ('top.jpg', top, 'image/jpeg'),
            'bottomClothImage': ('bottom.jpg', bottom, 'image/jpeg')
        }
        
        resp = requests.post(f'{BASE_URL}/api/tryon/combo', files=files, headers=self.headers)
        print(f'Status: {resp.status_code}')
        print(resp.json())
        assert resp.status_code == 200
        assert resp.json()['success']
        print('✓ COMBO TRY-ON PASS')

if __name__ == '__main__':
    tester = TryOnTester()
    tester.test_single_tryon()
    tester.test_combo_tryon()
    print('\\nVirtual Try-On Tests COMPLETE!')


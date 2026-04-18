"""
FitFinder API Test Suite
Comprehensive tests for all endpoints with proper authentication
"""

import requests
import json
import os
from pathlib import Path
from PIL import Image
import io

# Configuration
BASE_URL = "http://localhost:5000"
DEFAULT_USER = "admin123"
DEFAULT_PASS = "Secret@123"

class FitFinderAPITester:
    def __init__(self, base_url=BASE_URL):
        self.base_url = base_url
        self.token = None
        self.user_id = None
        self.headers = {"Content-Type": "application/json"}
    
    def create_test_image(self, width=100, height=100):
        """Create a simple test image"""
        img = Image.new('RGB', (width, height), color='red')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        return img_bytes
    
    def print_response(self, title, response):
        """Pretty print API response"""
        print(f"\n{'='*60}")
        print(f"🔹 {title}")
        print(f"{'='*60}")
        print(f"Status Code: {response.status_code}")
        try:
            print(json.dumps(response.json(), indent=2))
        except:
            print(response.text)
        print(f"{'='*60}\n")
    
    # ============ HEALTH & AUTH ============
    
    def test_health(self):
        """Test health endpoint"""
        print("\n✓ Testing Health Endpoint...")
        response = requests.get(f"{self.base_url}/api/health")
        self.print_response("HEALTH CHECK", response)
        return response.status_code == 200
    
    def test_register(self, userid="testuser", password="Test@123"):
        """Test user registration"""
        print(f"\n✓ Testing Registration (userid: {userid})...")
        payload = {"userid": userid, "password": password}
        response = requests.post(
            f"{self.base_url}/api/auth/register",
            json=payload,
            headers=self.headers
        )
        self.print_response("REGISTER", response)
        return response.status_code in [200, 400]  # 200 = success, 400 = already exists
    
    def test_login(self, userid=DEFAULT_USER, password=DEFAULT_PASS):
        """Test user login"""
        print(f"\n✓ Testing Login (userid: {userid})...")
        payload = {"userid": userid, "password": password}
        response = requests.post(
            f"{self.base_url}/api/auth/login",
            json=payload,
            headers=self.headers
        )
        self.print_response("LOGIN", response)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                self.token = data["data"]["token"]
                self.user_id = data["data"]["userId"]
                self.headers["Authorization"] = f"Bearer {self.token}"
                print(f"✓ Token obtained: {self.token[:50]}...")
                return True
        return False
    
    def test_logout(self):
        """Test user logout"""
        print("\n✓ Testing Logout...")
        response = requests.post(
            f"{self.base_url}/api/auth/logout",
            headers=self.headers
        )
        self.print_response("LOGOUT", response)
        return response.status_code == 200
    
    def test_refresh_token(self):
        """Test token refresh"""
        print("\n✓ Testing Token Refresh...")
        response = requests.post(
            f"{self.base_url}/api/auth/refresh",
            headers=self.headers
        )
        self.print_response("REFRESH TOKEN", response)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                self.token = data["data"]["token"]
                self.headers["Authorization"] = f"Bearer {self.token}"
                return True
        return False
    
    # ============ PROFILE ============
    
    def test_get_profile(self):
        """Test get user profile"""
        print("\n✓ Testing Get Profile...")
        response = requests.get(
            f"{self.base_url}/api/profile",
            headers=self.headers
        )
        self.print_response("GET PROFILE", response)
        return response.status_code == 200
    
    def test_update_profile(self):
        """Test update user profile"""
        print("\n✓ Testing Update Profile...")
        payload = {
            "name": "Test User",
            "email": "test@fitfinder.com",
            "gender": "female",
            "preferredStyle": "casual",
            "preferredColor": "blue"
        }
        response = requests.put(
            f"{self.base_url}/api/profile/update",
            json=payload,
            headers=self.headers
        )
        self.print_response("UPDATE PROFILE", response)
        return response.status_code == 200
    
    # ============ OUTFIT GENERATOR ============
    
    def test_generate_outfit(self):
        """Test outfit generation"""
        print("\n✓ Testing Outfit Generation...")
        payload = {
            "style": "casual",
            "occasion": "daily",
            "gender": "female",
            "season": "spring",
            "colorPreference": "neutral"
        }
        response = requests.post(
            f"{self.base_url}/api/outfit/generate",
            json=payload,
            headers=self.headers
        )
        self.print_response("GENERATE OUTFIT", response)
        return response.status_code == 200
    
    # ============ VIRTUAL TRY-ON ============
    
    def test_tryon_single(self):
        """Test single garment virtual try-on"""
        print("\n✓ Testing Single Virtual Try-On...")
        
        human_img = self.create_test_image()
        cloth_img = self.create_test_image()
        
        files = {
            'humanImage': ('person.png', human_img, 'image/png'),
            'clothImage': ('clothing.png', cloth_img, 'image/png')
        }
        data = {'garmentType': 'full_body'}
        
        # Remove Content-Type from headers for multipart
        headers = {"Authorization": f"Bearer {self.token}"}
        
        response = requests.post(
            f"{self.base_url}/api/tryon/single",
            files=files,
            data=data,
            headers=headers
        )
        self.print_response("TRY-ON SINGLE", response)
        return response.status_code == 200
    
    def test_tryon_combo(self):
        """Test combo (top + bottom) virtual try-on"""
        print("\n✓ Testing Combo Virtual Try-On...")
        
        human_img = self.create_test_image()
        top_img = self.create_test_image()
        bottom_img = self.create_test_image()
        
        files = {
            'humanImage': ('person.png', human_img, 'image/png'),
            'clothImage': ('top.png', top_img, 'image/png'),
            'bottomClothImage': ('bottom.png', bottom_img, 'image/png')
        }
        
        headers = {"Authorization": f"Bearer {self.token}"}
        
        response = requests.post(
            f"{self.base_url}/api/tryon/combo",
            files=files,
            headers=headers
        )
        self.print_response("TRY-ON COMBO", response)
        return response.status_code == 200
    
    # ============ GALLERY ============
    
    def test_get_gallery(self):
        """Test get saved outfits"""
        print("\n✓ Testing Get Gallery...")
        response = requests.get(
            f"{self.base_url}/api/gallery",
            headers=self.headers
        )
        self.print_response("GET GALLERY", response)
        return response.status_code == 200
    
    def test_save_to_gallery(self):
        """Test save outfit to gallery"""
        print("\n✓ Testing Save to Gallery...")
        payload = {
            "outfitName": "Summer Casual",
            "outfitDescription": "Perfect for summer days",
            "style": "casual",
            "occasion": "everyday",
            "gender": "female",
            "imageUrl": "https://example.com/outfit.jpg"
        }
        response = requests.post(
            f"{self.base_url}/api/gallery/save",
            json=payload,
            headers=self.headers
        )
        self.print_response("SAVE TO GALLERY", response)
        return response.status_code == 200
    
    # ============ HISTORY ============
    
    def test_get_history(self):
        """Test get try-on history"""
        print("\n✓ Testing Get History...")
        response = requests.get(
            f"{self.base_url}/api/history",
            headers=self.headers
        )
        self.print_response("GET HISTORY", response)
        return response.status_code == 200
    
    def test_save_history(self):
        """Test save try-on history"""
        print("\n✓ Testing Save History...")
        payload = {
            "humanImageUrl": "https://example.com/person.jpg",
            "clothingImageUrl": "https://example.com/clothing.jpg",
            "resultImageUrl": "https://example.com/result.jpg",
            "garmentType": "full_body",
            "description": "Test try-on"
        }
        response = requests.post(
            f"{self.base_url}/api/history/save",
            json=payload,
            headers=self.headers
        )
        self.print_response("SAVE HISTORY", response)
        return response.status_code == 200
    
    # ============ CONTACT ============
    
    def test_contact(self):
        """Test contact form submission"""
        print("\n✓ Testing Contact Form...")
        payload = {
            "name": "Test User",
            "email": "test@example.com",
            "message": "This is a test message"
        }
        response = requests.post(
            f"{self.base_url}/api/contact",
            json=payload,
            headers=self.headers
        )
        self.print_response("CONTACT FORM", response)
        return response.status_code == 200
    
    # ============ FULL TEST SUITE ============
    
    def run_all_tests(self):
        """Run complete test suite"""
        print("\n" + "="*60)
        print("🚀 FITFINDER API TEST SUITE")
        print("="*60)
        
        results = {}
        
        # Health & Auth
        results['Health'] = self.test_health()
        results['Login'] = self.test_login()
        results['Get Profile'] = self.test_get_profile()
        results['Update Profile'] = self.test_update_profile()
        results['Refresh Token'] = self.test_refresh_token()
        
        # Features
        results['Generate Outfit'] = self.test_generate_outfit()
        results['Single Try-On'] = self.test_tryon_single()
        results['Combo Try-On'] = self.test_tryon_combo()
        results['Get Gallery'] = self.test_get_gallery()
        results['Save to Gallery'] = self.test_save_to_gallery()
        results['Get History'] = self.test_get_history()
        results['Save History'] = self.test_save_history()
        results['Contact'] = self.test_contact()
        results['Logout'] = self.test_logout()
        
        # Summary
        print("\n" + "="*60)
        print("📊 TEST SUMMARY")
        print("="*60)
        passed = sum(1 for v in results.values() if v)
        total = len(results)
        
        for test_name, result in results.items():
            status = "✓ PASS" if result else "✗ FAIL"
            print(f"{test_name:.<40} {status}")
        
        print("="*60)
        print(f"Results: {passed}/{total} tests passed")
        print("="*60 + "\n")
        
        return passed == total


if __name__ == "__main__":
    tester = FitFinderAPITester()
    tester.run_all_tests()

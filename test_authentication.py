#!/usr/bin/env python3
"""
Test script to demonstrate proper authentication with the Ageri Research Platform API
"""

import requests
import json

# Configuration
BASE_URL = "http://127.0.0.1:8000"
LOGIN_URL = f"{BASE_URL}/api/auth/login/"
ANNOUNCEMENTS_URL = f"{BASE_URL}/api/content/announcements/"
ENROLL_URL = f"{BASE_URL}/api/training/courses/6/enroll/"

# Test credentials (use the superuser you created)
CREDENTIALS = {
    "email": "abdo@ageri.com",  # Your superuser email
    "password": "admin123"  # Replace with your actual password if different
}

def test_authentication():
    """Test the authentication flow"""
    print("🔐 Testing Authentication Flow")
    print("=" * 50)
    
    # Step 1: Login to get JWT tokens
    print("1️⃣ Logging in...")
    try:
        login_response = requests.post(
            LOGIN_URL,
            json=CREDENTIALS,
            headers={"Content-Type": "application/json"}
        )
        
        if login_response.status_code == 200:
            tokens = login_response.json()
            access_token = tokens.get('access')
            print(f"✅ Login successful! Access token: {access_token[:50]}...")
            
            # Step 2: Test protected endpoints with authentication
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            # Test announcements endpoint
            print("\n2️⃣ Testing announcements endpoint...")
            announcements_response = requests.get(ANNOUNCEMENTS_URL, headers=headers)
            print(f"Status: {announcements_response.status_code}")
            if announcements_response.status_code == 200:
                print("✅ Announcements retrieved successfully!")
                data = announcements_response.json()
                print(f"Found {len(data.get('results', []))} announcements")
            else:
                print(f"❌ Error: {announcements_response.text}")
            
            # Test course enrollment endpoint
            print("\n3️⃣ Testing course enrollment endpoint...")
            enroll_response = requests.post(ENROLL_URL, headers=headers, json={})
            print(f"Status: {enroll_response.status_code}")
            if enroll_response.status_code in [200, 201]:
                print("✅ Enrollment successful!")
            elif enroll_response.status_code == 400:
                print("⚠️ Enrollment failed (expected - might already be enrolled or course full)")
                print(f"Response: {enroll_response.json()}")
            else:
                print(f"❌ Error: {enroll_response.text}")
                
        else:
            print(f"❌ Login failed: {login_response.status_code}")
            print(f"Response: {login_response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")

def test_without_authentication():
    """Test endpoints without authentication to show the 401 errors"""
    print("\n🚫 Testing Without Authentication (Expected to Fail)")
    print("=" * 50)
    
    # Test announcements without auth
    print("1️⃣ Testing announcements without auth...")
    response = requests.get(ANNOUNCEMENTS_URL)
    print(f"Status: {response.status_code} (Expected: 401)")
    
    # Test enrollment without auth
    print("2️⃣ Testing enrollment without auth...")
    response = requests.post(ENROLL_URL, json={})
    print(f"Status: {response.status_code} (Expected: 401)")

if __name__ == "__main__":
    print("🧪 Ageri Research Platform - Authentication Test")
    print("=" * 60)
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/api/", timeout=5)
    except requests.exceptions.RequestException:
        print("❌ Server is not running! Please start the Django server first:")
        print("   source venv/bin/activate && python manage.py runserver")
        exit(1)
    
    test_without_authentication()
    test_authentication()
    
    print("\n" + "=" * 60)
    print("✅ Test completed!")
    print("\n📝 Key Points:")
    print("- All protected endpoints require JWT authentication")
    print("- Include 'Authorization: Bearer <token>' header in requests")
    print("- Users must be approved to access most content")
    print("- Login at /api/auth/login/ to get tokens")

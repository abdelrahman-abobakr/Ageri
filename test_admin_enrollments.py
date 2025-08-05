#!/usr/bin/env python3
"""
Test script to check admin enrollment data with authentication
"""

import requests
import json

# Configuration
BASE_URL = "http://127.0.0.1:8000"
LOGIN_URL = f"{BASE_URL}/api/auth/login/"
ENROLLMENTS_URL = f"{BASE_URL}/api/training/enrollments/"

# Admin credentials (use your superuser)
ADMIN_CREDENTIALS = {
    "email": "admin@test.com",
    "password": "admin123"  # Update with your actual password
}

def get_admin_token():
    """Get admin access token"""
    try:
        response = requests.post(
            LOGIN_URL,
            json=ADMIN_CREDENTIALS,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            return data.get('access')
        else:
            print(f"❌ Login failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Login error: {e}")
        return None

def test_admin_enrollments():
    """Test admin enrollments endpoint with authentication"""
    print("🔐 Testing Admin Enrollments with Authentication")
    print("=" * 60)
    
    # Step 1: Get admin token
    print("1️⃣ Getting admin access token...")
    token = get_admin_token()
    
    if not token:
        print("❌ Failed to get admin token. Please check credentials.")
        return
    
    print(f"✅ Got admin token: {token[:20]}...")
    
    # Step 2: Test enrollments endpoint
    print("\n2️⃣ Testing enrollments endpoint...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(ENROLLMENTS_URL, headers=headers)
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Enrollments data retrieved successfully!")
            
            print(f"\n📊 Total enrollments: {data.get('count', 0)}")
            
            if 'results' in data and len(data['results']) > 0:
                print(f"📋 Found {len(data['results'])} enrollments on this page")
                
                # Show first enrollment structure
                sample_enrollment = data['results'][0]
                print("\n🔍 Sample enrollment data structure:")
                print(json.dumps(sample_enrollment, indent=2, default=str))
                
                # Check for guest enrollment fields
                guest_fields = [
                    'first_name', 'last_name', 'email', 'phone', 
                    'organization', 'job_title', 'enrollment_token'
                ]
                helper_fields = ['enrollee_name', 'enrollee_email', 'is_guest_enrollment']
                
                print("\n📝 Guest enrollment fields check:")
                for field in guest_fields:
                    value = sample_enrollment.get(field)
                    status = "✅" if value is not None else "❌"
                    print(f"   {status} {field}: {value}")
                
                print("\n🔧 Helper fields check:")
                for field in helper_fields:
                    value = sample_enrollment.get(field)
                    status = "✅" if value is not None else "❌"
                    print(f"   {status} {field}: {value}")
                
                # Check enrollment types
                guest_count = sum(1 for e in data['results'] if e.get('is_guest_enrollment'))
                registered_count = len(data['results']) - guest_count
                
                print(f"\n📈 Enrollment breakdown:")
                print(f"   👤 Guest enrollments: {guest_count}")
                print(f"   🔐 Registered users: {registered_count}")
                
            else:
                print("📭 No enrollment data found")
                
        elif response.status_code == 403:
            print("❌ Access denied - User doesn't have admin permissions")
        elif response.status_code == 401:
            print("❌ Authentication failed - Token might be invalid")
        else:
            print(f"❌ Unexpected status: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Request error: {e}")

def test_enrollment_filtering():
    """Test enrollment filtering capabilities"""
    print("\n🔍 Testing Enrollment Filtering")
    print("=" * 60)
    
    token = get_admin_token()
    if not token:
        return
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Test different filters
    filters = [
        {"status": "approved", "description": "Approved enrollments"},
        {"payment_status": "pending", "description": "Pending payments"},
        {"search": "test", "description": "Search for 'test'"},
        {"course": "6", "description": "Course 6 enrollments"},
    ]
    
    for filter_params in filters:
        description = filter_params.pop("description")
        print(f"\n🔎 Testing: {description}")
        
        try:
            response = requests.get(
                ENROLLMENTS_URL,
                headers=headers,
                params=filter_params
            )
            
            if response.status_code == 200:
                data = response.json()
                count = data.get('count', 0)
                print(f"   ✅ Found {count} enrollments")
            else:
                print(f"   ❌ Error: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")

def test_single_enrollment():
    """Test getting a single enrollment"""
    print("\n📋 Testing Single Enrollment Retrieval")
    print("=" * 60)
    
    token = get_admin_token()
    if not token:
        return
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # First get list to find an enrollment ID
    try:
        response = requests.get(ENROLLMENTS_URL, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            
            if 'results' in data and len(data['results']) > 0:
                enrollment_id = data['results'][0]['id']
                print(f"🎯 Testing enrollment ID: {enrollment_id}")
                
                # Get single enrollment
                single_url = f"{ENROLLMENTS_URL}{enrollment_id}/"
                single_response = requests.get(single_url, headers=headers)
                
                if single_response.status_code == 200:
                    enrollment_data = single_response.json()
                    print("✅ Single enrollment retrieved successfully!")
                    
                    print(f"\n📊 Enrollment details:")
                    print(f"   ID: {enrollment_data.get('id')}")
                    print(f"   Enrollee: {enrollment_data.get('enrollee_name')}")
                    print(f"   Email: {enrollment_data.get('enrollee_email')}")
                    print(f"   Course: {enrollment_data.get('course_title')}")
                    print(f"   Status: {enrollment_data.get('status')}")
                    print(f"   Type: {'Guest' if enrollment_data.get('is_guest_enrollment') else 'Registered'}")
                    
                else:
                    print(f"❌ Failed to get single enrollment: {single_response.status_code}")
            else:
                print("📭 No enrollments found to test with")
        else:
            print(f"❌ Failed to get enrollments list: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🧪 Admin Enrollment Data Test")
    print("=" * 70)
    
    # Test basic admin enrollment access
    test_admin_enrollments()
    
    # Test filtering capabilities
    test_enrollment_filtering()
    
    # Test single enrollment retrieval
    test_single_enrollment()
    
    print("\n" + "=" * 70)
    print("📝 Summary:")
    print("• Admin endpoints require authentication")
    print("• Guest enrollment fields should be included in responses")
    print("• Helper fields provide unified access to enrollee data")
    print("• Filtering and search should work for both guest and registered users")
    print("• Use enrollee_name and enrollee_email for display in frontend")

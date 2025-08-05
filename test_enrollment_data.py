#!/usr/bin/env python3
"""
Test script to check enrollment data structure
"""

import requests
import json

# Configuration
BASE_URL = "http://127.0.0.1:8000"
ENROLLMENTS_URL = f"{BASE_URL}/api/training/enrollments/"

def test_enrollment_data():
    """Test what data is returned from enrollments endpoint"""
    print("🔍 Testing Enrollment Data Structure")
    print("=" * 50)
    
    try:
        # First, let's create a test enrollment to ensure we have data
        print("1️⃣ Creating a test enrollment...")
        enroll_response = requests.post(
            f"{BASE_URL}/api/training/courses/6/enroll/",
            json={
                "first_name": "Test",
                "last_name": "Admin",
                "email": "test.admin@example.com",
                "phone": "+1234567890",
                "organization": "Test Org",
                "job_title": "Tester"
            },
            headers={"Content-Type": "application/json"}
        )
        
        if enroll_response.status_code == 201:
            print("✅ Test enrollment created successfully")
        else:
            print(f"⚠️ Enrollment creation status: {enroll_response.status_code}")
        
        # Now test the enrollments endpoint (this requires admin auth)
        print("\n2️⃣ Testing enrollments endpoint (without auth - should fail)...")
        enrollments_response = requests.get(ENROLLMENTS_URL)
        
        print(f"Status: {enrollments_response.status_code}")
        
        if enrollments_response.status_code == 401:
            print("✅ Expected 401 - Authentication required for admin endpoint")
            print("📝 Response:", enrollments_response.json())
        elif enrollments_response.status_code == 200:
            data = enrollments_response.json()
            print("✅ Enrollments data retrieved!")
            
            if 'results' in data and len(data['results']) > 0:
                print("\n📊 Sample enrollment data structure:")
                sample_enrollment = data['results'][0]
                
                # Print all available fields
                print(json.dumps(sample_enrollment, indent=2, default=str))
                
                # Check for guest enrollment fields
                guest_fields = ['first_name', 'last_name', 'email', 'phone', 'organization', 'job_title']
                helper_fields = ['enrollee_name', 'enrollee_email', 'is_guest_enrollment']
                
                print("\n🔍 Guest enrollment fields:")
                for field in guest_fields:
                    value = sample_enrollment.get(field, 'NOT FOUND')
                    print(f"   {field}: {value}")
                
                print("\n🔍 Helper fields:")
                for field in helper_fields:
                    value = sample_enrollment.get(field, 'NOT FOUND')
                    print(f"   {field}: {value}")
                    
            else:
                print("📭 No enrollment data found")
        else:
            print(f"❌ Unexpected status: {enrollments_response.status_code}")
            print(f"Response: {enrollments_response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")

def test_course_enrollments():
    """Test course-specific enrollments endpoint"""
    print("\n🎓 Testing Course Enrollments Endpoint")
    print("=" * 50)
    
    try:
        course_enrollments_url = f"{BASE_URL}/api/training/courses/6/enrollments/"
        response = requests.get(course_enrollments_url)
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 401:
            print("✅ Expected 401 - Authentication required for admin endpoint")
        elif response.status_code == 200:
            data = response.json()
            print("✅ Course enrollments data retrieved!")
            print(f"📊 Found {len(data)} enrollments for course 6")
            
            if len(data) > 0:
                print("\n📋 Sample course enrollment:")
                print(json.dumps(data[0], indent=2, default=str))
        else:
            print(f"❌ Unexpected status: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")

if __name__ == "__main__":
    print("🧪 Enrollment Data Structure Test")
    print("=" * 60)
    
    test_enrollment_data()
    test_course_enrollments()
    
    print("\n" + "=" * 60)
    print("📝 Notes:")
    print("• Admin endpoints require authentication")
    print("• Guest enrollment fields should be included in responses")
    print("• Helper fields provide unified access to enrollee data")
    print("• Use enrollee_name and enrollee_email for display")
    
    print("\n🔧 For admin testing, you need to:")
    print("1. Login as admin to get access token")
    print("2. Include 'Authorization: Bearer <token>' header")
    print("3. Use the token in all admin API calls")

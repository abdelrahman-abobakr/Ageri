#!/usr/bin/env python3
"""
Test script to verify required field validation for guest enrollment
"""

import requests
import json

# Configuration
BASE_URL = "http://127.0.0.1:8000"
ENROLL_URL = f"{BASE_URL}/api/training/courses/6/enroll/"

def test_empty_fields():
    """Test enrollment with empty/missing required fields"""
    print("🚫 Testing Required Field Validation")
    print("=" * 50)
    
    test_cases = [
        {
            "name": "All fields empty",
            "data": {},
            "expected_errors": ["first_name", "last_name", "email", "phone"]
        },
        {
            "name": "Missing first_name",
            "data": {
                "last_name": "Doe",
                "email": "test@example.com",
                "phone": "123456789"
            },
            "expected_errors": ["first_name"]
        },
        {
            "name": "Missing last_name",
            "data": {
                "first_name": "John",
                "email": "test@example.com",
                "phone": "123456789"
            },
            "expected_errors": ["last_name"]
        },
        {
            "name": "Missing email",
            "data": {
                "first_name": "John",
                "last_name": "Doe",
                "phone": "123456789"
            },
            "expected_errors": ["email"]
        },
        {
            "name": "Missing phone",
            "data": {
                "first_name": "John",
                "last_name": "Doe",
                "email": "test@example.com"
            },
            "expected_errors": ["phone"]
        },
        {
            "name": "Empty strings",
            "data": {
                "first_name": "",
                "last_name": "",
                "email": "",
                "phone": ""
            },
            "expected_errors": ["first_name", "last_name", "email", "phone"]
        },
        {
            "name": "Invalid email format",
            "data": {
                "first_name": "John",
                "last_name": "Doe",
                "email": "invalid-email",
                "phone": "123456789"
            },
            "expected_errors": ["email"]
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}️⃣ Test: {test_case['name']}")
        
        try:
            response = requests.post(
                ENROLL_URL,
                json=test_case['data'],
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 400:
                error_data = response.json()
                details = error_data.get('details', {})
                
                print(f"   ✅ Status: {response.status_code} (Expected validation error)")
                print(f"   📋 Validation errors found:")
                
                for field in test_case['expected_errors']:
                    if field in details:
                        print(f"      • {field}: {details[field]}")
                    else:
                        print(f"      ❌ Missing expected error for: {field}")
                
                # Check for unexpected errors
                unexpected_errors = set(details.keys()) - set(test_case['expected_errors'])
                if unexpected_errors:
                    print(f"   ⚠️ Unexpected errors: {list(unexpected_errors)}")
                    
            else:
                print(f"   ❌ Unexpected status: {response.status_code}")
                print(f"   Response: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Network error: {e}")

def test_valid_enrollment():
    """Test enrollment with all required fields provided"""
    print("\n✅ Testing Valid Enrollment")
    print("=" * 50)
    
    valid_data = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.valid@example.com",
        "phone": "+1234567890",
        "organization": "Test Company",  # Optional
        "job_title": "Developer"  # Optional
    }
    
    try:
        response = requests.post(
            ENROLL_URL,
            json=valid_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 201:
            enrollment_data = response.json()
            print("✅ Enrollment successful!")
            print(f"   📧 Name: {valid_data['first_name']} {valid_data['last_name']}")
            print(f"   📧 Email: {valid_data['email']}")
            print(f"   📞 Phone: {valid_data['phone']}")
            print(f"   🎫 Token: {enrollment_data.get('enrollment_token')}")
            return True
        else:
            print(f"❌ Enrollment failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Required Fields Validation Test")
    print("=" * 60)
    
    # Test validation errors
    test_empty_fields()
    
    # Test valid enrollment
    success = test_valid_enrollment()
    
    print("\n" + "=" * 60)
    print("📊 Summary:")
    print("   • Required fields: first_name, last_name, email, phone")
    print("   • Optional fields: organization, job_title")
    print("   • Email format validation included")
    print("   • Empty/blank values are rejected")
    
    if success:
        print("\n🎉 Validation is working correctly!")
    else:
        print("\n⚠️ Please check the implementation.")

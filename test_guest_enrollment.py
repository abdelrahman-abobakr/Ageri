#!/usr/bin/env python3
"""
Test script to verify guest enrollment functionality
"""

import requests
import json

# Configuration
BASE_URL = "http://127.0.0.1:8000"
COURSES_URL = f"{BASE_URL}/api/training/courses/"

def test_guest_enrollment():
    """Test guest enrollment without authentication"""
    print("🎓 Testing Guest Course Enrollment")
    print("=" * 50)
    
    # Step 1: Get available courses
    print("1️⃣ Fetching available courses...")
    try:
        courses_response = requests.get(COURSES_URL)
        if courses_response.status_code == 200:
            courses_data = courses_response.json()
            courses = courses_data.get('results', [])
            print(f"✅ Found {len(courses)} courses")
            
            if courses:
                # Use the first course for testing
                test_course = courses[0]
                course_id = test_course['id']
                course_title = test_course.get('title', 'Unknown Course')
                print(f"📚 Testing with course: {course_title} (ID: {course_id})")
                
                # Step 2: Test guest enrollment
                print("\n2️⃣ Testing guest enrollment...")
                enroll_url = f"{COURSES_URL}{course_id}/enroll/"
                
                # Guest enrollment data
                guest_data = {
                    "first_name": "John",
                    "last_name": "Doe",
                    "email": "john.doe@example.com",
                    "phone": "+1234567890",
                    "organization": "Test Organization",
                    "job_title": "Software Developer"
                }
                
                enroll_response = requests.post(
                    enroll_url,
                    json=guest_data,
                    headers={"Content-Type": "application/json"}
                )
                
                print(f"Status: {enroll_response.status_code}")
                
                if enroll_response.status_code == 201:
                    enrollment_data = enroll_response.json()
                    print("✅ Guest enrollment successful!")
                    print(f"📧 Enrollee: {guest_data['first_name']} {guest_data['last_name']}")
                    print(f"🎫 Enrollment Token: {enrollment_data.get('enrollment_token')}")
                    print(f"💰 Payment Amount: ${enrollment_data.get('payment_amount', 0)}")
                    
                    # Display next steps
                    next_steps = enrollment_data.get('next_steps', [])
                    if next_steps:
                        print("\n📋 Next Steps:")
                        for i, step in enumerate(next_steps, 1):
                            print(f"   {i}. {step}")
                    
                    return True
                    
                elif enroll_response.status_code == 400:
                    error_data = enroll_response.json()
                    print("❌ Enrollment failed with validation errors:")
                    print(f"   Error: {error_data.get('error', 'Unknown error')}")
                    details = error_data.get('details', {})
                    if details:
                        print("   Details:")
                        for field, errors in details.items():
                            print(f"     {field}: {errors}")
                    return False
                    
                else:
                    print(f"❌ Enrollment failed: {enroll_response.status_code}")
                    print(f"Response: {enroll_response.text}")
                    return False
            else:
                print("❌ No courses available for testing")
                return False
        else:
            print(f"❌ Failed to fetch courses: {courses_response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
        return False

def test_duplicate_enrollment():
    """Test that duplicate enrollments are prevented"""
    print("\n🔄 Testing Duplicate Enrollment Prevention")
    print("=" * 50)
    
    try:
        # Get first course
        courses_response = requests.get(COURSES_URL)
        if courses_response.status_code == 200:
            courses = courses_response.json().get('results', [])
            if courses:
                course_id = courses[0]['id']
                enroll_url = f"{COURSES_URL}{course_id}/enroll/"
                
                # Try to enroll the same email again
                guest_data = {
                    "first_name": "Jane",
                    "last_name": "Smith",
                    "email": "john.doe@example.com",  # Same email as before
                    "phone": "+0987654321",
                    "organization": "Another Organization",
                    "job_title": "Designer"
                }
                
                enroll_response = requests.post(
                    enroll_url,
                    json=guest_data,
                    headers={"Content-Type": "application/json"}
                )
                
                if enroll_response.status_code == 400:
                    error_data = enroll_response.json()
                    print("✅ Duplicate enrollment correctly prevented!")
                    print(f"   Error: {error_data.get('error', 'Unknown error')}")
                    return True
                else:
                    print("❌ Duplicate enrollment was not prevented")
                    return False
    except Exception as e:
        print(f"❌ Error testing duplicate enrollment: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Guest Enrollment Test Suite")
    print("=" * 60)
    
    # Test 1: Basic guest enrollment
    success1 = test_guest_enrollment()
    
    # Test 2: Duplicate enrollment prevention
    success2 = test_duplicate_enrollment()
    
    print("\n" + "=" * 60)
    print("📊 Test Results:")
    print(f"   ✅ Guest Enrollment: {'PASS' if success1 else 'FAIL'}")
    print(f"   ✅ Duplicate Prevention: {'PASS' if success2 else 'FAIL'}")
    
    if success1 and success2:
        print("\n🎉 All tests passed! Guest enrollment is working correctly.")
    else:
        print("\n⚠️ Some tests failed. Please check the implementation.")
    
    print("\n📝 Key Features Implemented:")
    print("   • No authentication required for course enrollment")
    print("   • Guest user information stored with enrollment")
    print("   • Unique enrollment token generated for each guest")
    print("   • Duplicate email prevention per course")
    print("   • Auto-approval of guest enrollments")

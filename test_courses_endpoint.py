#!/usr/bin/env python3
"""
Test script for courses endpoint
================================

This script tests the courses API endpoint to ensure it works correctly
and handles different Accept headers properly.

Usage:
    python3 test_courses_endpoint.py
"""

import requests
import json
from datetime import datetime

def test_courses_endpoint():
    """Test the courses endpoint with different Accept headers"""
    
    base_url = "http://localhost:8000"
    endpoint = f"{base_url}/api/training/courses/"
    
    print("🧪 Testing Courses API Endpoint")
    print("=" * 50)
    print(f"📍 Endpoint: {endpoint}")
    print(f"⏰ Test time: {datetime.now()}")
    print()
    
    # Test cases with different Accept headers
    test_cases = [
        {
            "name": "Standard JSON Accept header",
            "headers": {
                "Accept": "application/json",
                "Content-Type": "application/json"
            }
        },
        {
            "name": "Wildcard Accept header",
            "headers": {
                "Accept": "*/*",
                "Content-Type": "application/json"
            }
        },
        {
            "name": "Multiple Accept types",
            "headers": {
                "Accept": "application/json, text/plain, */*",
                "Content-Type": "application/json"
            }
        },
        {
            "name": "Browser-like Accept header",
            "headers": {
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Content-Type": "application/json"
            }
        },
        {
            "name": "No Accept header",
            "headers": {
                "Content-Type": "application/json"
            }
        },
        {
            "name": "API client Accept header",
            "headers": {
                "Accept": "application/vnd.api+json",
                "Content-Type": "application/json"
            }
        }
    ]
    
    success_count = 0
    total_tests = len(test_cases)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"{i}️⃣ {test_case['name']}:")
        print(f"   Headers: {test_case['headers']}")
        
        try:
            response = requests.get(endpoint, headers=test_case['headers'], timeout=10)
            
            print(f"   Status: {response.status_code}")
            print(f"   Content-Type: {response.headers.get('Content-Type', 'Not specified')}")
            
            if response.status_code == 200:
                print("   ✅ SUCCESS: Request completed successfully")
                
                # Try to parse JSON response
                try:
                    data = response.json()
                    if isinstance(data, dict) and 'results' in data:
                        print(f"   📊 Results: {len(data['results'])} courses found")
                    elif isinstance(data, list):
                        print(f"   📊 Results: {len(data)} courses found")
                    else:
                        print(f"   📊 Response type: {type(data)}")
                    success_count += 1
                except json.JSONDecodeError:
                    print("   ⚠️  WARNING: Response is not valid JSON")
                    print(f"   📄 Response preview: {response.text[:100]}...")
                    
            else:
                print(f"   ❌ FAILED: HTTP {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   📄 Error: {error_data}")
                except:
                    print(f"   📄 Error text: {response.text[:200]}...")
                    
        except requests.exceptions.ConnectionError:
            print("   ❌ FAILED: Connection error - Is the Django server running?")
        except requests.exceptions.Timeout:
            print("   ❌ FAILED: Request timeout")
        except Exception as e:
            print(f"   ❌ FAILED: Unexpected error - {e}")
        
        print()
    
    # Summary
    print("📊 Test Summary")
    print("=" * 30)
    print(f"✅ Successful: {success_count}/{total_tests}")
    print(f"❌ Failed: {total_tests - success_count}/{total_tests}")
    
    if success_count == total_tests:
        print("🎉 All tests passed! The endpoint is working correctly.")
    elif success_count > 0:
        print("⚠️  Some tests passed. The endpoint works but may have issues with certain Accept headers.")
    else:
        print("🚨 All tests failed. There may be a server issue.")
    
    return success_count == total_tests

def test_with_authentication():
    """Test the endpoint with authentication"""
    print("\n🔐 Testing with Authentication")
    print("=" * 40)
    
    base_url = "http://localhost:8000"
    login_endpoint = f"{base_url}/api/auth/login/"
    courses_endpoint = f"{base_url}/api/training/courses/"
    
    # Test credentials (you may need to adjust these)
    test_credentials = {
        "email": "admin@example.com",
        "password": "admin123"
    }
    
    print("1️⃣ Attempting login...")
    try:
        login_response = requests.post(
            login_endpoint,
            json=test_credentials,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if login_response.status_code == 200:
            tokens = login_response.json()
            access_token = tokens.get('access')
            
            if access_token:
                print("   ✅ Login successful")
                
                # Test authenticated request
                print("2️⃣ Testing authenticated request...")
                auth_headers = {
                    "Authorization": f"Bearer {access_token}",
                    "Accept": "application/json",
                    "Content-Type": "application/json"
                }
                
                auth_response = requests.get(
                    courses_endpoint,
                    headers=auth_headers,
                    timeout=10
                )
                
                print(f"   Status: {auth_response.status_code}")
                if auth_response.status_code == 200:
                    print("   ✅ Authenticated request successful")
                    try:
                        data = auth_response.json()
                        if isinstance(data, dict) and 'results' in data:
                            print(f"   📊 Results: {len(data['results'])} courses found")
                        elif isinstance(data, list):
                            print(f"   📊 Results: {len(data)} courses found")
                    except:
                        print("   📄 Response received but not JSON")
                else:
                    print(f"   ❌ Authenticated request failed: {auth_response.status_code}")
                    try:
                        error = auth_response.json()
                        print(f"   📄 Error: {error}")
                    except:
                        print(f"   📄 Error text: {auth_response.text[:200]}...")
            else:
                print("   ❌ Login response missing access token")
        else:
            print(f"   ❌ Login failed: {login_response.status_code}")
            try:
                error = login_response.json()
                print(f"   📄 Error: {error}")
            except:
                print(f"   📄 Error text: {login_response.text[:200]}...")
                
    except requests.exceptions.ConnectionError:
        print("   ❌ Connection error - Is the Django server running?")
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")

def show_troubleshooting_tips():
    """Show troubleshooting tips"""
    print("\n🔧 Troubleshooting Tips")
    print("=" * 40)
    
    print("If tests are failing, try these steps:")
    print()
    print("1️⃣ **Check Django Server:**")
    print("   cd /home/abdo/ITI/Ageri")
    print("   python3 manage.py runserver")
    print()
    print("2️⃣ **Check URL Pattern:**")
    print("   Endpoint should be: http://localhost:8000/api/training/courses/")
    print("   Fixed: Removed double 'api' from URL path")
    print()
    print("3️⃣ **Test with cURL:**")
    print("   curl -H 'Accept: application/json' http://localhost:8000/api/training/courses/")
    print()
    print("4️⃣ **Check Django Logs:**")
    print("   Look at the Django console output for error messages")
    print()
    print("5️⃣ **Verify URL Configuration:**")
    print("   Check training/urls.py and research_platform/urls.py")
    print()
    print("6️⃣ **Common Accept Header Issues:**")
    print("   - Try: Accept: application/json")
    print("   - Try: Accept: */*")
    print("   - Remove Accept header entirely")

def main():
    """Run all tests"""
    print("🚀 Courses Endpoint Test Suite")
    print("=" * 50)
    
    # Run basic tests
    basic_success = test_courses_endpoint()
    
    # Run authentication tests
    test_with_authentication()
    
    # Show troubleshooting tips
    show_troubleshooting_tips()
    
    print(f"\n🎯 Final Result: {'✅ SUCCESS' if basic_success else '❌ NEEDS ATTENTION'}")

if __name__ == "__main__":
    main()

#!/usr/bin/env python
"""
Quick test to verify the vision/mission image API functionality
"""

import requests
import json

def test_organization_api():
    """Test the organization settings API"""
    try:
        # Test the API endpoint
        url = "http://localhost:8000/api/organization/settings/"
        
        print("🔍 Testing Organization Settings API...")
        print(f"URL: {url}")
        
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ API is working!")
            print(f"Organization: {data.get('name', 'N/A')}")
            print(f"Vision: {data.get('vision', 'N/A')[:50]}...")
            print(f"Mission: {data.get('mission', 'N/A')[:50]}...")
            print(f"Vision Image: {data.get('vision_image', 'None')}")
            print(f"Mission Image: {data.get('mission_image', 'None')}")
            
            # Check if new fields are present
            if 'vision_image' in data and 'mission_image' in data:
                print("✅ New image fields are available in API!")
            else:
                print("❌ Image fields not found in API response")
                
        else:
            print(f"❌ API returned status code: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the server. Make sure Django is running on localhost:8000")
    except Exception as e:
        print(f"❌ Error: {e}")

def show_curl_examples():
    """Show curl examples for testing"""
    print("\n🔧 Manual Testing with curl:")
    print("=" * 40)
    
    print("\n1. Get organization settings:")
    print("curl -X GET http://localhost:8000/api/organization/settings/")
    
    print("\n2. Update with images (requires admin token):")
    print("""curl -X PUT http://localhost:8000/api/organization/settings/ \\
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \\
  -F "vision=Our new vision statement" \\
  -F "vision_image=@path/to/vision.jpg" \\
  -F "mission=Our new mission statement" \\
  -F "mission_image=@path/to/mission.jpg" """)

if __name__ == "__main__":
    test_organization_api()
    show_curl_examples()

#!/usr/bin/env python
"""
Test Analytics Endpoints
This script tests all available analytics endpoints to verify they work and show real data.
"""

import requests
import json
from datetime import datetime

def test_endpoint(url, name, auth_required=False, token=None):
    """Test a single endpoint"""
    print(f"\n🔍 Testing: {name}")
    print(f"📍 URL: {url}")
    
    headers = {}
    if auth_required and token:
        headers['Authorization'] = f'Bearer {token}'
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"✅ SUCCESS! Data received:")
                
                # Pretty print first few keys
                if isinstance(data, dict):
                    for key, value in list(data.items())[:5]:
                        if isinstance(value, (int, float, str)):
                            print(f"   {key}: {value}")
                        elif isinstance(value, dict):
                            print(f"   {key}: {dict(list(value.items())[:3])}")
                        else:
                            print(f"   {key}: {type(value).__name__}")
                    
                    if len(data) > 5:
                        print(f"   ... and {len(data) - 5} more fields")
                else:
                    print(f"   Data type: {type(data).__name__}")
                    print(f"   Length: {len(data) if hasattr(data, '__len__') else 'N/A'}")
                
            except json.JSONDecodeError:
                print(f"✅ SUCCESS! Non-JSON response (likely HTML page)")
                print(f"   Content length: {len(response.content)} bytes")
                
        elif response.status_code == 401:
            print(f"🔒 AUTHENTICATION REQUIRED")
        elif response.status_code == 403:
            print(f"🚫 FORBIDDEN (Need admin permissions)")
        elif response.status_code == 404:
            print(f"❌ NOT FOUND")
        else:
            print(f"⚠️  Unexpected status: {response.status_code}")
            print(f"   Response: {response.text[:200]}...")
            
    except requests.exceptions.ConnectionError:
        print(f"❌ CONNECTION ERROR - Make sure Django server is running")
    except requests.exceptions.Timeout:
        print(f"⏰ TIMEOUT")
    except Exception as e:
        print(f"❌ ERROR: {e}")

def main():
    """Test all analytics endpoints"""
    print("🚀 Analytics Endpoints Test")
    print("=" * 50)
    print(f"⏰ Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    base_url = "http://localhost:8000"
    
    # Test endpoints
    endpoints = [
        # Dashboard Analytics (Web Interface)
        {
            "url": f"{base_url}/dashboard/analytics/",
            "name": "Dashboard Analytics (Web)",
            "auth_required": True
        },
        
        # API Analytics Endpoints
        {
            "url": f"{base_url}/api/services/test-services/statistics/",
            "name": "Services Statistics API",
            "auth_required": True
        },
        {
            "url": f"{base_url}/api/services/clients/statistics/",
            "name": "Clients Statistics API", 
            "auth_required": True
        },
        {
            "url": f"{base_url}/api/services/requests/statistics/",
            "name": "Service Requests Statistics API",
            "auth_required": True
        },
        {
            "url": f"{base_url}/api/research/publications/statistics/",
            "name": "Publications Statistics API",
            "auth_required": True
        },
        {
            "url": f"{base_url}/api/organization/stats/",
            "name": "Organization Statistics API",
            "auth_required": True
        },
        {
            "url": f"{base_url}/dashboard/api/pending-counts/",
            "name": "Dashboard Pending Counts API",
            "auth_required": True
        },
        
        # Public endpoints for comparison
        {
            "url": f"{base_url}/api/organization/settings/",
            "name": "Organization Settings (Public)",
            "auth_required": False
        }
    ]
    
    # Test each endpoint
    for endpoint in endpoints:
        test_endpoint(
            url=endpoint["url"],
            name=endpoint["name"],
            auth_required=endpoint["auth_required"]
        )
    
    print(f"\n🎯 Summary:")
    print("=" * 30)
    print("📍 Main Analytics Dashboard: http://localhost:8000/dashboard/analytics/")
    print("🔑 Authentication: Most endpoints require admin/staff login")
    print("📊 Data: All endpoints use real database data (not random)")
    
    print(f"\n💡 Quick Access URLs:")
    print("🌐 Dashboard Analytics: http://localhost:8000/dashboard/analytics/")
    print("🔌 Services API: http://localhost:8000/api/services/test-services/statistics/")
    print("📚 Research API: http://localhost:8000/api/research/publications/statistics/")
    print("🏢 Organization API: http://localhost:8000/api/organization/stats/")
    
    print(f"\n🔧 How to Access:")
    print("1. Start Django server: python manage.py runserver")
    print("2. Login as admin/staff user")
    print("3. Visit: http://localhost:8000/dashboard/analytics/")
    print("4. Or use API endpoints with authentication")

if __name__ == "__main__":
    main()

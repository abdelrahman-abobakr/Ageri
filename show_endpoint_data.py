#!/usr/bin/env python
"""
Show Organization Settings Endpoint Data Structure
This script demonstrates the exact data structure returned by the API endpoint
"""

import os
import sys
import django
import json
from django.test import Client
from django.contrib.auth import get_user_model

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'research_platform.settings')
django.setup()

from organization.models import OrganizationSettings

def show_endpoint_data():
    """Show the exact endpoint data structure"""
    print("🌐 Organization Settings API Endpoint Data")
    print("=" * 60)
    
    # Create a test client
    client = Client()
    
    # Get the endpoint URL
    endpoint_url = '/api/organization/settings/'
    print(f"📍 Endpoint: GET {endpoint_url}")
    print(f"🔓 Access: Public (no authentication required)")
    print(f"📄 Content-Type: application/json")
    
    # Make the API call
    print(f"\n🔄 Making API call...")
    response = client.get(endpoint_url)
    
    print(f"📊 Response Status: {response.status_code}")
    print(f"📋 Response Headers:")
    for header, value in response.items():
        print(f"   {header}: {value}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n✅ SUCCESS! API Response Data:")
        print("=" * 40)
        print(json.dumps(data, indent=2, default=str))
        
        print(f"\n🔍 Key Fields Analysis:")
        print("=" * 30)
        
        # Analyze the new image fields
        vision_image = data.get('vision_image')
        mission_image = data.get('mission_image')
        
        print(f"📝 Vision Text: {data.get('vision', 'Not set')[:50]}...")
        print(f"🖼️  Vision Image: {vision_image if vision_image else 'None'}")
        print(f"📝 Mission Text: {data.get('mission', 'Not set')[:50]}...")
        print(f"🖼️  Mission Image: {mission_image if mission_image else 'None'}")
        
        print(f"\n📋 All Available Fields:")
        print("-" * 25)
        for key, value in data.items():
            value_preview = str(value)[:50] + "..." if len(str(value)) > 50 else str(value)
            print(f"   {key}: {value_preview}")
            
    else:
        print(f"❌ ERROR: {response.status_code}")
        print(f"Response: {response.content.decode()}")

def show_update_endpoint_structure():
    """Show the structure for updating via API"""
    print(f"\n🔄 UPDATE Endpoint Structure")
    print("=" * 40)
    
    endpoint_url = '/api/organization/settings/'
    print(f"📍 Endpoint: PUT {endpoint_url}")
    print(f"🔒 Access: Admin authentication required")
    print(f"📄 Content-Type: multipart/form-data")
    
    print(f"\n📤 Request Data Structure (FormData):")
    print("-" * 35)
    
    form_data_example = {
        'name': 'Organization Name',
        'vision': 'Vision statement text',
        'vision_image': '[File object - JPG/JPEG/PNG]',
        'mission': 'Mission statement text', 
        'mission_image': '[File object - JPG/JPEG/PNG]',
        'about': 'About text',
        'email': 'contact@org.com',
        'phone': '+1-555-0123',
        'address': 'Organization address',
        'website': 'https://website.com',
        'facebook': 'https://facebook.com/page',
        'twitter': 'https://twitter.com/handle',
        'linkedin': 'https://linkedin.com/company/name',
        'instagram': 'https://instagram.com/handle',
        'logo': '[File object - JPG/JPEG/PNG/SVG]',
        'banner': '[File object - JPG/JPEG/PNG]',
        'enable_registration': 'true/false',
        'require_approval': 'true/false',
        'maintenance_mode': 'true/false',
        'maintenance_message': 'Maintenance message text'
    }
    
    for field, description in form_data_example.items():
        print(f"   {field}: {description}")
    
    print(f"\n🔑 Authentication Header:")
    print(f"   Authorization: Bearer <admin_jwt_token>")
    
    print(f"\n📋 JavaScript Example:")
    print("-" * 20)
    js_example = '''
const formData = new FormData();
formData.append('vision', 'Our vision statement');
formData.append('vision_image', visionImageFile);
formData.append('mission', 'Our mission statement');
formData.append('mission_image', missionImageFile);

const response = await fetch('/api/organization/settings/', {
    method: 'PUT',
    headers: {
        'Authorization': 'Bearer ' + adminToken
    },
    body: formData
});

const updatedSettings = await response.json();
'''
    print(js_example)

def show_field_validation():
    """Show field validation rules"""
    print(f"\n✅ Field Validation Rules")
    print("=" * 30)
    
    validations = {
        'vision_image': {
            'type': 'ImageField',
            'required': False,
            'formats': 'JPG, JPEG, PNG',
            'max_size': 'Django default (2.5MB typically)',
            'upload_path': 'media/organization/'
        },
        'mission_image': {
            'type': 'ImageField', 
            'required': False,
            'formats': 'JPG, JPEG, PNG',
            'max_size': 'Django default (2.5MB typically)',
            'upload_path': 'media/organization/'
        },
        'vision': {
            'type': 'TextField',
            'required': False,
            'max_length': 'Unlimited'
        },
        'mission': {
            'type': 'TextField',
            'required': False,
            'max_length': 'Unlimited'
        }
    }
    
    for field, rules in validations.items():
        print(f"\n📋 {field}:")
        for rule, value in rules.items():
            print(f"   {rule}: {value}")

if __name__ == "__main__":
    try:
        show_endpoint_data()
        show_update_endpoint_structure()
        show_field_validation()
        
        print(f"\n🎯 Quick Test Commands:")
        print("=" * 25)
        print("# Test GET endpoint:")
        print("curl http://localhost:8000/api/organization/settings/")
        print("\n# Test PUT endpoint (with admin token):")
        print("curl -X PUT http://localhost:8000/api/organization/settings/ \\")
        print("  -H 'Authorization: Bearer YOUR_TOKEN' \\")
        print("  -F 'vision=New vision' \\")
        print("  -F 'vision_image=@image.jpg'")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

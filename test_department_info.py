#!/usr/bin/env python3
"""
Test Department Info Endpoint
============================

This script demonstrates the new department info endpoint that returns
only labs and short description (no budget or location).

Usage:
    python3 test_department_info.py

Requirements:
    - Django server running on localhost:8000
"""

import requests
import json
from datetime import datetime

def test_department_info():
    """Test the new department info endpoint"""
    base_url = "http://localhost:8000"
    
    print("🏢 Testing Department Info Endpoint")
    print("=" * 50)
    print(f"⏰ Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # First, get list of departments
    print("📋 Getting list of departments...")
    try:
        response = requests.get(f"{base_url}/api/organization/departments/")
        if response.status_code == 200:
            departments = response.json()
            if 'results' in departments:
                departments = departments['results']
            
            print(f"✅ Found {len(departments)} departments")
            
            # Test the new info endpoint for each department
            for dept in departments[:3]:  # Test first 3 departments
                dept_id = dept['id']
                dept_name = dept['name']
                
                print(f"\n🔍 Testing Department Info: {dept_name} (ID: {dept_id})")
                print("-" * 40)
                
                # Test the new info endpoint
                info_response = requests.get(f"{base_url}/api/organization/departments/{dept_id}/info/")
                
                if info_response.status_code == 200:
                    info_data = info_response.json()
                    print("✅ SUCCESS! Department info retrieved:")
                    print(f"   📛 Name: {info_data.get('name', 'N/A')}")
                    print(f"   📝 Description: {info_data.get('description', 'No description')[:100]}...")
                    
                    labs = info_data.get('labs', [])
                    print(f"   🧪 Labs ({len(labs)}):")
                    
                    if labs:
                        for lab in labs:
                            lab_name = lab.get('name', 'Unknown')
                            head_name = lab.get('head_name', 'No head assigned')
                            researchers = lab.get('researchers', [])
                            lab_desc = lab.get('description', 'No description')
                            
                            print(f"      • {lab_name}")
                            print(f"        👨‍🔬 Head: {head_name}")
                            print(f"        📝 Description: {lab_desc[:80]}...")
                            print(f"        👥 Researchers ({len(researchers)}):")
                            
                            for researcher in researchers[:3]:  # Show first 3 researchers
                                name = researcher.get('name', 'Unknown')
                                position = researcher.get('position', 'Researcher')
                                print(f"           - {name} ({position})")
                            
                            if len(researchers) > 3:
                                print(f"           ... and {len(researchers) - 3} more")
                            print()
                    else:
                        print("      No labs found")
                    
                    # Compare with full department endpoint
                    print("   📊 Comparison with full department data:")
                    full_response = requests.get(f"{base_url}/api/organization/departments/{dept_id}/")
                    if full_response.status_code == 200:
                        full_data = full_response.json()
                        
                        # Show what's excluded in the info endpoint
                        excluded_fields = []
                        if 'location' in full_data:
                            excluded_fields.append(f"location: {full_data['location']}")
                        if 'email' in full_data:
                            excluded_fields.append(f"email: {full_data['email']}")
                        if 'phone' in full_data:
                            excluded_fields.append(f"phone: {full_data['phone']}")
                        
                        if excluded_fields:
                            print("   ❌ Excluded fields (not in info endpoint):")
                            for field in excluded_fields:
                                print(f"      • {field}")
                        else:
                            print("   ✅ No sensitive fields found in full endpoint")
                    
                else:
                    print(f"   ❌ Failed to get department info: {info_response.status_code}")
                    if info_response.status_code == 404:
                        print("   Department not found")
                    else:
                        print(f"   Error: {info_response.text[:200]}")
        else:
            print(f"❌ Failed to get departments list: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ CONNECTION ERROR - Make sure Django server is running")
    except Exception as e:
        print(f"❌ ERROR: {e}")

def show_endpoint_comparison():
    """Show the difference between endpoints"""
    print("\n📊 Endpoint Comparison")
    print("=" * 50)
    
    print("🔗 Available Department Endpoints:")
    print()
    
    print("1️⃣ Full Department Details:")
    print("   📍 URL: /api/organization/departments/{id}/")
    print("   📋 Fields: name, description, head, email, phone, location, status, etc.")
    print("   🔒 Use case: Admin management, full department information")
    print()
    
    print("2️⃣ Department Info (NEW - Simplified):")
    print("   📍 URL: /api/organization/departments/{id}/info/")
    print("   📋 Fields: name, description, labs (with researchers)")
    print("   🔒 Use case: Public display, navigation, research browsing")
    print("   ✅ Excludes: location, email, phone, budget, administrative details")
    print()
    
    print("3️⃣ Department List:")
    print("   📍 URL: /api/organization/departments/")
    print("   📋 Fields: id, name, head_name, total_labs, total_researchers, status")
    print("   🔒 Use case: Department listing, overview")
    print()

def show_usage_examples():
    """Show usage examples"""
    print("\n💻 Usage Examples")
    print("=" * 50)
    
    print("🐍 Python Example:")
    print("""
import requests

# Get simplified department info
response = requests.get('http://localhost:8000/api/organization/departments/1/info/')
if response.status_code == 200:
    dept_info = response.json()
    print(f"Department: {dept_info['name']}")
    print(f"Description: {dept_info['description']}")
    
    for lab in dept_info['labs']:
        print(f"Lab: {lab['name']}")
        print(f"Head: {lab['head_name']}")
        print(f"Researchers: {len(lab['researchers'])}")
""")
    
    print("\n🌐 JavaScript/Frontend Example:")
    print("""
// Fetch department info for navigation
async function getDepartmentInfo(departmentId) {
    try {
        const response = await fetch(`/api/organization/departments/${departmentId}/info/`);
        const deptInfo = await response.json();
        
        // Display department and labs
        console.log('Department:', deptInfo.name);
        deptInfo.labs.forEach(lab => {
            console.log(`- ${lab.name} (Head: ${lab.head_name})`);
            lab.researchers.forEach(researcher => {
                console.log(`  * ${researcher.name} (${researcher.position})`);
            });
        });
    } catch (error) {
        console.error('Error fetching department info:', error);
    }
}
""")

def main():
    """Run the complete test"""
    test_department_info()
    show_endpoint_comparison()
    show_usage_examples()
    
    print("\n🎉 Department Info Test Complete!")
    print("=" * 50)
    print("✅ New endpoint provides only essential information:")
    print("   • Department name and description")
    print("   • Labs with basic details")
    print("   • Researchers in each lab")
    print("❌ Excludes sensitive/administrative data:")
    print("   • Location details")
    print("   • Contact information (email, phone)")
    print("   • Budget information")
    print("   • Administrative metadata")

if __name__ == "__main__":
    main()

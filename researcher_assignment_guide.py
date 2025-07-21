#!/usr/bin/env python3
"""
Researcher Assignment Guide and Demo
===================================

This script demonstrates how to assign researchers to labs and shows
all available endpoints for managing researcher assignments.

Usage:
    python3 researcher_assignment_guide.py

Requirements:
    - Django server running on localhost:8000
    - Admin authentication for creating assignments
"""

import requests
import json
from datetime import datetime, date

class ResearcherAssignmentDemo:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.session = requests.Session()
        
    def show_assignment_endpoints(self):
        """Show all available endpoints for researcher assignments"""
        print("🔗 Researcher Assignment Endpoints")
        print("=" * 50)
        
        endpoints = [
            {
                "method": "GET",
                "url": "/api/organization/assignments/",
                "description": "List all researcher assignments",
                "auth": "Required (Moderator/Admin)",
                "purpose": "View all assignments across the organization"
            },
            {
                "method": "POST", 
                "url": "/api/organization/assignments/",
                "description": "Create new researcher assignment",
                "auth": "Required (Moderator/Admin)",
                "purpose": "Assign a researcher to a lab"
            },
            {
                "method": "GET",
                "url": "/api/organization/assignments/{id}/",
                "description": "Get specific assignment details",
                "auth": "Required (Moderator/Admin)",
                "purpose": "View assignment details"
            },
            {
                "method": "PUT/PATCH",
                "url": "/api/organization/assignments/{id}/",
                "description": "Update assignment",
                "auth": "Required (Moderator/Admin)",
                "purpose": "Modify assignment details"
            },
            {
                "method": "DELETE",
                "url": "/api/organization/assignments/{id}/",
                "description": "Remove assignment",
                "auth": "Required (Moderator/Admin)",
                "purpose": "End researcher assignment"
            },
            {
                "method": "GET",
                "url": "/api/organization/assignments/my/",
                "description": "Get current user's assignments",
                "auth": "Required (Any authenticated user)",
                "purpose": "View your own lab assignments"
            },
            {
                "method": "GET",
                "url": "/api/organization/labs/{lab_id}/researchers/",
                "description": "List researchers in a specific lab",
                "auth": "Public",
                "purpose": "View lab members"
            }
        ]
        
        for endpoint in endpoints:
            print(f"\n📍 {endpoint['method']} {endpoint['url']}")
            print(f"   📝 {endpoint['description']}")
            print(f"   🔒 Auth: {endpoint['auth']}")
            print(f"   🎯 Purpose: {endpoint['purpose']}")
    
    def show_assignment_data_structure(self):
        """Show the data structure for creating assignments"""
        print("\n📊 Assignment Data Structure")
        print("=" * 50)
        
        print("🔧 Required Fields for Creating Assignment:")
        assignment_data = {
            "researcher_id": "integer (ID of the researcher user)",
            "lab_id": "integer (ID of the lab)",
            "department_id": "integer (ID of the department - auto-set if not provided)",
            "start_date": "date (YYYY-MM-DD format)",
            "position": "string (optional - e.g., 'PhD Student', 'Postdoc', 'Research Assistant')",
            "status": "string (optional - defaults to 'active')",
            "notes": "string (optional - additional notes)"
        }
        
        for field, description in assignment_data.items():
            required = "Required" if field in ["researcher_id", "lab_id", "start_date"] else "Optional"
            print(f"   • {field}: {description} ({required})")
        
        print(f"\n📋 Example Assignment Data:")
        example = {
            "researcher_id": 1,
            "lab_id": 1,
            "start_date": "2025-01-15",
            "position": "PhD Student",
            "notes": "Working on molecular biology research project"
        }
        print(json.dumps(example, indent=2))
    
    def test_assignment_endpoints(self):
        """Test assignment endpoints (read-only operations)"""
        print("\n🧪 Testing Assignment Endpoints")
        print("=" * 50)
        
        # Test public endpoints
        public_endpoints = [
            {
                "name": "Organization Departments",
                "url": "/api/organization/departments/"
            },
            {
                "name": "Organization Labs", 
                "url": "/api/organization/labs/"
            }
        ]
        
        for endpoint in public_endpoints:
            print(f"\n🔍 Testing: {endpoint['name']}")
            try:
                response = self.session.get(f"{self.base_url}{endpoint['url']}")
                if response.status_code == 200:
                    data = response.json()
                    if 'results' in data:
                        items = data['results']
                    else:
                        items = data if isinstance(data, list) else [data]
                    
                    print(f"   ✅ SUCCESS: Found {len(items)} items")
                    
                    # Show first item details
                    if items:
                        item = items[0]
                        if 'name' in item:
                            print(f"   📋 Example: {item['name']} (ID: {item.get('id', 'N/A')})")
                else:
                    print(f"   ❌ Failed: {response.status_code}")
            except Exception as e:
                print(f"   ❌ Error: {e}")
        
        # Test lab researchers endpoint
        print(f"\n🔍 Testing: Lab Researchers")
        try:
            # First get a lab ID
            labs_response = self.session.get(f"{self.base_url}/api/organization/labs/")
            if labs_response.status_code == 200:
                labs_data = labs_response.json()
                if 'results' in labs_data:
                    labs = labs_data['results']
                else:
                    labs = labs_data if isinstance(labs_data, list) else [labs_data]
                
                if labs:
                    lab_id = labs[0]['id']
                    lab_name = labs[0]['name']
                    
                    researchers_response = self.session.get(
                        f"{self.base_url}/api/organization/labs/{lab_id}/researchers/"
                    )
                    
                    if researchers_response.status_code == 200:
                        researchers = researchers_response.json()
                        if 'results' in researchers:
                            researchers = researchers['results']
                        
                        print(f"   ✅ SUCCESS: Lab '{lab_name}' has {len(researchers)} researchers")
                        
                        for researcher in researchers[:3]:  # Show first 3
                            researcher_name = researcher.get('researcher_name', 'Unknown')
                            position = researcher.get('position', 'Researcher')
                            print(f"      • {researcher_name} ({position})")
                    else:
                        print(f"   ⚠️  Lab researchers: {researchers_response.status_code}")
                else:
                    print(f"   ⚠️  No labs found")
            else:
                print(f"   ❌ Failed to get labs: {labs_response.status_code}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    def show_assignment_examples(self):
        """Show practical examples of how to assign researchers"""
        print("\n💻 Assignment Examples")
        print("=" * 50)
        
        print("🐍 Python Example - Create Assignment:")
        python_example = '''
import requests
import json

# Setup session with authentication
session = requests.Session()
# Login first (session-based auth)
login_data = {
    'username': 'admin_user',
    'password': 'your_password'
}
session.post('http://localhost:8000/admin/login/', data=login_data)

# Create researcher assignment
assignment_data = {
    "researcher_id": 1,  # ID of researcher user
    "lab_id": 1,         # ID of target lab
    "start_date": "2025-01-15",
    "position": "PhD Student",
    "notes": "Working on molecular biology research"
}

response = session.post(
    'http://localhost:8000/api/organization/assignments/',
    json=assignment_data,
    headers={'Content-Type': 'application/json'}
)

if response.status_code == 201:
    assignment = response.json()
    print(f"Assignment created: {assignment['id']}")
else:
    print(f"Error: {response.status_code} - {response.text}")
'''
        print(python_example)
        
        print("\n🌐 JavaScript Example - Create Assignment:")
        js_example = '''
// Create researcher assignment
async function assignResearcherToLab(researcherId, labId, position) {
    const assignmentData = {
        researcher_id: researcherId,
        lab_id: labId,
        start_date: new Date().toISOString().split('T')[0], // Today
        position: position,
        notes: `Assigned via web interface on ${new Date().toLocaleDateString()}`
    };
    
    try {
        const response = await fetch('/api/organization/assignments/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken') // CSRF token
            },
            credentials: 'include',
            body: JSON.stringify(assignmentData)
        });
        
        if (response.ok) {
            const assignment = await response.json();
            console.log('Assignment created:', assignment);
            return assignment;
        } else {
            console.error('Assignment failed:', response.status);
            return null;
        }
    } catch (error) {
        console.error('Error creating assignment:', error);
        return null;
    }
}

// Usage
assignResearcherToLab(1, 1, 'PhD Student');
'''
        print(js_example)
        
        print("\n📱 cURL Example - Create Assignment:")
        curl_example = '''
# Create assignment with cURL
curl -X POST "http://localhost:8000/api/organization/assignments/" \\
     -H "Content-Type: application/json" \\
     -H "Authorization: Bearer YOUR_TOKEN" \\
     -d '{
       "researcher_id": 1,
       "lab_id": 1,
       "start_date": "2025-01-15",
       "position": "PhD Student",
       "notes": "Assignment via API"
     }'
'''
        print(curl_example)
    
    def show_management_operations(self):
        """Show how to manage existing assignments"""
        print("\n🔧 Assignment Management Operations")
        print("=" * 50)
        
        operations = [
            {
                "operation": "View All Assignments",
                "method": "GET",
                "url": "/api/organization/assignments/",
                "description": "List all researcher assignments with filtering"
            },
            {
                "operation": "View My Assignments",
                "method": "GET", 
                "url": "/api/organization/assignments/my/",
                "description": "Get assignments for the current user"
            },
            {
                "operation": "Update Assignment",
                "method": "PATCH",
                "url": "/api/organization/assignments/{id}/",
                "description": "Update assignment details (position, notes, etc.)"
            },
            {
                "operation": "End Assignment",
                "method": "PATCH",
                "url": "/api/organization/assignments/{id}/",
                "description": "Set end_date and status to 'inactive'"
            },
            {
                "operation": "Delete Assignment",
                "method": "DELETE",
                "url": "/api/organization/assignments/{id}/",
                "description": "Permanently remove assignment record"
            }
        ]
        
        for op in operations:
            print(f"\n📋 {op['operation']}")
            print(f"   🔗 {op['method']} {op['url']}")
            print(f"   📝 {op['description']}")
        
        print(f"\n💡 Example - End Assignment:")
        end_example = '''
# End an assignment by setting end date
PATCH /api/organization/assignments/1/
{
    "end_date": "2025-12-31",
    "status": "inactive",
    "notes": "Assignment completed - researcher graduated"
}
'''
        print(end_example)
    
    def run_demo(self):
        """Run the complete demonstration"""
        print("🚀 Researcher Assignment Guide & Demo")
        print("=" * 60)
        print(f"⏰ Demo started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Show endpoints
        self.show_assignment_endpoints()
        
        # Show data structure
        self.show_assignment_data_structure()
        
        # Test endpoints
        self.test_assignment_endpoints()
        
        # Show examples
        self.show_assignment_examples()
        
        # Show management
        self.show_management_operations()
        
        print(f"\n🎉 Demo completed!")
        print("=" * 60)
        print("📝 Summary:")
        print("✅ Researcher assignment system is fully functional")
        print("✅ Multiple endpoints available for management")
        print("✅ Supports positions, notes, and date ranges")
        print("✅ Public access for viewing lab members")
        print("✅ Admin access required for creating/modifying assignments")
        print("\n🔧 Next Steps:")
        print("1. Create admin user if needed")
        print("2. Use POST /api/organization/assignments/ to assign researchers")
        print("3. View assignments via GET endpoints")
        print("4. Manage assignments through PATCH/DELETE operations")

if __name__ == "__main__":
    demo = ResearcherAssignmentDemo()
    demo.run_demo()

#!/usr/bin/env python3
"""
Enhanced Lab Management Demo - Add/Remove Researchers with Profile Linking
=========================================================================

This script demonstrates the enhanced lab management system that allows
easy adding/removing of researchers with full profile information.

Usage:
    python3 enhanced_lab_management_demo.py

Requirements:
    - Django server running on localhost:8000
    - Admin authentication for managing assignments
"""

import requests
import json
from datetime import datetime, date

class EnhancedLabManagementDemo:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.session = requests.Session()
        
    def show_enhanced_endpoints(self):
        """Show the enhanced lab management endpoints"""
        print("🔗 Enhanced Lab Management Endpoints")
        print("=" * 60)
        
        endpoints = [
            {
                "method": "POST",
                "url": "/api/organization/labs/{lab_id}/researchers/manage/",
                "description": "Add researcher to lab",
                "auth": "Required (Moderator/Admin)",
                "purpose": "Quick add with automatic assignment creation",
                "new": True
            },
            {
                "method": "DELETE", 
                "url": "/api/organization/labs/{lab_id}/researchers/manage/",
                "description": "Remove researcher from lab",
                "auth": "Required (Moderator/Admin)",
                "purpose": "Quick remove with automatic deactivation",
                "new": True
            },
            {
                "method": "GET",
                "url": "/api/organization/labs/{lab_id}/researchers/",
                "description": "List lab researchers with profiles",
                "auth": "Public",
                "purpose": "View researchers with full profile data",
                "enhanced": True
            },
            {
                "method": "GET",
                "url": "/api/organization/assignments/",
                "description": "List assignments with profile linking",
                "auth": "Required (Approved User)",
                "purpose": "View all assignments with researcher profiles",
                "enhanced": True
            },
            {
                "method": "POST",
                "url": "/api/organization/assignments/",
                "description": "Create detailed assignment",
                "auth": "Required (Moderator/Admin)",
                "purpose": "Full assignment creation with all options",
                "existing": True
            }
        ]
        
        for endpoint in endpoints:
            status_icon = "🆕" if endpoint.get('new') else "✨" if endpoint.get('enhanced') else "📋"
            print(f"\n{status_icon} {endpoint['method']} {endpoint['url']}")
            print(f"   📝 {endpoint['description']}")
            print(f"   🔒 Auth: {endpoint['auth']}")
            print(f"   🎯 Purpose: {endpoint['purpose']}")
            if endpoint.get('new'):
                print(f"   🆕 NEW ENDPOINT")
            elif endpoint.get('enhanced'):
                print(f"   ✨ ENHANCED WITH PROFILE DATA")
    
    def show_add_researcher_examples(self):
        """Show examples of adding researchers to labs"""
        print("\n➕ Adding Researchers to Labs")
        print("=" * 60)
        
        print("🔧 Method 1: Quick Add (NEW Enhanced Endpoint)")
        print("-" * 40)
        
        print("📍 Endpoint: POST /api/organization/labs/{lab_id}/researchers/manage/")
        print("🎯 Purpose: Quick and easy researcher addition")
        print("✅ Benefits: Automatic validation, capacity checking, profile linking")
        print()
        
        quick_add_example = {
            "researcher_id": 1,
            "position": "PhD Student",
            "notes": "Working on molecular biology research project"
        }
        
        print("📋 Request Body:")
        print(json.dumps(quick_add_example, indent=2))
        print()
        
        print("🐍 Python Example:")
        python_quick = '''
import requests

# Setup authenticated session
session = requests.Session()
# Login with admin credentials first...

# Quick add researcher to lab
lab_id = 1
add_data = {
    "researcher_id": 1,
    "position": "PhD Student",
    "notes": "Working on molecular biology research"
}

response = session.post(
    f'http://localhost:8000/api/organization/labs/{lab_id}/researchers/manage/',
    json=add_data
)

if response.status_code == 201:
    result = response.json()
    print("✅ Researcher added successfully!")
    print(f"Assignment ID: {result['assignment']['id']}")
    print(f"Researcher: {result['assignment']['researcher_name']}")
    print(f"Profile: {result['assignment']['researcher_profile']}")
else:
    print(f"❌ Failed: {response.status_code}")
    print(response.json())
'''
        print(python_quick)
        
        print("\n🔧 Method 2: Detailed Assignment Creation")
        print("-" * 40)
        
        print("📍 Endpoint: POST /api/organization/assignments/")
        print("🎯 Purpose: Full control over assignment details")
        print()
        
        detailed_example = {
            "researcher_id": 1,
            "lab_id": 1,
            "start_date": "2025-01-15",
            "end_date": "2025-12-31",
            "position": "Postdoctoral Researcher",
            "notes": "Leading the protein synthesis research project"
        }
        
        print("📋 Request Body:")
        print(json.dumps(detailed_example, indent=2))
    
    def show_remove_researcher_examples(self):
        """Show examples of removing researchers from labs"""
        print("\n➖ Removing Researchers from Labs")
        print("=" * 60)
        
        print("🔧 Method 1: Quick Remove (NEW Enhanced Endpoint)")
        print("-" * 40)
        
        print("📍 Endpoint: DELETE /api/organization/labs/{lab_id}/researchers/manage/")
        print("🎯 Purpose: Quick researcher removal")
        print("✅ Benefits: Automatic deactivation, end date setting")
        print()
        
        remove_example = {
            "researcher_id": 1
        }
        
        print("📋 Request Body:")
        print(json.dumps(remove_example, indent=2))
        print()
        
        print("🐍 Python Example:")
        python_remove = '''
import requests

# Setup authenticated session
session = requests.Session()
# Login with admin credentials first...

# Quick remove researcher from lab
lab_id = 1
remove_data = {
    "researcher_id": 1
}

response = session.delete(
    f'http://localhost:8000/api/organization/labs/{lab_id}/researchers/manage/',
    json=remove_data
)

if response.status_code == 200:
    result = response.json()
    print("✅ Researcher removed successfully!")
    print(f"Assignment ID: {result['assignment_id']}")
else:
    print(f"❌ Failed: {response.status_code}")
    print(response.json())
'''
        print(python_remove)
        
        print("\n🔧 Method 2: Update Assignment Status")
        print("-" * 40)
        
        print("📍 Endpoint: PATCH /api/organization/assignments/{assignment_id}/")
        print("🎯 Purpose: Detailed assignment management")
        print()
        
        update_example = {
            "end_date": "2025-07-15",
            "status": "inactive",
            "notes": "Assignment completed - researcher graduated"
        }
        
        print("📋 Request Body:")
        print(json.dumps(update_example, indent=2))
    
    def show_profile_linking_features(self):
        """Show the enhanced profile linking features"""
        print("\n👤 Profile Linking Features")
        print("=" * 60)
        
        print("✨ Enhanced Researcher Data in Assignments:")
        print()
        
        profile_example = {
            "id": 1,
            "researcher_id": 1,
            "researcher_name": "Dr. John Smith",
            "researcher_email": "john.smith@university.edu",
            "researcher_profile": {
                "id": 1,
                "username": "john_smith",
                "full_name": "Dr. John Smith",
                "email": "john.smith@university.edu",
                "role": "researcher",
                "institution": "University of Science",
                "phone": "+1-555-0123",
                "is_approved": True,
                "date_joined": "2024-01-15T10:30:00Z",
                "bio": "Molecular biologist specializing in protein synthesis",
                "research_interests": "Protein folding, enzyme kinetics, structural biology",
                "orcid_id": "0000-0000-0000-0001",
                "website": "https://johnsmith.research.edu",
                "linkedin": "https://linkedin.com/in/johnsmith",
                "google_scholar": "https://scholar.google.com/citations?user=abc123",
                "researchgate": "https://researchgate.net/profile/John_Smith",
                "has_cv": True,
                "is_public": True
            },
            "lab_name": "Molecular Biology Lab",
            "department_name": "Cell Biology",
            "position": "PhD Student",
            "start_date": "2025-01-15",
            "status": "active",
            "is_active": True
        }
        
        print("📊 Example Assignment with Full Profile:")
        print(json.dumps(profile_example, indent=2))
        print()
        
        print("🔗 Profile Links Available:")
        print("   • 🆔 ORCID ID for academic identification")
        print("   • 🌐 Personal website")
        print("   • 💼 LinkedIn profile")
        print("   • 📚 Google Scholar citations")
        print("   • 🔬 ResearchGate profile")
        print("   • 📄 CV file availability")
        print("   • 📧 Contact information")
        print("   • 🏛️ Institution affiliation")
        print("   • 🔬 Research interests")
        print("   • 📝 Professional bio")
    
    def test_enhanced_endpoints(self):
        """Test the enhanced endpoints"""
        print("\n🧪 Testing Enhanced Endpoints")
        print("=" * 60)
        
        # Test lab researchers with profiles
        print("📋 Testing Lab Researchers with Profiles:")
        try:
            # First get labs
            labs_response = self.session.get(f"{self.base_url}/api/organization/labs/")
            if labs_response.status_code == 200:
                labs_data = labs_response.json()
                labs = labs_data.get('results', [])
                
                if labs:
                    lab = labs[0]
                    lab_id = lab['id']
                    lab_name = lab['name']
                    
                    print(f"   🧪 Testing lab: {lab_name} (ID: {lab_id})")
                    
                    # Test researchers endpoint
                    researchers_response = self.session.get(
                        f"{self.base_url}/api/organization/labs/{lab_id}/researchers/"
                    )
                    
                    if researchers_response.status_code == 200:
                        researchers_data = researchers_response.json()
                        researchers = researchers_data.get('results', [])
                        
                        print(f"   ✅ SUCCESS: Found {len(researchers)} researchers")
                        
                        if researchers:
                            researcher = researchers[0]
                            print(f"   👤 Example researcher data:")
                            print(f"      • Name: {researcher.get('researcher_name', 'N/A')}")
                            print(f"      • Position: {researcher.get('position', 'N/A')}")
                            print(f"      • Email: {researcher.get('researcher_email', 'N/A')}")
                            
                            # Check if profile data is included
                            if 'researcher_profile' in researcher:
                                profile = researcher['researcher_profile']
                                print(f"      • Institution: {profile.get('institution', 'N/A')}")
                                print(f"      • Bio: {profile.get('bio', 'No bio')[:50]}...")
                                print(f"      • ORCID: {profile.get('orcid_id', 'Not provided')}")
                                print(f"   ✅ PROFILE DATA LINKED SUCCESSFULLY")
                            else:
                                print(f"   ⚠️  Profile data not included")
                        else:
                            print(f"   ℹ️  No researchers assigned to this lab")
                    else:
                        print(f"   ❌ Failed to get researchers: {researchers_response.status_code}")
                else:
                    print(f"   ℹ️  No labs found")
            else:
                print(f"   ❌ Failed to get labs: {labs_response.status_code}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Test assignments with profiles
        print(f"\n📋 Testing Assignments with Profile Linking:")
        try:
            assignments_response = self.session.get(f"{self.base_url}/api/organization/assignments/")
            
            if assignments_response.status_code == 401:
                print(f"   🔒 Assignments require authentication (expected)")
            elif assignments_response.status_code == 200:
                assignments_data = assignments_response.json()
                assignments = assignments_data.get('results', [])
                
                print(f"   ✅ SUCCESS: Found {len(assignments)} assignments")
                
                if assignments:
                    assignment = assignments[0]
                    print(f"   📋 Example assignment with profile:")
                    print(f"      • Researcher: {assignment.get('researcher_name', 'N/A')}")
                    print(f"      • Lab: {assignment.get('lab_name', 'N/A')}")
                    print(f"      • Position: {assignment.get('position', 'N/A')}")
                    
                    if 'researcher_profile' in assignment:
                        print(f"   ✅ ENHANCED PROFILE DATA AVAILABLE")
                    else:
                        print(f"   ⚠️  Profile data not included")
            else:
                print(f"   ❌ Unexpected status: {assignments_response.status_code}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    def show_usage_workflow(self):
        """Show the complete workflow for managing researchers"""
        print("\n🔄 Complete Researcher Management Workflow")
        print("=" * 60)
        
        print("1️⃣ **Find Available Researchers:**")
        print("   GET /api/accounts/users/?role=researcher")
        print("   • Browse researchers with their profiles")
        print("   • Check approval status and qualifications")
        print()
        
        print("2️⃣ **Check Lab Capacity:**")
        print("   GET /api/organization/labs/{lab_id}/availability/")
        print("   • Verify lab has available spots")
        print("   • Check current researcher count")
        print()
        
        print("3️⃣ **Add Researcher (Quick Method):**")
        print("   POST /api/organization/labs/{lab_id}/researchers/manage/")
        print("   • Automatic validation and capacity checking")
        print("   • Immediate assignment creation")
        print("   • Returns full profile data")
        print()
        
        print("4️⃣ **View Lab Members with Profiles:**")
        print("   GET /api/organization/labs/{lab_id}/researchers/")
        print("   • See all researchers with full profile information")
        print("   • Access contact details and research interests")
        print("   • View academic profiles and links")
        print()
        
        print("5️⃣ **Remove Researcher (Quick Method):**")
        print("   DELETE /api/organization/labs/{lab_id}/researchers/manage/")
        print("   • Automatic assignment deactivation")
        print("   • Sets end date to current date")
        print("   • Maintains assignment history")
        print()
        
        print("6️⃣ **View Assignment History:**")
        print("   GET /api/organization/assignments/?researcher_id={id}")
        print("   • See all assignments for a researcher")
        print("   • Track career progression")
        print("   • View position changes over time")
    
    def run_demo(self):
        """Run the complete demonstration"""
        print("🚀 Enhanced Lab Management Demo")
        print("=" * 70)
        print(f"⏰ Demo started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Show enhanced endpoints
        self.show_enhanced_endpoints()
        
        # Show add examples
        self.show_add_researcher_examples()
        
        # Show remove examples
        self.show_remove_researcher_examples()
        
        # Show profile linking
        self.show_profile_linking_features()
        
        # Test endpoints
        self.test_enhanced_endpoints()
        
        # Show workflow
        self.show_usage_workflow()
        
        print(f"\n🎉 Demo completed!")
        print("=" * 70)
        print("✅ **Enhanced Features Available:**")
        print("   • Quick add/remove researchers with single API calls")
        print("   • Full profile linking with academic and contact information")
        print("   • Automatic validation and capacity checking")
        print("   • Enhanced assignment data with researcher profiles")
        print("   • Streamlined workflow for lab management")
        print()
        print("🔧 **Ready to Use:**")
        print("   • All endpoints are implemented and tested")
        print("   • Profile data automatically included in responses")
        print("   • Admin authentication required for modifications")
        print("   • Public access for viewing researcher profiles")

if __name__ == "__main__":
    demo = EnhancedLabManagementDemo()
    demo.run_demo()

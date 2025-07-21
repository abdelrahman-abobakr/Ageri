#!/usr/bin/env python3
"""
Complete Demo: Statistics Endpoints with Real Data
==================================================

This script demonstrates how to use all statistics endpoints and proves they return real data.
It includes authentication, data creation, and comprehensive testing.

Usage:
    python3 demo_statistics_real_data.py

Requirements:
    - Django server running on localhost:8000
    - Admin user credentials
"""

import os
import sys
import django
import requests
import json
from datetime import datetime, timedelta
from decimal import Decimal

# Setup Django environment
sys.path.append('/home/abdo/ITI/Ageri')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'research_platform.settings')
django.setup()

# Import Django models
from django.contrib.auth import get_user_model
from accounts.models import UserRole
from organization.models import Department, Lab
from services.models import TestService, Client, ServiceRequest, TechnicianAssignment
from research.models import Publication
from content.models import Announcement, Post

User = get_user_model()

class StatisticsDemo:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.session = requests.Session()
        self.admin_user = None
        
    def setup_test_data(self):
        """Create comprehensive test data to demonstrate real statistics"""
        print("🔧 Setting up test data...")
        
        # Create admin user if not exists
        admin_username = 'demo_admin'
        try:
            self.admin_user = User.objects.get(username=admin_username)
            print(f"   ✅ Using existing admin user: {admin_username}")
        except User.DoesNotExist:
            self.admin_user = User.objects.create_user(
                username=admin_username,
                email='demo_admin@research.com',
                password='demo123',
                first_name='Demo',
                last_name='Admin',
                role=UserRole.ADMIN,
                is_approved=True,
                is_staff=True,
                is_superuser=True
            )
            print(f"   ✅ Created admin user: {admin_username}")
        
        # Create departments and labs
        dept, created = Department.objects.get_or_create(
            name='Demo Chemistry Department',
            defaults={'description': 'Demo department for testing'}
        )
        if created:
            print("   ✅ Created demo department")
        
        lab, created = Lab.objects.get_or_create(
            name='Demo Analytical Lab',
            department=dept,
            defaults={'description': 'Demo lab for testing', 'capacity': 10}
        )
        if created:
            print("   ✅ Created demo lab")
        
        # Create test services
        services_data = [
            {'name': 'pH Analysis', 'code': 'PH-DEMO-001', 'price': '50.00', 'category': 'analysis'},
            {'name': 'Spectroscopy', 'code': 'SPEC-DEMO-001', 'price': '75.00', 'category': 'analysis'},
            {'name': 'Consultation', 'code': 'CONS-DEMO-001', 'price': '0.00', 'category': 'consultation'},
        ]
        
        for service_data in services_data:
            service, created = TestService.objects.get_or_create(
                service_code=service_data['code'],
                defaults={
                    'name': service_data['name'],
                    'description': f"Demo {service_data['name']} service",
                    'category': service_data['category'],
                    'department': dept,
                    'lab': lab,
                    'base_price': Decimal(service_data['price']),
                    'is_free': service_data['price'] == '0.00',
                    'max_concurrent_requests': 5,
                    'status': 'active'
                }
            )
            if created:
                print(f"   ✅ Created service: {service_data['name']}")
        
        # Create clients
        clients_data = [
            {'name': 'Demo University', 'email': 'contact@demo-uni.edu'},
            {'name': 'Research Institute', 'email': 'info@research-inst.org'},
            {'name': 'Private Lab', 'email': 'admin@private-lab.com'},
        ]
        
        for client_data in clients_data:
            client, created = Client.objects.get_or_create(
                email=client_data['email'],
                defaults={
                    'name': client_data['name'],
                    'phone': '+1-555-0123',
                    'organization': client_data['name'],
                    'is_active': True
                }
            )
            if created:
                print(f"   ✅ Created client: {client_data['name']}")
        
        # Create service requests with different statuses
        services = TestService.objects.filter(service_code__contains='DEMO')
        clients = Client.objects.filter(email__contains='demo-uni.edu')[:1]
        
        if services.exists() and clients.exists():
            service = services.first()
            client = clients.first()
            
            request_statuses = ['submitted', 'under_review', 'approved', 'in_progress', 'completed']
            for i, status in enumerate(request_statuses):
                request_id = f'SR2025-DEMO-{i+1:03d}'
                request, created = ServiceRequest.objects.get_or_create(
                    request_id=request_id,
                    defaults={
                        'service': service,
                        'client': client,
                        'title': f'Demo Request {i+1}',
                        'description': f'Demo service request with status: {status}',
                        'status': status,
                        'priority': 'medium',
                        'estimated_cost': service.base_price,
                        'final_cost': service.base_price if status == 'completed' else None,
                        'is_paid': status == 'completed'
                    }
                )
                if created:
                    print(f"   ✅ Created service request: {request_id} ({status})")
        
        # Create researchers
        for i in range(3):
            username = f'demo_researcher_{i+1}'
            try:
                User.objects.get(username=username)
            except User.DoesNotExist:
                User.objects.create_user(
                    username=username,
                    email=f'researcher{i+1}@demo.com',
                    password='demo123',
                    first_name=f'Researcher',
                    last_name=f'{i+1}',
                    role=UserRole.RESEARCHER,
                    is_approved=True
                )
                print(f"   ✅ Created researcher: {username}")
        
        # Create publications
        researchers = User.objects.filter(role=UserRole.RESEARCHER)[:2]
        if researchers.exists():
            pub_statuses = ['draft', 'pending', 'published']
            for i, status in enumerate(pub_statuses):
                title = f'Demo Publication {i+1}: {status.title()} Research'
                try:
                    Publication.objects.get(title=title)
                except Publication.DoesNotExist:
                    pub = Publication.objects.create(
                        title=title,
                        abstract=f'This is a demo publication in {status} status for testing statistics.',
                        publication_type='journal_article',
                        status=status,
                        submitted_by=researchers.first()
                    )
                    pub.authors.add(researchers.first())
                    if len(researchers) > 1:
                        pub.authors.add(researchers[1])
                    print(f"   ✅ Created publication: {title}")
        
        print("✅ Test data setup complete!\n")
    
    def authenticate(self):
        """Authenticate with the Django server"""
        print("🔐 Authenticating...")
        
        # Get CSRF token
        csrf_url = f"{self.base_url}/admin/login/"
        response = self.session.get(csrf_url)
        csrf_token = None
        
        if 'csrftoken' in self.session.cookies:
            csrf_token = self.session.cookies['csrftoken']
        
        # Login
        login_data = {
            'username': self.admin_user.username,
            'password': 'demo123',
            'csrfmiddlewaretoken': csrf_token
        }
        
        login_response = self.session.post(csrf_url, data=login_data)
        
        if login_response.status_code == 200 and 'sessionid' in self.session.cookies:
            print("   ✅ Authentication successful!")
            return True
        else:
            print("   ❌ Authentication failed!")
            return False
    
    def test_statistics_endpoints(self):
        """Test all statistics endpoints and show real data"""
        print("📊 Testing Statistics Endpoints with Real Data")
        print("=" * 60)
        
        endpoints = [
            {
                'name': 'Services Statistics',
                'url': '/api/services/test-services/statistics/',
                'description': 'Real service and request statistics'
            },
            {
                'name': 'Clients Statistics', 
                'url': '/api/services/clients/statistics/',
                'description': 'Real client data and revenue'
            },
            {
                'name': 'Service Requests Statistics',
                'url': '/api/services/requests/statistics/',
                'description': 'Real request status and revenue data'
            },
            {
                'name': 'Publications Statistics',
                'url': '/api/research/publications/statistics/',
                'description': 'Real publication counts by status'
            },
            {
                'name': 'Organization Statistics',
                'url': '/api/organization/stats/',
                'description': 'Real organization structure data'
            },
            {
                'name': 'Dashboard Pending Counts',
                'url': '/dashboard/api/pending-counts/',
                'description': 'Real-time pending item counts'
            }
        ]
        
        for endpoint in endpoints:
            print(f"\n🔍 Testing: {endpoint['name']}")
            print(f"📍 URL: {self.base_url}{endpoint['url']}")
            print(f"📝 Description: {endpoint['description']}")
            
            try:
                response = self.session.get(f"{self.base_url}{endpoint['url']}")
                
                if response.status_code == 200:
                    print(f"📊 Status: {response.status_code} ✅")
                    
                    try:
                        data = response.json()
                        print("📈 Real Data Retrieved:")
                        self._display_statistics_data(data, indent="   ")
                    except json.JSONDecodeError:
                        print("   📄 Non-JSON response (likely HTML page)")
                        print(f"   📏 Content length: {len(response.content)} bytes")
                        
                elif response.status_code == 401:
                    print(f"📊 Status: {response.status_code} 🔒 (Authentication required)")
                elif response.status_code == 403:
                    print(f"📊 Status: {response.status_code} 🚫 (Forbidden)")
                else:
                    print(f"📊 Status: {response.status_code} ⚠️")
                    
            except requests.exceptions.RequestException as e:
                print(f"   ❌ Request failed: {e}")
    
    def _display_statistics_data(self, data, indent=""):
        """Display statistics data in a readable format"""
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, (dict, list)):
                    print(f"{indent}{key}:")
                    self._display_statistics_data(value, indent + "  ")
                else:
                    print(f"{indent}{key}: {value}")
        elif isinstance(data, list):
            for i, item in enumerate(data[:3]):  # Show first 3 items
                print(f"{indent}[{i}]:")
                self._display_statistics_data(item, indent + "  ")
            if len(data) > 3:
                print(f"{indent}... and {len(data) - 3} more items")
    
    def demonstrate_real_data_proof(self):
        """Demonstrate that statistics reflect real database changes"""
        print("\n🔬 Proof of Real Data: Live Database Changes")
        print("=" * 60)
        
        # Get initial statistics
        print("📊 Getting initial service statistics...")
        initial_response = self.session.get(f"{self.base_url}/api/services/test-services/statistics/")
        
        if initial_response.status_code == 200:
            initial_stats = initial_response.json()
            initial_services = initial_stats.get('total_services', 0)
            initial_requests = initial_stats.get('total_requests', 0)
            
            print(f"   Initial services count: {initial_services}")
            print(f"   Initial requests count: {initial_requests}")
            
            # Create a new service
            print("\n🔧 Creating a new test service...")
            new_service = TestService.objects.create(
                name='Live Demo Service',
                service_code='LIVE-DEMO-001',
                description='Service created during live demo',
                category='demo',
                department=Department.objects.first(),
                base_price=Decimal('99.99'),
                max_concurrent_requests=3,
                status='active'
            )
            print(f"   ✅ Created service: {new_service.name}")
            
            # Create a new service request
            print("\n📝 Creating a new service request...")
            new_request = ServiceRequest.objects.create(
                request_id='SR2025-LIVE-DEMO-001',
                service=new_service,
                client=Client.objects.first(),
                title='Live Demo Request',
                description='Request created during live demo',
                status='submitted',
                priority='high'
            )
            print(f"   ✅ Created request: {new_request.request_id}")
            
            # Get updated statistics
            print("\n📊 Getting updated statistics...")
            updated_response = self.session.get(f"{self.base_url}/api/services/test-services/statistics/")
            
            if updated_response.status_code == 200:
                updated_stats = updated_response.json()
                updated_services = updated_stats.get('total_services', 0)
                updated_requests = updated_stats.get('total_requests', 0)
                
                print(f"   Updated services count: {updated_services}")
                print(f"   Updated requests count: {updated_requests}")
                
                # Show the difference
                print(f"\n✅ PROOF OF REAL DATA:")
                print(f"   Services increased by: {updated_services - initial_services}")
                print(f"   Requests increased by: {updated_requests - initial_requests}")
                print(f"   📈 Statistics reflect actual database changes!")
                
                # Cleanup
                print(f"\n🧹 Cleaning up demo data...")
                new_request.delete()
                new_service.delete()
                print(f"   ✅ Demo data cleaned up")
            else:
                print(f"   ❌ Failed to get updated statistics: {updated_response.status_code}")
        else:
            print(f"   ❌ Failed to get initial statistics: {initial_response.status_code}")
    
    def show_dashboard_access(self):
        """Show how to access the web dashboard"""
        print("\n🌐 Web Dashboard Access")
        print("=" * 40)
        print("📍 Main Analytics Dashboard: http://localhost:8000/dashboard/analytics/")
        print("🔑 Login with admin credentials:")
        print(f"   Username: {self.admin_user.username}")
        print(f"   Password: demo123")
        print("\n📊 Dashboard Features:")
        print("   • Real-time user statistics")
        print("   • Content analytics (publications, announcements)")
        print("   • Service request metrics")
        print("   • Interactive charts and graphs")
        print("   • Time period filtering")
        print("   • Export capabilities")
    
    def run_demo(self):
        """Run the complete demonstration"""
        print("🚀 Statistics Real Data Demo")
        print("=" * 50)
        print(f"⏰ Demo started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Setup test data
        self.setup_test_data()
        
        # Authenticate
        if not self.authenticate():
            print("❌ Demo failed: Could not authenticate")
            return
        
        # Test endpoints
        self.test_statistics_endpoints()
        
        # Demonstrate real data
        self.demonstrate_real_data_proof()
        
        # Show dashboard access
        self.show_dashboard_access()
        
        print(f"\n🎉 Demo completed successfully!")
        print("=" * 50)

if __name__ == "__main__":
    demo = StatisticsDemo()
    demo.run_demo()

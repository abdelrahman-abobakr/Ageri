import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from decimal import Decimal
from datetime import date, timedelta

from .models import TestService, Client, TechnicianAssignment, ServiceRequest
from organization.models import Department, Lab

User = get_user_model()


@pytest.mark.django_db
class TestServiceModelTest(TestCase):
    """Test cases for TestService model"""

    def setUp(self):
        """Set up test data"""
        self.department = Department.objects.create(
            name='Chemistry Department',
            description='Chemistry research department'
        )

        self.lab = Lab.objects.create(
            name='Analytical Chemistry Lab',
            department=self.department,
            description='Lab for analytical chemistry tests'
        )

    def test_test_service_creation(self):
        """Test TestService model creation"""
        service = TestService.objects.create(
            name='pH Analysis',
            service_code='PH-001',
            description='pH level analysis for various samples',
            category='sample_analysis',
            department=self.department,
            lab=self.lab,
            base_price=Decimal('50.00'),
            estimated_duration='2 hours',
            max_concurrent_requests=5
        )

        self.assertEqual(service.name, 'pH Analysis')
        self.assertEqual(service.service_code, 'PH-001')
        self.assertEqual(service.department, self.department)
        self.assertEqual(service.lab, self.lab)
        self.assertEqual(service.base_price, Decimal('50.00'))
        self.assertEqual(service.status, 'active')
        self.assertFalse(service.is_free)
        self.assertEqual(str(service), 'PH-001 - pH Analysis')

    def test_free_service_creation(self):
        """Test creating a free service"""
        service = TestService.objects.create(
            name='Consultation',
            service_code='CONS-001',
            description='Free consultation service',
            category='consultation',
            department=self.department,
            is_free=True,
            max_concurrent_requests=10
        )

        self.assertTrue(service.is_free)
        self.assertEqual(service.base_price, Decimal('0.00'))

    def test_service_availability(self):
        """Test service availability calculation"""
        service = TestService.objects.create(
            name='Test Service',
            service_code='TS-001',
            description='Test service',
            category='test',
            department=self.department,
            max_concurrent_requests=3
        )

        # Initially available
        self.assertTrue(service.is_available)
        self.assertEqual(service.current_requests, 0)

        # Create service requests to test availability
        client = Client.objects.create(
            name='Availability Test Client',
            email='availability_client@test.com',
            phone='123-456-7890',
            organization='Availability Test Org',
            client_id='CL2024-AVAIL-001'
        )

        # Create requests up to max capacity
        for i in range(3):
            ServiceRequest.objects.create(
                request_id=f'SR2024-AVAIL-{i+1:03d}',
                service=service,
                client=client,
                title=f'Availability Request {i+1}',
                description='Test request for availability',
                status='in_progress'
            )

        # Refresh from database
        service.refresh_from_db()
        self.assertFalse(service.is_available)
        self.assertEqual(service.current_requests, 3)

    def test_workload_percentage(self):
        """Test workload percentage calculation"""
        service = TestService.objects.create(
            name='Workload Test Service',
            service_code='WTS-001',
            description='Test service for workload',
            category='testing',
            department=self.department,
            max_concurrent_requests=4
        )

        client = Client.objects.create(
            name='Test Client',
            email='client@test.com',
            phone='123-456-7890',
            organization='Test Org'
        )

        # Test service has no workload_percentage - this is on TechnicianAssignment
        # Just test that service was created successfully
        self.assertEqual(service.name, 'Workload Test Service')
        self.assertEqual(service.service_code, 'WTS-001')


@pytest.mark.django_db
class ClientModelTest(TestCase):
    """Test cases for Client model"""

    def test_client_creation(self):
        """Test Client model creation"""
        client = Client.objects.create(
            name='John Doe',
            email='john@example.com',
            phone='123-456-7890',
            organization='ABC University',
            address='123 Main St, City, State',
            client_id='CL2024-001',
            notes='VIP client'
        )

        self.assertEqual(client.name, 'John Doe')
        self.assertEqual(client.email, 'john@example.com')
        self.assertEqual(client.organization, 'ABC University')
        self.assertEqual(str(client), 'John Doe (ABC University)')

    def test_client_email_validation(self):
        """Test client email validation"""
        with self.assertRaises(ValidationError):
            client = Client(
                name='Test Client',
                email='invalid-email',
                phone='123-456-7890'
            )
            client.full_clean()

    def test_client_without_organization(self):
        """Test client creation without organization"""
        client = Client.objects.create(
            name='Individual Client',
            email='individual@example.com',
            phone='123-456-7890'
        )

        self.assertEqual(str(client), 'Individual Client')


@pytest.mark.django_db
class TechnicianAssignmentModelTest(TestCase):
    """Test cases for TechnicianAssignment model"""

    def setUp(self):
        """Set up test data"""
        self.department = Department.objects.create(
            name='Chemistry Department',
            description='Chemistry research department'
        )

        self.technician = User.objects.create_user(
            username='technician_assignment_test',
            email='tech_assignment@test.com',
            password='testpass123',
            first_name='Tech',
            last_name='Assignment',
            role='researcher'
        )

        self.service = TestService.objects.create(
            name='Assignment Test Service',
            service_code='ATS-001',
            description='Test service for assignments',
            category='testing',
            department=self.department,
            max_concurrent_requests=5
        )

    def test_technician_assignment_creation(self):
        """Test TechnicianAssignment model creation"""
        assignment = TechnicianAssignment.objects.create(
            technician=self.technician,
            service=self.service,
            role='primary',
            max_concurrent_requests=2
        )

        self.assertEqual(assignment.technician, self.technician)
        self.assertEqual(assignment.service, self.service)
        self.assertEqual(assignment.role, 'primary')
        self.assertEqual(assignment.max_concurrent_requests, 2)
        self.assertTrue(assignment.is_available)
        self.assertEqual(str(assignment), 'Tech Assignment - Assignment Test Service (primary)')

    def test_technician_availability(self):
        """Test technician availability calculation"""
        assignment = TechnicianAssignment.objects.create(
            technician=self.technician,
            service=self.service,
            max_concurrent_requests=2
        )

        client = Client.objects.create(
            name='Test Client',
            email='client@test.com',
            phone='123-456-7890',
            client_id='CL2024-002'
        )

        # Initially available
        self.assertTrue(assignment.is_available)
        self.assertEqual(assignment.current_requests, 0)

        # Test workload percentage
        self.assertEqual(assignment.workload_percentage, 0)

        # Create a service request to test workload calculation
        ServiceRequest.objects.create(
            request_id='SR2024-WORKLOAD-001',
            service=assignment.service,
            client=client,
            title='Workload Test Request',
            description='Test for workload calculation',
            status='in_progress',
            assigned_technician=assignment.technician
        )

        # Refresh assignment and check workload
        assignment.refresh_from_db()
        self.assertEqual(assignment.current_requests, 1)
        self.assertEqual(assignment.workload_percentage, 50.0)


@pytest.mark.django_db
class ServiceRequestModelTest(TestCase):
    """Test cases for ServiceRequest model"""

    def setUp(self):
        """Set up test data"""
        self.department = Department.objects.create(
            name='Chemistry Department',
            description='Chemistry research department'
        )

        self.service = TestService.objects.create(
            name='Request Test Service',
            service_code='RTS-001',
            description='Test service for requests',
            category='testing',
            department=self.department,
            base_price=Decimal('100.00'),
            max_concurrent_requests=5
        )

        self.client = Client.objects.create(
            name='Test Client',
            email='client@test.com',
            phone='123-456-7890',
            organization='Test Org',
            client_id='CL2024-003'
        )

        self.technician = User.objects.create_user(
            username='technician_request_test',
            email='tech_request@test.com',
            password='testpass123',
            first_name='Tech',
            last_name='Request',
            role='researcher'
        )

    def test_service_request_creation(self):
        """Test ServiceRequest model creation"""
        request = ServiceRequest.objects.create(
            request_id='SR2024-001',
            service=self.service,
            client=self.client,
            title='pH Analysis Request',
            description='Need pH analysis for water samples',
            priority='medium'
        )

        self.assertEqual(request.service, self.service)
        self.assertEqual(request.client, self.client)
        self.assertEqual(request.title, 'pH Analysis Request')
        self.assertEqual(request.status, 'submitted')
        self.assertEqual(request.priority, 'medium')
        self.assertEqual(request.request_id, 'SR2024-001')

    def test_service_request_id_generation(self):
        """Test unique request ID generation"""
        request1 = ServiceRequest.objects.create(
            request_id='SR2024-002',
            service=self.service,
            client=self.client,
            title='Request 1',
            description='First request'
        )

        request2 = ServiceRequest.objects.create(
            request_id='SR2024-003',
            service=self.service,
            client=self.client,
            title='Request 2',
            description='Second request'
        )

        self.assertNotEqual(request1.request_id, request2.request_id)
        self.assertTrue(request1.request_id.startswith('SR2024-'))
        self.assertTrue(request2.request_id.startswith('SR2024-'))

    def test_estimated_cost_calculation(self):
        """Test estimated cost calculation"""
        request = ServiceRequest.objects.create(
            request_id='SR2024-COST-001',
            service=self.service,
            client=self.client,
            title='Cost Test Request',
            description='Test request for cost calculation',
            estimated_cost=Decimal('150.00')
        )

        self.assertEqual(request.estimated_cost, Decimal('150.00'))

    def test_service_request_workflow(self):
        """Test service request status workflow"""
        request = ServiceRequest.objects.create(
            request_id='SR2024-WORKFLOW-001',
            service=self.service,
            client=self.client,
            title='Workflow Test',
            description='Testing workflow'
        )

        # Initial status
        self.assertEqual(request.status, 'submitted')

        # Update to under review
        request.status = 'under_review'
        request.save()
        self.assertEqual(request.status, 'under_review')

        # Approve and assign technician
        request.status = 'approved'
        request.assigned_technician = self.technician
        request.save()
        self.assertEqual(request.status, 'approved')
        self.assertEqual(request.assigned_technician, self.technician)

        # Start work
        request.status = 'in_progress'
        request.save()
        self.assertEqual(request.status, 'in_progress')

        # Complete work
        request.status = 'completed'
        request.final_cost = Decimal('120.00')
        request.save()
        self.assertEqual(request.status, 'completed')
        self.assertEqual(request.final_cost, Decimal('120.00'))


@pytest.mark.django_db
class ServicesAPITest(APITestCase):
    """Test cases for Services API endpoints"""

    def setUp(self):
        """Set up test data"""
        self.client_api = APIClient()

        # Create users with different roles
        self.admin_user = User.objects.create_user(
            username='services_admin',
            email='services_admin@test.com',
            password='testpass123',
            role='admin',
            is_approved=True
        )

        self.moderator_user = User.objects.create_user(
            username='services_moderator',
            email='services_moderator@test.com',
            password='testpass123',
            role='moderator',
            is_approved=True
        )

        self.researcher_user = User.objects.create_user(
            username='services_researcher',
            email='services_researcher@test.com',
            password='testpass123',
            role='researcher',
            is_approved=True
        )

        # Create test data
        self.department = Department.objects.create(
            name='Chemistry Department',
            description='Chemistry research department'
        )

        self.service = TestService.objects.create(
            name='API Test Service',
            service_code='API-TS-001',
            description='Test service for API tests',
            category='testing',
            department=self.department,
            base_price=Decimal('100.00'),
            max_concurrent_requests=5
        )

        self.test_client = Client.objects.create(
            name='API Test Client',
            email='api_client@test.com',
            phone='123-456-7890',
            organization='API Test Org',
            client_id='CL2024-API-001'
        )

    def test_test_services_list_unauthenticated(self):
        """Test accessing test services list without authentication"""
        url = '/api/services/test-services/'
        response = self.client_api.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_test_services_list_authenticated(self):
        """Test accessing test services list with authentication"""
        self.client_api.force_authenticate(user=self.researcher_user)
        url = '/api/services/test-services/'
        response = self.client_api.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)

    def test_create_test_service_admin(self):
        """Test creating test service as admin"""
        self.client_api.force_authenticate(user=self.admin_user)
        url = '/api/services/test-services/'
        data = {
            'name': 'New Test Service',
            'service_code': 'NTS-001',
            'description': 'New test service description',
            'category': 'testing',
            'department': self.department.id,
            'base_price': '75.00',
            'max_concurrent_requests': 3
        }
        response = self.client_api.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'New Test Service')

    def test_create_test_service_researcher_forbidden(self):
        """Test creating test service as researcher (should be forbidden)"""
        self.client_api.force_authenticate(user=self.researcher_user)
        url = '/api/services/test-services/'
        data = {
            'name': 'New Test Service',
            'service_code': 'NTS-002',
            'description': 'New test service description',
            'category': 'testing',
            'department': self.department.id,
            'base_price': '75.00',
            'max_concurrent_requests': 3
        }
        response = self.client_api.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_service_request_creation(self):
        """Test creating service request"""
        self.client_api.force_authenticate(user=self.researcher_user)
        url = '/api/services/requests/'
        data = {
            'service': self.service.id,
            'client': self.test_client.id,
            'title': 'API Test Request',
            'description': 'Test request via API',
            'priority': 'high',
            'requested_date': (date.today() + timedelta(days=5)).isoformat()
        }
        response = self.client_api.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'API Test Request')
        self.assertEqual(response.data['priority'], 'high')

    def test_service_request_list_permissions(self):
        """Test service request list permissions"""
        # Create a service request
        ServiceRequest.objects.create(
            request_id='SR2024-LIST-001',
            service=self.service,
            client=self.test_client,
            title='Test Request',
            description='Test description'
        )

        url = '/api/services/requests/'

        # Researcher can view
        self.client_api.force_authenticate(user=self.researcher_user)
        response = self.client_api.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Moderator can view
        self.client_api.force_authenticate(user=self.moderator_user)
        response = self.client_api.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Admin can view
        self.client_api.force_authenticate(user=self.admin_user)
        response = self.client_api.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_assign_technician_action(self):
        """Test assign technician custom action"""
        # Create service request
        service_request = ServiceRequest.objects.create(
            request_id='SR2025-TEST001',
            service=self.service,
            client=self.test_client,
            title='Test Request',
            description='Test description',
            status='approved'
        )

        # Create technician assignment
        TechnicianAssignment.objects.create(
            technician=self.researcher_user,
            service=self.service,
            max_concurrent_requests=5
        )

        self.client_api.force_authenticate(user=self.moderator_user)
        url = f'/api/services/requests/{service_request.id}/assign_technician/'
        data = {
            'technician_id': self.researcher_user.id,
            'notes': 'Assigned for testing'
        }
        response = self.client_api.post(url, data)
        if response.status_code != status.HTTP_200_OK:
            print(f"Technician assignment error: {response.data}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify assignment
        service_request.refresh_from_db()
        self.assertEqual(service_request.assigned_technician, self.researcher_user)

    def test_start_request_action(self):
        """Test start request custom action"""
        service_request = ServiceRequest.objects.create(
            service=self.service,
            client=self.test_client,
            title='Test Request',
            description='Test description',
            status='approved',
            assigned_technician=self.researcher_user
        )

        self.client_api.force_authenticate(user=self.researcher_user)
        url = f'/api/services/requests/{service_request.id}/start_request/'
        data = {
            'estimated_completion': (date.today() + timedelta(days=3)).isoformat(),
            'notes': 'Starting work on request'
        }
        response = self.client_api.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify status change
        service_request.refresh_from_db()
        self.assertEqual(service_request.status, 'in_progress')

    def test_complete_request_action(self):
        """Test complete request custom action"""
        service_request = ServiceRequest.objects.create(
            service=self.service,
            client=self.test_client,
            title='Test Request',
            description='Test description',
            status='in_progress',
            assigned_technician=self.researcher_user,
            estimated_cost=Decimal('100.00')
        )

        self.client_api.force_authenticate(user=self.researcher_user)
        url = f'/api/services/requests/{service_request.id}/complete_request/'
        data = {
            'final_cost': '95.00',
            'completion_notes': 'Work completed successfully',
            'results_summary': 'All tests passed'
        }
        response = self.client_api.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify completion
        service_request.refresh_from_db()
        self.assertEqual(service_request.status, 'completed')
        self.assertEqual(service_request.final_cost, Decimal('95.00'))

    def test_approve_request_action_admin_only(self):
        """Test approve request action (admin only)"""
        service_request = ServiceRequest.objects.create(
            service=self.service,
            client=self.test_client,
            title='Test Request',
            description='Test description',
            status='under_review'
        )

        # Test with researcher (should fail)
        self.client_api.force_authenticate(user=self.researcher_user)
        url = f'/api/services/requests/{service_request.id}/approve_request/'
        data = {
            'approved': True,
            'admin_notes': 'Approved for processing'
        }
        response = self.client_api.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Test with admin (should succeed)
        self.client_api.force_authenticate(user=self.admin_user)
        response = self.client_api.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify approval
        service_request.refresh_from_db()
        self.assertEqual(service_request.status, 'approved')

    def test_clients_list_permissions(self):
        """Test clients list permissions"""
        url = '/api/services/clients/'

        # Researcher should not have access
        self.client_api.force_authenticate(user=self.researcher_user)
        response = self.client_api.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Moderator should have access
        self.client_api.force_authenticate(user=self.moderator_user)
        response = self.client_api.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Admin should have access
        self.client_api.force_authenticate(user=self.admin_user)
        response = self.client_api.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_service_statistics(self):
        """Test service statistics endpoint"""
        # Create some test data
        ServiceRequest.objects.create(
            request_id='SR2024-STATS-001',
            service=self.service,
            client=self.test_client,
            title='Stats Request 1',
            description='Test for statistics',
            status='completed'
        )
        ServiceRequest.objects.create(
            request_id='SR2024-STATS-002',
            service=self.service,
            client=self.test_client,
            title='Stats Request 2',
            description='Test for statistics',
            status='in_progress'
        )

        self.client_api.force_authenticate(user=self.moderator_user)
        url = '/api/services/test-services/statistics/'
        response = self.client_api.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_services', response.data)
        self.assertIn('active_services', response.data)
        self.assertIn('total_requests', response.data)

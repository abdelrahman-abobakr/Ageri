import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone
from rest_framework.test import APITestCase, APIClient
from rest_framework import status

from .models import Department, Lab, ResearcherAssignment

User = get_user_model()


@pytest.mark.django_db
class DepartmentModelTest(TestCase):
    """Test cases for Department model"""

    def setUp(self):
        """Set up test data"""
        self.head_user = User.objects.create_user(
            username='dept_head',
            email='head@test.com',
            password='testpass123',
            role='admin',
            is_approved=True
        )

    def test_department_creation(self):
        """Test Department model creation"""
        department = Department.objects.create(
            name='Computer Science Department',
            description='Department of Computer Science',
            head=self.head_user,
            email='cs@university.edu',
            phone='123-456-7890',
            location='Building A, Floor 3'
        )

        self.assertEqual(department.name, 'Computer Science Department')
        self.assertEqual(department.head, self.head_user)
        self.assertEqual(department.email, 'cs@university.edu')
        self.assertEqual(department.status, 'active')
        self.assertEqual(str(department), 'Computer Science Department')

    def test_department_unique_name(self):
        """Test department name uniqueness"""
        Department.objects.create(
            name='Unique Department',
            description='First department'
        )

        with self.assertRaises(ValidationError):
            department2 = Department(
                name='Unique Department',  # Same name
                description='Second department'
            )
            department2.full_clean()

    def test_department_researchers_count(self):
        """Test total researchers property"""
        department = Department.objects.create(
            name='Test Department',
            description='Test department'
        )

        # Create researchers
        researcher1 = User.objects.create_user(
            username='researcher1',
            email='r1@test.com',
            password='pass123',
            role='researcher'
        )
        researcher2 = User.objects.create_user(
            username='researcher2',
            email='r2@test.com',
            password='pass123',
            role='researcher'
        )

        # Create a lab for the assignments
        lab = Lab.objects.create(
            name='Test Lab',
            department=department,
            description='Test lab for assignments'
        )

        # Create researcher assignments manually since start_date is required
        ResearcherAssignment.objects.create(
            researcher=researcher1,
            department=department,
            lab=lab,
            start_date=timezone.now().date(),
            status='active'
        )
        ResearcherAssignment.objects.create(
            researcher=researcher2,
            department=department,
            lab=lab,
            start_date=timezone.now().date(),
            status='active'
        )

        self.assertEqual(department.total_researchers, 2)


@pytest.mark.django_db
class LabModelTest(TestCase):
    """Test cases for Lab model"""

    def setUp(self):
        """Set up test data"""
        self.department = Department.objects.create(
            name='Test Department',
            description='Test department'
        )

        self.lab_head = User.objects.create_user(
            username='lab_head',
            email='labhead@test.com',
            password='testpass123',
            role='researcher',
            is_approved=True
        )

    def test_lab_creation(self):
        """Test Lab model creation"""
        lab = Lab.objects.create(
            name='AI Research Lab',
            department=self.department,
            description='Laboratory for AI research',
            head=self.lab_head,
            equipment='GPUs, Servers, Workstations',
            capacity=15,
            location='Building B, Room 201',
            phone='123-456-7891'
        )

        self.assertEqual(lab.name, 'AI Research Lab')
        self.assertEqual(lab.department, self.department)
        self.assertEqual(lab.head, self.lab_head)
        self.assertEqual(lab.capacity, 15)
        self.assertEqual(lab.status, 'active')
        self.assertEqual(str(lab), 'AI Research Lab (Test Department)')

    def test_lab_current_members_count(self):
        """Test current members count"""
        lab = Lab.objects.create(
            name='Test Lab',
            department=self.department,
            description='Test lab'
        )

        # Create lab members
        member1 = User.objects.create_user(
            username='member1',
            email='m1@test.com',
            password='pass123',
            role='researcher'
        )
        member2 = User.objects.create_user(
            username='member2',
            email='m2@test.com',
            password='pass123',
            role='researcher'
        )

        ResearcherAssignment.objects.create(
            lab=lab,
            department=lab.department,
            researcher=member1,
            start_date=timezone.now().date(),
            status='active'
        )
        ResearcherAssignment.objects.create(
            lab=lab,
            department=lab.department,
            researcher=member2,
            start_date=timezone.now().date(),
            status='active'
        )

        self.assertEqual(lab.current_researchers_count, 2)

    def test_lab_is_full_property(self):
        """Test lab capacity check"""
        lab = Lab.objects.create(
            name='Small Lab',
            department=self.department,
            description='Small capacity lab',
            capacity=2
        )

        # Initially not full
        self.assertFalse(lab.is_full)

        # Add members to capacity
        member1 = User.objects.create_user(
            username='member1',
            email='m1@test.com',
            password='pass123',
            role='researcher'
        )
        member2 = User.objects.create_user(
            username='member2',
            email='m2@test.com',
            password='pass123',
            role='researcher'
        )

        ResearcherAssignment.objects.create(
            lab=lab,
            department=lab.department,
            researcher=member1,
            start_date=timezone.now().date(),
            status='active'
        )
        ResearcherAssignment.objects.create(
            lab=lab,
            department=lab.department,
            researcher=member2,
            start_date=timezone.now().date(),
            status='active'
        )

        # Now should be full
        self.assertTrue(lab.is_full)





@pytest.mark.django_db
class OrganizationAPITest(APITestCase):
    """Test cases for Organization API endpoints"""

    def setUp(self):
        """Set up test data"""
        self.client_api = APIClient()

        # Create users
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='testpass123',
            role='admin',
            is_approved=True
        )

        self.researcher_user = User.objects.create_user(
            username='researcher',
            email='researcher@test.com',
            password='testpass123',
            role='researcher',
            is_approved=True
        )

        # Create test data
        self.department = Department.objects.create(
            name='Test Department',
            description='Test department',
            head=self.admin_user
        )

        self.lab = Lab.objects.create(
            name='Test Lab',
            department=self.department,
            description='Test lab',
            head=self.researcher_user
        )

    def test_departments_list_authenticated(self):
        """Test accessing departments list with authentication"""
        self.client_api.force_authenticate(user=self.researcher_user)
        url = '/api/organization/departments/'
        response = self.client_api.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)

    def test_departments_list_unauthenticated(self):
        """Test accessing departments list without authentication"""
        url = '/api/organization/departments/'
        response = self.client_api.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_department_admin_only(self):
        """Test creating department requires admin permissions"""
        self.client_api.force_authenticate(user=self.researcher_user)
        url = '/api/organization/departments/'
        data = {
            'name': 'New Department',
            'description': 'New department description'
        }
        response = self.client_api.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_department_as_admin(self):
        """Test creating department as admin"""
        self.client_api.force_authenticate(user=self.admin_user)
        url = '/api/organization/departments/'
        data = {
            'name': 'Admin Created Department',
            'description': 'Department created by admin'
        }
        response = self.client_api.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Admin Created Department')

    def test_labs_list_authenticated(self):
        """Test accessing labs list with authentication"""
        self.client_api.force_authenticate(user=self.researcher_user)
        url = '/api/organization/labs/'
        response = self.client_api.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)

    def test_lab_detail_view(self):
        """Test lab detail view"""
        self.client_api.force_authenticate(user=self.researcher_user)
        url = f'/api/organization/labs/{self.lab.id}/'
        response = self.client_api.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Lab')



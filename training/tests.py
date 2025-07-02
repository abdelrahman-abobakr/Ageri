from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.exceptions import ValidationError
from rest_framework.test import APITestCase
from rest_framework import status
from decimal import Decimal
from datetime import date, timedelta

from .models import (
    Course, SummerTraining, PublicService,
    CourseEnrollment, SummerTrainingApplication, PublicServiceRequest
)

User = get_user_model()


class CourseModelTest(TestCase):
    """Test cases for Course model"""

    def setUp(self):
        """Set up test data"""
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='testpass123',
            first_name='Admin',
            last_name='User',
            role='admin'
        )

        self.course = Course.objects.create(
            title='Test Course',
            description='Test course description',
            course_code='TEST101',
            credits=3,
            duration_hours=40,
            instructor=self.admin_user,
            start_date=date.today() + timedelta(days=30),
            end_date=date.today() + timedelta(days=60),
            registration_deadline=date.today() + timedelta(days=20),
            max_participants=30,
            min_participants=5,
            price=Decimal('100.00')
        )

    def test_course_creation(self):
        """Test course creation"""
        self.assertEqual(self.course.title, 'Test Course')
        self.assertEqual(self.course.course_code, 'TEST101')
        self.assertEqual(self.course.credits, 3)
        self.assertEqual(self.course.instructor, self.admin_user)
        self.assertEqual(str(self.course), 'TEST101 - Test Course')

    def test_course_validation(self):
        """Test course validation"""
        # Test invalid date range
        course = Course(
            title='Invalid Course',
            course_code='INVALID',
            start_date=date.today() + timedelta(days=60),
            end_date=date.today() + timedelta(days=30),  # End before start
            registration_deadline=date.today() + timedelta(days=20)
        )

        with self.assertRaises(ValidationError):
            course.clean()

    def test_enrollment_percentage(self):
        """Test enrollment percentage calculation"""
        self.course.current_enrollment = 15
        self.course.save()
        self.assertEqual(self.course.enrollment_percentage, 50.0)

    def test_can_register(self):
        """Test registration availability"""
        self.course.status = 'published'
        self.course.save()
        self.assertTrue(self.course.can_register())

        # Test when full
        self.course.current_enrollment = 30
        self.course.save()
        self.assertFalse(self.course.can_register())

    def test_is_registration_open(self):
        """Test registration deadline check"""
        self.course.status = 'published'
        self.course.save()
        self.assertTrue(self.course.is_registration_open)

        # Test past deadline
        self.course.registration_deadline = date.today() - timedelta(days=1)
        self.course.save()
        self.assertFalse(self.course.is_registration_open)


class SummerTrainingModelTest(TestCase):
    """Test cases for SummerTraining model"""

    def setUp(self):
        """Set up test data"""
        self.supervisor = User.objects.create_user(
            username='supervisor',
            email='supervisor@test.com',
            password='testpass123',
            first_name='Supervisor',
            last_name='User',
            role='moderator'
        )

        self.program = SummerTraining.objects.create(
            title='Test Summer Program',
            description='Test program description',
            program_code='SP2024-01',
            duration_weeks=8,
            hours_per_week=40,
            supervisor=self.supervisor,
            start_date=date.today() + timedelta(days=60),
            end_date=date.today() + timedelta(days=116),
            application_deadline=date.today() + timedelta(days=30),
            max_trainees=10,
            min_trainees=3,
            academic_requirements='Minimum GPA 3.0',
            learning_objectives='Learn research skills',
            is_paid=True,
            stipend_amount=Decimal('500.00')
        )

    def test_summer_training_creation(self):
        """Test summer training creation"""
        self.assertEqual(self.program.title, 'Test Summer Program')
        self.assertEqual(self.program.program_code, 'SP2024-01')
        self.assertEqual(self.program.duration_weeks, 8)
        self.assertEqual(self.program.supervisor, self.supervisor)
        self.assertEqual(str(self.program), 'SP2024-01 - Test Summer Program')

    def test_total_hours_calculation(self):
        """Test total hours calculation"""
        self.assertEqual(self.program.total_hours, 320)  # 8 weeks * 40 hours

    def test_can_apply(self):
        """Test application availability"""
        self.program.status = 'published'
        self.program.save()
        self.assertTrue(self.program.can_apply())

        # Test when full
        self.program.current_enrollment = 10
        self.program.save()
        self.assertFalse(self.program.can_apply())


class PublicServiceModelTest(TestCase):
    """Test cases for PublicService model"""

    def setUp(self):
        """Set up test data"""
        self.coordinator = User.objects.create_user(
            username='coordinator',
            email='coordinator@test.com',
            password='testpass123',
            first_name='Coordinator',
            last_name='User',
            role='admin'
        )

        self.service = PublicService.objects.create(
            title='Test Service',
            description='Test service description',
            service_code='PS2024-01',
            service_category='consultation',
            coordinator=self.coordinator,
            is_ongoing=True,
            max_concurrent_requests=5,
            is_free=True,
            process_description='Contact us for consultation'
        )

    def test_public_service_creation(self):
        """Test public service creation"""
        self.assertEqual(self.service.title, 'Test Service')
        self.assertEqual(self.service.service_code, 'PS2024-01')
        self.assertEqual(self.service.service_category, 'consultation')
        self.assertEqual(self.service.coordinator, self.coordinator)
        self.assertEqual(str(self.service), 'PS2024-01 - Test Service')

    def test_is_available(self):
        """Test service availability"""
        self.service.status = 'published'
        self.service.save()
        self.assertTrue(self.service.is_available)

        # Test non-ongoing service
        self.service.is_ongoing = False
        self.service.start_date = date.today()
        self.service.end_date = date.today() + timedelta(days=30)
        self.service.save()
        self.assertTrue(self.service.is_available)

    def test_can_request(self):
        """Test request availability"""
        self.service.status = 'published'
        self.service.save()
        self.assertTrue(self.service.can_request())

        # Test at capacity
        self.service.current_requests = 5
        self.service.save()
        self.assertFalse(self.service.can_request())


class CourseAPITest(APITestCase):
    """Test cases for Course API"""

    def setUp(self):
        """Set up test data"""
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='testpass123',
            first_name='Admin',
            last_name='User',
            role='admin'
        )

        self.researcher_user = User.objects.create_user(
            username='researcher',
            email='researcher@test.com',
            password='testpass123',
            first_name='Researcher',
            last_name='User',
            role='researcher'
        )

        self.course = Course.objects.create(
            title='Test Course',
            description='Test course description',
            course_code='TEST101',
            credits=3,
            duration_hours=40,
            instructor=self.admin_user,
            start_date=date.today() + timedelta(days=30),
            end_date=date.today() + timedelta(days=60),
            registration_deadline=date.today() + timedelta(days=20),
            max_participants=30,
            min_participants=5,
            price=Decimal('100.00'),
            status='published'
        )

    def test_course_list_unauthenticated(self):
        """Test course list access without authentication"""
        url = '/api/training/api/courses/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_course_list_authenticated(self):
        """Test course list access with authentication"""
        self.client.force_authenticate(user=self.researcher_user)
        url = '/api/training/api/courses/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_course_detail(self):
        """Test course detail view"""
        self.client.force_authenticate(user=self.researcher_user)
        url = f'/api/training/api/courses/{self.course.id}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Course')

    def test_course_enrollment(self):
        """Test course enrollment"""
        self.client.force_authenticate(user=self.researcher_user)
        url = f'/api/training/api/courses/{self.course.id}/enroll/'
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Check enrollment was created
        enrollment = CourseEnrollment.objects.get(
            course=self.course,
            student=self.researcher_user
        )
        self.assertEqual(enrollment.status, 'pending')

    def test_duplicate_enrollment(self):
        """Test duplicate enrollment prevention"""
        # Create initial enrollment
        CourseEnrollment.objects.create(
            course=self.course,
            student=self.researcher_user
        )

        self.client.force_authenticate(user=self.researcher_user)
        url = f'/api/training/api/courses/{self.course.id}/enroll/'
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_course_creation_admin_only(self):
        """Test course creation requires admin permissions"""
        self.client.force_authenticate(user=self.researcher_user)
        url = '/api/training/api/courses/'
        data = {
            'title': 'New Course',
            'course_code': 'NEW101',
            'start_date': date.today() + timedelta(days=30),
            'end_date': date.today() + timedelta(days=60),
            'registration_deadline': date.today() + timedelta(days=20)
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class SummerTrainingAPITest(APITestCase):
    """Test cases for Summer Training API"""

    def setUp(self):
        """Set up test data"""
        self.supervisor = User.objects.create_user(
            username='supervisor',
            email='supervisor@test.com',
            password='testpass123',
            first_name='Supervisor',
            last_name='User',
            role='moderator'
        )

        self.researcher_user = User.objects.create_user(
            username='researcher',
            email='researcher@test.com',
            password='testpass123',
            first_name='Researcher',
            last_name='User',
            role='researcher'
        )

        self.program = SummerTraining.objects.create(
            title='Test Summer Program',
            description='Test program description',
            program_code='SP2024-01',
            duration_weeks=8,
            hours_per_week=40,
            supervisor=self.supervisor,
            start_date=date.today() + timedelta(days=60),
            end_date=date.today() + timedelta(days=116),
            application_deadline=date.today() + timedelta(days=30),
            max_trainees=10,
            min_trainees=3,
            academic_requirements='Minimum GPA 3.0',
            learning_objectives='Learn research skills',
            status='published'
        )

    def test_summer_training_list(self):
        """Test summer training list"""
        self.client.force_authenticate(user=self.researcher_user)
        url = '/api/training/api/summer-training/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_summer_training_application(self):
        """Test summer training application"""
        self.client.force_authenticate(user=self.researcher_user)
        url = f'/api/training/api/summer-training/{self.program.id}/apply/'
        data = {
            'university': 'Test University',
            'major': 'Computer Science',
            'year_of_study': 'junior',
            'gpa': 3.5,
            'motivation_letter': 'I want to learn research skills',
            'skills_and_interests': 'Programming, AI, Machine Learning'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Check application was created
        application = SummerTrainingApplication.objects.get(
            program=self.program,
            applicant=self.researcher_user
        )
        self.assertEqual(application.status, 'submitted')


class PublicServiceAPITest(APITestCase):
    """Test cases for Public Service API"""

    def setUp(self):
        """Set up test data"""
        self.coordinator = User.objects.create_user(
            username='coordinator',
            email='coordinator@test.com',
            password='testpass123',
            first_name='Coordinator',
            last_name='User',
            role='admin'
        )

        self.researcher_user = User.objects.create_user(
            username='researcher',
            email='researcher@test.com',
            password='testpass123',
            first_name='Researcher',
            last_name='User',
            role='researcher'
        )

        self.service = PublicService.objects.create(
            title='Test Service',
            description='Test service description',
            service_code='PS2024-01',
            service_category='consultation',
            coordinator=self.coordinator,
            is_ongoing=True,
            max_concurrent_requests=5,
            is_free=True,
            process_description='Contact us for consultation',
            status='published'
        )

    def test_public_service_list(self):
        """Test public service list"""
        self.client.force_authenticate(user=self.researcher_user)
        url = '/api/training/api/public-services/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_service_request(self):
        """Test service request creation"""
        self.client.force_authenticate(user=self.researcher_user)
        url = f'/api/training/api/public-services/{self.service.id}/request_service/'
        data = {
            'request_description': 'I need consultation on my research',
            'urgency_level': 'medium',
            'contact_person': 'John Doe',
            'contact_email': 'john@example.com',
            'organization': 'Test University'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Check request was created
        service_request = PublicServiceRequest.objects.get(
            service=self.service,
            requester=self.researcher_user
        )
        self.assertEqual(service_request.status, 'submitted')

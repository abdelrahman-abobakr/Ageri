import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User
from .permissions import IsAdminOrReadOnly, IsModeratorOrAdmin

User = get_user_model()


@pytest.mark.django_db
class UserModelTest(TestCase):
    """Test cases for User model"""

    def test_user_creation(self):
        """Test basic user creation"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User',
            role='researcher'
        )

        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.first_name, 'Test')
        self.assertEqual(user.last_name, 'User')
        self.assertEqual(user.role, 'researcher')
        self.assertFalse(user.is_approved)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertTrue(user.check_password('testpass123'))

    def test_admin_user_creation(self):
        """Test admin user creation"""
        admin = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='adminpass123',
            role='admin',
            is_approved=True
        )

        self.assertEqual(admin.role, 'admin')
        self.assertTrue(admin.is_approved)
        self.assertTrue(admin.is_staff)  # Admins should be staff
        self.assertFalse(admin.is_superuser)

    def test_superuser_creation(self):
        """Test superuser creation"""
        superuser = User.objects.create_superuser(
            username='superuser',
            email='super@example.com',
            password='superpass123'
        )

        self.assertTrue(superuser.is_superuser)
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_approved)
        self.assertEqual(superuser.role, 'admin')

    def test_unique_email_constraint(self):
        """Test that email must be unique"""
        User.objects.create_user(
            username='user1',
            email='test@example.com',
            password='pass123'
        )

        with self.assertRaises(IntegrityError):
            User.objects.create_user(
                username='user2',
                email='test@example.com',  # Same email
                password='pass123'
            )

    def test_unique_username_constraint(self):
        """Test that username must be unique"""
        User.objects.create_user(
            username='testuser',
            email='test1@example.com',
            password='pass123'
        )

        with self.assertRaises(IntegrityError):
            User.objects.create_user(
                username='testuser',  # Same username
                email='test2@example.com',
                password='pass123'
            )

    def test_user_string_representation(self):
        """Test user string representation"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            first_name='Test',
            last_name='User'
        )

        self.assertEqual(str(user), 'Test User (test@example.com)')

    def test_user_full_name_property(self):
        """Test user full name property"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            first_name='Test',
            last_name='User'
        )

        self.assertEqual(user.get_full_name(), 'Test User')

    def test_role_choices_validation(self):
        """Test role choices validation"""
        # Valid role
        user = User(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            role='researcher'
        )
        user.full_clean()  # Should not raise

        # Invalid role
        user_invalid = User(
            username='testuser2',
            email='test2@example.com',
            password='testpass123',
            role='invalid_role'
        )
        with self.assertRaises(ValidationError):
            user_invalid.full_clean()

    def test_is_staff_property_for_admin(self):
        """Test that admin users automatically get is_staff=True"""
        admin = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='pass123',
            role='admin'
        )

        self.assertTrue(admin.is_staff)

    def test_is_staff_property_for_non_admin(self):
        """Test that non-admin users don't automatically get is_staff=True"""
        researcher = User.objects.create_user(
            username='researcher',
            email='researcher@example.com',
            password='pass123',
            role='researcher'
        )

        moderator = User.objects.create_user(
            username='moderator',
            email='moderator@example.com',
            password='pass123',
            role='moderator'
        )

        self.assertFalse(researcher.is_staff)
        self.assertFalse(moderator.is_staff)


@pytest.mark.django_db
class AuthenticationAPITest(APITestCase):
    """Test cases for Authentication API endpoints"""

    def setUp(self):
        """Set up test data"""
        self.client_api = APIClient()

        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123',
            'password_confirm': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User',
            'institution': 'Test University'
        }

        self.approved_user = User.objects.create_user(
            username='approved',
            email='approved@example.com',
            password='testpass123',
            role='researcher',
            is_approved=True
        )

        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='adminpass123',
            role='admin',
            is_approved=True
        )

    def test_user_registration(self):
        """Test user registration endpoint"""
        url = '/api/auth/register/'
        response = self.client_api.post(url, self.user_data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Check if user data is in the response
        if 'user' in response.data:
            user_data = response.data['user']
            self.assertEqual(user_data['username'], 'testuser')
            self.assertEqual(user_data['email'], 'test@example.com')
            self.assertFalse(user_data['is_approved'])
        else:
            self.assertEqual(response.data['username'], 'testuser')
            self.assertEqual(response.data['email'], 'test@example.com')
            self.assertFalse(response.data['is_approved'])

        # Verify user was created in database
        user = User.objects.get(username='testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertFalse(user.is_approved)

    def test_user_registration_duplicate_email(self):
        """Test registration with duplicate email"""
        # Create first user
        User.objects.create_user(
            username='existing',
            email='test@example.com',
            password='pass123'
        )

        url = '/api/auth/register/'
        response = self.client_api.post(url, self.user_data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_login_approved(self):
        """Test login with approved user"""
        url = '/api/auth/login/'
        data = {
            'email': 'approved@example.com',
            'password': 'testpass123'
        }
        response = self.client_api.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('user', response.data)

    def test_user_login_unapproved(self):
        """Test login with unapproved user"""
        unapproved_user = User.objects.create_user(
            username='unapproved',
            email='unapproved@example.com',
            password='testpass123',
            role='researcher',
            is_approved=False
        )

        url = '/api/auth/login/'
        data = {
            'email': 'unapproved@example.com',
            'password': 'testpass123'
        }
        response = self.client_api.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Check if the error message is in any of the response fields
        response_str = str(response.data).lower()
        self.assertIn('not approved', response_str)

    def test_user_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        url = '/api/auth/login/'
        data = {
            'email': 'approved@example.com',
            'password': 'wrongpassword'
        }
        response = self.client_api.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_token_refresh(self):
        """Test token refresh endpoint"""
        # Get initial tokens
        refresh = RefreshToken.for_user(self.approved_user)

        url = '/api/auth/token/refresh/'
        data = {'refresh': str(refresh)}
        response = self.client_api.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    def test_current_user_profile(self):
        """Test getting current user profile"""
        self.client_api.force_authenticate(user=self.approved_user)

        url = '/api/auth/users/me/'
        response = self.client_api.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'approved')
        self.assertEqual(response.data['email'], 'approved@example.com')

    def test_update_user_profile(self):
        """Test updating user profile"""
        self.client_api.force_authenticate(user=self.approved_user)

        url = '/api/auth/users/me/'
        data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'institution': 'New University',
            'phone': '123-456-7890'
        }
        response = self.client_api.put(url, data)

        if response.status_code != status.HTTP_200_OK:
            print(f"Profile update error: {response.data}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], 'Updated')
        self.assertEqual(response.data['last_name'], 'Name')

        # Verify in database
        self.approved_user.refresh_from_db()
        self.assertEqual(self.approved_user.first_name, 'Updated')

    def test_users_list_admin_only(self):
        """Test that only admins can list all users"""
        # Create some users
        User.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='pass123',
            role='researcher'
        )

        url = '/api/auth/users/'

        # Test with regular user (should fail)
        self.client_api.force_authenticate(user=self.approved_user)
        response = self.client_api.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Test with admin (should succeed)
        self.client_api.force_authenticate(user=self.admin_user)
        response = self.client_api.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)

    def test_user_approval_admin_only(self):
        """Test user approval endpoint (admin only)"""
        unapproved_user = User.objects.create_user(
            username='unapproved',
            email='unapproved@example.com',
            password='pass123',
            role='researcher',
            is_approved=False
        )

        url = f'/api/auth/users/{unapproved_user.id}/approve/'
        data = {'approved': True}

        # Test with regular user (should fail)
        self.client_api.force_authenticate(user=self.approved_user)
        response = self.client_api.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Test with admin (should succeed)
        self.client_api.force_authenticate(user=self.admin_user)
        response = self.client_api.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify approval
        unapproved_user.refresh_from_db()
        self.assertTrue(unapproved_user.is_approved)

    def test_logout_endpoint(self):
        """Test logout endpoint"""
        self.client_api.force_authenticate(user=self.approved_user)

        url = '/api/auth/logout/'
        response = self.client_api.post(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)


@pytest.mark.django_db
class PermissionsTest(TestCase):
    """Test cases for custom permissions"""

    def setUp(self):
        """Set up test data"""
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='pass123',
            role='admin',
            is_approved=True
        )

        self.moderator_user = User.objects.create_user(
            username='moderator',
            email='moderator@example.com',
            password='pass123',
            role='moderator',
            is_approved=True
        )

        self.researcher_user = User.objects.create_user(
            username='researcher',
            email='researcher@example.com',
            password='pass123',
            role='researcher',
            is_approved=True
        )

    def test_is_admin_or_read_only_permission(self):
        """Test IsAdminOrReadOnly permission"""
        permission = IsAdminOrReadOnly()

        # Mock request objects
        class MockRequest:
            def __init__(self, method, user):
                self.method = method
                self.user = user

        # Test GET request (should allow all authenticated users)
        get_request = MockRequest('GET', self.researcher_user)
        self.assertTrue(permission.has_permission(get_request, None))

        # Test POST request with admin (should allow)
        post_request_admin = MockRequest('POST', self.admin_user)
        self.assertTrue(permission.has_permission(post_request_admin, None))

        # Test POST request with researcher (should deny)
        post_request_researcher = MockRequest('POST', self.researcher_user)
        self.assertFalse(permission.has_permission(post_request_researcher, None))

    def test_is_moderator_or_admin_permission(self):
        """Test IsModeratorOrAdmin permission"""
        permission = IsModeratorOrAdmin()

        class MockRequest:
            def __init__(self, method, user):
                self.method = method
                self.user = user

        # Test with admin
        request_admin = MockRequest('POST', self.admin_user)
        self.assertTrue(permission.has_permission(request_admin, None))

        # Test with moderator
        request_moderator = MockRequest('POST', self.moderator_user)
        self.assertTrue(permission.has_permission(request_moderator, None))

        # Test with researcher
        request_researcher = MockRequest('POST', self.researcher_user)
        self.assertFalse(permission.has_permission(request_researcher, None))

    def test_unapproved_user_permissions(self):
        """Test that unapproved users are denied access"""
        unapproved_user = User.objects.create_user(
            username='unapproved',
            email='unapproved@example.com',
            password='pass123',
            role='researcher',
            is_approved=False
        )

        permission = IsAdminOrReadOnly()

        class MockRequest:
            def __init__(self, method, user):
                self.method = method
                self.user = user

        request = MockRequest('GET', unapproved_user)
        self.assertFalse(permission.has_permission(request, None))

"""
Pytest configuration file for the research platform project.
"""

import pytest
import os
import django
from django.conf import settings
from django.test.utils import get_runner

# Configure Django settings before importing models
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'research_platform.test_settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.fixture(scope='session')
def django_db_setup():
    """
    Configure the test database.
    """
    settings.DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }


@pytest.fixture
def admin_user(db):
    """Create an admin user for testing."""
    return User.objects.create_user(
        username='admin_test',
        email='admin@test.com',
        password='testpass123',
        role='admin',
        is_approved=True,
        first_name='Admin',
        last_name='User'
    )


@pytest.fixture
def moderator_user(db):
    """Create a moderator user for testing."""
    return User.objects.create_user(
        username='moderator_test',
        email='moderator@test.com',
        password='testpass123',
        role='moderator',
        is_approved=True,
        first_name='Moderator',
        last_name='User'
    )


@pytest.fixture
def researcher_user(db):
    """Create a researcher user for testing."""
    return User.objects.create_user(
        username='researcher_test',
        email='researcher@test.com',
        password='testpass123',
        role='researcher',
        is_approved=True,
        first_name='Researcher',
        last_name='User'
    )


@pytest.fixture
def unapproved_user(db):
    """Create an unapproved user for testing."""
    return User.objects.create_user(
        username='unapproved_test',
        email='unapproved@test.com',
        password='testpass123',
        role='researcher',
        is_approved=False,
        first_name='Unapproved',
        last_name='User'
    )


@pytest.fixture
def api_client():
    """Create an API client for testing."""
    from rest_framework.test import APIClient
    return APIClient()


@pytest.fixture
def authenticated_client(api_client, researcher_user):
    """Create an authenticated API client."""
    api_client.force_authenticate(user=researcher_user)
    return api_client


@pytest.fixture
def admin_client(api_client, admin_user):
    """Create an admin authenticated API client."""
    api_client.force_authenticate(user=admin_user)
    return api_client


@pytest.fixture
def moderator_client(api_client, moderator_user):
    """Create a moderator authenticated API client."""
    api_client.force_authenticate(user=moderator_user)
    return api_client


@pytest.fixture
def sample_department(db):
    """Create a sample department for testing."""
    from organization.models import Department
    return Department.objects.create(
        name='Test Department',
        description='Test department for testing'
    )


@pytest.fixture
def sample_lab(db, sample_department):
    """Create a sample lab for testing."""
    from organization.models import Lab
    return Lab.objects.create(
        name='Test Lab',
        department=sample_department,
        description='Test lab for testing'
    )


@pytest.fixture
def sample_service(db, sample_department):
    """Create a sample test service for testing."""
    from services.models import TestService
    from decimal import Decimal
    return TestService.objects.create(
        name='Sample Test Service',
        service_code='STS-001',
        description='Sample test service for testing',
        category='testing',
        department=sample_department,
        base_price=Decimal('100.00'),
        max_concurrent_requests=5
    )


@pytest.fixture
def sample_client(db):
    """Create a sample client for testing."""
    from services.models import Client
    return Client.objects.create(
        name='Sample Client',
        email='client@test.com',
        phone='123-456-7890',
        organization='Test Organization'
    )


@pytest.fixture
def sample_publication(db, researcher_user):
    """Create a sample publication for testing."""
    from research.models import Publication
    return Publication.objects.create(
        title='Sample Publication',
        abstract='This is a sample publication for testing purposes.',
        corresponding_author=researcher_user,
        journal='Test Journal',
        status='draft'
    )


@pytest.fixture
def sample_announcement(db, moderator_user):
    """Create a sample announcement for testing."""
    from content.models import Announcement
    return Announcement.objects.create(
        title='Sample Announcement',
        content='This is a sample announcement for testing.',
        author=moderator_user,
        status='published',
        target_audience='all'
    )


@pytest.fixture
def sample_course(db, moderator_user, sample_department):
    """Create a sample course for testing."""
    from training.models import Course
    from datetime import date, timedelta
    from decimal import Decimal
    
    return Course.objects.create(
        title='Sample Course',
        description='Sample course for testing',
        course_code='SC-001',
        instructor=moderator_user,
        department=sample_department,
        duration_weeks=4,
        max_participants=20,
        start_date=date.today() + timedelta(days=30),
        end_date=date.today() + timedelta(days=58),
        enrollment_deadline=date.today() + timedelta(days=15),
        fee=Decimal('100.00')
    )


# Pytest markers for different test categories
pytest_plugins = []

def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "api: mark test as an API test"
    )
    config.addinivalue_line(
        "markers", "models: mark test as a model test"
    )
    config.addinivalue_line(
        "markers", "views: mark test as a view test"
    )
    config.addinivalue_line(
        "markers", "permissions: mark test as a permissions test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )

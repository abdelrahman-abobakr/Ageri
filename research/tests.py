import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from datetime import date

from .models import Publication, PublicationAuthor, PublicationMetrics
from organization.models import Department

User = get_user_model()


@pytest.mark.django_db
class PublicationModelTest(TestCase):
    """Test cases for Publication model"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='researcher',
            email='researcher@test.com',
            password='testpass123',
            role='researcher',
            is_approved=True
        )

    def test_publication_creation(self):
        """Test Publication model creation"""
        publication = Publication.objects.create(
            title='Test Publication',
            abstract='This is a test publication abstract.',
            corresponding_author=self.user,
            submitted_by=self.user,
            journal_name='Test Journal',
            status='draft'
        )

        self.assertEqual(publication.title, 'Test Publication')
        self.assertEqual(publication.corresponding_author, self.user)
        self.assertEqual(publication.journal_name, 'Test Journal')
        self.assertEqual(publication.status, 'draft')
        self.assertEqual(str(publication), 'Test Publication')

    def test_publication_with_authors(self):
        """Test publication with multiple authors"""
        author2 = User.objects.create_user(
            username='author2',
            email='author2@test.com',
            password='testpass123',
            role='researcher'
        )

        publication = Publication.objects.create(
            title='Multi-Author Publication',
            abstract='Publication with multiple authors.',
            corresponding_author=self.user,
            submitted_by=self.user,
            journal_name='Multi Journal',
            status='published'
        )

        publication.authors.add(self.user, author2)

        self.assertEqual(publication.authors.count(), 2)
        self.assertIn(self.user, publication.authors.all())
        self.assertIn(author2, publication.authors.all())

    def test_publication_status_choices(self):
        """Test publication status validation"""
        publication = Publication(
            title='Status Test',
            abstract='Testing status choices',
            corresponding_author=self.user,
            submitted_by=self.user,
            journal_name='Status Journal',
            status='invalid_status'
        )

        with self.assertRaises(ValidationError):
            publication.full_clean()





@pytest.mark.django_db
class ResearchAPITest(APITestCase):
    """Test cases for Research API endpoints"""

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
            description='Test department'
        )

        self.publication = Publication.objects.create(
            title='Test Publication',
            abstract='Test abstract',
            corresponding_author=self.researcher_user,
            submitted_by=self.researcher_user,
            journal_name='Test Journal',
            status='published'
        )

    def test_publications_list_authenticated(self):
        """Test accessing publications list with authentication"""
        self.client_api.force_authenticate(user=self.researcher_user)
        url = '/api/research/publications/'
        response = self.client_api.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)

    def test_create_publication_authenticated(self):
        """Test creating publication as authenticated user"""
        self.client_api.force_authenticate(user=self.researcher_user)
        url = '/api/research/publications/'
        data = {
            'title': 'New Publication',
            'abstract': 'New publication abstract',
            'journal_name': 'New Journal',
            'status': 'draft'
        }
        response = self.client_api.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'New Publication')



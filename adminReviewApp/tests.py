from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from research.models import Publication

User = get_user_model()


class AdminReviewAPITestCase(APITestCase):
    """Test cases for admin review functionality"""
    
    def setUp(self):
        # Create admin user
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='testpass123',
            role='admin'  # Assuming role field exists
        )
        
        # Create researcher user
        self.researcher_user = User.objects.create_user(
            username='researcher',
            email='researcher@test.com',
            password='testpass123',
            role='researcher'
        )
        
        # Create test publication
        self.publication = Publication.objects.create(
            title='Test Publication',
            abstract='Test abstract',
            status='pending',
            submitted_by=self.researcher_user
        )
    
    def test_pending_publications_list(self):
        """Test listing pending publications"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('admin_review:admin-review-pending')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_approve_publication(self):
        """Test approving a publication"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('admin_review:admin-review-approve', kwargs={'pk': self.publication.pk})
        
        data = {'review_notes': 'Approved after review'}
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.publication.refresh_from_db()
        self.assertEqual(self.publication.status, 'approved')
        self.assertEqual(self.publication.reviewed_by, self.admin_user)
    
    def test_reject_publication(self):
        """Test rejecting a publication"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('admin_review:admin-review-reject', kwargs={'pk': self.publication.pk})
        
        data = {'review_notes': 'Rejected due to quality issues'}
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.publication.refresh_from_db()
        self.assertEqual(self.publication.status, 'rejected')
    
    def test_publish_approved_publication(self):
        """Test publishing an approved publication"""
        # First approve the publication
        self.publication.status = 'approved'
        self.publication.save()
        
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('admin_review:admin-review-publish', kwargs={'pk': self.publication.pk})
        
        data = {'is_featured': True, 'priority': 5}
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.publication.refresh_from_db()
        self.assertEqual(self.publication.status, 'published')
        self.assertTrue(self.publication.is_public)
        self.assertTrue(self.publication.is_featured)
    
    def test_non_admin_access_denied(self):
        """Test that non-admin users cannot access admin endpoints"""
        self.client.force_authenticate(user=self.researcher_user)
        url = reverse('admin_review:admin-review-pending')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
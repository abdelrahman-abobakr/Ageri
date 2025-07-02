from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Announcement, Post, Comment, CommentLike

User = get_user_model()


class ContentModelTests(TestCase):
    """Test cases for content models"""

    def setUp(self):
        """Set up test data"""
        self.admin_user = User.objects.create_user(
            username='admin_user',
            email='admin@test.com',
            password='testpass123',
            first_name='Admin',
            last_name='User',
            role='admin',
            is_approved=True
        )

        self.moderator_user = User.objects.create_user(
            username='moderator_user',
            email='moderator@test.com',
            password='testpass123',
            first_name='Moderator',
            last_name='User',
            role='moderator',
            is_approved=True
        )

        self.researcher_user = User.objects.create_user(
            username='researcher_user',
            email='researcher@test.com',
            password='testpass123',
            first_name='Researcher',
            last_name='User',
            role='researcher',
            is_approved=True
        )

    def test_announcement_creation(self):
        """Test announcement model creation"""
        announcement = Announcement.objects.create(
            title='Test Announcement',
            content='This is a test announcement content.',
            summary='Test summary',
            announcement_type='general',
            priority='medium',
            target_audience='all',
            author=self.moderator_user,
            publish_at=timezone.now()
        )

        self.assertEqual(announcement.title, 'Test Announcement')
        self.assertEqual(announcement.author, self.moderator_user)
        self.assertEqual(announcement.status, 'draft')
        self.assertFalse(announcement.is_published)
        self.assertFalse(announcement.is_expired)

    def test_post_creation(self):
        """Test post model creation"""
        post = Post.objects.create(
            title='Test Post',
            content='This is a test post content.',
            excerpt='Test excerpt',
            category='news',
            author=self.moderator_user,
            publish_at=timezone.now()
        )

        self.assertEqual(post.title, 'Test Post')
        self.assertEqual(post.author, self.moderator_user)
        self.assertEqual(post.status, 'draft')
        self.assertFalse(post.is_published)
        self.assertFalse(post.is_event)

    def test_comment_creation(self):
        """Test comment model creation"""
        post = Post.objects.create(
            title='Test Post',
            content='Test content',
            author=self.moderator_user
        )

        comment = Comment.objects.create(
            content='This is a test comment.',
            author=self.researcher_user,
            content_object=post
        )

        self.assertEqual(comment.content, 'This is a test comment.')
        self.assertEqual(comment.author, self.researcher_user)
        self.assertEqual(comment.content_object, post)
        self.assertFalse(comment.is_approved)


    def test_comment_like_creation(self):
        """Test comment like creation"""
        post = Post.objects.create(
            title='Test Post',
            content='Test content',
            author=self.moderator_user
        )

        comment = Comment.objects.create(
            content='Test comment',
            author=self.researcher_user,
            content_object=post
        )

        like = CommentLike.objects.create(
            comment=comment,
            user=self.admin_user
        )

        self.assertEqual(like.comment, comment)
        self.assertEqual(like.user, self.admin_user)

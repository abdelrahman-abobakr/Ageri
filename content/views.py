from django.shortcuts import render, get_object_or_404
from django.db.models import Q, Count
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from accounts.permissions import IsAdminOrReadOnly, IsOwnerOrReadOnly, IsModeratorOrAdmin, IsApprovedUser
from .models import Announcement, Post, Comment, CommentLike, AnnouncementImage, AnnouncementAttachment
from .serializers import (
    AnnouncementListSerializer, AnnouncementDetailSerializer,
    AnnouncementCreateUpdateSerializer, AnnouncementApprovalSerializer,
    PostListSerializer, PostDetailSerializer, PostCreateUpdateSerializer,
    PostApprovalSerializer, CommentSerializer, CommentCreateSerializer,
    CommentLikeSerializer, AnnouncementImageSerializer, AnnouncementAttachmentSerializer
)


class AnnouncementViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing announcements
    """
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = [
        'announcement_type', 'priority', 'target_audience', 'status',
        'is_pinned', 'is_featured'
    ]
    search_fields = ['title', 'content', 'summary']
    ordering_fields = ['priority', 'publish_at', 'created_at', 'view_count']
    ordering = ['-is_pinned', '-priority', '-publish_at']

    def get_queryset(self):
        """Get queryset based on user permissions"""
        user = self.request.user

        queryset = Announcement.objects.select_related('author', 'approved_by')

        # Handle anonymous users
        if not user.is_authenticated:
            return queryset.filter(status='published', target_audience='all')

        if user.is_admin:
            return queryset
        elif user.is_moderator:
            # Moderators see published announcements and their own
            return queryset.filter(
                Q(status='published') | Q(author=user)
            )
        else:
            # Regular users see only published announcements they can view
            published_announcements = queryset.filter(status='published')
            return published_announcements.filter(
                Q(target_audience='all') |
                Q(target_audience='approved', **{'author__is_approved': True}) |
                Q(target_audience='researchers') |
                Q(target_audience='moderators', **{'author__role__in': ['moderator', 'admin']}) |
                Q(target_audience='admins', **{'author__role': 'admin'})
            )

    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'list':
            return AnnouncementListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return AnnouncementCreateUpdateSerializer
        elif self.action == 'approve':
            return AnnouncementApprovalSerializer
        else:
            return AnnouncementDetailSerializer

    def get_permissions(self):
        """Get permissions based on action"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsModeratorOrAdmin()]
        elif self.action == 'approve':
            return [IsAdminOrReadOnly()]
        else:
            return [IsApprovedUser()]

    def perform_create(self, serializer):
        """Set author when creating announcement"""
        serializer.save(author=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        """Retrieve announcement and increment view count"""
        instance = self.get_object()

        # Check if user can view this announcement
        if not instance.can_be_viewed_by(request.user):
            return Response(
                {'error': 'You do not have permission to view this announcement'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Increment view count
        instance.increment_view_count()

        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsAdminOrReadOnly])
    def approve(self, request, pk=None):
        """Approve or reject an announcement"""
        announcement = self.get_object()
        serializer = AnnouncementApprovalSerializer(
            announcement,
            data=request.data,
            context={'request': request}
        )

        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': f'Announcement {serializer.validated_data["status"]}',
                'announcement': AnnouncementDetailSerializer(
                    announcement, context={'request': request}
                ).data
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured announcements"""
        queryset = self.get_queryset().filter(is_featured=True, status='published')
        serializer = AnnouncementListSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def pinned(self, request):
        """Get pinned announcements"""
        queryset = self.get_queryset().filter(is_pinned=True, status='published')
        serializer = AnnouncementListSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def my_announcements(self, request):
        """Get current user's announcements"""
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Authentication required'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        queryset = self.get_queryset().filter(author=request.user)
        serializer = AnnouncementListSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[IsAdminOrReadOnly])
    def pending_review(self, request):
        """Get announcements pending review (admin only)"""
        queryset = self.get_queryset().filter(status='pending')
        serializer = AnnouncementListSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['get', 'post'], permission_classes=[IsModeratorOrAdmin])
    def images(self, request, pk=None):
        """Manage announcement images"""
        announcement = self.get_object()

        if request.method == 'GET':
            images = announcement.images.all()
            serializer = AnnouncementImageSerializer(images, many=True, context={'request': request})
            return Response(serializer.data)

        elif request.method == 'POST':
            serializer = AnnouncementImageSerializer(data=request.data, context={'request': request})
            if serializer.is_valid():
                serializer.save(announcement=announcement)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['delete'], permission_classes=[IsModeratorOrAdmin], url_path='images/(?P<image_id>[^/.]+)')
    def delete_image(self, request, pk=None, image_id=None):
        """Delete announcement image"""
        announcement = self.get_object()
        try:
            image = announcement.images.get(id=image_id)
            image.delete()
            return Response({'message': 'Image deleted successfully'})
        except AnnouncementImage.DoesNotExist:
            return Response({'error': 'Image not found'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['get', 'post'], permission_classes=[IsModeratorOrAdmin])
    def attachments(self, request, pk=None):
        """Manage announcement attachments"""
        announcement = self.get_object()

        if request.method == 'GET':
            attachments = announcement.attachments.all()
            serializer = AnnouncementAttachmentSerializer(attachments, many=True, context={'request': request})
            return Response(serializer.data)

        elif request.method == 'POST':
            serializer = AnnouncementAttachmentSerializer(data=request.data, context={'request': request})
            if serializer.is_valid():
                serializer.save(announcement=announcement)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['delete'], permission_classes=[IsModeratorOrAdmin], url_path='attachments/(?P<attachment_id>[^/.]+)')
    def delete_attachment(self, request, pk=None, attachment_id=None):
        """Delete announcement attachment"""
        announcement = self.get_object()
        try:
            attachment = announcement.attachments.get(id=attachment_id)
            attachment.delete()
            return Response({'message': 'Attachment deleted successfully'})
        except AnnouncementAttachment.DoesNotExist:
            return Response({'error': 'Attachment not found'}, status=status.HTTP_404_NOT_FOUND)


class PostViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing posts
    """
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = [
        'category', 'status', 'is_featured', 'is_public',
        'registration_required'
    ]
    search_fields = ['title', 'content', 'excerpt', 'tags', 'event_location']
    ordering_fields = ['publish_at', 'created_at', 'event_date', 'view_count', 'like_count']
    ordering = ['-is_featured', '-publish_at']

    def get_queryset(self):
        """Get queryset based on user permissions"""
        user = self.request.user

        queryset = Post.objects.select_related('author', 'approved_by')

        # Handle anonymous users
        if not user.is_authenticated:
            return queryset.filter(status='published', is_public=True)

        if user.is_admin:
            return queryset
        elif user.is_moderator:
            # Moderators see published posts and their own
            return queryset.filter(
                Q(status='published') | Q(author=user)
            )
        else:
            # Regular users see published posts they can view
            return queryset.filter(
                Q(status='published') &
                (Q(is_public=True) | Q(author=user))
            )

    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'list':
            return PostListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return PostCreateUpdateSerializer
        elif self.action == 'approve':
            return PostApprovalSerializer
        else:
            return PostDetailSerializer

    def get_permissions(self):
        """Get permissions based on action"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsModeratorOrAdmin()]
        elif self.action == 'approve':
            return [IsAdminOrReadOnly()]
        elif self.action in ['like', 'unlike']:
            return [IsApprovedUser()]
        else:
            return [permissions.AllowAny()]  # Public posts can be viewed by anyone

    def perform_create(self, serializer):
        """Set author when creating post"""
        serializer.save(author=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        """Retrieve post and increment view count"""
        instance = self.get_object()

        # Check if user can view this post
        if not instance.can_be_viewed_by(request.user):
            return Response(
                {'error': 'You do not have permission to view this post'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Increment view count
        instance.increment_view_count()

        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsAdminOrReadOnly])
    def approve(self, request, pk=None):
        """Approve or reject a post"""
        post = self.get_object()
        serializer = PostApprovalSerializer(
            post,
            data=request.data,
            context={'request': request}
        )

        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': f'Post {serializer.validated_data["status"]}',
                'post': PostDetailSerializer(
                    post, context={'request': request}
                ).data
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured posts"""
        queryset = self.get_queryset().filter(is_featured=True, status='published')
        serializer = PostListSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def events(self, request):
        """Get event posts"""
        queryset = self.get_queryset().filter(
            category__in=['event', 'workshop', 'seminar', 'conference', 'training'],
            status='published'
        ).order_by('event_date')
        serializer = PostListSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def upcoming_events(self, request):
        """Get upcoming events"""
        now = timezone.now()
        queryset = self.get_queryset().filter(
            category__in=['event', 'workshop', 'seminar', 'conference', 'training'],
            status='published',
            event_date__gt=now
        ).order_by('event_date')
        serializer = PostListSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def my_posts(self, request):
        """Get current user's posts"""
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Authentication required'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        queryset = self.get_queryset().filter(author=request.user)
        serializer = PostListSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[IsAdminOrReadOnly])
    def pending_review(self, request):
        """Get posts pending review (admin only)"""
        queryset = self.get_queryset().filter(status='pending')
        serializer = PostListSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)


class CommentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing comments
    """
    serializer_class = CommentSerializer
    permission_classes = [IsApprovedUser]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['content_type', 'object_id', 'is_approved', 'parent']
    ordering_fields = ['created_at', 'like_count']
    ordering = ['created_at']

    def get_queryset(self):
        """Get queryset based on user permissions"""
        user = self.request.user

        queryset = Comment.objects.select_related(
            'author', 'approved_by', 'content_type', 'parent'
        ).prefetch_related('replies')

        if user.is_admin or user.is_moderator:
            return queryset
        else:
            # Regular users see approved comments and their own
            return queryset.filter(
                Q(is_approved=True) | Q(author=user)
            )

    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action in ['create', 'update', 'partial_update']:
            return CommentCreateSerializer
        else:
            return CommentSerializer

    def perform_create(self, serializer):
        """Set author and content object when creating comment"""
        # Get content type and object from URL parameters or request data
        content_type_id = self.request.data.get('content_type')
        object_id = self.request.data.get('object_id')

        if content_type_id and object_id:
            content_type = get_object_or_404(ContentType, id=content_type_id)
            serializer.save(
                author=self.request.user,
                content_type=content_type,
                object_id=object_id
            )
        else:
            return Response(
                {'error': 'content_type and object_id are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'], permission_classes=[IsApprovedUser])
    def like(self, request, pk=None):
        """Like a comment"""
        comment = self.get_object()

        # Check if user already liked this comment
        like, created = CommentLike.objects.get_or_create(
            comment=comment,
            user=request.user
        )

        if created:
            comment.like_count += 1
            comment.save(update_fields=['like_count'])
            return Response({
                'message': 'Comment liked',
                'like_count': comment.like_count
            })
        else:
            return Response({
                'message': 'Comment already liked',
                'like_count': comment.like_count
            })

    @action(detail=True, methods=['post'], permission_classes=[IsApprovedUser])
    def unlike(self, request, pk=None):
        """Unlike a comment"""
        comment = self.get_object()

        try:
            like = CommentLike.objects.get(comment=comment, user=request.user)
            like.delete()
            comment.like_count = max(0, comment.like_count - 1)
            comment.save(update_fields=['like_count'])

            return Response({
                'message': 'Comment unliked',
                'like_count': comment.like_count
            })
        except CommentLike.DoesNotExist:
            return Response({
                'message': 'Comment not liked',
                'like_count': comment.like_count
            })

    @action(detail=True, methods=['post'], permission_classes=[IsModeratorOrAdmin])
    def approve(self, request, pk=None):
        """Approve a comment"""
        comment = self.get_object()
        comment.is_approved = True
        comment.approved_by = request.user
        comment.approved_at = timezone.now()
        comment.save()

        return Response({
            'message': 'Comment approved',
            'comment': CommentSerializer(comment, context={'request': request}).data
        })

    @action(detail=True, methods=['post'], permission_classes=[IsModeratorOrAdmin])
    def reject(self, request, pk=None):
        """Reject a comment"""
        comment = self.get_object()
        comment.is_approved = False
        comment.approved_by = request.user
        comment.approved_at = timezone.now()
        comment.save()

        return Response({
            'message': 'Comment rejected',
            'comment': CommentSerializer(comment, context={'request': request}).data
        })

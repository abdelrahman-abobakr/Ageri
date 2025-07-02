from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import Announcement, Post, Comment, CommentLike

User = get_user_model()


class AuthorSerializer(serializers.ModelSerializer):
    """Serializer for author information"""
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'full_name', 'email']


class AnnouncementListSerializer(serializers.ModelSerializer):
    """Serializer for announcement list view"""
    author = AuthorSerializer(read_only=True)
    is_published = serializers.BooleanField(read_only=True)
    is_expired = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Announcement
        fields = [
            'id', 'title', 'summary', 'announcement_type', 'priority',
            'target_audience', 'status', 'is_pinned', 'is_featured',
            'publish_at', 'expires_at', 'author', 'view_count',
            'is_published', 'is_expired', 'created_at'
        ]


class AnnouncementDetailSerializer(serializers.ModelSerializer):
    """Serializer for announcement detail view"""
    author = AuthorSerializer(read_only=True)
    approved_by = AuthorSerializer(read_only=True)
    is_published = serializers.BooleanField(read_only=True)
    is_expired = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Announcement
        fields = [
            'id', 'title', 'content', 'summary', 'announcement_type',
            'priority', 'target_audience', 'status', 'is_pinned',
            'is_featured', 'publish_at', 'expires_at', 'author',
            'approved_by', 'approved_at', 'attachment', 'view_count',
            'is_published', 'is_expired', 'created_at', 'updated_at'
        ]


class AnnouncementCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating announcements"""
    
    class Meta:
        model = Announcement
        fields = [
            'title', 'content', 'summary', 'announcement_type',
            'priority', 'target_audience', 'is_pinned', 'is_featured',
            'publish_at', 'expires_at', 'attachment'
        ]
    
    def validate_expires_at(self, value):
        """Validate that expiration date is in the future"""
        if value and value <= timezone.now():
            raise serializers.ValidationError("Expiration date must be in the future.")
        return value
    
    def validate_publish_at(self, value):
        """Validate publish date"""
        if value and value < timezone.now() - timezone.timedelta(days=1):
            raise serializers.ValidationError("Publish date cannot be more than 1 day in the past.")
        return value


class AnnouncementApprovalSerializer(serializers.ModelSerializer):
    """Serializer for announcement approval"""
    
    class Meta:
        model = Announcement
        fields = ['status']
    
    def validate_status(self, value):
        """Validate status transition"""
        if value not in ['approved', 'rejected']:
            raise serializers.ValidationError("Status must be 'approved' or 'rejected'.")
        return value
    
    def update(self, instance, validated_data):
        """Update with approval metadata"""
        instance.status = validated_data['status']
        instance.approved_by = self.context['request'].user
        instance.approved_at = timezone.now()
        instance.save()
        return instance


class PostListSerializer(serializers.ModelSerializer):
    """Serializer for post list view"""
    author = AuthorSerializer(read_only=True)
    is_published = serializers.BooleanField(read_only=True)
    is_event = serializers.BooleanField(read_only=True)
    is_upcoming_event = serializers.BooleanField(read_only=True)
    tags_list = serializers.ListField(read_only=True)
    
    class Meta:
        model = Post
        fields = [
            'id', 'title', 'excerpt', 'category', 'tags_list',
            'event_date', 'event_location', 'status', 'is_featured',
            'is_public', 'publish_at', 'author', 'featured_image',
            'view_count', 'is_published', 'is_event',
            'is_upcoming_event', 'created_at'
        ]


class PostDetailSerializer(serializers.ModelSerializer):
    """Serializer for post detail view"""
    author = AuthorSerializer(read_only=True)
    approved_by = AuthorSerializer(read_only=True)
    is_published = serializers.BooleanField(read_only=True)
    is_event = serializers.BooleanField(read_only=True)
    is_upcoming_event = serializers.BooleanField(read_only=True)
    is_past_event = serializers.BooleanField(read_only=True)
    registration_open = serializers.BooleanField(read_only=True)
    tags_list = serializers.ListField(read_only=True)
    
    class Meta:
        model = Post
        fields = [
            'id', 'title', 'content', 'excerpt', 'category', 'tags',
            'tags_list', 'event_date', 'event_location', 'registration_required',
            'registration_deadline', 'max_participants', 'status',
            'is_featured', 'is_public', 'publish_at', 'author',
            'approved_by', 'approved_at', 'featured_image', 'attachment',
            'view_count', 'is_published', 'is_event',
            'is_upcoming_event', 'is_past_event', 'registration_open',
            'created_at', 'updated_at'
        ]


class PostCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating posts"""
    
    class Meta:
        model = Post
        fields = [
            'title', 'content', 'excerpt', 'category', 'tags',
            'event_date', 'event_location', 'registration_required',
            'registration_deadline', 'max_participants', 'is_featured',
            'is_public', 'publish_at', 'featured_image', 'attachment'
        ]
    
    def validate_event_date(self, value):
        """Validate event date"""
        if value and value <= timezone.now():
            raise serializers.ValidationError("Event date must be in the future.")
        return value
    
    def validate_registration_deadline(self, value):
        """Validate registration deadline"""
        if value and value <= timezone.now():
            raise serializers.ValidationError("Registration deadline must be in the future.")
        return value
    
    def validate(self, data):
        """Cross-field validation"""
        event_date = data.get('event_date')
        registration_deadline = data.get('registration_deadline')
        
        if event_date and registration_deadline:
            if registration_deadline >= event_date:
                raise serializers.ValidationError(
                    "Registration deadline must be before event date."
                )
        
        return data


class PostApprovalSerializer(serializers.ModelSerializer):
    """Serializer for post approval"""
    
    class Meta:
        model = Post
        fields = ['status']
    
    def validate_status(self, value):
        """Validate status transition"""
        if value not in ['approved', 'rejected']:
            raise serializers.ValidationError("Status must be 'approved' or 'rejected'.")
        return value
    
    def update(self, instance, validated_data):
        """Update with approval metadata"""
        instance.status = validated_data['status']
        instance.approved_by = self.context['request'].user
        instance.approved_at = timezone.now()
        instance.save()
        return instance


class CommentSerializer(serializers.ModelSerializer):
    """Serializer for comments"""
    author = AuthorSerializer(read_only=True)
    replies = serializers.SerializerMethodField()
    
    class Meta:
        model = Comment
        fields = [
            'id', 'content', 'author', 'is_approved', 'parent',
            'replies', 'created_at', 'updated_at'
        ]
    
    def get_replies(self, obj):
        """Get comment replies"""
        if obj.replies.exists():
            return CommentSerializer(
                obj.replies.filter(is_approved=True),
                many=True,
                context=self.context
            ).data
        return []


class CommentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating comments"""
    
    class Meta:
        model = Comment
        fields = ['content', 'parent']
    
    def validate_content(self, value):
        """Validate comment content"""
        if len(value.strip()) < 3:
            raise serializers.ValidationError("Comment must be at least 3 characters long.")
        return value





class CommentLikeSerializer(serializers.ModelSerializer):
    """Serializer for comment likes"""
    user = AuthorSerializer(read_only=True)
    
    class Meta:
        model = CommentLike
        fields = ['id', 'user', 'created_at']

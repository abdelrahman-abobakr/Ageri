from rest_framework import serializers
from django.contrib.auth import get_user_model
from research.models import Publication, PublicationAuthor

User = get_user_model()


class AuthorSerializer(serializers.ModelSerializer):
    """Serializer for publication authors"""
    name = serializers.SerializerMethodField()
    email = serializers.EmailField(source='author.email', read_only=True)
    
    class Meta:
        model = PublicationAuthor
        fields = [
            'name', 'email', 'order', 'role', 
            'is_corresponding', 'is_first_author', 'is_last_author',
            'affiliation_at_publication', 'contribution'
        ]
    
    def get_name(self, obj):
        return obj.author.get_full_name() or obj.author.username


class UserBasicSerializer(serializers.ModelSerializer):
    """Basic user serializer for submitted_by and reviewed_by fields"""
    name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'name', 'email']
    
    def get_name(self, obj):
        return obj.get_full_name() or obj.username


class PublicationReviewSerializer(serializers.ModelSerializer):
    """Comprehensive serializer for publication review"""
    submitted_by = UserBasicSerializer(read_only=True)
    reviewed_by = UserBasicSerializer(read_only=True)
    authors = AuthorSerializer(source='author_assignments', many=True, read_only=True)
    document_file_url = serializers.SerializerMethodField()
    author_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Publication
        fields = [
            'id', 'title', 'abstract', 'status', 'publication_type',
            'research_area', 'keywords', 'journal_name', 'conference_name',
            'publisher', 'publication_date', 'doi', 'url', 'pdf_url',
            'submitted_by', 'submitted_at', 'reviewed_by', 'reviewed_at',
            'review_notes', 'is_public', 'is_featured', 'priority',
            'citation_count', 'authors', 'author_count', 'document_file_url'
        ]
        read_only_fields = [
            'id', 'submitted_by', 'submitted_at', 'reviewed_by', 
            'reviewed_at', 'authors', 'author_count', 'document_file_url'
        ]
    
    def get_document_file_url(self, obj):
        if obj.document_file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.document_file.url)
            return obj.document_file.url
        return None
    
    def get_author_count(self, obj):
        return obj.author_assignments.count()


class PublicationListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for publication lists"""
    submitted_by = UserBasicSerializer(read_only=True)
    author_count = serializers.SerializerMethodField()
    days_pending = serializers.SerializerMethodField()
    authors = AuthorSerializer(source='author_assignments', many=True, read_only=True)
    document_file_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Publication
        fields = [
            'id', 'title', 'abstract', 'status', 'publication_type', 'research_area',
            'keywords', 'journal_name', 'conference_name', 'publisher', 'publication_date',
            'doi', 'url', 'pdf_url',
            'submitted_by', 'submitted_at', 'author_count', 'days_pending',
            'is_featured', 'priority', 'citation_count', 'authors', 'document_file_url'
        ]
    
    def get_author_count(self, obj):
        return obj.author_assignments.count()
    
    def get_days_pending(self, obj):
        from django.utils import timezone
        if obj.submitted_at:
            delta = timezone.now() - obj.submitted_at
            return delta.days
        return 0
    
    def get_document_file_url(self, obj):
        if obj.document_file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.document_file.url)
            return obj.document_file.url
        return None


class PublicationApprovalSerializer(serializers.Serializer):
    """Serializer for publication approval"""
    review_notes = serializers.CharField(
        required=False, 
        allow_blank=True,
        help_text="Optional notes about the approval"
    )


class PublicationRejectionSerializer(serializers.Serializer):
    """Serializer for publication rejection"""
    review_notes = serializers.CharField(
        required=True,
        help_text="Required reason for rejection"
    )
    
    def validate_review_notes(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Rejection reason is required.")
        return value.strip()


class PublicationPublishSerializer(serializers.Serializer):
    """Serializer for publication publishing"""
    is_featured = serializers.BooleanField(
        default=False,
        help_text="Mark as featured publication"
    )
    priority = serializers.IntegerField(
        default=0,
        min_value=0,
        max_value=10,
        help_text="Priority for ordering (0-10)"
    )
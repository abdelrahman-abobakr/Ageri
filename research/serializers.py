from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import Publication, PublicationAuthor, PublicationMetrics, PublicationType

User = get_user_model()


class PublicationAuthorSerializer(serializers.ModelSerializer):
    """Serializer for PublicationAuthor model"""
    author_name = serializers.CharField(source='author.get_full_name', read_only=True)
    author_email = serializers.EmailField(source='author.email', read_only=True)
    author_orcid = serializers.CharField(source='author.profile.orcid_id', read_only=True)
    
    class Meta:
        model = PublicationAuthor
        fields = [
            'id', 'author', 'author_name', 'author_email', 'author_orcid',
            'order', 'role', 'affiliation_at_publication', 'contribution',
            'is_corresponding', 'is_first_author', 'is_last_author'
        ]
        read_only_fields = ['id']


class PublicationMetricsSerializer(serializers.ModelSerializer):
    """Serializer for PublicationMetrics model"""
    total_engagement = serializers.ReadOnlyField()
    
    class Meta:
        model = PublicationMetrics
        fields = [
            'view_count', 'download_count', 'citation_count', 'altmetric_score',
            'twitter_mentions', 'facebook_shares', 'linkedin_shares',
            'mendeley_readers', 'researchgate_reads', 'total_engagement',
            'last_citation_update', 'last_altmetric_update'
        ]
        read_only_fields = [
            'last_citation_update', 'last_altmetric_update', 'total_engagement'
        ]


class PublicationListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for publication lists"""
    author_names = serializers.ReadOnlyField()
    corresponding_author_name = serializers.CharField(
        source='corresponding_author.get_full_name', read_only=True
    )
    submitted_by_name = serializers.CharField(
        source='submitted_by.get_full_name', read_only=True
    )
    author_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Publication
        fields = [
            'id', 'title', 'publication_type', 'status', 'publication_date',
            'journal_name', 'conference_name', 'author_names', 'author_count',
            'corresponding_author_name', 'submitted_by_name', 'is_public',
            'citation_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_author_count(self, obj):
        """Get number of authors"""
        return obj.authors.count()


class PublicationDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for publication detail views"""
    authors = PublicationAuthorSerializer(source='author_assignments', many=True, read_only=True)
    metrics = PublicationMetricsSerializer(read_only=True)
    corresponding_author_name = serializers.CharField(
        source='corresponding_author.get_full_name', read_only=True
    )
    submitted_by_name = serializers.CharField(
        source='submitted_by.get_full_name', read_only=True
    )
    reviewed_by_name = serializers.CharField(
        source='reviewed_by.get_full_name', read_only=True
    )
    can_edit = serializers.SerializerMethodField()
    can_approve = serializers.SerializerMethodField()
    
    class Meta:
        model = Publication
        fields = [
            'id', 'title', 'abstract', 'publication_type', 'journal_name',
            'conference_name', 'publisher', 'volume', 'issue', 'pages',
            'publication_date', 'doi', 'isbn', 'issn', 'pmid', 'url', 'pdf_url',
            'document_file', 'keywords', 'research_area', 'status', 'is_public',
            'citation_count', 'corresponding_author', 'corresponding_author_name',
            'submitted_by', 'submitted_by_name', 'submitted_at',
            'reviewed_by', 'reviewed_by_name', 'reviewed_at', 'review_notes',
            'authors', 'metrics', 'can_edit', 'can_approve',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'submitted_at', 'created_at', 'updated_at',
            'can_edit', 'can_approve'
        ]
    
    def get_can_edit(self, obj):
        """Check if current user can edit this publication"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.can_be_edited_by(request.user)
        return False
    
    def get_can_approve(self, obj):
        """Check if current user can approve this publication"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.can_be_approved_by(request.user)
        return False


class PublicationCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating publications"""
    authors_data = PublicationAuthorSerializer(many=True, write_only=True, required=False)
    
    class Meta:
        model = Publication
        fields = [
            'title', 'abstract', 'publication_type', 'journal_name',
            'conference_name', 'publisher', 'volume', 'issue', 'pages',
            'publication_date', 'doi', 'isbn', 'issn', 'pmid', 'url', 'pdf_url',
            'document_file', 'keywords', 'research_area', 'corresponding_author',
            'is_public', 'citation_count', 'authors_data'
        ]
    
    def validate_doi(self, value):
        """Validate DOI format"""
        if value and not value.startswith('10.'):
            raise serializers.ValidationError("DOI must start with '10.'")
        return value
    
    def validate_publication_date(self, value):
        """Validate publication date is not in the future"""
        if value and value > timezone.now().date():
            raise serializers.ValidationError("Publication date cannot be in the future")
        return value
    
    def create(self, validated_data):
        """Create publication with authors"""
        authors_data = validated_data.pop('authors_data', [])
        
        # Set submitted_by to current user
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['submitted_by'] = request.user
        
        publication = Publication.objects.create(**validated_data)
        
        # Create author assignments
        for author_data in authors_data:
            PublicationAuthor.objects.create(
                publication=publication,
                **author_data
            )
        
        return publication
    
    def update(self, instance, validated_data):
        """Update publication and authors"""
        authors_data = validated_data.pop('authors_data', None)
        
        # Update publication fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update authors if provided
        if authors_data is not None:
            # Clear existing authors
            instance.author_assignments.all().delete()
            
            # Create new author assignments
            for author_data in authors_data:
                PublicationAuthor.objects.create(
                    publication=instance,
                    **author_data
                )
        
        return instance


class PublicationApprovalSerializer(serializers.ModelSerializer):
    """Serializer for publication approval workflow"""
    
    class Meta:
        model = Publication
        fields = ['status', 'review_notes', 'is_public']
    
    def validate_status(self, value):
        """Validate status transitions"""
        instance = self.instance
        if instance:
            current_status = instance.status
            
            # Define allowed transitions
            allowed_transitions = {
                'draft': ['pending'],
                'pending': ['approved', 'rejected'],
                'approved': ['published', 'rejected'],
                'rejected': ['pending'],
                'published': ['approved']  # Can unpublish
            }
            
            if value not in allowed_transitions.get(current_status, []):
                raise serializers.ValidationError(
                    f"Cannot change status from {current_status} to {value}"
                )
        
        return value
    
    def update(self, instance, validated_data):
        """Update with approval metadata"""
        request = self.context.get('request')
        
        if 'status' in validated_data:
            new_status = validated_data['status']
            
            # Set review metadata for admin actions
            if request and request.user.is_authenticated and request.user.is_admin:
                if new_status in ['approved', 'rejected']:
                    validated_data['reviewed_by'] = request.user
                    validated_data['reviewed_at'] = timezone.now()
        
        return super().update(instance, validated_data)

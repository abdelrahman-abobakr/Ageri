
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from .models import Publication, PublicationAuthor, PublicationMetrics

User = get_user_model()

# Define publication types if not in models
PUBLICATION_TYPES = [
    ('journal_article', 'Journal Article'),
    ('conference_paper', 'Conference Paper'),
    ('book_chapter', 'Book Chapter'),
    ('book', 'Book'),
    ('thesis', 'Thesis'),
    ('report', 'Report'),
    ('preprint', 'Preprint'),
    ('other', 'Other'),
]

class PublicationAuthorSerializer(serializers.ModelSerializer):
    """Enhanced serializer for PublicationAuthor model"""
    author_name = serializers.CharField(source='author.get_full_name', read_only=True)
    author_email = serializers.EmailField(source='author.email', read_only=True)
    author_orcid = serializers.CharField(source='author.profile.orcid_id', read_only=True)
    author_institution = serializers.CharField(source='author.institution', read_only=True)
    
    class Meta:
        model = PublicationAuthor
        fields = [
            'id', 'author', 'author_name', 'author_email', 'author_orcid',
            'author_institution', 'order', 'role', 'affiliation_at_publication',
            'contribution', 'is_corresponding', 'is_first_author', 'is_last_author',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_order(self, value):
        """Validate author order"""
        if value < 1 or value > 100:
            raise serializers.ValidationError("Order must be between 1 and 100")
        return value

    def validate(self, attrs):
        """Cross-field validation"""
        # Check if first author has order 1
        if attrs.get('is_first_author') and attrs.get('order', 1) != 1:
            raise serializers.ValidationError(
                "First author must have order = 1"
            )
        
        return attrs


class PublicationMetricsSerializer(serializers.ModelSerializer):
    """Enhanced serializer for PublicationMetrics model"""
    total_engagement = serializers.ReadOnlyField()
    engagement_level = serializers.ReadOnlyField()
    
    class Meta:
        model = PublicationMetrics
        fields = [
            'view_count', 'download_count', 'citation_count', 'altmetric_score',
            'twitter_mentions', 'facebook_shares', 'linkedin_shares',
            'mendeley_readers', 'researchgate_reads', 'quality_score',
            'total_engagement', 'engagement_level',
            'last_citation_update', 'last_altmetric_update',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'total_engagement', 'engagement_level', 'quality_score',
            'last_citation_update', 'last_altmetric_update',
            'created_at', 'updated_at'
        ]

    def validate_altmetric_score(self, value):
        """Validate altmetric score"""
        if value is not None and (value < 0 or value > 1000):
            raise serializers.ValidationError("Altmetric score must be between 0 and 1000")
        return value


class PublicationListSerializer(serializers.ModelSerializer):
    """Enhanced lightweight serializer for publication lists"""
    author_names = serializers.ReadOnlyField()
    corresponding_author_name = serializers.CharField(
        source='corresponding_author.get_full_name', read_only=True
    )
    submitted_by_name = serializers.CharField(
        source='submitted_by.get_full_name', read_only=True
    )
    author_count = serializers.SerializerMethodField()
    total_views = serializers.ReadOnlyField()
    total_downloads = serializers.ReadOnlyField()
    engagement_level = serializers.SerializerMethodField()
    publication_type_display = serializers.CharField(
        source='get_publication_type_display', read_only=True
    )
    status_display = serializers.CharField(
        source='get_status_display', read_only=True
    )
    
    class Meta:
        model = Publication
        fields = [
            'id', 'title', 'publication_type', 'publication_type_display',
            'status', 'status_display', 'publication_date', 'journal_name',
            'conference_name', 'author_names', 'author_count',
            'corresponding_author_name', 'submitted_by_name', 'is_public',
            'is_featured', 'priority', 'citation_count', 'total_views',
            'total_downloads', 'engagement_level', 'research_area',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_author_count(self, obj):
        """Get number of authors with caching"""
        if hasattr(obj, '_author_count'):
            return obj._author_count
        return obj.authors.count()

    def get_engagement_level(self, obj):
        """Get engagement level from metrics"""
        if hasattr(obj, 'metrics'):
            return obj.metrics.engagement_level
        return 'Very Low'


class PublicationDetailSerializer(serializers.ModelSerializer):
    """Enhanced detailed serializer for publication detail views"""
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
    publication_type_display = serializers.CharField(
        source='get_publication_type_display', read_only=True
    )
    status_display = serializers.CharField(
        source='get_status_display', read_only=True
    )
    first_authors = PublicationAuthorSerializer(many=True, read_only=True)
    corresponding_authors = PublicationAuthorSerializer(many=True, read_only=True)
    can_edit = serializers.SerializerMethodField()
    can_approve = serializers.SerializerMethodField()
    keywords_list = serializers.SerializerMethodField()
    
    class Meta:
        model = Publication
        fields = [
            'id', 'title', 'abstract', 'publication_type', 'publication_type_display',
            'journal_name', 'conference_name', 'publisher', 'volume', 'issue',
            'pages', 'publication_date', 'doi', 'isbn', 'issn', 'pmid',
            'url', 'pdf_url', 'document_file', 'keywords', 'keywords_list',
            'research_area', 'status', 'status_display', 'is_public',
            'is_featured', 'priority', 'citation_count',
            'corresponding_author', 'corresponding_author_name',
            'submitted_by', 'submitted_by_name', 'submitted_at',
            'reviewed_by', 'reviewed_by_name', 'reviewed_at', 'review_notes',
            'authors', 'first_authors', 'corresponding_authors', 'metrics',
            'can_edit', 'can_approve', 'created_at', 'updated_at'
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

    def get_keywords_list(self, obj):
        """Convert keywords string to list"""
        if obj.keywords:
            return [kw.strip() for kw in obj.keywords.split(',') if kw.strip()]
        return []


class PublicationCreateUpdateSerializer(serializers.ModelSerializer):
    """Enhanced serializer for creating and updating publications"""
    authors_data = PublicationAuthorSerializer(many=True, write_only=True, required=False)
    keywords_list = serializers.ListField(
        child=serializers.CharField(max_length=50),
        write_only=True,
        required=False,
        help_text="List of keywords"
    )
    doi = serializers.CharField(
        max_length=200,
        required=False,
        allow_blank=True,
        help_text="Digital Object Identifier (optional, must be unique if provided)"
    )
    
    class Meta:
        model = Publication
        fields = [
            'title', 'abstract', 'publication_type', 'journal_name',
            'conference_name', 'publisher', 'volume', 'issue', 'pages',
            'publication_date', 'doi', 'isbn', 'issn', 'pmid', 'url', 'pdf_url',
            'document_file', 'keywords', 'keywords_list', 'research_area',
            'corresponding_author', 'citation_count', 'is_featured',
            'priority', 'authors_data', 'is_public'
        ]
        extra_kwargs = {
            'doi': {
                'required': False,
                'allow_blank': True,
                'error_messages': {
                    'unique': 'This DOI already exists in the database.'
                }
            }
        }

    def validate_doi(self, value):
        """Enhanced DOI validation with clear messages"""
        # Handle empty/null DOI - make it truly optional
        if not value or value.strip() == '':
            return None  # Store as NULL in database
        
        value = value.strip()
        
        # Format validation
        if not value.startswith('10.'):
            raise serializers.ValidationError(
                "DOI must start with '10.' (e.g., 10.1000/xyz123)",
                code='invalid_format'
            )
        
        # Check for duplicate DOI (excluding current instance)
        existing_query = Publication.objects.filter(doi=value)
        if self.instance:
            existing_query = existing_query.exclude(pk=self.instance.pk)
        
        if existing_query.exists():
            existing_pub = existing_query.first()
            raise serializers.ValidationError(
                f"DOI '{value}' already exists for publication: {existing_pub.title[:50]}...",
                code='duplicate_doi'
            )
        
        return value

    def validate_publication_date(self, value):
        """Enhanced publication date validation"""
        if value and value > timezone.now().date():
            raise serializers.ValidationError("Publication date cannot be in the future")
        return value

    def validate_priority(self, value):
        """Validate priority range"""
        if value is not None and (value < 0 or value > 10):
            raise serializers.ValidationError("Priority must be between 0 and 10")
        return value

    def validate_title(self, value):
        """Validate title length and content"""
        if not value or len(value.strip()) < 10:
            raise serializers.ValidationError("Title must be at least 10 characters long")
        if len(value) > 500:
            raise serializers.ValidationError("Title cannot exceed 500 characters")
        return value.strip()

    def validate_abstract(self, value):
        """Validate abstract length"""
        if value and len(value) > 2000:
            raise serializers.ValidationError("Abstract cannot exceed 2000 characters")
        return value

    def validate_keywords_list(self, value):
        """Validate keywords list"""
        if value and len(value) > 20:
            raise serializers.ValidationError("Cannot have more than 20 keywords")
        if value:
            for keyword in value:
                if len(keyword) > 50:
                    raise serializers.ValidationError("Each keyword cannot exceed 50 characters")
        return value

    def validate_authors_data(self, value):
        """Validate authors data"""
        if not value:
            return value

        orders = [author.get('order', 1) for author in value]
        if len(orders) != len(set(orders)):
            raise serializers.ValidationError("Author orders must be unique")

        first_authors = [author for author in value if author.get('is_first_author')]
        if len(first_authors) > 1:
            raise serializers.ValidationError("Only one first author is allowed")

        if first_authors and first_authors[0].get('order', 1) != 1:
            raise serializers.ValidationError("First author must have order = 1")

        return value

    def validate(self, attrs):
        """Enhanced cross-field validation with clear field-specific errors"""
        errors = {}
        
        # Publication type validation
        pub_type = attrs.get('publication_type')
        if pub_type == 'journal_article' and not attrs.get('journal_name'):
            errors['journal_name'] = ['Journal name is required for journal articles']
        
        if pub_type == 'conference_paper' and not attrs.get('conference_name'):
            errors['conference_name'] = ['Conference name is required for conference papers']
        
        # Authors validation
        authors_data = attrs.get('authors_data', [])
        if authors_data:
            author_errors = self._validate_authors_structure(authors_data)
            if author_errors:
                errors['authors_data'] = author_errors
        
        # Publication date validation
        pub_date = attrs.get('publication_date')
        if pub_date and pub_date > timezone.now().date():
            errors['publication_date'] = ['Publication date cannot be in the future']
        
        # If we have field-specific errors, raise them
        if errors:
            raise serializers.ValidationError(errors)
        
        return super().validate(attrs)

    def _validate_authors_structure(self, authors_data):
        """Validate authors data structure"""
        errors = []
        
        # Check for first author
        first_authors = [a for a in authors_data if a.get('is_first_author')]
        if len(first_authors) > 1:
            errors.append('Only one first author is allowed')
        elif len(first_authors) == 1 and first_authors[0].get('order') != 1:
            errors.append('First author must have order = 1')
        
        # Check for unique orders
        orders = [a.get('order') for a in authors_data if a.get('order')]
        if len(orders) != len(set(orders)):
            errors.append('Author orders must be unique')
        
        return errors

    @transaction.atomic
    def create(self, validated_data):
        """Enhanced create with DOI integrity error handling"""
        print(f"📤 Creating publication with validated data: {validated_data}")
        
        authors_data = validated_data.pop('authors_data', [])
        keywords_list = validated_data.pop('keywords_list', [])
        
        # Convert keywords list to string
        if keywords_list:
            validated_data['keywords'] = ', '.join(keywords_list)
        
        # Set submitted_by to current user
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['submitted_by'] = request.user
        
        # Set default values
        validated_data.setdefault('status', 'draft')
        validated_data.setdefault('is_public', False)
        validated_data.setdefault('priority', 0)
        validated_data.setdefault('citation_count', 0)
        
        try:
            publication = Publication.objects.create(**validated_data)
            print(f"✅ Publication created with ID: {publication.id}")
            
            # Create author assignments
            for order, author_data in enumerate(authors_data, 1):
                if 'order' not in author_data:
                    author_data['order'] = order
                
                PublicationAuthor.objects.create(
                    publication=publication,
                    **author_data
                )
                print(f"✅ Author assignment created: {author_data}")
            
            # Create initial metrics
            PublicationMetrics.objects.create(publication=publication)
            print(f"✅ Initial metrics created for publication {publication.id}")
            
            return publication
            
        except IntegrityError as e:
            print(f"❌ Integrity error during publication creation: {str(e)}")
            if 'doi' in str(e).lower():
                raise serializers.ValidationError({
                    'doi': 'This DOI already exists in the database.'
                })
            raise serializers.ValidationError({
                'non_field_errors': 'A database constraint was violated. Please check your data.'
            })
        except Exception as e:
            print(f"❌ Error during publication creation: {str(e)}")
            print(f"❌ Validated data was: {validated_data}")
            raise
    
    @transaction.atomic
    def update(self, instance, validated_data):
        """Enhanced update with transaction safety"""
        print(f"📤 Updating publication {instance.id} with data: {validated_data}")
        
        authors_data = validated_data.pop('authors_data', None)
        keywords_list = validated_data.pop('keywords_list', None)
        
        # Convert keywords list to string
        if keywords_list is not None:
            validated_data['keywords'] = ', '.join(keywords_list)
        
        # Update publication fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update authors if provided
        if authors_data is not None:
            # Clear existing authors
            instance.author_assignments.all().delete()
            
            # Create new author assignments
            for order, author_data in enumerate(authors_data, 1):
                if 'order' not in author_data:
                    author_data['order'] = order
                PublicationAuthor.objects.create(
                    publication=instance,
                    **author_data
                )
        
        print(f"✅ Publication {instance.id} updated successfully")
        return instance


class PublicationApprovalSerializer(serializers.ModelSerializer):
    """Enhanced serializer for publication approval workflow"""
    
    class Meta:
        model = Publication
        fields = ['status', 'review_notes', 'is_public', 'is_featured', 'priority']
    
    def validate_status(self, value):
        """Enhanced status transition validation"""
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

    def validate(self, attrs):
        """Cross-field validation for approval"""
        status = attrs.get('status')
        is_public = attrs.get('is_public', False)
        
        # Published publications must be public
        if status == 'published' and not is_public:
            attrs['is_public'] = True
        
        # Rejected publications cannot be public
        if status == 'rejected':
            attrs['is_public'] = False
        
        return attrs
    
    @transaction.atomic
    def update(self, instance, validated_data):
        """Enhanced update with approval metadata"""
        request = self.context.get('request')
        
        if 'status' in validated_data:
            new_status = validated_data['status']
            
            # Set review metadata for admin actions
            if request and request.user.is_authenticated and hasattr(request.user, 'is_admin') and request.user.is_admin:
                if new_status in ['approved', 'rejected']:
                    validated_data['reviewed_by'] = request.user
                    validated_data['reviewed_at'] = timezone.now()
        
        return super().update(instance, validated_data)


class PublicationStatsSerializer(serializers.Serializer):
    """Serializer for publication statistics"""
    total_publications = serializers.IntegerField()
    published_publications = serializers.IntegerField()
    pending_publications = serializers.IntegerField()
    draft_publications = serializers.IntegerField()
    approved_publications = serializers.IntegerField()
    rejected_publications = serializers.IntegerField()
    recent_publications = serializers.IntegerField()
    featured_publications = serializers.IntegerField()
    by_type = serializers.DictField()
    by_status = serializers.DictField()
    by_research_area = serializers.DictField()
    user_stats = serializers.DictField(required=False)
    top_cited = serializers.ListField(required=False)
    most_viewed = serializers.ListField(required=False)


class BulkActionSerializer(serializers.Serializer):
    """Serializer for bulk actions"""
    publication_ids = serializers.ListField(
        child=serializers.IntegerField(),
        min_length=1,
        max_length=100
    )
    action = serializers.ChoiceField(
        choices=['approve', 'reject', 'publish', 'unpublish', 'feature', 'unfeature']
    )
    review_notes = serializers.CharField(max_length=1000, required=False, allow_blank=True)
    
    def validate_publication_ids(self, value):
        """Validate publication IDs exist"""
        existing_ids = set(Publication.objects.filter(id__in=value).values_list('id', flat=True))
        missing_ids = set(value) - existing_ids
        
        if missing_ids:
            raise serializers.ValidationError(
                f"Publications with IDs {list(missing_ids)} do not exist"
            )
        
        return value


class PublicationSearchSerializer(serializers.Serializer):
    """Serializer for advanced search parameters"""
    q = serializers.CharField(max_length=200, required=False)
    publication_type = serializers.MultipleChoiceField(
        choices=PUBLICATION_TYPES,
        required=False
    )
    status = serializers.MultipleChoiceField(
        choices=[
            ('draft', 'Draft'),
            ('pending', 'Pending'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected'),
            ('published', 'Published')
        ],
        required=False
    )
    research_area = serializers.CharField(max_length=200, required=False)
    date_from = serializers.DateField(required=False)
    date_to = serializers.DateField(required=False)
    author_id = serializers.IntegerField(required=False)
    min_citations = serializers.IntegerField(min_value=0, required=False)
    max_citations = serializers.IntegerField(min_value=0, required=False)
    is_featured = serializers.BooleanField(required=False)
    has_doi = serializers.BooleanField(required=False)
    has_pdf = serializers.BooleanField(required=False)
    
    def validate(self, attrs):
        """Cross-field validation for search"""
        date_from = attrs.get('date_from')
        date_to = attrs.get('date_to')
        
        if date_from and date_to and date_from > date_to:
            raise serializers.ValidationError("date_from cannot be after date_to")
        
        min_citations = attrs.get('min_citations')
        max_citations = attrs.get('max_citations')
        
        if min_citations is not None and max_citations is not None and min_citations > max_citations:
            raise serializers.ValidationError("min_citations cannot be greater than max_citations")
        
        return attrs

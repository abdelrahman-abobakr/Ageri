from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.utils import timezone
from .models import User, UserProfile, UserRole


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for UserProfile model - Enhanced like medical"""
    has_cv = serializers.ReadOnlyField()
    has_orcid = serializers.ReadOnlyField()
    
    class Meta:
        model = UserProfile
        fields = [
            'profile_picture',
            'position',
            'academic_degree',
            'specialization',
            'phone',
            'orcid_id',
            'bio',
            'research_interests',
            'cv_file',
            'website',
            'linkedin',
            'google_scholar',
            'researchgate',
            'is_public',
            'created_at',
            'updated_at',
            'has_cv',
            'has_orcid'
        ]
        read_only_fields = ['created_at', 'updated_at', 'has_cv', 'has_orcid']


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model - Enhanced like medical"""
    profile = UserProfileSerializer(read_only=True)
    password = serializers.CharField(write_only=True, validators=[validate_password], required=False)
    password_confirm = serializers.CharField(write_only=True, required=False)
    full_name = serializers.CharField(source='get_full_name', read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'full_name',
            'role', 'is_approved', 'approval_date', 'phone',
            'institution', 'department', 'date_joined', 'profile',
            'password', 'password_confirm'
        ]
        read_only_fields = ['id', 'is_approved', 'approval_date', 'date_joined', 'full_name']
        extra_kwargs = {
            'username': {'required': False},
            'email': {'required': False},
        }

    def validate(self, attrs):
        # Only validate password if it's being updated
        if attrs.get('password') or attrs.get('password_confirm'):
            if attrs.get('password') != attrs.get('password_confirm'):
                raise serializers.ValidationError("Passwords don't match")
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm', None)
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()

        # Create user profile automatically
        UserProfile.objects.create(user=user)
        return user

    def update(self, instance, validated_data):
        validated_data.pop('password_confirm', None)
        password = validated_data.pop('password', None)

        # Update user fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # Update password if provided
        if password:
            instance.set_password(password)

        instance.save()
        return instance


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration - Enhanced like medical"""
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = [
            'username', 'email', 'first_name', 'last_name',
            'password', 'password_confirm', 'phone', 'institution', 'department'
        ]
    
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("User with this email already exists.")
        return value
    
    def validate(self, attrs):
        if attrs.get('password') != attrs.get('password_confirm'):
            raise serializers.ValidationError("Passwords don't match")
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm', None)
        password = validated_data.pop('password')
        
        # Create user with researcher role by default
        user = User.objects.create_user(
            role=UserRole.RESEARCHER,
            is_approved=False,  # Requires admin approval
            **validated_data
        )
        user.set_password(password)
        user.save()
        
        # Create user profile automatically
        UserProfile.objects.create(user=user)
        return user


class LoginSerializer(serializers.Serializer):
    """Serializer for user login - Enhanced like medical"""
    email = serializers.EmailField()
    password = serializers.CharField()
    
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        
        if email and password:
            user = authenticate(username=email, password=password)
            if not user:
                raise serializers.ValidationError('Invalid credentials')
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled')
            if not user.is_approved:
                raise serializers.ValidationError('User account is not approved yet')
            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError('Must include email and password')


class UserApprovalSerializer(serializers.ModelSerializer):
    """Serializer for user approval by admin - Enhanced like medical"""
    
    class Meta:
        model = User
        fields = ['is_approved']
    
    def update(self, instance, validated_data):
        if validated_data.get('is_approved'):
            instance.is_approved = True
            instance.approved_by = self.context['request'].user
            instance.approval_date = timezone.now()
        else:
            instance.is_approved = False
            instance.approved_by = None
            instance.approval_date = None
        instance.save()
        return instance


class UserListSerializer(serializers.ModelSerializer):
    """Simplified serializer for user lists - Enhanced like medical"""
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    profile_complete = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'full_name', 'role',
            'is_approved', 'date_joined', 'institution', 'department',
            'profile_complete'
        ]
    
    def get_profile_complete(self, obj):
        """Check if user profile is complete"""
        try:
            profile = obj.profile
            return bool(profile.bio and profile.research_interests)
        except:
            return False


# Additional serializers for better profile management
class UserProfileUpdateSerializer(serializers.ModelSerializer):
    profile_picture = serializers.ImageField(required=False)
    
    class Meta:
        model = UserProfile
        fields = [
            'profile_picture',
            'position',
            'academic_degree',
            'specialization',
            'phone',
            'orcid_id',
            'bio',
            'research_interests',
            'cv_file',
            'website',
            'linkedin',
            'google_scholar',
            'researchgate',
            'is_public',
            'admin_notes',
        ]
        extra_kwargs = {
            'admin_notes': {'read_only': True}
        }

    def update(self, instance, validated_data):
        """Custom update to handle all fields properly"""
        print(f"Serializer update called with: {validated_data}")
        
        # Update all fields including is_public
        for attr, value in validated_data.items():
            if attr == 'admin_notes' and not self.context['request'].user.is_admin:
                continue  # Skip admin_notes for non-admin users
            setattr(instance, attr, value)
            print(f"Set {attr} = {value}")
        
        instance.save()
        print(f"Saved instance. is_public is now: {instance.is_public}")
        return instance


class UserDetailSerializer(serializers.ModelSerializer):
    """Detailed user serializer with profile information"""
    profile = UserProfileSerializer(read_only=True)
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    is_profile_owner = serializers.SerializerMethodField()
    can_edit = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'full_name',
            'role', 'is_approved', 'approval_date', 'phone',
            'institution', 'department', 'date_joined', 'profile',
            'is_profile_owner', 'can_edit'
        ]
        read_only_fields = ['id', 'is_approved', 'approval_date', 'date_joined']
    
    def get_is_profile_owner(self, obj):
        """Check if current user is the profile owner"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return request.user.id == obj.id
        return False
    
    def get_can_edit(self, obj):
        """Check if current user can edit this profile"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return (request.user.id == obj.id or 
                   request.user.role == UserRole.ADMIN)
        return False

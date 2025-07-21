from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.utils import timezone
from .models import User, UserProfile, UserRole


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for UserProfile model"""
    
    class Meta:
        model = UserProfile
        fields = [
            'orcid_id', 'bio', 'research_interests', 'cv_file',
            'website', 'linkedin', 'google_scholar', 'researchgate',
            'is_public', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""
    profile = UserProfileSerializer(read_only=True)
    password = serializers.CharField(write_only=True, validators=[validate_password], required=False)
    password_confirm = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'role', 'is_approved', 'approval_date', 'phone',
            'institution', 'date_joined', 'profile',
            'password', 'password_confirm'
        ]
        read_only_fields = ['id', 'is_approved', 'approval_date', 'date_joined']
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

        # Create user profile
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
    """Serializer for user registration"""
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = [
            'username', 'email', 'first_name', 'last_name',
            'password', 'password_confirm', 'phone', 'institution'
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
        
        # Create user profile
        UserProfile.objects.create(user=user)
        return user


class LoginSerializer(serializers.Serializer):
    """Serializer for user login"""
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
    """Serializer for user approval by admin"""
    
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
    """Simplified serializer for user lists"""
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'full_name', 'role',
            'is_approved', 'date_joined', 'institution'
        ]

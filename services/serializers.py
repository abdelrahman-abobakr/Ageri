from rest_framework import serializers
from django.utils import timezone
from .models import TestService, ServiceImage


class ServiceImageSerializer(serializers.ModelSerializer):
    """Serializer for service images"""
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = ServiceImage
        fields = ['id', 'image', 'image_url', 'is_primary', 'created_at']
        read_only_fields = ['created_at']
    
    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None


class TestServiceListSerializer(serializers.ModelSerializer):
    """Simplified serializer for service lists"""
    display_price = serializers.ReadOnlyField()
    image_url = serializers.ReadOnlyField()
    has_image = serializers.ReadOnlyField()
    
    class Meta:
        model = TestService
        fields = [
            'id', 'name', 'service_code', 'category', 'description',
            'base_price', 'is_free', 'display_price', 'estimated_duration',
            'status', 'is_featured', 'contact_email', 'contact_phone',
            'tags', 'is_available', 'featured_image', 'image_url', 'has_image'
        ]


class TestServiceDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for service details"""
    display_price = serializers.ReadOnlyField()
    image_url = serializers.ReadOnlyField()
    has_image = serializers.ReadOnlyField()
    
    class Meta:
        model = TestService
        fields = [
            'id', 'name', 'service_code', 'category', 'description',
            'base_price', 'is_free', 'display_price', 'estimated_duration',
            'status', 'is_featured', 'contact_email', 'contact_phone',
            'tags', 'featured_image', 'image_url', 'has_image',
            'is_available', 'created_at', 'updated_at'
        ]


class TestServiceCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating services"""
    
    class Meta:
        model = TestService
        fields = [
            'name', 'service_code', 'category', 'description',
            'base_price', 'is_free', 'estimated_duration', 'status',
            'is_featured', 'contact_email', 'contact_phone', 'tags',
            'featured_image'
        ]
    
    def validate_service_code(self, value):
        """Validate service code uniqueness"""
        if self.instance and self.instance.service_code == value:
            return value
        if TestService.objects.filter(service_code=value).exists():
            raise serializers.ValidationError("Service code must be unique.")
        return value.upper()
    
    def validate(self, data):
        """Custom validation"""
        # If marked as free, ensure price is 0
        if data.get('is_free') and data.get('base_price', 0) > 0:
            data['base_price'] = 0
        
        return data


class TestServiceWithImagesSerializer(serializers.ModelSerializer):
    """Serializer for service with associated images"""
    images = ServiceImageSerializer(many=True, read_only=True)
    display_price = serializers.ReadOnlyField()
    image_url = serializers.ReadOnlyField()
    has_image = serializers.ReadOnlyField()
    
    class Meta:
        model = TestService
        fields = [
            'id', 'name', 'service_code', 'category', 'description',
            'base_price', 'is_free', 'display_price', 'estimated_duration',
            'status', 'is_featured', 'contact_email', 'contact_phone',
            'tags', 'featured_image', 'image_url', 'has_image',
            'images', 'is_available', 'created_at', 'updated_at'
        ]


class ServiceImageUploadSerializer(serializers.ModelSerializer):
    """Serializer for uploading service images"""
    
    class Meta:
        model = ServiceImage
        fields = ['image', 'is_primary']
    
    def validate_image(self, value):
        """Validate image file"""
        if value.size > 5 * 1024 * 1024:  # 5MB limit
            raise serializers.ValidationError("Image size should not exceed 5MB")
        return value


class ServiceImageUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating service images"""
    
    class Meta:
        model = ServiceImage
        fields = ['is_primary']
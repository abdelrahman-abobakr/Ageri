from rest_framework import serializers
from .models import ServiceImage, TestService
from django.core.files.images import get_image_dimensions
from PIL import Image
import os


class ServiceImageSerializer(serializers.ModelSerializer):
    """Serializer for service images"""
    image_url = serializers.SerializerMethodField()
    thumbnail_url = serializers.SerializerMethodField()
    
    class Meta:
        model = ServiceImage
        fields = [
            'id', 'service', 'image', 'image_url', 'thumbnail_url',
            'alt_text', 'is_primary', 'order', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'image_url', 'thumbnail_url']
    
    def get_image_url(self, obj):
        """Return the full URL of the image"""
        request = self.context.get('request')
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None
    
    def get_thumbnail_url(self, obj):
        """Return the thumbnail URL of the image"""
        request = self.context.get('request')
        if obj.image and request:
            # Generate thumbnail URL (assuming thumbnails are created)
            image_path = obj.image.url
            base, ext = os.path.splitext(image_path)
            thumbnail_path = f"{base}_thumbnail{ext}"
            return request.build_absolute_uri(thumbnail_path)
        return None
    
    def validate_image(self, value):
        """Validate image file"""
        if value:
            # Check file size (5MB limit)
            if value.size > 5 * 1024 * 1024:
                raise serializers.ValidationError("Image file too large ( > 5MB )")
            
            # Check file type
            valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
            ext = os.path.splitext(value.name)[1].lower()
            if ext not in valid_extensions:
                raise serializers.ValidationError(
                    f"Unsupported file extension. Use: {', '.join(valid_extensions)}"
                )
            
            # Check image dimensions
            try:
                width, height = get_image_dimensions(value)
                if width < 300 or height < 300:
                    raise serializers.ValidationError(
                        "Image dimensions too small. Minimum 300x300 pixels required."
                    )
                if width > 4000 or height > 4000:
                    raise serializers.ValidationError(
                        "Image dimensions too large. Maximum 4000x4000 pixels allowed."
                    )
            except Exception:
                raise serializers.ValidationError("Invalid image file")
        
        return value
    
    def validate(self, data):
        """Validate the image data"""
        # Ensure only one primary image per service
        if data.get('is_primary', False):
            service = data.get('service')
            if service and service.service_images.filter(is_primary=True).exists():
                # If this is an update, allow the current image to remain primary
                if self.instance and self.instance.is_primary:
                    pass
                else:
                    # Otherwise, set all other images to non-primary
                    service.service_images.update(is_primary=False)
        
        return data


class ServiceImageUploadSerializer(serializers.ModelSerializer):
    """Serializer specifically for image upload"""
    
    class Meta:
        model = ServiceImage
        fields = ['image', 'alt_text', 'is_primary', 'order']
    
    def create(self, validated_data):
        """Create a new service image"""
        service = validated_data.pop('service')
        image = ServiceImage.objects.create(service=service, **validated_data)
        return image


class ServiceImageUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating image metadata"""
    
    class Meta:
        model = ServiceImage
        fields = ['alt_text', 'is_primary', 'order']
    
    def update(self, instance, validated_data):
        """Update image metadata"""
        if validated_data.get('is_primary', False):
            # Ensure only one primary image
            ServiceImage.objects.filter(
                service=instance.service,
                is_primary=True
            ).update(is_primary=False)
        
        return super().update(instance, validated_data)


class TestServiceWithImagesSerializer(serializers.ModelSerializer):
    """Extended serializer that includes all service images"""
    images = ServiceImageSerializer(source='service_images', many=True, read_only=True)
    primary_image = serializers.SerializerMethodField()
    image_count = serializers.SerializerMethodField()
    
    class Meta:
        model = TestService
        fields = [
            'id', 'name', 'description', 'short_description', 'service_code',
            'category', 'department', 'lab', 'base_price', 'is_free',
            'estimated_duration', 'status', 'is_featured', 'is_public',
            'featured_image', 'images', 'primary_image', 'image_count'
        ]
    
    def get_primary_image(self, obj):
        """Get the primary image for the service"""
        primary = obj.service_images.filter(is_primary=True).first()
        if primary:
            return ServiceImageSerializer(primary, context=self.context).data
        return None
    
    def get_image_count(self, obj):
        """Get the total number of images for the service"""
        return obj.service_images.count()

from rest_framework import serializers
from .models import PostImage

class PostImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = PostImage
        fields = [
            'id', 'image', 'image_url', 'caption', 'alt_text', 'order', 'created_at'
        ]
        read_only_fields = ['image_url']

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None

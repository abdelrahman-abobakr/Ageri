from django.contrib import admin
from django.utils.html import format_html
from .models import TestService, ServiceImage


@admin.register(TestService)
class TestServiceAdmin(admin.ModelAdmin):
    list_display = [
        'service_code', 'name', 'category', 'display_price', 
        'status', 'is_featured', 'is_available', 'has_image', 'created_at'
    ]
    list_filter = ['category', 'status', 'is_featured', 'is_free', 'created_at']
    search_fields = ['name', 'service_code', 'description', 'tags']
    readonly_fields = ['created_at', 'updated_at', 'display_price', 'image_preview']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'service_code', 'category', 'description', 'tags')
        }),
        ('Pricing', {
            'fields': ('is_free', 'base_price', 'display_price')
        }),
        ('Service Details', {
            'fields': ('estimated_duration', 'status', 'is_featured')
        }),
        ('Contact Information', {
            'fields': ('contact_email', 'contact_phone')
        }),
        ('Media', {
            'fields': ('featured_image', 'image_preview')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def image_preview(self, obj):
        if obj.featured_image:
            return format_html(
                '<img src="{}" width="100" height="100" style="object-fit: cover;" />',
                obj.featured_image.url
            )
        return "No image"
    image_preview.short_description = "Image Preview"
    
    def has_image(self, obj):
        return obj.has_image
    has_image.boolean = True
    has_image.short_description = "Has Image"
    
    actions = ['make_featured', 'remove_featured', 'activate_services', 'deactivate_services']
    
    def make_featured(self, request, queryset):
        updated = queryset.update(is_featured=True)
        self.message_user(request, f'{updated} services marked as featured.')
    make_featured.short_description = "Mark selected services as featured"
    
    def remove_featured(self, request, queryset):
        updated = queryset.update(is_featured=False)
        self.message_user(request, f'{updated} services removed from featured.')
    remove_featured.short_description = "Remove selected services from featured"
    
    def activate_services(self, request, queryset):
        updated = queryset.update(status='active')
        self.message_user(request, f'{updated} services activated.')
    activate_services.short_description = "Activate selected services"
    
    def deactivate_services(self, request, queryset):
        updated = queryset.update(status='inactive')
        self.message_user(request, f'{updated} services deactivated.')
    deactivate_services.short_description = "Deactivate selected services"


@admin.register(ServiceImage)
class ServiceImageAdmin(admin.ModelAdmin):
    list_display = ['id', 'service', 'is_primary', 'image_preview', 'created_at']
    list_filter = ['is_primary', 'created_at', 'service__category']
    search_fields = ['service__name', 'service__service_code']
    readonly_fields = ['created_at', 'updated_at', 'image_preview']
    
    fieldsets = (
        ('Image Details', {
            'fields': ('service', 'image', 'image_preview', 'is_primary')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="100" height="100" style="object-fit: cover;" />',
                obj.image.url
            )
        return "No image"
    image_preview.short_description = "Preview"
    
    actions = ['make_primary', 'remove_primary']
    
    def make_primary(self, request, queryset):
        for image in queryset:
            # Reset all images for this service to non-primary
            ServiceImage.objects.filter(service=image.service).update(is_primary=False)
            # Set this image as primary
            image.is_primary = True
            image.save()
        self.message_user(request, f'{queryset.count()} images set as primary.')
    make_primary.short_description = "Set selected images as primary"
    
    def remove_primary(self, request, queryset):
        updated = queryset.update(is_primary=False)
        self.message_user(request, f'{updated} images removed from primary.')
    remove_primary.short_description = "Remove primary status from selected images"
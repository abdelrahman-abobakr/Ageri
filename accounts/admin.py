from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import User, UserProfile


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fields = (
        'orcid_id', 'bio', 'research_interests', 'cv_file',
        'website', 'linkedin', 'google_scholar', 'researchgate',
        'is_public', 'admin_notes'
    )


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = (
        'email', 'get_full_name', 'role', 'is_approved',
        'is_active', 'date_joined', 'approval_status'
    )
    list_filter = ('role', 'is_approved', 'is_active', 'date_joined')
    search_fields = ('email', 'first_name', 'last_name', 'username')
    ordering = ('-date_joined',)

    fieldsets = BaseUserAdmin.fieldsets + (
        ('Role & Approval', {
            'fields': ('role', 'is_approved', 'approval_date', 'approved_by')
        }),
        ('Additional Info', {
            'fields': ('phone', 'institution', 'department')
        }),
    )

    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Role & Additional Info', {
            'fields': ('email', 'role', 'phone', 'institution', 'department')
        }),
    )

    def approval_status(self, obj):
        if obj.is_approved:
            return format_html(
                '<span style="color: green;">✓ Approved</span>'
            )
        else:
            return format_html(
                '<span style="color: red;">✗ Pending</span>'
            )
    approval_status.short_description = 'Status'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('approved_by')


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'has_cv', 'has_orcid', 'is_public', 'created_at')
    list_filter = ('is_public', 'created_at')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'orcid_id')
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Professional Information', {
            'fields': ('orcid_id', 'bio', 'research_interests')
        }),
        ('Documents', {
            'fields': ('cv_file',)
        }),
        ('Social Links', {
            'fields': ('website', 'linkedin', 'google_scholar', 'researchgate')
        }),
        ('Settings', {
            'fields': ('is_public', 'admin_notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

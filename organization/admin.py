from django.contrib import admin
from django.utils.html import format_html
from .models import Department, Lab, ResearcherAssignment, OrganizationSettings


class LabInline(admin.TabularInline):
    model = Lab
    extra = 0
    fields = ('name', 'head', 'capacity', 'status')
    readonly_fields = ('current_researchers_count',)


class ResearcherAssignmentInline(admin.TabularInline):
    model = ResearcherAssignment
    extra = 0
    fields = ('researcher', 'position', 'start_date', 'end_date', 'status')
    autocomplete_fields = ['researcher']


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'head', 'total_labs', 'total_researchers',
        'status', 'created_at'
    )
    list_filter = ('status', 'created_at')
    search_fields = ('name', 'description', 'head__email')
    inlines = [LabInline]

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'head', 'status')
        }),
        ('Contact Information', {
            'fields': ('email', 'phone', 'location')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('created_at', 'updated_at')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('head')


@admin.register(Lab)
class LabAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'department', 'head', 'current_researchers_count',
        'capacity', 'available_spots', 'status'
    )
    list_filter = ('department', 'status', 'created_at')
    search_fields = ('name', 'description', 'department__name', 'head__email')
    inlines = [ResearcherAssignmentInline]

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'department', 'description', 'head', 'status')
        }),
        ('Resources', {
            'fields': ('equipment', 'capacity')
        }),
        ('Contact Information', {
            'fields': ('location', 'phone')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('created_at', 'updated_at')

    def available_spots(self, obj):
        spots = obj.available_spots
        if spots == 0:
            return format_html('<span style="color: red;">Full</span>')
        elif spots <= 2:
            return format_html('<span style="color: orange;">{}</span>', spots)
        else:
            return format_html('<span style="color: green;">{}</span>', spots)
    available_spots.short_description = 'Available Spots'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('department', 'head')


@admin.register(ResearcherAssignment)
class ResearcherAssignmentAdmin(admin.ModelAdmin):
    list_display = (
        'researcher', 'lab', 'department', 'position',
        'start_date', 'end_date', 'status', 'is_active'
    )
    list_filter = ('status', 'department', 'lab', 'start_date')
    search_fields = (
        'researcher__email', 'researcher__first_name', 'researcher__last_name',
        'lab__name', 'department__name', 'position'
    )
    date_hierarchy = 'start_date'
    autocomplete_fields = ['researcher', 'lab', 'department', 'assigned_by']

    fieldsets = (
        ('Assignment Details', {
            'fields': ('researcher', 'lab', 'department', 'position')
        }),
        ('Timeline', {
            'fields': ('start_date', 'end_date', 'status')
        }),
        ('Metadata', {
            'fields': ('assigned_by', 'notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('created_at', 'updated_at')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'researcher', 'lab', 'department', 'assigned_by'
        )

    def save_model(self, request, obj, form, change):
        if not change:  # Only set assigned_by for new assignments
            obj.assigned_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(OrganizationSettings)
class OrganizationSettingsAdmin(admin.ModelAdmin):
    """
    Admin interface for organization settings (singleton model)
    """

    def has_add_permission(self, request):
        # Only allow adding if no instance exists
        return not OrganizationSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        # Never allow deletion
        return False

    fieldsets = (
        ('Organization Identity', {
            'fields': ('name',)
        }),
        ('Vision & Mission', {
            'fields': ('vision', 'vision_image', 'mission', 'mission_image')
        }),
        ('About Organization', {
            'fields': ('about',)
        }),
        ('Contact Information', {
            'fields': ('email', 'phone', 'address')
        }),
        ('Social Media', {
            'fields': ('website', 'facebook', 'twitter', 'linkedin', 'instagram'),
            'classes': ('collapse',)
        }),
        ('Media Files', {
            'fields': ('logo', 'banner')
        }),
        ('System Settings', {
            'fields': (
                'enable_registration', 'require_approval',
                'maintenance_mode', 'maintenance_message'
            ),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ('created_at', 'updated_at')

    def changelist_view(self, request, extra_context=None):
        # Redirect to the single instance if it exists, otherwise show add form
        if OrganizationSettings.objects.exists():
            obj = OrganizationSettings.objects.first()
            return self.change_view(request, str(obj.pk), extra_context)
        else:
            return self.add_view(request, extra_context)

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import TestService, Client, TechnicianAssignment, ServiceRequest


class TechnicianAssignmentInline(admin.TabularInline):
    model = TechnicianAssignment
    extra = 0
    fields = ['technician', 'role', 'is_active', 'start_date', 'end_date', 'max_concurrent_requests', 'current_requests']
    readonly_fields = ['current_requests']


@admin.register(TestService)
class TestServiceAdmin(admin.ModelAdmin):
    list_display = [
        'service_code', 'name', 'category', 'department', 'lab',
        'base_price', 'is_free', 'status', 'is_featured', 'availability_status'
    ]
    list_filter = ['category', 'department', 'lab', 'status', 'is_featured', 'is_public', 'is_free']
    search_fields = ['name', 'service_code', 'description', 'tags']
    readonly_fields = ['current_requests', 'availability_percentage', 'created_at', 'updated_at']
    inlines = [TechnicianAssignmentInline]

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'short_description', 'service_code', 'category')
        }),
        ('Organization', {
            'fields': ('department', 'lab')
        }),
        ('Pricing', {
            'fields': ('base_price', 'is_free', 'pricing_structure')
        }),
        ('Service Details', {
            'fields': ('estimated_duration', 'sample_requirements', 'equipment_used', 'methodology')
        }),
        ('Capacity & Availability', {
            'fields': ('max_concurrent_requests', 'current_requests', 'availability_percentage')
        }),
        ('Requirements', {
            'fields': ('required_documents', 'safety_requirements')
        }),
        ('Status & Visibility', {
            'fields': ('status', 'is_featured', 'is_public')
        }),
        ('Contact & Media', {
            'fields': ('contact_email', 'contact_phone', 'featured_image', 'service_brochure')
        }),
        ('Metadata', {
            'fields': ('tags', 'created_at', 'updated_at')
        }),
    )

    def availability_status(self, obj):
        if obj.is_available:
            color = 'green'
            text = f'Available ({obj.current_requests}/{obj.max_concurrent_requests})'
        else:
            color = 'red'
            text = f'At Capacity ({obj.current_requests}/{obj.max_concurrent_requests})'
        return format_html(
            '<span style="color: {};">{}</span>',
            color, text
        )
    availability_status.short_description = 'Availability'


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = [
        'client_id', 'name', 'organization', 'client_type', 'email',
        'is_active', 'total_requests', 'total_spent', 'registration_date'
    ]
    list_filter = ['client_type', 'is_active', 'payment_terms', 'registration_date']
    search_fields = ['name', 'organization', 'email', 'client_id']
    readonly_fields = ['total_requests', 'total_spent', 'registration_date', 'created_at', 'updated_at']

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'organization', 'client_type', 'client_id')
        }),
        ('Contact Information', {
            'fields': ('email', 'phone', 'address', 'position', 'department', 'website')
        }),
        ('Account Information', {
            'fields': ('registration_date', 'is_active')
        }),
        ('Billing Information', {
            'fields': ('billing_address', 'tax_id', 'payment_terms')
        }),
        ('Statistics', {
            'fields': ('total_requests', 'total_spent')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


class ServiceRequestInline(admin.TabularInline):
    model = ServiceRequest
    extra = 0
    fields = ['request_id', 'title', 'status', 'priority', 'requested_date', 'estimated_cost']
    readonly_fields = ['request_id', 'requested_date']


@admin.register(TechnicianAssignment)
class TechnicianAssignmentAdmin(admin.ModelAdmin):
    list_display = [
        'technician', 'service', 'role', 'is_active', 'workload_display',
        'total_completed', 'start_date'
    ]
    list_filter = ['role', 'is_active', 'service__category', 'start_date']
    search_fields = ['technician__first_name', 'technician__last_name', 'service__name']
    readonly_fields = ['current_requests', 'total_completed', 'workload_percentage', 'created_at', 'updated_at']

    fieldsets = (
        ('Assignment Details', {
            'fields': ('service', 'technician', 'role', 'is_active')
        }),
        ('Schedule', {
            'fields': ('start_date', 'end_date')
        }),
        ('Workload', {
            'fields': ('max_concurrent_requests', 'current_requests', 'workload_percentage')
        }),
        ('Performance', {
            'fields': ('total_completed', 'average_completion_time')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )

    def workload_display(self, obj):
        percentage = obj.workload_percentage
        if percentage >= 90:
            color = 'red'
        elif percentage >= 70:
            color = 'orange'
        else:
            color = 'green'
        return format_html(
            '<span style="color: {};">{:.1f}% ({}/{})</span>',
            color, percentage, obj.current_requests, obj.max_concurrent_requests
        )
    workload_display.short_description = 'Workload'


@admin.register(ServiceRequest)
class ServiceRequestAdmin(admin.ModelAdmin):
    list_display = [
        'request_id', 'title', 'service', 'client', 'assigned_technician',
        'status', 'priority', 'requested_date', 'cost_display', 'is_paid'
    ]
    list_filter = [
        'status', 'priority', 'urgency', 'is_paid', 'service__category',
        'requested_date', 'preferred_completion_date'
    ]
    search_fields = ['request_id', 'title', 'description', 'client__name', 'service__name']
    readonly_fields = [
        'requested_date', 'is_overdue', 'duration_in_progress', 'total_duration',
        'created_at', 'updated_at'
    ]

    fieldsets = (
        ('Request Information', {
            'fields': ('request_id', 'service', 'client', 'title', 'description')
        }),
        ('Sample Details', {
            'fields': ('sample_description', 'quantity')
        }),
        ('Priority & Scheduling', {
            'fields': ('priority', 'urgency', 'requested_date', 'preferred_completion_date')
        }),
        ('Assignment & Status', {
            'fields': ('assigned_technician', 'status', 'started_date', 'completed_date')
        }),
        ('Pricing', {
            'fields': ('estimated_cost', 'final_cost', 'is_paid', 'payment_date')
        }),
        ('Files', {
            'fields': ('request_documents', 'results_file')
        }),
        ('Communication', {
            'fields': ('client_notes', 'internal_notes')
        }),
        ('Review', {
            'fields': ('reviewed_by', 'review_date', 'review_notes')
        }),
        ('Performance Metrics', {
            'fields': ('is_overdue', 'duration_in_progress', 'total_duration')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )

    def cost_display(self, obj):
        if obj.final_cost:
            return f"${obj.final_cost}"
        elif obj.estimated_cost:
            return f"~${obj.estimated_cost}"
        return "Not set"
    cost_display.short_description = 'Cost'

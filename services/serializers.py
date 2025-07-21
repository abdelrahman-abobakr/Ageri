from rest_framework import serializers
from django.utils import timezone
from accounts.serializers import UserListSerializer
from organization.serializers import DepartmentListSerializer, LabListSerializer
from .models import TestService, Client, TechnicianAssignment, ServiceRequest


class TestServiceListSerializer(serializers.ModelSerializer):
    """Simplified serializer for service lists"""
    department_name = serializers.CharField(source='department.name', read_only=True)
    lab_name = serializers.CharField(source='lab.name', read_only=True)
    technician_count = serializers.SerializerMethodField()
    
    class Meta:
        model = TestService
        fields = [
            'id', 'name', 'short_description', 'service_code', 'category',
            'department_name', 'lab_name', 'base_price', 'is_free',
            'estimated_duration', 'status', 'is_featured', 'is_public',
            'is_available', 'is_at_capacity', 'availability_percentage',
            'technician_count', 'current_requests', 'max_concurrent_requests'
        ]
    
    def get_technician_count(self, obj):
        return obj.technician_assignments.filter(is_active=True).count()


class TestServiceDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for service details"""
    department = DepartmentListSerializer(read_only=True)
    lab = LabListSerializer(read_only=True)
    technicians = serializers.SerializerMethodField()
    request_count = serializers.SerializerMethodField()
    
    class Meta:
        model = TestService
        fields = [
            'id', 'name', 'description', 'short_description', 'service_code',
            'category', 'department', 'lab', 'technicians', 'base_price',
            'is_free', 'pricing_structure', 'estimated_duration',
            'sample_requirements', 'equipment_used', 'methodology',
            'max_concurrent_requests', 'current_requests', 'required_documents',
            'safety_requirements', 'status', 'is_featured', 'is_public',
            'contact_email', 'contact_phone', 'featured_image',
            'service_brochure', 'tags', 'is_available', 'is_at_capacity',
            'availability_percentage', 'request_count', 'created_at', 'updated_at'
        ]
    
    def get_technicians(self, obj):
        assignments = obj.technician_assignments.filter(is_active=True)
        return TechnicianAssignmentSerializer(assignments, many=True).data
    
    def get_request_count(self, obj):
        return obj.requests.count()


class TestServiceCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating services"""
    
    class Meta:
        model = TestService
        fields = [
            'name', 'description', 'short_description', 'service_code',
            'category', 'department', 'lab', 'base_price', 'is_free',
            'pricing_structure', 'estimated_duration', 'sample_requirements',
            'equipment_used', 'methodology', 'max_concurrent_requests',
            'required_documents', 'safety_requirements', 'status',
            'is_featured', 'is_public', 'contact_email', 'contact_phone',
            'featured_image', 'service_brochure', 'tags'
        ]
    
    def validate_service_code(self, value):
        """Validate service code uniqueness"""
        if self.instance and self.instance.service_code == value:
            return value
        if TestService.objects.filter(service_code=value).exists():
            raise serializers.ValidationError("Service code must be unique.")
        return value


class ClientListSerializer(serializers.ModelSerializer):
    """Simplified serializer for client lists"""
    
    class Meta:
        model = Client
        fields = [
            'id', 'name', 'organization', 'client_type', 'email',
            'phone', 'client_id', 'registration_date', 'is_active',
            'total_requests', 'total_spent'
        ]


class ClientDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for client details"""
    recent_requests = serializers.SerializerMethodField()
    
    class Meta:
        model = Client
        fields = [
            'id', 'name', 'organization', 'client_type', 'email', 'phone',
            'address', 'position', 'department', 'website', 'client_id',
            'registration_date', 'is_active', 'billing_address', 'tax_id',
            'payment_terms', 'notes', 'total_requests', 'total_spent',
            'full_contact_info', 'recent_requests', 'created_at', 'updated_at'
        ]
    
    def get_recent_requests(self, obj):
        recent = obj.service_requests.all()[:5]
        return ServiceRequestListSerializer(recent, many=True).data


class ClientCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating clients"""
    
    class Meta:
        model = Client
        fields = [
            'name', 'organization', 'client_type', 'email', 'phone',
            'address', 'position', 'department', 'website', 'client_id',
            'is_active', 'billing_address', 'tax_id', 'payment_terms', 'notes'
        ]
    
    def validate_client_id(self, value):
        """Validate client ID uniqueness"""
        if self.instance and self.instance.client_id == value:
            return value
        if Client.objects.filter(client_id=value).exists():
            raise serializers.ValidationError("Client ID must be unique.")
        return value


class TechnicianAssignmentSerializer(serializers.ModelSerializer):
    """Serializer for technician assignments"""
    technician = UserListSerializer(read_only=True)
    service_name = serializers.CharField(source='service.name', read_only=True)
    
    class Meta:
        model = TechnicianAssignment
        fields = [
            'id', 'service', 'service_name', 'technician', 'role',
            'is_active', 'start_date', 'end_date', 'max_concurrent_requests',
            'current_requests', 'total_completed', 'average_completion_time',
            'notes', 'is_available', 'workload_percentage'
        ]


class TechnicianAssignmentCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating technician assignments"""
    
    class Meta:
        model = TechnicianAssignment
        fields = [
            'service', 'technician', 'role', 'is_active', 'start_date',
            'end_date', 'max_concurrent_requests', 'notes'
        ]
    
    def validate(self, data):
        """Validate assignment constraints"""
        if data.get('end_date') and data.get('start_date'):
            if data['end_date'] < data['start_date']:
                raise serializers.ValidationError("End date cannot be before start date.")
        return data


class ServiceRequestListSerializer(serializers.ModelSerializer):
    """Simplified serializer for request lists"""
    service_name = serializers.CharField(source='service.name', read_only=True)
    client_name = serializers.CharField(source='client.name', read_only=True)
    assigned_technician_name = serializers.CharField(
        source='assigned_technician.get_full_name', 
        read_only=True
    )
    
    class Meta:
        model = ServiceRequest
        fields = [
            'id', 'request_id', 'title', 'service_name', 'client_name',
            'assigned_technician_name', 'priority', 'urgency', 'status',
            'requested_date', 'preferred_completion_date', 'estimated_cost',
            'final_cost', 'is_paid', 'is_overdue'
        ]


class ServiceRequestDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for request details"""
    service = TestServiceListSerializer(read_only=True)
    client = ClientListSerializer(read_only=True)
    assigned_technician = UserListSerializer(read_only=True)
    reviewed_by = UserListSerializer(read_only=True)
    
    class Meta:
        model = ServiceRequest
        fields = [
            'id', 'request_id', 'service', 'client', 'assigned_technician',
            'title', 'description', 'sample_description', 'quantity',
            'priority', 'urgency', 'requested_date', 'preferred_completion_date',
            'started_date', 'completed_date', 'status', 'estimated_cost',
            'final_cost', 'is_paid', 'payment_date', 'request_documents',
            'results_file', 'client_notes', 'internal_notes', 'reviewed_by',
            'review_date', 'review_notes', 'is_overdue', 'duration_in_progress',
            'total_duration', 'created_at', 'updated_at'
        ]


class ServiceRequestCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating service requests"""
    request_id = serializers.CharField(required=False)

    class Meta:
        model = ServiceRequest
        fields = [
            'request_id', 'service', 'client', 'assigned_technician', 'title',
            'description', 'sample_description', 'quantity', 'priority',
            'urgency', 'preferred_completion_date', 'status', 'estimated_cost',
            'final_cost', 'is_paid', 'payment_date', 'request_documents',
            'results_file', 'client_notes', 'internal_notes', 'review_notes'
        ]
    
    def validate_request_id(self, value):
        """Validate request ID uniqueness"""
        if self.instance and self.instance.request_id == value:
            return value
        if ServiceRequest.objects.filter(request_id=value).exists():
            raise serializers.ValidationError("Request ID must be unique.")
        return value
    
    def validate(self, data):
        """Validate request constraints"""
        if data.get('preferred_completion_date'):
            if data['preferred_completion_date'] < timezone.now().date():
                raise serializers.ValidationError(
                    "Preferred completion date cannot be in the past."
                )
        return data

    def create(self, validated_data):
        """Auto-generate request_id if not provided"""
        if not validated_data.get('request_id'):
            # Generate a unique request ID
            import uuid
            validated_data['request_id'] = f"SR{timezone.now().year}-{str(uuid.uuid4())[:8].upper()}"
        return super().create(validated_data)

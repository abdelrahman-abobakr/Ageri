from rest_framework import serializers
from django.utils import timezone
from accounts.serializers import UserListSerializer
from .models import Department, Lab, ResearcherAssignment, OrganizationSettings


class DepartmentListSerializer(serializers.ModelSerializer):
    """Simplified serializer for department lists"""
    head_name = serializers.CharField(source='head.get_full_name', read_only=True)

    class Meta:
        model = Department
        fields = [
            'id', 'name', 'head_name', 'total_labs',
            'total_researchers', 'status', 'created_at'
        ]


class DepartmentInfoSerializer(serializers.ModelSerializer):
    """Minimal serializer for department info - only labs and short description"""
    labs = serializers.SerializerMethodField()

    class Meta:
        model = Department
        fields = ['id', 'name', 'description', 'labs']

    def get_labs(self, obj):
        """Get simplified lab information"""
        labs = obj.labs.filter(status='active').select_related('head')
        return LabInfoSerializer(labs, many=True).data


class DepartmentSerializer(serializers.ModelSerializer):
    """Full serializer for department details"""
    head = UserListSerializer(read_only=True)
    head_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    total_labs = serializers.ReadOnlyField()
    total_researchers = serializers.ReadOnlyField()
    
    class Meta:
        model = Department
        fields = [
            'id', 'name', 'description', 'head', 'head_id',
            'email', 'phone', 'location', 'status',
            'total_labs', 'total_researchers',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def validate_head_id(self, value):
        if value:
            from accounts.models import User, UserRole
            try:
                user = User.objects.get(id=value)
                if user.role not in [UserRole.ADMIN, UserRole.MODERATOR]:
                    raise serializers.ValidationError(
                        "Department head must be an admin or moderator"
                    )
                return value
            except User.DoesNotExist:
                raise serializers.ValidationError("User not found")
        return value
    
    def create(self, validated_data):
        head_id = validated_data.pop('head_id', None)
        department = Department.objects.create(**validated_data)
        if head_id:
            from accounts.models import User
            department.head = User.objects.get(id=head_id)
            department.save()
        return department
    
    def update(self, instance, validated_data):
        head_id = validated_data.pop('head_id', None)
        if head_id is not None:
            if head_id:
                from accounts.models import User
                instance.head = User.objects.get(id=head_id)
            else:
                instance.head = None
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class LabListSerializer(serializers.ModelSerializer):
    """Simplified serializer for lab lists"""
    department_name = serializers.CharField(source='department.name', read_only=True)
    head_name = serializers.CharField(source='head.get_full_name', read_only=True)

    class Meta:
        model = Lab
        fields = [
            'id', 'name', 'department_name', 'head_name',
            'current_researchers_count', 'capacity', 'available_spots',
            'status', 'created_at'
        ]


class LabInfoSerializer(serializers.ModelSerializer):
    """Minimal serializer for lab info - only basic details"""
    head_name = serializers.CharField(source='head.get_full_name', read_only=True)
    researchers = serializers.SerializerMethodField()

    class Meta:
        model = Lab
        fields = ['id', 'name', 'description', 'head_name', 'researchers']

    def get_researchers(self, obj):
        """Get researchers in this lab"""
        assignments = obj.researcher_assignments.filter(status='active').select_related('researcher')
        return [
            {
                'id': assignment.researcher.id,
                'name': assignment.researcher.get_full_name(),
                'position': assignment.position or 'Researcher'
            }
            for assignment in assignments
        ]


class LabSerializer(serializers.ModelSerializer):
    """Full serializer for lab details"""
    department = DepartmentListSerializer(read_only=True)
    department_id = serializers.IntegerField(write_only=True)
    head = UserListSerializer(read_only=True)
    head_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    current_researchers_count = serializers.ReadOnlyField()
    available_spots = serializers.ReadOnlyField()
    is_at_capacity = serializers.ReadOnlyField()
    
    class Meta:
        model = Lab
        fields = [
            'id', 'name', 'department', 'department_id', 'description',
            'head', 'head_id', 'equipment', 'capacity', 'phone',
            'current_researchers_count', 'available_spots', 'is_at_capacity',
            'status', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def validate_head_id(self, value):
        if value:
            from accounts.models import User, UserRole
            try:
                user = User.objects.get(id=value)
                if user.role not in [UserRole.ADMIN, UserRole.MODERATOR, UserRole.RESEARCHER]:
                    raise serializers.ValidationError(
                        "Lab head must be an admin, moderator, or researcher"
                    )
                return value
            except User.DoesNotExist:
                raise serializers.ValidationError("User not found")
        return value
    
    def validate_capacity(self, value):
        if value < 1:
            raise serializers.ValidationError("Capacity must be at least 1")
        return value
    
    def create(self, validated_data):
        head_id = validated_data.pop('head_id', None)
        lab = Lab.objects.create(**validated_data)
        if head_id:
            from accounts.models import User
            lab.head = User.objects.get(id=head_id)
            lab.save()
        return lab
    
    def update(self, instance, validated_data):
        head_id = validated_data.pop('head_id', None)
        if head_id is not None:
            if head_id:
                from accounts.models import User
                instance.head = User.objects.get(id=head_id)
            else:
                instance.head = None
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class ResearcherAssignmentSerializer(serializers.ModelSerializer):
    """Serializer for researcher assignments"""
    researcher = UserListSerializer(read_only=True)
    researcher_id = serializers.IntegerField(write_only=True)
    lab = LabListSerializer(read_only=True)
    lab_id = serializers.IntegerField(write_only=True)
    department = DepartmentListSerializer(read_only=True)
    department_id = serializers.IntegerField(write_only=True)
    assigned_by = UserListSerializer(read_only=True)
    duration_days = serializers.ReadOnlyField()
    is_active = serializers.ReadOnlyField()
    
    class Meta:
        model = ResearcherAssignment
        fields = [
            'id', 'researcher', 'researcher_id', 'lab', 'lab_id',
            'department', 'department_id', 'start_date', 'end_date',
            'position', 'status', 'assigned_by', 'notes',
            'duration_days', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'assigned_by']
    
    def validate_researcher_id(self, value):
        from accounts.models import User, UserRole
        try:
            user = User.objects.get(id=value)
            if user.role != UserRole.RESEARCHER:
                raise serializers.ValidationError("Only researchers can be assigned to labs")
            if not user.is_approved:
                raise serializers.ValidationError("Researcher must be approved")
            return value
        except User.DoesNotExist:
            raise serializers.ValidationError("Researcher not found")
    
    def validate(self, attrs):
        # Validate dates
        if attrs.get('end_date') and attrs.get('start_date'):
            if attrs['end_date'] <= attrs['start_date']:
                raise serializers.ValidationError("End date must be after start date")
        
        # Validate lab capacity
        lab_id = attrs.get('lab_id')
        if lab_id:
            try:
                lab = Lab.objects.get(id=lab_id)
                if lab.is_at_capacity:
                    # Check if this is an update of existing assignment
                    if not self.instance:
                        raise serializers.ValidationError("Lab is at full capacity")
                
                # Ensure department matches lab's department
                department_id = attrs.get('department_id')
                if department_id and department_id != lab.department.id:
                    raise serializers.ValidationError(
                        "Department must match the lab's department"
                    )
                
                # Auto-set department if not provided
                if not department_id:
                    attrs['department_id'] = lab.department.id
                    
            except Lab.DoesNotExist:
                raise serializers.ValidationError("Lab not found")
        
        return attrs
    
    def create(self, validated_data):
        # Set assigned_by to current user
        validated_data['assigned_by'] = self.context['request'].user
        return super().create(validated_data)


class ResearcherAssignmentListSerializer(serializers.ModelSerializer):
    """Simplified serializer for assignment lists with profile linking"""
    researcher_name = serializers.CharField(source='researcher.get_full_name', read_only=True)
    researcher_email = serializers.CharField(source='researcher.email', read_only=True)
    researcher_profile = serializers.SerializerMethodField()
    lab_name = serializers.CharField(source='lab.name', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)

    class Meta:
        model = ResearcherAssignment
        fields = [
            'id', 'researcher_id', 'researcher_name', 'researcher_email', 'researcher_profile',
            'lab_name', 'department_name', 'position', 'start_date', 'end_date',
            'status', 'is_active', 'created_at'
        ]

    def get_researcher_profile(self, obj):
        """Get researcher profile information"""
        researcher = obj.researcher
        profile_data = {
            'id': researcher.id,
            'username': researcher.username,
            'full_name': researcher.get_full_name(),
            'email': researcher.email,
            'role': researcher.role,
            'institution': researcher.institution,
            'phone': researcher.phone,
            'is_approved': researcher.is_approved,
            'date_joined': researcher.date_joined
        }

        # Add profile details if available
        if hasattr(researcher, 'profile'):
            profile = researcher.profile
            profile_data.update({
                'bio': profile.bio,
                'research_interests': profile.research_interests,
                'orcid_id': profile.orcid_id,
                'website': profile.website,
                'linkedin': profile.linkedin,
                'google_scholar': profile.google_scholar,
                'researchgate': profile.researchgate,
                'has_cv': profile.has_cv,
                'is_public': profile.is_public
            })

        return profile_data


class OrganizationSettingsSerializer(serializers.ModelSerializer):
    """Serializer for organization settings"""

    class Meta:
        model = OrganizationSettings
        fields = [
            'id', 'name', 'vision', 'vision_image', 'mission', 'mission_image', 'about',
            'email', 'phone', 'address',
            'website', 'facebook', 'twitter', 'linkedin', 'instagram',
            'logo', 'banner', 'enable_registration', 'require_approval',
            'maintenance_mode', 'maintenance_message',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class OrganizationPublicSerializer(serializers.ModelSerializer):
    """Public serializer for organization settings (limited fields)"""

    class Meta:
        model = OrganizationSettings
        fields = [
            'name', 'vision', 'vision_image', 'mission', 'mission_image', 'about',
            'email', 'phone', 'address',
            'website', 'facebook', 'twitter', 'linkedin', 'instagram',
            'logo', 'banner', 'enable_registration'
        ]

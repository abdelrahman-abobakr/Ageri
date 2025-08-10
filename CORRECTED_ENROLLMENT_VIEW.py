# CORRECTED ENROLLMENT VIEW - Copy this to your training/views.py

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.db import transaction
from .models import Course, CourseEnrollment
from .serializers import CourseSerializer, GuestEnrollmentSerializer, EnrollmentDetailSerializer

class CourseViewSet(viewsets.ModelViewSet):
    """ViewSet for managing courses"""
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    
    @action(
        detail=True, 
        methods=['post'], 
        permission_classes=[AllowAny],  # No authentication required
        url_path='enroll'
    )
    def enroll(self, request, pk=None):
        """Guest enrollment in course - no authentication required"""
        try:
            course = self.get_object()
            
            # Add course to the data
            enrollment_data = request.data.copy()
            enrollment_data['course'] = course.id
            
            # Create enrollment using serializer
            serializer = GuestEnrollmentSerializer(data=enrollment_data)
            
            if serializer.is_valid():
                with transaction.atomic():
                    enrollment = serializer.save()
                
                return Response({
                    'message': 'Successfully enrolled in course',
                    'enrollment': EnrollmentDetailSerializer(enrollment).data,
                    'enrollment_token': enrollment.enrollment_token,
                    'payment_amount': course.cost if not course.is_free else 0,  # ✅ FIXED: Use 'cost' not 'price'
                    'next_steps': [
                        'Save your enrollment ID for future reference',
                        'Check course start date and prepare materials',
                        'Contact support if you have questions'
                    ]
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    'error': 'Invalid enrollment data',
                    'details': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Course.DoesNotExist:
            return Response({
                'error': 'Course not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'error': 'An unexpected error occurred',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(
        detail=False,
        methods=['get'],
        permission_classes=[AllowAny],
        url_path='enrollment/(?P<token>[^/.]+)'
    )
    def get_enrollment(self, request, token=None):
        """Get enrollment details by token (for guests)"""
        try:
            enrollment = CourseEnrollment.objects.select_related('course').get(
                enrollment_token=token
            )
            serializer = EnrollmentDetailSerializer(enrollment)
            return Response(serializer.data)
        except CourseEnrollment.DoesNotExist:
            return Response({
                'error': 'Enrollment not found'
            }, status=status.HTTP_404_NOT_FOUND)

# INSTRUCTIONS:
# 1. Copy the enroll method above (lines 18-58)
# 2. Replace your current enroll method in training/views.py
# 3. The key change is on line 32: course.cost instead of course.price
# 4. Save the file and restart your Django server

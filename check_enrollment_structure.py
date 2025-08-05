#!/usr/bin/env python3
"""
Check enrollment data structure directly from database
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'research_platform.settings')
django.setup()

from training.models import CourseEnrollment
from training.serializers import CourseEnrollmentSerializer
import json

def check_enrollment_structure():
    """Check the enrollment data structure"""
    print("🔍 Checking Enrollment Data Structure")
    print("=" * 60)
    
    # Get all enrollments
    enrollments = CourseEnrollment.objects.all()
    print(f"📊 Total enrollments in database: {enrollments.count()}")
    
    if enrollments.exists():
        # Get the first enrollment
        enrollment = enrollments.first()
        print(f"\n📋 Sample enrollment (ID: {enrollment.id}):")
        
        # Show raw model data
        print("\n🔧 Raw model fields:")
        model_fields = [
            'id', 'course_id', 'student_id', 'first_name', 'last_name', 
            'email', 'phone', 'organization', 'job_title', 'enrollment_token',
            'status', 'payment_status', 'payment_amount', 'grade',
            'attendance_percentage', 'certificate_issued', 'notes'
        ]
        
        for field in model_fields:
            try:
                value = getattr(enrollment, field, 'NOT_FOUND')
                print(f"   {field}: {value}")
            except Exception as e:
                print(f"   {field}: ERROR - {e}")
        
        # Show helper properties
        print("\n🔧 Helper properties:")
        helper_properties = [
            'enrollee_name', 'enrollee_email', 'is_guest_enrollment', 'is_active'
        ]
        
        for prop in helper_properties:
            try:
                value = getattr(enrollment, prop, 'NOT_FOUND')
                print(f"   {prop}: {value}")
            except Exception as e:
                print(f"   {prop}: ERROR - {e}")
        
        # Show serialized data
        print("\n📡 Serialized data (API response):")
        try:
            serializer = CourseEnrollmentSerializer(enrollment)
            serialized_data = serializer.data
            print(json.dumps(serialized_data, indent=2, default=str))
            
            # Check for missing fields
            expected_fields = [
                'first_name', 'last_name', 'email', 'phone', 
                'enrollee_name', 'enrollee_email', 'is_guest_enrollment'
            ]
            
            print("\n✅ Field availability check:")
            for field in expected_fields:
                if field in serialized_data:
                    value = serialized_data[field]
                    print(f"   ✅ {field}: {value}")
                else:
                    print(f"   ❌ {field}: MISSING")
                    
        except Exception as e:
            print(f"❌ Serialization error: {e}")
    
    else:
        print("📭 No enrollments found in database")
        print("\n💡 Creating a test enrollment...")
        
        # Create a test enrollment
        from training.models import Course
        
        try:
            course = Course.objects.first()
            if course:
                enrollment = CourseEnrollment.objects.create(
                    course=course,
                    first_name="Test",
                    last_name="User",
                    email="test@example.com",
                    phone="123456789",
                    organization="Test Org",
                    job_title="Tester",
                    status="approved"
                )
                print(f"✅ Created test enrollment with ID: {enrollment.id}")
                
                # Now check the structure
                print("\n📋 Test enrollment structure:")
                serializer = CourseEnrollmentSerializer(enrollment)
                print(json.dumps(serializer.data, indent=2, default=str))
                
            else:
                print("❌ No courses found to create test enrollment")
                
        except Exception as e:
            print(f"❌ Error creating test enrollment: {e}")

def check_course_enrollments_endpoint():
    """Check what the course enrollments endpoint returns"""
    print("\n🎓 Checking Course Enrollments Endpoint Structure")
    print("=" * 60)
    
    from training.models import Course
    
    try:
        course = Course.objects.first()
        if course:
            enrollments = course.enrollments.all()
            print(f"📊 Course '{course.title}' has {enrollments.count()} enrollments")
            
            if enrollments.exists():
                serializer = CourseEnrollmentSerializer(enrollments, many=True)
                print("\n📡 Course enrollments API data:")
                print(json.dumps(serializer.data, indent=2, default=str))
            else:
                print("📭 No enrollments for this course")
        else:
            print("❌ No courses found")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🧪 Enrollment Data Structure Check")
    print("=" * 70)
    
    check_enrollment_structure()
    check_course_enrollments_endpoint()
    
    print("\n" + "=" * 70)
    print("📝 Summary:")
    print("• This script checks the actual database structure")
    print("• Shows what fields are available in the serializer")
    print("• Identifies any missing fields in API responses")
    print("• Helps debug frontend data access issues")

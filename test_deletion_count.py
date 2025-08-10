#!/usr/bin/env python3
"""
Test enrollment deletion and count updates
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'research_platform.settings')
django.setup()

from training.models import Course, CourseEnrollment

def test_deletion_count():
    """Test that deleting enrollments updates the count"""
    print("🗑️ Testing Enrollment Deletion Count Updates")
    print("=" * 60)
    
    # Get the course
    course = Course.objects.get(id=6)
    print(f"📚 Course: {course.course_name}")
    
    # Check current state
    initial_count = course.current_enrollment
    actual_enrollments = CourseEnrollment.objects.filter(course=course)
    
    print(f"📊 Current enrollment count: {initial_count}")
    print(f"📋 Actual enrollments in database: {actual_enrollments.count()}")
    
    if actual_enrollments.exists():
        print(f"\n📝 Current enrollments:")
        for enrollment in actual_enrollments:
            print(f"   ID: {enrollment.id} - {enrollment.enrollee_name} ({enrollment.enrollee_email})")
        
        # Test deletion
        print(f"\n🗑️ Deleting enrollment ID: {actual_enrollments.first().id}")
        enrollment_to_delete = actual_enrollments.first()
        enrollment_to_delete.delete()
        
        # Check count after deletion
        course.refresh_from_db()
        new_count = course.current_enrollment
        remaining_enrollments = CourseEnrollment.objects.filter(course=course).count()
        
        print(f"📊 Count after deletion: {new_count}")
        print(f"📋 Remaining enrollments: {remaining_enrollments}")
        
        if new_count == initial_count - 1:
            print("✅ Deletion count update works correctly!")
        else:
            print(f"❌ Expected {initial_count - 1}, got {new_count}")
        
        if new_count == remaining_enrollments:
            print("✅ Count matches actual enrollments!")
        else:
            print(f"❌ Count mismatch: stored={new_count}, actual={remaining_enrollments}")
    
    else:
        print("📭 No enrollments found to test deletion")

if __name__ == "__main__":
    test_deletion_count()

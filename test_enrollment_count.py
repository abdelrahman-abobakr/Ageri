#!/usr/bin/env python3
"""
Test script to verify enrollment count updates work correctly
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'research_platform.settings')
django.setup()

from training.models import Course, CourseEnrollment
from django.db import transaction

def test_enrollment_count_updates():
    """Test that enrollment counts update correctly when enrollments are created/deleted"""
    print("🧪 Testing Enrollment Count Updates")
    print("=" * 60)
    
    # Get or create a test course
    try:
        course = Course.objects.first()
        if not course:
            print("❌ No courses found. Please create a course first.")
            return
        
        print(f"📚 Testing with course: {course.course_name} (ID: {course.id})")
        
        # Get initial enrollment count
        initial_count = course.current_enrollment
        print(f"📊 Initial enrollment count: {initial_count}")
        
        # Test 1: Create an enrollment
        print("\n1️⃣ Testing enrollment creation...")
        enrollment = CourseEnrollment.objects.create(
            course=course,
            first_name="Test",
            last_name="User",
            email="test.count@example.com",
            phone="123456789",
            status="approved"
        )
        
        # Refresh course from database
        course.refresh_from_db()
        new_count = course.current_enrollment
        print(f"   ✅ Created enrollment ID: {enrollment.id}")
        print(f"   📊 New enrollment count: {new_count}")
        
        if new_count == initial_count + 1:
            print("   ✅ Count increased correctly!")
        else:
            print(f"   ❌ Count should be {initial_count + 1}, but got {new_count}")
        
        # Test 2: Delete the enrollment
        print("\n2️⃣ Testing enrollment deletion...")
        enrollment_id = enrollment.id
        enrollment.delete()
        
        # Refresh course from database
        course.refresh_from_db()
        final_count = course.current_enrollment
        print(f"   ✅ Deleted enrollment ID: {enrollment_id}")
        print(f"   📊 Final enrollment count: {final_count}")
        
        if final_count == initial_count:
            print("   ✅ Count decreased correctly!")
        else:
            print(f"   ❌ Count should be {initial_count}, but got {final_count}")
        
        # Test 3: Multiple enrollments
        print("\n3️⃣ Testing multiple enrollments...")
        enrollments = []
        for i in range(3):
            enrollment = CourseEnrollment.objects.create(
                course=course,
                first_name=f"Test{i}",
                last_name="User",
                email=f"test{i}.count@example.com",
                phone=f"12345678{i}",
                status="approved"
            )
            enrollments.append(enrollment)
        
        course.refresh_from_db()
        multi_count = course.current_enrollment
        print(f"   ✅ Created 3 enrollments")
        print(f"   📊 Count after adding 3: {multi_count}")
        
        if multi_count == initial_count + 3:
            print("   ✅ Multiple enrollments counted correctly!")
        else:
            print(f"   ❌ Count should be {initial_count + 3}, but got {multi_count}")
        
        # Clean up
        print("\n🧹 Cleaning up test enrollments...")
        for enrollment in enrollments:
            enrollment.delete()
        
        course.refresh_from_db()
        cleanup_count = course.current_enrollment
        print(f"   📊 Count after cleanup: {cleanup_count}")
        
        if cleanup_count == initial_count:
            print("   ✅ Cleanup successful!")
        else:
            print(f"   ❌ Count should be {initial_count}, but got {cleanup_count}")
        
        print(f"\n🎯 Summary:")
        print(f"   Initial count: {initial_count}")
        print(f"   Final count: {cleanup_count}")
        print(f"   Test result: {'✅ PASSED' if cleanup_count == initial_count else '❌ FAILED'}")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

def test_api_enrollment_count():
    """Test enrollment count through API (simulated)"""
    print("\n🌐 Testing API Enrollment Count Updates")
    print("=" * 60)
    
    try:
        course = Course.objects.first()
        if not course:
            print("❌ No courses found.")
            return
        
        initial_count = course.current_enrollment
        print(f"📚 Course: {course.course_name}")
        print(f"📊 Initial count: {initial_count}")
        
        # Simulate API enrollment creation (like the guest enrollment endpoint)
        print("\n📝 Simulating API enrollment...")
        
        enrollment_data = {
            'course': course,
            'first_name': 'API',
            'last_name': 'Test',
            'email': 'api.test@example.com',
            'phone': '+1234567890',
            'organization': 'Test Org',
            'job_title': 'Tester',
            'status': 'approved'
        }
        
        # Create enrollment (this should trigger the signal)
        enrollment = CourseEnrollment.objects.create(**enrollment_data)
        
        # Check count
        course.refresh_from_db()
        api_count = course.current_enrollment
        print(f"   ✅ API enrollment created: {enrollment.id}")
        print(f"   📊 Count after API enrollment: {api_count}")
        
        if api_count == initial_count + 1:
            print("   ✅ API enrollment counted correctly!")
        else:
            print(f"   ❌ Expected {initial_count + 1}, got {api_count}")
        
        # Test deletion through admin action
        print("\n🗑️ Simulating admin deletion...")
        enrollment.delete()
        
        course.refresh_from_db()
        delete_count = course.current_enrollment
        print(f"   ✅ Enrollment deleted")
        print(f"   📊 Count after deletion: {delete_count}")
        
        if delete_count == initial_count:
            print("   ✅ Admin deletion counted correctly!")
        else:
            print(f"   ❌ Expected {initial_count}, got {delete_count}")
        
    except Exception as e:
        print(f"❌ Error during API testing: {e}")
        import traceback
        traceback.print_exc()

def show_current_enrollments():
    """Show current enrollment counts for all courses"""
    print("\n📊 Current Enrollment Counts")
    print("=" * 60)
    
    courses = Course.objects.all()
    
    if not courses.exists():
        print("📭 No courses found")
        return
    
    print(f"{'Course Name':<30} {'Code':<10} {'Count':<8} {'Max':<8} {'%':<8}")
    print("-" * 70)
    
    for course in courses:
        actual_count = CourseEnrollment.objects.filter(course=course).count()
        percentage = (course.current_enrollment / course.max_participants * 100) if course.max_participants > 0 else 0
        
        # Check if stored count matches actual count
        status = "✅" if course.current_enrollment == actual_count else "❌"
        
        print(f"{course.course_name[:29]:<30} {course.course_code:<10} {course.current_enrollment:<8} {course.max_participants:<8} {percentage:.1f}%  {status}")
        
        if course.current_enrollment != actual_count:
            print(f"   ⚠️ Mismatch: Stored={course.current_enrollment}, Actual={actual_count}")

if __name__ == "__main__":
    print("🧪 Enrollment Count Update Test")
    print("=" * 70)
    
    # Show current state
    show_current_enrollments()
    
    # Test enrollment count updates
    test_enrollment_count_updates()
    
    # Test API-style enrollment
    test_api_enrollment_count()
    
    # Show final state
    show_current_enrollments()
    
    print("\n" + "=" * 70)
    print("📝 Test completed!")
    print("💡 The enrollment count should now automatically update when:")
    print("   • New enrollments are created (guest or registered)")
    print("   • Enrollments are deleted by admin")
    print("   • Bulk operations are performed")

#!/usr/bin/env python
"""
Simple test script to verify the Course model works correctly
"""
import os
import sys
import django
from datetime import date, timedelta
from decimal import Decimal

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'research_platform.settings')
django.setup()

from training.models import Course, TrainingType

def test_course_creation():
    """Test creating a course with the new model structure"""
    print("Testing Course model creation...")
    
    # Create a test course
    course = Course.objects.create(
        course_name="Introduction to Python Programming",
        instructor="Dr. Ahmed Hassan",
        cost=Decimal('500.00'),
        start_date=date.today() + timedelta(days=30),
        end_date=date.today() + timedelta(days=60),
        registration_deadline=date.today() + timedelta(days=20),
        type=TrainingType.COURSE,
        training_hours=40,
        description="A comprehensive introduction to Python programming for beginners.",
        course_code="PY101",
        max_participants=25,
        prerequisites="Basic computer skills",
        materials_provided="Course materials and Python IDE setup guide"
    )
    
    print(f"✅ Course created successfully!")
    print(f"   Course Name: {course.course_name}")
    print(f"   Instructor: {course.instructor}")
    print(f"   Cost: ${course.cost}")
    print(f"   Training Hours: {course.training_hours}")
    print(f"   Start Date: {course.start_date}")
    print(f"   End Date: {course.end_date}")
    print(f"   Registration Deadline: {course.registration_deadline}")
    print(f"   Type: {course.get_type_display()}")
    print(f"   Is Free: {course.is_free}")
    print(f"   Can Register: {course.can_register()}")
    print(f"   Enrollment Percentage: {course.enrollment_percentage}%")
    
    return course

def test_course_properties():
    """Test course properties and methods"""
    print("\nTesting Course properties...")
    
    # Create a free course
    free_course = Course.objects.create(
        course_name="Free Web Development Workshop",
        instructor="Sarah Ahmed",
        cost=Decimal('0.00'),
        start_date=date.today() + timedelta(days=15),
        end_date=date.today() + timedelta(days=16),
        registration_deadline=date.today() + timedelta(days=10),
        type=TrainingType.WORKSHOP,
        training_hours=8,
        description="Free workshop on web development basics.",
        course_code="WEB001",
        status='published'
    )
    
    print(f"✅ Free course properties:")
    print(f"   Is Free: {free_course.is_free}")
    print(f"   Registration Open: {free_course.is_registration_open}")
    print(f"   Can Register: {free_course.can_register()}")
    
    return free_course

if __name__ == "__main__":
    print("🚀 Starting Course Model Tests\n")
    
    try:
        # Test course creation
        course1 = test_course_creation()
        
        # Test course properties
        course2 = test_course_properties()
        
        print(f"\n✅ All tests passed!")
        print(f"📊 Total courses created: {Course.objects.count()}")
        
        # Display all courses
        print("\n📋 All Courses:")
        for course in Course.objects.all():
            print(f"   - {course}")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        sys.exit(1)

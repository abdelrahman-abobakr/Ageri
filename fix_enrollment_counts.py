#!/usr/bin/env python3
"""
Script to fix enrollment count mismatches
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'research_platform.settings')
django.setup()

from training.models import Course, CourseEnrollment, SummerTraining, SummerTrainingApplication

def fix_course_enrollment_counts():
    """Fix course enrollment count mismatches"""
    print("🔧 Fixing Course Enrollment Counts")
    print("=" * 50)
    
    courses = Course.objects.all()
    fixed_count = 0
    
    for course in courses:
        # Get actual enrollment count
        actual_count = CourseEnrollment.objects.filter(course=course).count()
        stored_count = course.current_enrollment
        
        if actual_count != stored_count:
            print(f"📚 {course.course_name} ({course.course_code})")
            print(f"   Stored: {stored_count}, Actual: {actual_count}")
            
            # Update the stored count
            course.current_enrollment = actual_count
            course.save(update_fields=['current_enrollment'])
            
            print(f"   ✅ Fixed: Updated to {actual_count}")
            fixed_count += 1
        else:
            print(f"✅ {course.course_name}: {actual_count} (correct)")
    
    print(f"\n📊 Summary: Fixed {fixed_count} courses")
    return fixed_count

def fix_summer_training_counts():
    """Fix summer training enrollment count mismatches"""
    print("\n🔧 Fixing Summer Training Enrollment Counts")
    print("=" * 50)
    
    programs = SummerTraining.objects.all()
    fixed_count = 0
    
    for program in programs:
        # Get actual approved application count
        actual_count = SummerTrainingApplication.objects.filter(
            program=program, 
            status='approved'
        ).count()
        stored_count = program.current_enrollment
        
        if actual_count != stored_count:
            print(f"🏫 {program.title}")
            print(f"   Stored: {stored_count}, Actual: {actual_count}")
            
            # Update the stored count
            program.current_enrollment = actual_count
            program.save(update_fields=['current_enrollment'])
            
            print(f"   ✅ Fixed: Updated to {actual_count}")
            fixed_count += 1
        else:
            print(f"✅ {program.title}: {actual_count} (correct)")
    
    print(f"\n📊 Summary: Fixed {fixed_count} summer training programs")
    return fixed_count

def show_enrollment_summary():
    """Show enrollment summary after fixes"""
    print("\n📊 Enrollment Summary After Fixes")
    print("=" * 50)
    
    # Course summary
    courses = Course.objects.all()
    total_course_enrollments = sum(course.current_enrollment for course in courses)
    
    print(f"📚 Courses: {courses.count()}")
    print(f"👥 Total Course Enrollments: {total_course_enrollments}")
    
    # Summer training summary
    programs = SummerTraining.objects.all()
    total_summer_enrollments = sum(program.current_enrollment for program in programs)
    
    print(f"🏫 Summer Training Programs: {programs.count()}")
    print(f"👥 Total Summer Training Enrollments: {total_summer_enrollments}")
    
    print(f"\n🎯 Grand Total Enrollments: {total_course_enrollments + total_summer_enrollments}")

if __name__ == "__main__":
    print("🔧 Enrollment Count Fix Utility")
    print("=" * 60)
    
    # Fix course enrollment counts
    course_fixes = fix_course_enrollment_counts()
    
    # Fix summer training counts
    summer_fixes = fix_summer_training_counts()
    
    # Show summary
    show_enrollment_summary()
    
    print("\n" + "=" * 60)
    print("✅ Enrollment count fixes completed!")
    print(f"📊 Total fixes applied: {course_fixes + summer_fixes}")
    print("\n💡 From now on, enrollment counts will automatically update when:")
    print("   • New enrollments/applications are created")
    print("   • Enrollments/applications are deleted")
    print("   • Status changes occur (for summer training)")

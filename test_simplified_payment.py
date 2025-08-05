#!/usr/bin/env python3
"""
Test script for the simplified payment system
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'research_platform.settings')
django.setup()

from training.models import Course, CourseEnrollment, PaymentStatus, PaymentMethod
from decimal import Decimal

def test_simplified_payment_system():
    """Test the simplified payment system with only method, status, and amount"""
    print("💳 Testing Simplified Payment System")
    print("=" * 60)
    
    # Clean up any existing test enrollments
    CourseEnrollment.objects.filter(email='simplified.payment@example.com').delete()
    
    # Get a course
    course = Course.objects.first()
    if not course:
        print("❌ No courses found")
        return
    
    print(f"📚 Course: {course.course_name}")
    print(f"💰 Course Cost: ${course.cost}")
    
    # Test 1: Create enrollment with pending payment
    print(f"\n1️⃣ Test 1: Create Enrollment (Pending Payment)")
    enrollment = CourseEnrollment.objects.create(
        course=course,
        first_name="Simplified",
        last_name="Payment",
        email="simplified.payment@example.com",
        phone="555-0123",
        payment_amount=course.cost
    )
    
    print(f"   ✅ Enrollment created: ID {enrollment.id}")
    print(f"   💳 Payment Status: {enrollment.payment_status}")
    print(f"   💰 Payment Amount: ${enrollment.payment_amount}")
    print(f"   🔧 Payment Method: {enrollment.payment_method or 'Not set'}")
    
    # Test 2: Update payment with bank transfer
    print(f"\n2️⃣ Test 2: Process Bank Transfer Payment")
    enrollment.payment_status = PaymentStatus.PAID
    enrollment.payment_method = PaymentMethod.BANK_TRANSFER
    enrollment.save(update_fields=['payment_status', 'payment_method'])
    
    print(f"   ✅ Payment processed via: {enrollment.get_payment_method_display()}")
    print(f"   💳 Payment Status: {enrollment.get_payment_status_display()}")
    print(f"   💰 Amount: ${enrollment.payment_amount}")
    
    # Test 3: Test different payment methods
    print(f"\n3️⃣ Test 3: Testing Different Payment Methods")
    
    payment_scenarios = [
        (PaymentMethod.CASH, PaymentStatus.PAID, "Cash payment at office"),
        (PaymentMethod.CREDIT_CARD, PaymentStatus.PAID, "Credit card payment"),
        (PaymentMethod.MOBILE_PAYMENT, PaymentStatus.FAILED, "Mobile payment failed"),
        (PaymentMethod.CHECK, PaymentStatus.PENDING, "Check payment pending"),
        (PaymentMethod.OTHER, PaymentStatus.REFUNDED, "Other method refunded")
    ]
    
    test_enrollments = []
    for i, (method, status, description) in enumerate(payment_scenarios, 1):
        test_enrollment = CourseEnrollment.objects.create(
            course=course,
            first_name=f"Test{i}",
            last_name="User",
            email=f"test{i}.payment@example.com",
            phone=f"555-012{i}",
            payment_amount=course.cost,
            payment_method=method,
            payment_status=status
        )
        test_enrollments.append(test_enrollment)
        
        print(f"   {i}. {description}")
        print(f"      Method: {test_enrollment.get_payment_method_display()}")
        print(f"      Status: {test_enrollment.get_payment_status_display()}")
        print(f"      Amount: ${test_enrollment.payment_amount}")
    
    # Test 4: Payment summary
    print(f"\n4️⃣ Test 4: Payment Summary")
    
    all_test_enrollments = [enrollment] + test_enrollments
    
    # Group by payment method
    method_summary = {}
    status_summary = {}
    
    for enroll in all_test_enrollments:
        method = enroll.get_payment_method_display() or 'Not Set'
        status = enroll.get_payment_status_display()
        
        method_summary[method] = method_summary.get(method, 0) + 1
        status_summary[status] = status_summary.get(status, 0) + 1
    
    print(f"   📊 Payment Methods:")
    for method, count in method_summary.items():
        print(f"      {method}: {count}")
    
    print(f"   📊 Payment Status:")
    for status, count in status_summary.items():
        print(f"      {status}: {count}")
    
    # Calculate revenue
    paid_enrollments = [e for e in all_test_enrollments if e.payment_status == PaymentStatus.PAID]
    total_revenue = sum(e.payment_amount for e in paid_enrollments)
    
    print(f"   💰 Total Revenue: ${total_revenue}")
    print(f"   📈 Paid Enrollments: {len(paid_enrollments)}/{len(all_test_enrollments)}")
    
    # Test 5: API Response Structure
    print(f"\n5️⃣ Test 5: API Response Structure")
    
    from training.serializers import CourseEnrollmentSerializer
    
    serializer = CourseEnrollmentSerializer(enrollment)
    payment_fields = {
        'payment_status': serializer.data.get('payment_status'),
        'payment_method': serializer.data.get('payment_method'),
        'payment_amount': serializer.data.get('payment_amount')
    }
    
    print(f"   📡 API Payment Fields:")
    for field, value in payment_fields.items():
        print(f"      {field}: {value}")
    
    # Cleanup
    print(f"\n🧹 Cleaning up test enrollments...")
    CourseEnrollment.objects.filter(
        email__in=[e.email for e in all_test_enrollments]
    ).delete()
    print(f"   ✅ Deleted {len(all_test_enrollments)} test enrollments")

def show_payment_options():
    """Show available payment methods and statuses"""
    print(f"\n💳 Available Payment Options")
    print("=" * 50)
    
    print(f"📋 Payment Methods:")
    for method_code, method_label in PaymentMethod.choices:
        print(f"   {method_code}: {method_label}")
    
    print(f"\n📊 Payment Statuses:")
    for status_code, status_label in PaymentStatus.choices:
        print(f"   {status_code}: {status_label}")

def test_frontend_integration():
    """Test how frontend would interact with simplified payment system"""
    print(f"\n🌐 Frontend Integration Example")
    print("=" * 50)
    
    # Simulate enrollment creation
    course = Course.objects.first()
    if not course:
        return
    
    enrollment = CourseEnrollment.objects.create(
        course=course,
        first_name="Frontend",
        last_name="Test",
        email="frontend.test@example.com",
        phone="555-9999",
        payment_amount=course.cost
    )
    
    print(f"📝 Initial Enrollment:")
    print(f"   Payment Status: {enrollment.payment_status}")
    print(f"   Payment Method: {enrollment.payment_method or 'None'}")
    print(f"   Payment Amount: ${enrollment.payment_amount}")
    
    # Simulate admin updating payment
    print(f"\n👨‍💼 Admin Updates Payment:")
    enrollment.payment_status = PaymentStatus.PAID
    enrollment.payment_method = PaymentMethod.CREDIT_CARD
    enrollment.save(update_fields=['payment_status', 'payment_method'])
    
    print(f"   ✅ Updated Payment Status: {enrollment.get_payment_status_display()}")
    print(f"   ✅ Updated Payment Method: {enrollment.get_payment_method_display()}")
    print(f"   💰 Amount: ${enrollment.payment_amount}")
    
    # Show what frontend would receive
    from training.serializers import EnrollmentDetailSerializer
    serializer = EnrollmentDetailSerializer(enrollment)
    
    print(f"\n📡 Frontend API Response:")
    payment_data = {
        'payment_status': serializer.data['payment_status'],
        'payment_method': serializer.data['payment_method'],
        'payment_amount': serializer.data['payment_amount']
    }
    
    import json
    print(json.dumps(payment_data, indent=2))
    
    # Cleanup
    enrollment.delete()

if __name__ == "__main__":
    print("💳 Simplified Payment System Test")
    print("=" * 70)
    
    # Show available options
    show_payment_options()
    
    # Test the simplified payment system
    test_simplified_payment_system()
    
    # Test frontend integration
    test_frontend_integration()
    
    print("\n" + "=" * 70)
    print("✅ Simplified Payment System Summary:")
    print("   • Payment Status: pending, paid, failed, refunded")
    print("   • Payment Method: cash, bank_transfer, credit_card, mobile_payment, check, other")
    print("   • Payment Amount: decimal field for amount")
    print("   • Removed: payment_date, payment_reference (simplified)")
    print("   • Perfect for: basic payment tracking without complex details")
    print("\n🎯 The payment system is now simplified and focused on essentials!")

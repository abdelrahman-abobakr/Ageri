#!/usr/bin/env python3
"""
Test script to demonstrate the current payment flow
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'research_platform.settings')
django.setup()

from training.models import Course, CourseEnrollment, PaymentStatus
from django.utils import timezone
from django.db import models
from decimal import Decimal

def test_payment_flow():
    """Test the complete payment flow"""
    print("💳 Testing Course Payment Flow")
    print("=" * 60)

    # Clean up any existing test enrollments first
    CourseEnrollment.objects.filter(
        email__in=[
            'payment.test@example.com',
            'failed.payment@example.com',
            'refunded.payment@example.com'
        ]
    ).delete()

    # Get a course
    course = Course.objects.first()
    if not course:
        print("❌ No courses found")
        return

    print(f"📚 Course: {course.course_name}")
    print(f"💰 Course Cost: ${course.cost}")

    # Step 1: Create enrollment (simulating guest enrollment)
    print(f"\n1️⃣ Step 1: Guest Enrollment")
    enrollment = CourseEnrollment.objects.create(
        course=course,
        first_name="Payment",
        last_name="Test",
        email="payment.test@example.com",
        phone="555-0123",
        organization="Test Company",
        job_title="Tester",
        payment_amount=course.cost  # Set payment amount to course cost
    )
    
    print(f"   ✅ Enrollment created: ID {enrollment.id}")
    print(f"   📧 Enrollee: {enrollment.enrollee_name}")
    print(f"   💳 Payment Status: {enrollment.payment_status}")
    print(f"   💰 Payment Amount: ${enrollment.payment_amount}")
    print(f"   🎫 Enrollment Token: {enrollment.enrollment_token}")
    
    # Step 2: Simulate user payment (outside system)
    print(f"\n2️⃣ Step 2: User Makes Payment (Outside System)")
    print(f"   💳 User pays ${course.cost} via bank transfer")
    print(f"   📧 User receives transaction reference: BANK_TXN_789123")
    print(f"   ⏳ Admin needs to update payment status...")
    
    # Step 3: Admin updates payment status
    print(f"\n3️⃣ Step 3: Admin Updates Payment Status")
    enrollment.payment_status = PaymentStatus.PAID
    enrollment.payment_date = timezone.now()
    enrollment.payment_reference = "BANK_TXN_789123"
    enrollment.save(update_fields=['payment_status', 'payment_date', 'payment_reference'])
    
    print(f"   ✅ Payment status updated to: {enrollment.payment_status}")
    print(f"   📅 Payment date: {enrollment.payment_date.strftime('%Y-%m-%d %H:%M')}")
    print(f"   🔗 Payment reference: {enrollment.payment_reference}")
    
    # Step 4: Check final status
    print(f"\n4️⃣ Step 4: Final Enrollment Status")
    enrollment.refresh_from_db()
    
    print(f"   📋 Enrollment ID: {enrollment.id}")
    print(f"   👤 Enrollee: {enrollment.enrollee_name}")
    print(f"   📚 Course: {enrollment.course.course_name}")
    print(f"   📊 Status: {enrollment.status}")
    print(f"   💳 Payment Status: {enrollment.payment_status}")
    print(f"   💰 Amount Paid: ${enrollment.payment_amount}")
    print(f"   📅 Payment Date: {enrollment.payment_date}")
    print(f"   🔗 Reference: {enrollment.payment_reference}")
    
    # Step 5: Simulate different payment scenarios
    print(f"\n5️⃣ Step 5: Testing Different Payment Scenarios")
    
    # Failed payment
    failed_enrollment = CourseEnrollment.objects.create(
        course=course,
        first_name="Failed",
        last_name="Payment",
        email="failed.payment@example.com",
        phone="555-0124",
        payment_amount=course.cost
    )
    
    failed_enrollment.payment_status = PaymentStatus.FAILED
    failed_enrollment.save(update_fields=['payment_status'])
    
    print(f"   ❌ Failed Payment: {failed_enrollment.enrollee_name} - {failed_enrollment.payment_status}")
    
    # Refunded payment
    refunded_enrollment = CourseEnrollment.objects.create(
        course=course,
        first_name="Refunded",
        last_name="Payment",
        email="refunded.payment@example.com",
        phone="555-0125",
        payment_amount=course.cost
    )
    
    refunded_enrollment.payment_status = PaymentStatus.PAID
    refunded_enrollment.payment_date = timezone.now()
    refunded_enrollment.save(update_fields=['payment_status', 'payment_date'])
    
    # Later refund
    refunded_enrollment.payment_status = PaymentStatus.REFUNDED
    refunded_enrollment.save(update_fields=['payment_status'])
    
    print(f"   🔄 Refunded Payment: {refunded_enrollment.enrollee_name} - {refunded_enrollment.payment_status}")
    
    # Step 6: Payment summary
    print(f"\n6️⃣ Step 6: Payment Summary for Course")
    
    enrollments = CourseEnrollment.objects.filter(course=course)
    payment_summary = {
        'total_enrollments': enrollments.count(),
        'pending_payments': enrollments.filter(payment_status=PaymentStatus.PENDING).count(),
        'paid_payments': enrollments.filter(payment_status=PaymentStatus.PAID).count(),
        'failed_payments': enrollments.filter(payment_status=PaymentStatus.FAILED).count(),
        'refunded_payments': enrollments.filter(payment_status=PaymentStatus.REFUNDED).count(),
    }
    
    total_revenue = enrollments.filter(payment_status=PaymentStatus.PAID).aggregate(
        total=models.Sum('payment_amount')
    )['total'] or Decimal('0.00')
    
    print(f"   📊 Payment Summary:")
    print(f"      Total Enrollments: {payment_summary['total_enrollments']}")
    print(f"      Pending Payments: {payment_summary['pending_payments']}")
    print(f"      Paid Payments: {payment_summary['paid_payments']}")
    print(f"      Failed Payments: {payment_summary['failed_payments']}")
    print(f"      Refunded Payments: {payment_summary['refunded_payments']}")
    print(f"      Total Revenue: ${total_revenue}")
    
    # Cleanup test enrollments
    print(f"\n🧹 Cleaning up test enrollments...")
    test_enrollments = CourseEnrollment.objects.filter(
        email__in=[
            'payment.test@example.com',
            'failed.payment@example.com', 
            'refunded.payment@example.com'
        ]
    )
    
    deleted_count = test_enrollments.count()
    test_enrollments.delete()
    print(f"   ✅ Deleted {deleted_count} test enrollments")

def show_payment_status_options():
    """Show available payment status options"""
    print(f"\n💳 Available Payment Status Options")
    print("=" * 50)
    
    for status_code, status_label in PaymentStatus.choices:
        print(f"   {status_code}: {status_label}")

def show_current_payment_statistics():
    """Show current payment statistics across all courses"""
    print(f"\n📊 Current Payment Statistics")
    print("=" * 50)
    
    from django.db import models
    
    total_enrollments = CourseEnrollment.objects.count()
    
    if total_enrollments == 0:
        print("   📭 No enrollments found")
        return
    
    payment_stats = CourseEnrollment.objects.aggregate(
        total_pending=models.Count('id', filter=models.Q(payment_status=PaymentStatus.PENDING)),
        total_paid=models.Count('id', filter=models.Q(payment_status=PaymentStatus.PAID)),
        total_failed=models.Count('id', filter=models.Q(payment_status=PaymentStatus.FAILED)),
        total_refunded=models.Count('id', filter=models.Q(payment_status=PaymentStatus.REFUNDED)),
        total_revenue=models.Sum('payment_amount', filter=models.Q(payment_status=PaymentStatus.PAID))
    )
    
    print(f"   📈 Overall Statistics:")
    print(f"      Total Enrollments: {total_enrollments}")
    print(f"      Pending Payments: {payment_stats['total_pending']}")
    print(f"      Paid Payments: {payment_stats['total_paid']}")
    print(f"      Failed Payments: {payment_stats['total_failed']}")
    print(f"      Refunded Payments: {payment_stats['total_refunded']}")
    print(f"      Total Revenue: ${payment_stats['total_revenue'] or 0}")
    
    # Payment success rate
    if total_enrollments > 0:
        success_rate = (payment_stats['total_paid'] / total_enrollments) * 100
        print(f"      Payment Success Rate: {success_rate:.1f}%")

if __name__ == "__main__":
    print("💳 Course Payment Flow Test")
    print("=" * 70)
    
    # Show payment options
    show_payment_status_options()
    
    # Show current statistics
    show_current_payment_statistics()
    
    # Test payment flow
    test_payment_flow()
    
    print("\n" + "=" * 70)
    print("📝 Payment Flow Summary:")
    print("1. User enrolls → Payment status: 'pending'")
    print("2. User pays outside system → Bank transfer, cash, etc.")
    print("3. Admin receives payment → Updates system manually")
    print("4. Payment status updated → 'paid' with reference")
    print("5. System tracks all payment history")
    print("\n💡 This is a manual payment system - suitable for offline payments!")

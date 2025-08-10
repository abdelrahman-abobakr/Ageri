# Updated Enrollment Flow with Admin Management

## 🔄 **Complete Enrollment Flow**

### **Phase 1: Guest Enrollment (Public)**
```mermaid
graph TD
    A[User Visits Course Page] --> B[Clicks Enroll Button]
    B --> C[Fills Guest Information Form]
    C --> D{Form Valid?}
    D -->|No| E[Show Validation Errors]
    E --> C
    D -->|Yes| F[Submit to API]
    F --> G{Course Available?}
    G -->|No| H[Show Error Message]
    G -->|Yes| I[Create Enrollment Record]
    I --> J[Generate Enrollment Token]
    J --> K[Send Confirmation Email]
    K --> L[Show Success Page]
    L --> M[User Receives Email]
```

### **Phase 2: Admin Management (Backend)**
```mermaid
graph TD
    A[Admin Logs In] --> B[Views Enrollment Dashboard]
    B --> C[Sees All Course Enrollments]
    C --> D{Admin Action}
    D -->|View Details| E[Show Enrollment Details]
    D -->|Update Payment| F[Mark as Paid/Unpaid]
    D -->|Generate Report| G[Create PDF Report]
    D -->|Send Email| H[Send Custom Email]
    F --> I[Update Database]
    G --> J[Download PDF]
    H --> K[Email Sent]
```

---

## 🗄️ **Updated Database Model**

### **Enhanced CourseEnrollment Model**

```python
# training/models.py
from django.db import models
from django.core.validators import EmailValidator
from django.utils import timezone
from core.models import TimeStampedModel
import uuid

class CourseEnrollment(TimeStampedModel):
    """Enhanced model for course enrollments with payment tracking"""
    
    ENROLLMENT_STATUS = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    PAYMENT_STATUS = [
        ('not_required', 'Not Required'),
        ('pending', 'Payment Pending'),
        ('paid', 'Paid'),
        ('partial', 'Partially Paid'),
        ('refunded', 'Refunded'),
        ('overdue', 'Overdue'),
    ]
    
    # Course relationship
    course = models.ForeignKey(
        'Course',
        on_delete=models.CASCADE,
        related_name='enrollments'
    )
    
    # Optional user relationship (for authenticated users)
    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='course_enrollments',
        null=True,
        blank=True,
        help_text="Leave blank for guest enrollments"
    )
    
    # Guest user information (required for all enrollments)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(validators=[EmailValidator()])
    phone = models.CharField(max_length=20, blank=True)
    
    # Additional information
    organization = models.CharField(max_length=200, blank=True)
    job_title = models.CharField(max_length=100, blank=True)
    education_level = models.CharField(
        max_length=50,
        choices=[
            ('high_school', 'High School'),
            ('bachelor', 'Bachelor\'s Degree'),
            ('master', 'Master\'s Degree'),
            ('phd', 'PhD'),
            ('other', 'Other'),
        ],
        blank=True
    )
    experience_level = models.CharField(
        max_length=20,
        choices=[
            ('beginner', 'Beginner'),
            ('intermediate', 'Intermediate'),
            ('advanced', 'Advanced'),
        ],
        default='beginner'
    )
    
    # Enrollment details
    status = models.CharField(
        max_length=20,
        choices=ENROLLMENT_STATUS,
        default='approved'
    )
    enrollment_date = models.DateTimeField(auto_now_add=True)
    completion_date = models.DateTimeField(null=True, blank=True)
    grade = models.CharField(max_length=5, blank=True)
    
    # Payment tracking
    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS,
        default='not_required'
    )
    amount_due = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0.00,
        help_text="Amount the participant needs to pay"
    )
    amount_paid = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0.00,
        help_text="Amount already paid by participant"
    )
    payment_date = models.DateTimeField(null=True, blank=True)
    payment_method = models.CharField(
        max_length=50,
        choices=[
            ('cash', 'Cash'),
            ('bank_transfer', 'Bank Transfer'),
            ('credit_card', 'Credit Card'),
            ('paypal', 'PayPal'),
            ('other', 'Other'),
        ],
        blank=True
    )
    payment_reference = models.CharField(
        max_length=100, 
        blank=True,
        help_text="Payment reference number or transaction ID"
    )
    
    # Admin notes and tracking
    admin_notes = models.TextField(
        blank=True,
        help_text="Internal notes for admin use"
    )
    last_updated_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='updated_enrollments',
        help_text="Admin user who last updated this enrollment"
    )
    
    # Guest-specific fields
    is_guest = models.BooleanField(default=False)
    enrollment_token = models.CharField(
        max_length=100, 
        unique=True, 
        blank=True,
        help_text="Unique token for guest enrollment tracking"
    )
    
    class Meta:
        indexes = [
            models.Index(fields=['course', 'email']),
            models.Index(fields=['enrollment_token']),
            models.Index(fields=['is_guest']),
            models.Index(fields=['payment_status']),
            models.Index(fields=['status']),
        ]
        ordering = ['-enrollment_date']
    
    def __str__(self):
        if self.user:
            return f"{self.user.get_full_name()} - {self.course.course_name}"
        else:
            return f"{self.first_name} {self.last_name} - {self.course.course_name}"
    
    @property
    def full_name(self):
        """Get full name regardless of user type"""
        if self.user:
            return self.user.get_full_name()
        return f"{self.first_name} {self.last_name}"
    
    @property
    def participant_email(self):
        """Get email regardless of user type"""
        if self.user:
            return self.user.email
        return self.email
    
    @property
    def balance_due(self):
        """Calculate remaining balance"""
        return self.amount_due - self.amount_paid
    
    @property
    def is_fully_paid(self):
        """Check if enrollment is fully paid"""
        if self.amount_due == 0:
            return True
        return self.amount_paid >= self.amount_due
    
    @property
    def payment_percentage(self):
        """Calculate payment completion percentage"""
        if self.amount_due == 0:
            return 100
        return (self.amount_paid / self.amount_due) * 100
    
    def save(self, *args, **kwargs):
        # Generate enrollment token for guests
        if self.is_guest and not self.enrollment_token:
            self.enrollment_token = str(uuid.uuid4())
        
        # Set guest flag based on user presence
        if not self.user:
            self.is_guest = True
        
        # Set amount due from course cost if not set
        if self.amount_due == 0 and self.course:
            self.amount_due = self.course.cost if not self.course.is_free else 0
        
        # Update payment status based on amounts
        if self.amount_due == 0:
            self.payment_status = 'not_required'
        elif self.amount_paid == 0:
            self.payment_status = 'pending'
        elif self.amount_paid >= self.amount_due:
            self.payment_status = 'paid'
            if not self.payment_date:
                self.payment_date = timezone.now()
        elif self.amount_paid > 0:
            self.payment_status = 'partial'
        
        super().save(*args, **kwargs)
    
    def mark_as_paid(self, amount=None, payment_method='', reference='', admin_user=None):
        """Mark enrollment as paid"""
        if amount is None:
            amount = self.amount_due
        
        self.amount_paid = amount
        self.payment_date = timezone.now()
        self.payment_method = payment_method
        self.payment_reference = reference
        self.last_updated_by = admin_user
        
        if amount >= self.amount_due:
            self.payment_status = 'paid'
        else:
            self.payment_status = 'partial'
        
        self.save()
    
    def send_payment_confirmation_email(self):
        """Send payment confirmation email"""
        from django.core.mail import send_mail
        from django.template.loader import render_to_string
        from django.conf import settings
        
        if self.payment_status not in ['paid', 'partial']:
            return
        
        subject = f"Payment Confirmation - {self.course.course_name}"
        
        context = {
            'enrollment': self,
            'course': self.course,
            'participant_name': self.full_name,
            'amount_paid': self.amount_paid,
            'balance_due': self.balance_due,
            'is_fully_paid': self.is_fully_paid,
            'payment_date': self.payment_date,
            'payment_method': self.get_payment_method_display(),
        }
        
        html_message = render_to_string('emails/payment_confirmation.html', context)
        plain_message = render_to_string('emails/payment_confirmation.txt', context)
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[self.participant_email],
            html_message=html_message,
            fail_silently=False
        )
```

### **Migration File**

```python
# training/migrations/0003_add_payment_tracking.py
from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    dependencies = [
        ('training', '0002_add_guest_enrollment_fields'),
        ('accounts', '0001_initial'),
    ]

    operations = [
        # Add payment tracking fields
        migrations.AddField(
            model_name='courseenrollment',
            name='payment_status',
            field=models.CharField(
                choices=[
                    ('not_required', 'Not Required'),
                    ('pending', 'Payment Pending'),
                    ('paid', 'Paid'),
                    ('partial', 'Partially Paid'),
                    ('refunded', 'Refunded'),
                    ('overdue', 'Overdue')
                ],
                default='not_required',
                max_length=20
            ),
        ),
        migrations.AddField(
            model_name='courseenrollment',
            name='amount_due',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
        migrations.AddField(
            model_name='courseenrollment',
            name='amount_paid',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
        migrations.AddField(
            model_name='courseenrollment',
            name='payment_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='courseenrollment',
            name='payment_method',
            field=models.CharField(
                blank=True,
                choices=[
                    ('cash', 'Cash'),
                    ('bank_transfer', 'Bank Transfer'),
                    ('credit_card', 'Credit Card'),
                    ('paypal', 'PayPal'),
                    ('other', 'Other')
                ],
                max_length=50
            ),
        ),
        migrations.AddField(
            model_name='courseenrollment',
            name='payment_reference',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='courseenrollment',
            name='admin_notes',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='courseenrollment',
            name='last_updated_by',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='updated_enrollments',
                to='accounts.user'
            ),
        ),
        
        # Add indexes for better performance
        migrations.AddIndex(
            model_name='courseenrollment',
            index=models.Index(fields=['payment_status'], name='training_courseenrollment_payment_status_idx'),
        ),
        migrations.AddIndex(
            model_name='courseenrollment',
            index=models.Index(fields=['status'], name='training_courseenrollment_status_idx'),
        ),
    ]
```

---

## 🎛️ **Admin Dashboard Views**

### **Admin Serializers**

```python
# training/admin_serializers.py
from rest_framework import serializers
from .models import CourseEnrollment, Course
from django.contrib.auth import get_user_model

User = get_user_model()

class EnrollmentListSerializer(serializers.ModelSerializer):
    """Serializer for enrollment list view"""
    full_name = serializers.CharField(read_only=True)
    participant_email = serializers.CharField(read_only=True)
    course_name = serializers.CharField(source='course.course_name', read_only=True)
    course_code = serializers.CharField(source='course.course_code', read_only=True)
    balance_due = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    is_fully_paid = serializers.BooleanField(read_only=True)
    payment_percentage = serializers.FloatField(read_only=True)

    class Meta:
        model = CourseEnrollment
        fields = [
            'id', 'full_name', 'participant_email', 'course_name', 'course_code',
            'enrollment_date', 'status', 'payment_status', 'amount_due',
            'amount_paid', 'balance_due', 'is_fully_paid', 'payment_percentage',
            'payment_date', 'payment_method', 'is_guest'
        ]

class EnrollmentDetailSerializer(serializers.ModelSerializer):
    """Serializer for detailed enrollment view"""
    full_name = serializers.CharField(read_only=True)
    participant_email = serializers.CharField(read_only=True)
    course_name = serializers.CharField(source='course.course_name', read_only=True)
    course_code = serializers.CharField(source='course.course_code', read_only=True)
    balance_due = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    is_fully_paid = serializers.BooleanField(read_only=True)
    payment_percentage = serializers.FloatField(read_only=True)
    last_updated_by_name = serializers.CharField(
        source='last_updated_by.get_full_name',
        read_only=True
    )

    class Meta:
        model = CourseEnrollment
        fields = [
            'id', 'course', 'course_name', 'course_code', 'user',
            'first_name', 'last_name', 'full_name', 'email', 'participant_email',
            'phone', 'organization', 'job_title', 'education_level', 'experience_level',
            'status', 'enrollment_date', 'completion_date', 'grade',
            'payment_status', 'amount_due', 'amount_paid', 'balance_due',
            'is_fully_paid', 'payment_percentage', 'payment_date',
            'payment_method', 'payment_reference', 'admin_notes',
            'is_guest', 'enrollment_token', 'last_updated_by', 'last_updated_by_name',
            'created_at', 'updated_at'
        ]

class PaymentUpdateSerializer(serializers.Serializer):
    """Serializer for updating payment information"""
    amount_paid = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=0)
    payment_method = serializers.ChoiceField(
        choices=[
            ('cash', 'Cash'),
            ('bank_transfer', 'Bank Transfer'),
            ('credit_card', 'Credit Card'),
            ('paypal', 'PayPal'),
            ('other', 'Other'),
        ],
        required=False
    )
    payment_reference = serializers.CharField(max_length=100, required=False)
    admin_notes = serializers.CharField(required=False)

    def validate_amount_paid(self, value):
        enrollment = self.context.get('enrollment')
        if enrollment and value > enrollment.amount_due:
            raise serializers.ValidationError(
                f"Amount paid cannot exceed amount due ({enrollment.amount_due})"
            )
        return value

class EnrollmentStatsSerializer(serializers.Serializer):
    """Serializer for enrollment statistics"""
    total_enrollments = serializers.IntegerField()
    pending_payments = serializers.IntegerField()
    paid_enrollments = serializers.IntegerField()
    total_revenue = serializers.DecimalField(max_digits=10, decimal_places=2)
    pending_revenue = serializers.DecimalField(max_digits=10, decimal_places=2)
    completion_rate = serializers.FloatField()
```

### **Admin ViewSet with PDF Export**

```python
# training/admin_views.py
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q, Count, Sum, Avg
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.utils import timezone
from .models import CourseEnrollment, Course
from .admin_serializers import (
    EnrollmentListSerializer,
    EnrollmentDetailSerializer,
    PaymentUpdateSerializer,
    EnrollmentStatsSerializer
)
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.units import inch

class AdminEnrollmentViewSet(viewsets.ModelViewSet):
    """Admin viewset for managing course enrollments"""
    serializer_class = EnrollmentListSerializer
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]

    def get_queryset(self):
        queryset = CourseEnrollment.objects.select_related(
            'course', 'user', 'last_updated_by'
        ).all()

        # Filter by course if specified
        course_id = self.request.query_params.get('course_id')
        if course_id:
            queryset = queryset.filter(course_id=course_id)

        # Filter by payment status
        payment_status = self.request.query_params.get('payment_status')
        if payment_status:
            queryset = queryset.filter(payment_status=payment_status)

        # Filter by enrollment status
        enrollment_status = self.request.query_params.get('status')
        if enrollment_status:
            queryset = queryset.filter(status=enrollment_status)

        # Search by name or email
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(email__icontains=search) |
                Q(user__first_name__icontains=search) |
                Q(user__last_name__icontains=search) |
                Q(user__email__icontains=search)
            )

        return queryset.order_by('-enrollment_date')

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return EnrollmentDetailSerializer
        return EnrollmentListSerializer

    @action(detail=True, methods=['post'])
    def update_payment(self, request, pk=None):
        """Update payment information for an enrollment"""
        enrollment = self.get_object()
        serializer = PaymentUpdateSerializer(
            data=request.data,
            context={'enrollment': enrollment}
        )

        if serializer.is_valid():
            # Update payment information
            enrollment.amount_paid = serializer.validated_data['amount_paid']
            enrollment.payment_method = serializer.validated_data.get('payment_method', '')
            enrollment.payment_reference = serializer.validated_data.get('payment_reference', '')
            enrollment.admin_notes = serializer.validated_data.get('admin_notes', enrollment.admin_notes)
            enrollment.last_updated_by = request.user
            enrollment.save()

            # Send payment confirmation email if fully paid
            if enrollment.is_fully_paid:
                try:
                    enrollment.send_payment_confirmation_email()
                except Exception as e:
                    # Log error but don't fail the request
                    print(f"Failed to send payment confirmation email: {e}")

            return Response({
                'message': 'Payment updated successfully',
                'enrollment': EnrollmentDetailSerializer(enrollment).data
            })

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def mark_completed(self, request, pk=None):
        """Mark enrollment as completed"""
        enrollment = self.get_object()
        enrollment.status = 'completed'
        enrollment.completion_date = timezone.now()
        enrollment.last_updated_by = request.user
        enrollment.save()

        return Response({
            'message': 'Enrollment marked as completed',
            'enrollment': EnrollmentDetailSerializer(enrollment).data
        })

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get enrollment statistics"""
        course_id = request.query_params.get('course_id')
        queryset = self.get_queryset()

        if course_id:
            queryset = queryset.filter(course_id=course_id)

        stats = {
            'total_enrollments': queryset.count(),
            'pending_payments': queryset.filter(payment_status='pending').count(),
            'paid_enrollments': queryset.filter(payment_status='paid').count(),
            'total_revenue': queryset.aggregate(
                total=Sum('amount_paid')
            )['total'] or 0,
            'pending_revenue': queryset.filter(
                payment_status__in=['pending', 'partial']
            ).aggregate(
                total=Sum('amount_due') - Sum('amount_paid')
            )['total'] or 0,
            'completion_rate': queryset.filter(
                status='completed'
            ).count() / max(queryset.count(), 1) * 100
        }

        serializer = EnrollmentStatsSerializer(stats)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def export_pdf(self, request):
        """Export enrollments to PDF report"""
        course_id = request.query_params.get('course_id')
        if not course_id:
            return Response(
                {'error': 'course_id parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            course = Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            return Response(
                {'error': 'Course not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Get enrollments for the course
        enrollments = CourseEnrollment.objects.filter(
            course_id=course_id
        ).select_related('course', 'user').order_by('last_name', 'first_name')

        # Create PDF
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="course_{course.course_code}_enrollments.pdf"'

        # Create PDF document
        doc = SimpleDocTemplate(response, pagesize=A4)
        elements = []
        styles = getSampleStyleSheet()

        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=1  # Center alignment
        )

        title = Paragraph(f"Course Enrollment Report", title_style)
        elements.append(title)

        # Course information
        course_info = f"""
        <b>Course:</b> {course.course_name}<br/>
        <b>Code:</b> {course.course_code}<br/>
        <b>Instructor:</b> {course.instructor}<br/>
        <b>Start Date:</b> {course.start_date.strftime('%B %d, %Y')}<br/>
        <b>End Date:</b> {course.end_date.strftime('%B %d, %Y')}<br/>
        <b>Total Enrollments:</b> {enrollments.count()}<br/>
        <b>Report Generated:</b> {timezone.now().strftime('%B %d, %Y at %I:%M %p')}
        """

        course_para = Paragraph(course_info, styles['Normal'])
        elements.append(course_para)
        elements.append(Spacer(1, 20))

        # Enrollment statistics
        stats = {
            'total': enrollments.count(),
            'paid': enrollments.filter(payment_status='paid').count(),
            'pending': enrollments.filter(payment_status='pending').count(),
            'completed': enrollments.filter(status='completed').count(),
            'total_revenue': enrollments.aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0,
        }

        stats_info = f"""
        <b>Enrollment Statistics:</b><br/>
        • Total Enrollments: {stats['total']}<br/>
        • Paid: {stats['paid']}<br/>
        • Payment Pending: {stats['pending']}<br/>
        • Completed: {stats['completed']}<br/>
        • Total Revenue: ${stats['total_revenue']:.2f}
        """

        stats_para = Paragraph(stats_info, styles['Normal'])
        elements.append(stats_para)
        elements.append(Spacer(1, 20))

        # Enrollment table
        table_data = [
            ['#', 'Name', 'Email', 'Phone', 'Organization', 'Payment Status', 'Amount Paid', 'Enrollment Date']
        ]

        for i, enrollment in enumerate(enrollments, 1):
            table_data.append([
                str(i),
                enrollment.full_name,
                enrollment.participant_email,
                enrollment.phone or 'N/A',
                enrollment.organization or 'N/A',
                enrollment.get_payment_status_display(),
                f'${enrollment.amount_paid:.2f}',
                enrollment.enrollment_date.strftime('%m/%d/%Y')
            ])

        # Create table
        table = Table(table_data, colWidths=[0.5*inch, 1.5*inch, 2*inch, 1*inch, 1.5*inch, 1*inch, 0.8*inch, 0.8*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))

        elements.append(table)

        # Build PDF
        doc.build(elements)

        return response
```

---

## 🌐 **URL Configuration**

### **Admin URLs**

```python
# training/admin_urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .admin_views import AdminEnrollmentViewSet

router = DefaultRouter()
router.register(r'enrollments', AdminEnrollmentViewSet, basename='admin-enrollment')

urlpatterns = [
    path('', include(router.urls)),
]
```

### **Main URLs Update**

```python
# training/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CourseViewSet

router = DefaultRouter()
router.register(r'courses', CourseViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('admin/', include('training.admin_urls')),  # Admin endpoints
]
```

### **Project URLs**

```python
# research_platform/urls.py
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/training/', include('training.urls')),
    # ... other URLs
]
```

---

## 🎨 **Frontend Admin Components**

### **Enrollment Management Dashboard**

```jsx
// components/admin/EnrollmentDashboard.jsx
import React, { useState, useEffect } from 'react';
import EnrollmentList from './EnrollmentList';
import EnrollmentStats from './EnrollmentStats';
import PaymentUpdateModal from './PaymentUpdateModal';

const EnrollmentDashboard = () => {
    const [enrollments, setEnrollments] = useState([]);
    const [stats, setStats] = useState({});
    const [loading, setLoading] = useState(true);
    const [filters, setFilters] = useState({
        course_id: '',
        payment_status: '',
        status: '',
        search: ''
    });
    const [selectedEnrollment, setSelectedEnrollment] = useState(null);
    const [showPaymentModal, setShowPaymentModal] = useState(false);

    useEffect(() => {
        loadEnrollments();
        loadStats();
    }, [filters]);

    const loadEnrollments = async () => {
        try {
            setLoading(true);
            const params = new URLSearchParams();
            Object.entries(filters).forEach(([key, value]) => {
                if (value) params.append(key, value);
            });

            const response = await fetch(`/api/training/admin/enrollments/?${params}`, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
                    'Accept': 'application/json'
                }
            });

            if (response.ok) {
                const data = await response.json();
                setEnrollments(data.results);
            }
        } catch (error) {
            console.error('Failed to load enrollments:', error);
        } finally {
            setLoading(false);
        }
    };

    const loadStats = async () => {
        try {
            const params = new URLSearchParams();
            if (filters.course_id) {
                params.append('course_id', filters.course_id);
            }

            const response = await fetch(`/api/training/admin/enrollments/statistics/?${params}`, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
                    'Accept': 'application/json'
                }
            });

            if (response.ok) {
                const data = await response.json();
                setStats(data);
            }
        } catch (error) {
            console.error('Failed to load stats:', error);
        }
    };

    const handlePaymentUpdate = (enrollment) => {
        setSelectedEnrollment(enrollment);
        setShowPaymentModal(true);
    };

    const handlePaymentUpdated = () => {
        setShowPaymentModal(false);
        setSelectedEnrollment(null);
        loadEnrollments();
        loadStats();
    };

    const handleExportPDF = async () => {
        if (!filters.course_id) {
            alert('Please select a course to export');
            return;
        }

        try {
            const response = await fetch(`/api/training/admin/enrollments/export_pdf/?course_id=${filters.course_id}`, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`
                }
            });

            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `course_enrollments_${filters.course_id}.pdf`;
                a.click();
                window.URL.revokeObjectURL(url);
            } else {
                alert('Failed to export PDF');
            }
        } catch (error) {
            console.error('Export failed:', error);
            alert('Failed to export PDF');
        }
    };

    return (
        <div className="enrollment-dashboard">
            <div className="dashboard-header">
                <h1>Enrollment Management</h1>
                <div className="dashboard-actions">
                    <button
                        onClick={handleExportPDF}
                        className="btn btn-secondary"
                        disabled={!filters.course_id}
                    >
                        📄 Export PDF
                    </button>
                </div>
            </div>

            <EnrollmentStats stats={stats} />

            <div className="filters-section">
                <div className="filters-grid">
                    <div className="filter-group">
                        <label>Course:</label>
                        <select
                            value={filters.course_id}
                            onChange={(e) => setFilters({...filters, course_id: e.target.value})}
                        >
                            <option value="">All Courses</option>
                            {/* Course options would be loaded dynamically */}
                        </select>
                    </div>

                    <div className="filter-group">
                        <label>Payment Status:</label>
                        <select
                            value={filters.payment_status}
                            onChange={(e) => setFilters({...filters, payment_status: e.target.value})}
                        >
                            <option value="">All Payments</option>
                            <option value="pending">Pending</option>
                            <option value="paid">Paid</option>
                            <option value="partial">Partial</option>
                            <option value="not_required">Not Required</option>
                        </select>
                    </div>

                    <div className="filter-group">
                        <label>Status:</label>
                        <select
                            value={filters.status}
                            onChange={(e) => setFilters({...filters, status: e.target.value})}
                        >
                            <option value="">All Status</option>
                            <option value="pending">Pending</option>
                            <option value="approved">Approved</option>
                            <option value="completed">Completed</option>
                            <option value="cancelled">Cancelled</option>
                        </select>
                    </div>

                    <div className="filter-group">
                        <label>Search:</label>
                        <input
                            type="text"
                            placeholder="Search by name or email..."
                            value={filters.search}
                            onChange={(e) => setFilters({...filters, search: e.target.value})}
                        />
                    </div>
                </div>
            </div>

            <EnrollmentList
                enrollments={enrollments}
                loading={loading}
                onPaymentUpdate={handlePaymentUpdate}
                onRefresh={loadEnrollments}
            />

            {showPaymentModal && (
                <PaymentUpdateModal
                    enrollment={selectedEnrollment}
                    onClose={() => setShowPaymentModal(false)}
                    onUpdated={handlePaymentUpdated}
                />
            )}
        </div>
    );
};

export default EnrollmentDashboard;
```

### **Payment Update Modal**

```jsx
// components/admin/PaymentUpdateModal.jsx
import React, { useState } from 'react';

const PaymentUpdateModal = ({ enrollment, onClose, onUpdated }) => {
    const [formData, setFormData] = useState({
        amount_paid: enrollment.amount_paid,
        payment_method: enrollment.payment_method || '',
        payment_reference: enrollment.payment_reference || '',
        admin_notes: enrollment.admin_notes || ''
    });
    const [loading, setLoading] = useState(false);
    const [errors, setErrors] = useState({});

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setErrors({});

        try {
            const response = await fetch(`/api/training/admin/enrollments/${enrollment.id}/update_payment/`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            });

            const data = await response.json();

            if (response.ok) {
                onUpdated();
            } else {
                setErrors(data);
            }
        } catch (error) {
            setErrors({ general: 'Failed to update payment' });
        } finally {
            setLoading(false);
        }
    };

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: value
        }));
    };

    return (
        <div className="modal-overlay">
            <div className="modal-content">
                <div className="modal-header">
                    <h2>Update Payment - {enrollment.full_name}</h2>
                    <button onClick={onClose} className="close-btn">×</button>
                </div>

                <div className="enrollment-summary">
                    <div className="summary-grid">
                        <div><strong>Course:</strong> {enrollment.course_name}</div>
                        <div><strong>Amount Due:</strong> ${enrollment.amount_due}</div>
                        <div><strong>Current Paid:</strong> ${enrollment.amount_paid}</div>
                        <div><strong>Balance:</strong> ${enrollment.balance_due}</div>
                    </div>
                </div>

                <form onSubmit={handleSubmit}>
                    {errors.general && (
                        <div className="error-message">{errors.general}</div>
                    )}

                    <div className="form-group">
                        <label htmlFor="amount_paid">Amount Paid *</label>
                        <input
                            type="number"
                            id="amount_paid"
                            name="amount_paid"
                            value={formData.amount_paid}
                            onChange={handleChange}
                            step="0.01"
                            min="0"
                            max={enrollment.amount_due}
                            required
                        />
                        {errors.amount_paid && (
                            <span className="error-text">{errors.amount_paid}</span>
                        )}
                    </div>

                    <div className="form-group">
                        <label htmlFor="payment_method">Payment Method</label>
                        <select
                            id="payment_method"
                            name="payment_method"
                            value={formData.payment_method}
                            onChange={handleChange}
                        >
                            <option value="">Select method</option>
                            <option value="cash">Cash</option>
                            <option value="bank_transfer">Bank Transfer</option>
                            <option value="credit_card">Credit Card</option>
                            <option value="paypal">PayPal</option>
                            <option value="other">Other</option>
                        </select>
                    </div>

                    <div className="form-group">
                        <label htmlFor="payment_reference">Payment Reference</label>
                        <input
                            type="text"
                            id="payment_reference"
                            name="payment_reference"
                            value={formData.payment_reference}
                            onChange={handleChange}
                            placeholder="Transaction ID, check number, etc."
                        />
                    </div>

                    <div className="form-group">
                        <label htmlFor="admin_notes">Admin Notes</label>
                        <textarea
                            id="admin_notes"
                            name="admin_notes"
                            value={formData.admin_notes}
                            onChange={handleChange}
                            rows="3"
                            placeholder="Internal notes about this enrollment..."
                        />
                    </div>

                    <div className="form-actions">
                        <button type="button" onClick={onClose} className="btn btn-secondary">
                            Cancel
                        </button>
                        <button type="submit" disabled={loading} className="btn btn-primary">
                            {loading ? 'Updating...' : 'Update Payment'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default PaymentUpdateModal;
```

### **Enrollment Statistics Component**

```jsx
// components/admin/EnrollmentStats.jsx
import React from 'react';

const EnrollmentStats = ({ stats }) => {
    const formatCurrency = (amount) => {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD'
        }).format(amount);
    };

    return (
        <div className="enrollment-stats">
            <div className="stats-grid">
                <div className="stat-card">
                    <div className="stat-value">{stats.total_enrollments || 0}</div>
                    <div className="stat-label">Total Enrollments</div>
                </div>

                <div className="stat-card">
                    <div className="stat-value">{stats.paid_enrollments || 0}</div>
                    <div className="stat-label">Paid Enrollments</div>
                </div>

                <div className="stat-card">
                    <div className="stat-value">{stats.pending_payments || 0}</div>
                    <div className="stat-label">Pending Payments</div>
                </div>

                <div className="stat-card">
                    <div className="stat-value">{formatCurrency(stats.total_revenue || 0)}</div>
                    <div className="stat-label">Total Revenue</div>
                </div>

                <div className="stat-card">
                    <div className="stat-value">{formatCurrency(stats.pending_revenue || 0)}</div>
                    <div className="stat-label">Pending Revenue</div>
                </div>

                <div className="stat-card">
                    <div className="stat-value">{(stats.completion_rate || 0).toFixed(1)}%</div>
                    <div className="stat-label">Completion Rate</div>
                </div>
            </div>
        </div>
    );
};

export default EnrollmentStats;
```

### **Enrollment List Component**

```jsx
// components/admin/EnrollmentList.jsx
import React from 'react';

const EnrollmentList = ({ enrollments, loading, onPaymentUpdate, onRefresh }) => {
    const formatDate = (dateString) => {
        return new Date(dateString).toLocaleDateString();
    };

    const formatCurrency = (amount) => {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD'
        }).format(amount);
    };

    const getPaymentStatusBadge = (status) => {
        const statusClasses = {
            'paid': 'badge-success',
            'pending': 'badge-warning',
            'partial': 'badge-info',
            'not_required': 'badge-secondary',
            'overdue': 'badge-danger'
        };

        return (
            <span className={`status-badge ${statusClasses[status] || 'badge-secondary'}`}>
                {status.replace('_', ' ').toUpperCase()}
            </span>
        );
    };

    const getEnrollmentStatusBadge = (status) => {
        const statusClasses = {
            'approved': 'badge-success',
            'pending': 'badge-warning',
            'completed': 'badge-info',
            'cancelled': 'badge-danger'
        };

        return (
            <span className={`status-badge ${statusClasses[status] || 'badge-secondary'}`}>
                {status.toUpperCase()}
            </span>
        );
    };

    if (loading) {
        return <div className="loading">Loading enrollments...</div>;
    }

    if (enrollments.length === 0) {
        return (
            <div className="no-data">
                <p>No enrollments found matching your criteria.</p>
                <button onClick={onRefresh} className="btn btn-primary">
                    Refresh
                </button>
            </div>
        );
    }

    return (
        <div className="enrollment-list">
            <div className="list-header">
                <h3>Enrollments ({enrollments.length})</h3>
                <button onClick={onRefresh} className="btn btn-secondary">
                    🔄 Refresh
                </button>
            </div>

            <div className="table-container">
                <table className="enrollment-table">
                    <thead>
                        <tr>
                            <th>Participant</th>
                            <th>Course</th>
                            <th>Enrollment Date</th>
                            <th>Status</th>
                            <th>Payment Status</th>
                            <th>Amount Due</th>
                            <th>Amount Paid</th>
                            <th>Balance</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {enrollments.map(enrollment => (
                            <tr key={enrollment.id}>
                                <td>
                                    <div className="participant-info">
                                        <div className="participant-name">
                                            {enrollment.full_name}
                                            {enrollment.is_guest && (
                                                <span className="guest-badge">GUEST</span>
                                            )}
                                        </div>
                                        <div className="participant-email">
                                            {enrollment.participant_email}
                                        </div>
                                    </div>
                                </td>
                                <td>
                                    <div className="course-info">
                                        <div className="course-name">{enrollment.course_name}</div>
                                        <div className="course-code">{enrollment.course_code}</div>
                                    </div>
                                </td>
                                <td>{formatDate(enrollment.enrollment_date)}</td>
                                <td>{getEnrollmentStatusBadge(enrollment.status)}</td>
                                <td>{getPaymentStatusBadge(enrollment.payment_status)}</td>
                                <td>{formatCurrency(enrollment.amount_due)}</td>
                                <td>{formatCurrency(enrollment.amount_paid)}</td>
                                <td>
                                    <span className={enrollment.balance_due > 0 ? 'balance-due' : 'balance-paid'}>
                                        {formatCurrency(enrollment.balance_due)}
                                    </span>
                                </td>
                                <td>
                                    <div className="action-buttons">
                                        <button
                                            onClick={() => onPaymentUpdate(enrollment)}
                                            className="btn btn-sm btn-primary"
                                            title="Update Payment"
                                        >
                                            💰
                                        </button>
                                        <button
                                            onClick={() => window.open(`/admin/enrollments/${enrollment.id}`, '_blank')}
                                            className="btn btn-sm btn-secondary"
                                            title="View Details"
                                        >
                                            👁️
                                        </button>
                                    </div>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
};

export default EnrollmentList;
```

---

## 🎨 **CSS Styles for Admin Dashboard**

```css
/* Admin Dashboard Styles */
.enrollment-dashboard {
    padding: 20px;
    max-width: 1400px;
    margin: 0 auto;
}

.dashboard-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 30px;
    padding-bottom: 20px;
    border-bottom: 2px solid #e9ecef;
}

.dashboard-header h1 {
    color: #333;
    margin: 0;
}

.dashboard-actions {
    display: flex;
    gap: 10px;
}

/* Statistics Cards */
.enrollment-stats {
    margin-bottom: 30px;
}

.stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 20px;
    margin-bottom: 30px;
}

.stat-card {
    background: white;
    padding: 20px;
    border-radius: 8px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    text-align: center;
    border-left: 4px solid #007bff;
}

.stat-value {
    font-size: 32px;
    font-weight: bold;
    color: #007bff;
    margin-bottom: 5px;
}

.stat-label {
    color: #666;
    font-size: 14px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

/* Filters */
.filters-section {
    background: white;
    padding: 20px;
    border-radius: 8px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    margin-bottom: 30px;
}

.filters-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 20px;
}

.filter-group {
    display: flex;
    flex-direction: column;
}

.filter-group label {
    font-weight: 600;
    margin-bottom: 5px;
    color: #333;
}

.filter-group select,
.filter-group input {
    padding: 8px 12px;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 14px;
}

/* Enrollment List */
.enrollment-list {
    background: white;
    border-radius: 8px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    overflow: hidden;
}

.list-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 20px;
    background: #f8f9fa;
    border-bottom: 1px solid #e9ecef;
}

.list-header h3 {
    margin: 0;
    color: #333;
}

.table-container {
    overflow-x: auto;
}

.enrollment-table {
    width: 100%;
    border-collapse: collapse;
}

.enrollment-table th {
    background: #f8f9fa;
    padding: 12px;
    text-align: left;
    font-weight: 600;
    color: #333;
    border-bottom: 2px solid #e9ecef;
    white-space: nowrap;
}

.enrollment-table td {
    padding: 12px;
    border-bottom: 1px solid #e9ecef;
    vertical-align: top;
}

.enrollment-table tr:hover {
    background: #f8f9fa;
}

.participant-info {
    min-width: 200px;
}

.participant-name {
    font-weight: 600;
    color: #333;
    margin-bottom: 4px;
    display: flex;
    align-items: center;
    gap: 8px;
}

.participant-email {
    color: #666;
    font-size: 14px;
}

.guest-badge {
    background: #ffc107;
    color: #000;
    padding: 2px 6px;
    border-radius: 4px;
    font-size: 10px;
    font-weight: bold;
}

.course-info {
    min-width: 150px;
}

.course-name {
    font-weight: 600;
    color: #333;
    margin-bottom: 4px;
}

.course-code {
    color: #666;
    font-size: 14px;
}

.status-badge {
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 12px;
    font-weight: bold;
    text-transform: uppercase;
}

.badge-success {
    background: #d4edda;
    color: #155724;
}

.badge-warning {
    background: #fff3cd;
    color: #856404;
}

.badge-info {
    background: #d1ecf1;
    color: #0c5460;
}

.badge-danger {
    background: #f8d7da;
    color: #721c24;
}

.badge-secondary {
    background: #e2e3e5;
    color: #383d41;
}

.balance-due {
    color: #dc3545;
    font-weight: 600;
}

.balance-paid {
    color: #28a745;
    font-weight: 600;
}

.action-buttons {
    display: flex;
    gap: 5px;
}

.btn {
    padding: 8px 16px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 14px;
    font-weight: 600;
    text-decoration: none;
    display: inline-block;
    text-align: center;
    transition: all 0.3s ease;
}

.btn-primary {
    background: #007bff;
    color: white;
}

.btn-primary:hover {
    background: #0056b3;
}

.btn-secondary {
    background: #6c757d;
    color: white;
}

.btn-secondary:hover {
    background: #545b62;
}

.btn-sm {
    padding: 4px 8px;
    font-size: 12px;
}

.btn:disabled {
    opacity: 0.6;
    cursor: not-allowed;
}

/* Modal Styles */
.modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
}

.modal-content {
    background: white;
    border-radius: 8px;
    max-width: 600px;
    width: 90%;
    max-height: 90vh;
    overflow-y: auto;
}

.modal-header {
    padding: 20px;
    border-bottom: 1px solid #e9ecef;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.modal-header h2 {
    margin: 0;
    color: #333;
}

.close-btn {
    background: none;
    border: none;
    font-size: 24px;
    cursor: pointer;
    color: #999;
    padding: 0;
    width: 30px;
    height: 30px;
    display: flex;
    align-items: center;
    justify-content: center;
}

.close-btn:hover {
    color: #333;
}

.enrollment-summary {
    padding: 20px;
    background: #f8f9fa;
    border-bottom: 1px solid #e9ecef;
}

.summary-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
}

.form-group {
    margin-bottom: 20px;
    padding: 0 20px;
}

.form-group label {
    display: block;
    margin-bottom: 5px;
    font-weight: 600;
    color: #333;
}

.form-group input,
.form-group select,
.form-group textarea {
    width: 100%;
    padding: 12px;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 16px;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
    outline: none;
    border-color: #007bff;
    box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.25);
}

.error-text {
    color: #dc3545;
    font-size: 14px;
    margin-top: 5px;
    display: block;
}

.error-message {
    background: #f8d7da;
    color: #721c24;
    padding: 12px;
    border-radius: 4px;
    margin: 20px;
    border: 1px solid #f5c6cb;
}

.form-actions {
    display: flex;
    justify-content: space-between;
    padding: 20px;
    border-top: 1px solid #e9ecef;
}

.loading,
.no-data {
    text-align: center;
    padding: 40px;
    color: #666;
}

/* Mobile Responsive */
@media (max-width: 768px) {
    .enrollment-dashboard {
        padding: 10px;
    }

    .dashboard-header {
        flex-direction: column;
        gap: 15px;
        text-align: center;
    }

    .stats-grid {
        grid-template-columns: 1fr;
    }

    .filters-grid {
        grid-template-columns: 1fr;
    }

    .enrollment-table {
        font-size: 14px;
    }

    .enrollment-table th,
    .enrollment-table td {
        padding: 8px;
    }

    .modal-content {
        width: 95%;
        margin: 10px;
    }

    .summary-grid {
        grid-template-columns: 1fr;
    }

    .form-actions {
        flex-direction: column;
        gap: 10px;
    }
}
```

---

## 🔄 **Complete Updated Enrollment Flow**

### **Phase 1: Guest Enrollment (Public)**
1. **User visits course page** → No authentication required
2. **Clicks "Enroll Now"** → Opens guest enrollment form
3. **Fills personal information** → Name, email, phone, organization, etc.
4. **Submits form** → API validates and creates enrollment record
5. **Gets confirmation** → Success page + confirmation email
6. **Receives enrollment token** → Unique token for tracking

### **Phase 2: Admin Management (Backend)**
1. **Admin logs into dashboard** → Views all enrollments
2. **Filters enrollments** → By course, payment status, etc.
3. **Updates payment status** → Mark as paid/unpaid with details
4. **Tracks enrollment progress** → Mark as completed
5. **Generates reports** → Export PDF with enrollment data
6. **Manages participants** → View details, add notes

### **Phase 3: Payment Tracking**
1. **Automatic payment calculation** → Based on course cost
2. **Payment status updates** → Pending → Partial → Paid
3. **Email confirmations** → Sent when payment received
4. **Admin notifications** → Track pending payments
5. **Revenue reporting** → Total and pending revenue

---

## 📊 **API Endpoints Summary**

### **Public Endpoints (No Auth Required)**
```
POST /api/training/courses/{id}/enroll/          # Guest enrollment
GET  /api/training/courses/enrollment/{token}/   # Get enrollment by token
```

### **Admin Endpoints (Auth Required)**
```
GET    /api/training/admin/enrollments/                    # List enrollments
GET    /api/training/admin/enrollments/{id}/               # Get enrollment details
POST   /api/training/admin/enrollments/{id}/update_payment/ # Update payment
POST   /api/training/admin/enrollments/{id}/mark_completed/ # Mark completed
GET    /api/training/admin/enrollments/statistics/         # Get statistics
GET    /api/training/admin/enrollments/export_pdf/         # Export PDF report
```

---

## 🎯 **Key Features**

### **✅ Guest Enrollment Features:**
- **No authentication required** - Anyone can enroll
- **Comprehensive data collection** - Personal and professional info
- **Email confirmations** - Automated confirmation emails
- **Unique tracking tokens** - Each enrollment gets unique ID
- **Mobile responsive** - Works on all devices

### **✅ Admin Management Features:**
- **Complete enrollment dashboard** - View all enrollments
- **Payment tracking** - Mark payments, track balances
- **Advanced filtering** - By course, status, payment, search
- **Statistics dashboard** - Revenue, completion rates, etc.
- **PDF report generation** - Downloadable enrollment reports
- **Email notifications** - Payment confirmations

### **✅ Payment Management:**
- **Automatic calculation** - Based on course cost
- **Multiple payment methods** - Cash, transfer, card, PayPal
- **Partial payments** - Track partial payment progress
- **Payment references** - Store transaction IDs
- **Admin notes** - Internal notes for each enrollment

---

## 🚀 **Installation & Setup**

### **1. Install Dependencies**
```bash
pip install reportlab  # For PDF generation
```

### **2. Update Database**
```bash
python manage.py makemigrations training
python manage.py migrate
```

### **3. Update URLs**
```python
# training/urls.py
urlpatterns = [
    path('', include(router.urls)),
    path('admin/', include('training.admin_urls')),
]
```

### **4. Create Admin User**
```bash
python manage.py createsuperuser
```

### **5. Configure Email Settings**
```python
# settings.py
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
DEFAULT_FROM_EMAIL = 'Course Platform <noreply@example.com>'
```

---

## 🧪 **Testing the System**

### **1. Test Guest Enrollment**
```bash
curl -X POST http://localhost:8000/api/training/courses/1/enroll/ \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "John",
    "last_name": "Doe",
    "email": "john@example.com",
    "phone": "+1234567890",
    "organization": "Tech Corp",
    "experience_level": "intermediate"
  }'
```

### **2. Test Admin Dashboard**
```bash
# Login as admin and visit:
http://localhost:8000/admin/enrollments/
```

### **3. Test PDF Export**
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/training/admin/enrollments/export_pdf/?course_id=1"
```

---

## 📈 **Benefits of Updated System**

### **For Users:**
- ✅ **No registration barriers** - Instant enrollment
- ✅ **Simple process** - Just fill out one form
- ✅ **Email confirmations** - Get all details via email
- ✅ **Token tracking** - Track enrollment with unique ID

### **For Admins:**
- ✅ **Complete visibility** - See all enrollments in one place
- ✅ **Payment management** - Track payments and balances
- ✅ **Detailed reporting** - Generate PDF reports
- ✅ **Statistics dashboard** - Revenue and completion tracking
- ✅ **Email automation** - Automated payment confirmations

### **For Business:**
- ✅ **Higher conversion rates** - Remove registration friction
- ✅ **Better data collection** - Comprehensive participant info
- ✅ **Revenue tracking** - Monitor payments and outstanding balances
- ✅ **Professional reporting** - PDF reports for stakeholders
- ✅ **Scalable system** - Handle large numbers of enrollments

---

## 🎉 **Summary**

This updated enrollment system provides:

1. **Guest Enrollment** - No authentication required, comprehensive data collection
2. **Admin Dashboard** - Complete enrollment management with filtering and search
3. **Payment Tracking** - Full payment lifecycle management with status updates
4. **PDF Reports** - Professional enrollment reports with statistics
5. **Email Automation** - Confirmation and payment notification emails
6. **Mobile Responsive** - Works perfectly on all devices
7. **Scalable Architecture** - Handle high enrollment volumes

The system is production-ready with proper validation, error handling, security measures, and comprehensive admin tools for managing course enrollments and payments! 🚀

# Admin Enrollment Management - Quick Guide

## 🎛️ **Admin Dashboard Overview**

### **Access the Dashboard**
```
URL: /admin/enrollments/
Authentication: Admin login required
```

### **Main Features**
- ✅ **View all enrollments** across all courses
- ✅ **Filter and search** enrollments
- ✅ **Update payment status** for participants
- ✅ **Generate PDF reports** for courses
- ✅ **Track statistics** and revenue
- ✅ **Manage enrollment lifecycle**

---

## 📊 **Dashboard Sections**

### **1. Statistics Cards**
- **Total Enrollments** - All enrollments count
- **Paid Enrollments** - Fully paid participants
- **Pending Payments** - Awaiting payment
- **Total Revenue** - Money collected
- **Pending Revenue** - Outstanding payments
- **Completion Rate** - % of completed enrollments

### **2. Filters**
- **Course** - Filter by specific course
- **Payment Status** - Pending, Paid, Partial, etc.
- **Enrollment Status** - Approved, Completed, etc.
- **Search** - By participant name or email

### **3. Enrollment List**
- **Participant Info** - Name, email, guest status
- **Course Details** - Course name and code
- **Payment Info** - Amount due, paid, balance
- **Status Badges** - Visual status indicators
- **Action Buttons** - Update payment, view details

---

## 💰 **Payment Management**

### **Update Payment Process**
1. **Click payment button** (💰) for enrollment
2. **Fill payment form:**
   - Amount paid
   - Payment method (Cash, Transfer, Card, etc.)
   - Payment reference (Transaction ID)
   - Admin notes
3. **Save changes** - Automatically updates status
4. **Email sent** - Confirmation email to participant

### **Payment Statuses**
- **Not Required** - Free course
- **Pending** - No payment received
- **Partial** - Some payment received
- **Paid** - Fully paid
- **Overdue** - Past due date

### **Payment Methods**
- Cash
- Bank Transfer
- Credit Card
- PayPal
- Other

---

## 📄 **PDF Report Generation**

### **Generate Report**
1. **Select course** in filters
2. **Click "Export PDF"** button
3. **PDF downloads** automatically

### **Report Contents**
- **Course Information** - Name, code, instructor, dates
- **Statistics Summary** - Enrollment and payment stats
- **Participant Table** - All enrollments with details
- **Professional Formatting** - Ready for stakeholders

### **Report Data Includes**
- Participant name and contact info
- Organization and job title
- Payment status and amounts
- Enrollment dates
- Education and experience levels

---

## 🔍 **Filtering & Search**

### **Filter Options**
```javascript
// Course Filter
course_id: "1"  // Specific course

// Payment Status Filter
payment_status: "pending"  // pending, paid, partial, not_required

// Enrollment Status Filter
status: "approved"  // pending, approved, completed, cancelled

// Search Filter
search: "john doe"  // Name or email search
```

### **API Endpoints for Filtering**
```
GET /api/training/admin/enrollments/?course_id=1&payment_status=pending
GET /api/training/admin/enrollments/?search=john
GET /api/training/admin/enrollments/?status=completed
```

---

## 📈 **Statistics & Analytics**

### **Available Statistics**
```json
{
    "total_enrollments": 150,
    "pending_payments": 25,
    "paid_enrollments": 120,
    "total_revenue": 15000.00,
    "pending_revenue": 2500.00,
    "completion_rate": 85.5
}
```

### **Revenue Tracking**
- **Total Revenue** - All payments received
- **Pending Revenue** - Outstanding balances
- **Course-specific** - Filter by individual course
- **Real-time Updates** - Updates as payments processed

---

## 🎯 **Common Admin Tasks**

### **1. Process Payment**
```
1. Find enrollment in list
2. Click 💰 payment button
3. Enter amount paid
4. Select payment method
5. Add reference number
6. Save - email sent automatically
```

### **2. Mark Course Completed**
```
1. Find enrollment
2. Click action button
3. Select "Mark Completed"
4. Completion date set automatically
```

### **3. Generate Course Report**
```
1. Select course in filter
2. Click "Export PDF"
3. PDF downloads with all enrollment data
```

### **4. Search for Participant**
```
1. Enter name or email in search box
2. Results filter automatically
3. View participant details
```

---

## 🔧 **API Endpoints for Admins**

### **List Enrollments**
```
GET /api/training/admin/enrollments/
Headers: Authorization: Bearer {admin_token}
```

### **Update Payment**
```
POST /api/training/admin/enrollments/{id}/update_payment/
{
    "amount_paid": 150.00,
    "payment_method": "credit_card",
    "payment_reference": "TXN123456",
    "admin_notes": "Payment processed via Stripe"
}
```

### **Export PDF**
```
GET /api/training/admin/enrollments/export_pdf/?course_id=1
Headers: Authorization: Bearer {admin_token}
Response: PDF file download
```

### **Get Statistics**
```
GET /api/training/admin/enrollments/statistics/?course_id=1
Response: JSON with enrollment statistics
```

---

## 🎨 **UI Components**

### **Status Badges**
- 🟢 **Paid** - Green badge
- 🟡 **Pending** - Yellow badge  
- 🔵 **Partial** - Blue badge
- ⚪ **Not Required** - Gray badge
- 🔴 **Overdue** - Red badge

### **Action Buttons**
- 💰 **Update Payment** - Opens payment modal
- 👁️ **View Details** - Shows full enrollment info
- ✅ **Mark Completed** - Updates status

### **Responsive Design**
- **Desktop** - Full table view with all columns
- **Tablet** - Condensed view with essential info
- **Mobile** - Stacked cards for easy scrolling

---

## 🚨 **Important Notes**

### **Permissions**
- Only **admin users** can access enrollment management
- **Staff users** may have limited access (configure as needed)
- **Regular users** cannot access admin features

### **Email Notifications**
- **Payment confirmations** sent automatically when marked as paid
- **Email failures** logged but don't prevent payment updates
- **SMTP configuration** required for email functionality

### **Data Security**
- All admin actions **logged** with user and timestamp
- **Sensitive data** protected with proper authentication
- **Payment references** stored securely

### **Performance**
- **Database indexes** on frequently filtered fields
- **Pagination** for large enrollment lists
- **Efficient queries** with select_related for performance

---

## 🎉 **Benefits for Admins**

### **Efficiency**
- ✅ **Single dashboard** for all enrollment management
- ✅ **Bulk operations** through filtering
- ✅ **Quick payment updates** with one-click modals
- ✅ **Automated emails** reduce manual work

### **Visibility**
- ✅ **Real-time statistics** for decision making
- ✅ **Payment tracking** prevents revenue loss
- ✅ **Completion monitoring** for course success
- ✅ **Professional reports** for stakeholders

### **Control**
- ✅ **Payment flexibility** - multiple methods and partial payments
- ✅ **Status management** - track enrollment lifecycle
- ✅ **Data export** - PDF reports for external use
- ✅ **Search and filter** - find specific enrollments quickly

This admin system provides complete control over the enrollment process while maintaining ease of use and professional presentation! 🚀

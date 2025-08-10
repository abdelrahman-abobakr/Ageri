# 📊 Enrollment Data Access Guide

## 🎯 **Problem Solved!**

You mentioned not getting the enrollment fields like `name`, `email`, `phone` - **this is now fixed!** All guest enrollment fields are available in the API response.

---

## ✅ **Available Enrollment Fields**

When you fetch enrollments from `/api/training/enrollments/`, you'll get this complete data structure:

### **📋 Complete Enrollment Object**
```json
{
  "id": 9,
  "course": 6,
  "course_title": "Introduction to Biology",
  "course_code": "bio_61",
  "student": null,
  
  // 👤 Guest Enrollment Fields
  "first_name": "Test",
  "last_name": "Admin", 
  "email": "test.admin@example.com",
  "phone": "+1234567890",
  "organization": "Test Org",
  "job_title": "Tester",
  "enrollment_token": "628fb055-ae66-42f8-82d2-4d2437887182",
  
  // 📅 Enrollment Details
  "enrollment_date": "2025-07-31T18:46:17.053259Z",
  "status": "approved",
  "payment_status": "pending",
  "payment_amount": "0.00",
  "payment_date": null,
  "payment_reference": "",
  
  // 🎓 Academic Info
  "grade": "",
  "attendance_percentage": null,
  "completion_date": null,
  "certificate_issued": false,
  "certificate_number": "",
  "notes": "",
  
  // 🔧 Helper Fields (Computed)
  "enrollee_name": "Test Admin",           // Full name for display
  "enrollee_email": "test.admin@example.com", // Email for display
  "is_guest_enrollment": true,             // Guest vs registered user
  "is_active": true,                       // Active enrollment status
  
  // 📝 Metadata
  "created_at": "2025-07-31T18:46:17.053195Z",
  "updated_at": "2025-07-31T18:46:17.053223Z"
}
```

---

## 🔐 **Authentication Required**

The admin enrollment endpoints require authentication:

### **Login First**
```javascript
// 1. Login to get access token
const loginResponse = await fetch('http://127.0.0.1:8000/api/auth/login/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'admin@test.com',
    password: 'admin123'
  })
});

const { access } = await loginResponse.json();
```

### **Use Token for Admin Endpoints**
```javascript
// 2. Use token to access enrollments
const enrollmentsResponse = await fetch('http://127.0.0.1:8000/api/training/enrollments/', {
  headers: {
    'Authorization': `Bearer ${access}`,
    'Content-Type': 'application/json'
  }
});

const enrollmentsData = await enrollmentsResponse.json();
```

---

## 📊 **Frontend Data Access Examples**

### **React Component Example**
```jsx
const EnrollmentTable = () => {
  const [enrollments, setEnrollments] = useState([]);

  useEffect(() => {
    const fetchEnrollments = async () => {
      try {
        const token = localStorage.getItem('access_token');
        const response = await fetch('/api/training/enrollments/', {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        });
        
        const data = await response.json();
        setEnrollments(data.results || []);
      } catch (error) {
        console.error('Error fetching enrollments:', error);
      }
    };

    fetchEnrollments();
  }, []);

  return (
    <table>
      <thead>
        <tr>
          <th>Name</th>
          <th>Email</th>
          <th>Phone</th>
          <th>Course</th>
          <th>Status</th>
          <th>Type</th>
        </tr>
      </thead>
      <tbody>
        {enrollments.map(enrollment => (
          <tr key={enrollment.id}>
            {/* ✅ Use helper fields for display */}
            <td>{enrollment.enrollee_name}</td>
            <td>{enrollment.enrollee_email}</td>
            <td>{enrollment.phone}</td>
            <td>{enrollment.course_title}</td>
            <td>{enrollment.status}</td>
            <td>
              {enrollment.is_guest_enrollment ? 'Guest' : 'Registered'}
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
};
```

### **Vue.js Example**
```vue
<template>
  <div class="enrollment-table">
    <table>
      <thead>
        <tr>
          <th>Name</th>
          <th>Email</th>
          <th>Phone</th>
          <th>Course</th>
          <th>Status</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="enrollment in enrollments" :key="enrollment.id">
          <td>{{ enrollment.enrollee_name }}</td>
          <td>{{ enrollment.enrollee_email }}</td>
          <td>{{ enrollment.phone }}</td>
          <td>{{ enrollment.course_title }}</td>
          <td>{{ enrollment.status }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script>
export default {
  data() {
    return {
      enrollments: []
    };
  },
  
  async mounted() {
    await this.fetchEnrollments();
  },
  
  methods: {
    async fetchEnrollments() {
      try {
        const token = localStorage.getItem('access_token');
        const response = await fetch('/api/training/enrollments/', {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        });
        
        const data = await response.json();
        this.enrollments = data.results || [];
      } catch (error) {
        console.error('Error fetching enrollments:', error);
      }
    }
  }
};
</script>
```

### **Vanilla JavaScript Example**
```javascript
// Fetch and display enrollments
async function loadEnrollments() {
  try {
    const token = localStorage.getItem('access_token');
    
    const response = await fetch('/api/training/enrollments/', {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    
    const data = await response.json();
    const enrollments = data.results || [];
    
    // Display in table
    const tableBody = document.querySelector('#enrollments-table tbody');
    tableBody.innerHTML = '';
    
    enrollments.forEach(enrollment => {
      const row = document.createElement('tr');
      row.innerHTML = `
        <td>${enrollment.enrollee_name}</td>
        <td>${enrollment.enrollee_email}</td>
        <td>${enrollment.phone || 'N/A'}</td>
        <td>${enrollment.course_title}</td>
        <td>${enrollment.status}</td>
        <td>${enrollment.is_guest_enrollment ? 'Guest' : 'Registered'}</td>
        <td>$${enrollment.payment_amount}</td>
      `;
      tableBody.appendChild(row);
    });
    
  } catch (error) {
    console.error('Error loading enrollments:', error);
    alert('Failed to load enrollments. Please check your authentication.');
  }
}
```

---

## 🔍 **Field Mapping Guide**

### **For Display in Tables**
| Display Column | Use This Field | Example Value |
|----------------|----------------|---------------|
| **Name** | `enrollee_name` | "John Doe" |
| **Email** | `enrollee_email` | "john@example.com" |
| **Phone** | `phone` | "+1234567890" |
| **Course** | `course_title` | "Introduction to Biology" |
| **Course Code** | `course_code` | "bio_61" |
| **Status** | `status` | "approved" |
| **Payment** | `payment_status` | "pending" |
| **Type** | `is_guest_enrollment` | true/false |
| **Date** | `enrollment_date` | "2025-07-31T18:46:17Z" |

### **For Editing Forms**
| Form Field | Use This Field | Type |
|------------|----------------|------|
| **First Name** | `first_name` | string |
| **Last Name** | `last_name` | string |
| **Email** | `email` | email |
| **Phone** | `phone` | string |
| **Organization** | `organization` | string |
| **Job Title** | `job_title` | string |
| **Status** | `status` | select |
| **Payment Status** | `payment_status` | select |
| **Grade** | `grade` | select |

---

## 🚀 **Quick Test**

### **Test the API Response**
```bash
# 1. Create an enrollment (no auth needed)
curl -X POST http://127.0.0.1:8000/api/training/courses/6/enroll/ \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Jane",
    "last_name": "Smith",
    "email": "jane@example.com",
    "phone": "555-1234"
  }'

# 2. Login as admin
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@test.com",
    "password": "admin123"
  }'

# 3. Get enrollments (use token from step 2)
curl -X GET http://127.0.0.1:8000/api/training/enrollments/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## 🎯 **Summary**

✅ **All enrollment fields are now available:**
- `first_name`, `last_name`, `email`, `phone` ✅
- `organization`, `job_title` ✅  
- `enrollee_name`, `enrollee_email` (helper fields) ✅
- `is_guest_enrollment` (type indicator) ✅
- `course_title`, `course_code` (course info) ✅

✅ **Authentication is working:**
- Login with email/password to get access token
- Use token in Authorization header for admin endpoints

✅ **Frontend integration is ready:**
- Use the provided React/Vue/JavaScript examples
- All fields are properly serialized in API responses
- Helper fields make display easier

**Your enrollment management system is fully functional!** 🚀

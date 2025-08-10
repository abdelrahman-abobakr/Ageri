# Course API Quick Reference

## 🚀 **Quick Start**

### **Base Configuration**
```javascript
const API_BASE_URL = 'http://localhost:8000/api';
const COURSES_ENDPOINT = `${API_BASE_URL}/training/courses/`;
```

### **Authentication Headers**
```javascript
const headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'Authorization': `Bearer ${localStorage.getItem('access_token')}`
};
```

---

## 📋 **API Endpoints**

| Method | Endpoint | Auth Required | Description |
|--------|----------|---------------|-------------|
| `GET` | `/api/training/courses/` | ❌ | List all courses |
| `POST` | `/api/training/courses/` | ✅ | Create new course |
| `GET` | `/api/training/courses/{id}/` | ❌ | Get course details |
| `PUT` | `/api/training/courses/{id}/` | ✅ | Update course |
| `PATCH` | `/api/training/courses/{id}/` | ✅ | Partial update |
| `DELETE` | `/api/training/courses/{id}/` | ✅ | Delete course |
| `POST` | `/api/training/courses/{id}/enroll/` | ✅ | Enroll in course |
| `GET` | `/api/training/courses/featured/` | ❌ | Featured courses |
| `GET` | `/api/training/courses/upcoming/` | ❌ | Upcoming courses |

---

## 🔍 **Query Parameters**

### **Filtering**
```javascript
const filters = {
    search: 'python',           // Search in name, code, description
    type: 'course',            // course, workshop, seminar
    status: 'published',       // draft, published, inactive
    is_featured: true,         // true, false
    is_public: true,          // true, false
    department: 1,            // Department ID
    ordering: '-start_date'   // Sort by field (- for desc)
};
```

### **Pagination**
```javascript
const params = {
    page: 2,        // Page number
    page_size: 20   // Items per page (default: 20)
};
```

---

## 💻 **Code Examples**

### **1. Fetch All Courses**
```javascript
async function getCourses(filters = {}) {
    const params = new URLSearchParams(filters);
    const response = await fetch(`${COURSES_ENDPOINT}?${params}`, {
        headers: { 'Accept': 'application/json' }
    });
    return await response.json();
}
```

### **2. Create Course**
```javascript
async function createCourse(courseData) {
    const response = await fetch(COURSES_ENDPOINT, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${accessToken}`
        },
        body: JSON.stringify(courseData)
    });
    return await response.json();
}
```

### **3. Enroll in Course**
```javascript
async function enrollInCourse(courseId) {
    const response = await fetch(`${COURSES_ENDPOINT}${courseId}/enroll/`, {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${accessToken}`,
            'Content-Type': 'application/json'
        }
    });
    return await response.json();
}
```

---

## 📊 **Response Format**

### **Course List Response**
```json
{
    "count": 25,
    "next": "http://localhost:8000/api/training/courses/?page=2",
    "previous": null,
    "results": [
        {
            "id": 1,
            "course_name": "Python Programming",
            "course_code": "PY101",
            "instructor": "Dr. Smith",
            "cost": "150.00",
            "is_free": false,
            "start_date": "2025-03-01",
            "end_date": "2025-03-31",
            "registration_deadline": "2025-02-25",
            "training_hours": 40,
            "max_participants": 30,
            "current_enrollment": 15,
            "enrollment_percentage": 50.0,
            "status": "published",
            "is_featured": true,
            "is_registration_open": true,
            "is_full": false,
            "can_register": true,
            "created_at": "2025-01-15T10:30:00Z"
        }
    ]
}
```

### **Single Course Response**
```json
{
    "id": 1,
    "course_name": "Python Programming",
    "course_code": "PY101",
    "instructor": "Dr. Smith",
    "description": "Learn Python programming from basics to advanced",
    "cost": "150.00",
    "is_free": false,
    "start_date": "2025-03-01",
    "end_date": "2025-03-31",
    "registration_deadline": "2025-02-25",
    "training_hours": 40,
    "type": "course",
    "max_participants": 30,
    "current_enrollment": 15,
    "enrollment_percentage": 50.0,
    "status": "published",
    "is_featured": true,
    "is_public": true,
    "featured_image": "http://localhost:8000/media/courses/python.jpg",
    "syllabus": "http://localhost:8000/media/syllabi/python_syllabus.pdf",
    "prerequisites": "Basic computer knowledge",
    "materials_provided": "Laptop, course materials, certificate",
    "tags": "programming, python, beginner",
    "department": 1,
    "department_name": "Computer Science",
    "is_registration_open": true,
    "is_full": false,
    "can_register": true,
    "enrollments_count": 15,
    "created_at": "2025-01-15T10:30:00Z",
    "updated_at": "2025-01-20T14:45:00Z"
}
```

---

## ⚠️ **Error Responses**

### **Validation Error (400)**
```json
{
    "course_name": ["This field is required."],
    "end_date": ["End date must be after start date."],
    "cost": ["Ensure this value is greater than or equal to 0."]
}
```

### **Authentication Error (401)**
```json
{
    "detail": "Authentication credentials were not provided."
}
```

### **Permission Error (403)**
```json
{
    "detail": "You do not have permission to perform this action."
}
```

### **Not Found Error (404)**
```json
{
    "detail": "Not found."
}
```

---

## 🎯 **Common Use Cases**

### **1. Course Listing Page**
```javascript
// Load courses with search and filters
const loadCourses = async () => {
    const filters = {
        search: document.getElementById('search').value,
        type: document.getElementById('type').value,
        status: 'published'
    };
    
    const data = await getCourses(filters);
    displayCourses(data.results);
    setupPagination(data);
};
```

### **2. Course Enrollment**
```javascript
// Check authentication and enroll
const handleEnroll = async (courseId) => {
    const token = localStorage.getItem('access_token');
    if (!token) {
        window.location.href = '/login';
        return;
    }
    
    try {
        await enrollInCourse(courseId);
        alert('Successfully enrolled!');
        loadCourses(); // Refresh list
    } catch (error) {
        alert('Enrollment failed: ' + error.message);
    }
};
```

### **3. Admin Course Management**
```javascript
// Create/Edit course form
const handleSubmit = async (formData) => {
    try {
        if (isEditing) {
            await updateCourse(courseId, formData);
        } else {
            await createCourse(formData);
        }
        window.location.href = '/admin/courses';
    } catch (error) {
        displayFormErrors(error.errors);
    }
};
```

---

## 🔧 **Utility Functions**

### **Date Formatting**
```javascript
const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
};
```

### **Currency Formatting**
```javascript
const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(amount);
};
```

### **Progress Calculation**
```javascript
const calculateProgress = (current, max) => {
    return max > 0 ? Math.round((current / max) * 100) : 0;
};
```

---

## 🎨 **CSS Classes**

### **Course Card Styling**
```css
.course-card { border: 1px solid #ddd; border-radius: 8px; padding: 16px; }
.course-card.featured { border-color: #007bff; background: #f8f9ff; }
.course-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; }
.btn-primary { background: #007bff; color: white; padding: 8px 16px; border: none; border-radius: 4px; }
.progress-bar { background: #f0f0f0; height: 8px; border-radius: 4px; overflow: hidden; }
.progress-fill { background: #007bff; height: 100%; transition: width 0.3s; }
```

---

## 📱 **Mobile Responsive**

### **Responsive Grid**
```css
@media (max-width: 768px) {
    .course-grid { grid-template-columns: 1fr; }
    .filters { flex-direction: column; gap: 10px; }
    .course-card { margin: 10px 0; }
}
```

---

## 🔐 **Security Notes**

- Always validate user input on both client and server
- Use HTTPS in production
- Store JWT tokens securely (consider httpOnly cookies)
- Implement CSRF protection for state-changing operations
- Sanitize user-generated content before display
- Rate limit API calls to prevent abuse

---

## 📚 **Additional Resources**

- **Full Guide:** `FRONTEND_COURSES_GUIDE.md`
- **API Documentation:** `http://localhost:8000/api/docs/`
- **Django Admin:** `http://localhost:8000/admin/`
- **Browsable API:** `http://localhost:8000/api/training/courses/`

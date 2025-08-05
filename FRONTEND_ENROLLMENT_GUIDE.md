# Frontend Course Enrollment Guide

## 🎯 **Overview**

This guide provides everything your frontend developers need to implement the course enrollment system. The system supports **guest enrollment** - no authentication required!

---

## 🔗 **API Endpoints**

### **Base URL**
```
http://127.0.0.1:8000/api/training/
```

### **Key Endpoints**
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/courses/` | List all published courses | ❌ No |
| `GET` | `/courses/{id}/` | Get course details | ❌ No |
| `POST` | `/courses/{id}/enroll/` | Enroll in course (guest) | ❌ No |

---

## 📚 **1. Fetching Courses**

### **List All Courses**
```javascript
// Fetch all published courses
const fetchCourses = async () => {
  try {
    const response = await fetch('http://127.0.0.1:8000/api/training/courses/');
    const data = await response.json();
    
    if (response.ok) {
      return data.results; // Array of courses
    } else {
      throw new Error('Failed to fetch courses');
    }
  } catch (error) {
    console.error('Error fetching courses:', error);
    throw error;
  }
};
```

### **Course Object Structure**
```javascript
{
  "id": 6,
  "title": "Introduction to Biology",
  "course_code": "bio_61",
  "description": "Basic biology concepts and principles",
  "instructor": "Dr. Sarah Johnson",
  "department_name": "Biology Department",
  "start_date": "2025-02-01",
  "end_date": "2025-05-30",
  "cost": "500.00",
  "max_participants": 30,
  "current_enrollment": 15,
  "status": "published",
  "is_registration_open": true,
  "is_full": false,
  "can_register": true,
  "is_free": false,
  "enrollment_percentage": 50.0
}
```

### **Get Course Details**
```javascript
const fetchCourseDetails = async (courseId) => {
  try {
    const response = await fetch(`http://127.0.0.1:8000/api/training/courses/${courseId}/`);
    const course = await response.json();
    
    if (response.ok) {
      return course;
    } else {
      throw new Error('Course not found');
    }
  } catch (error) {
    console.error('Error fetching course details:', error);
    throw error;
  }
};
```

---

## 🎓 **2. Course Enrollment**

### **Enrollment Function**
```javascript
const enrollInCourse = async (courseId, enrollmentData) => {
  try {
    const response = await fetch(`http://127.0.0.1:8000/api/training/courses/${courseId}/enroll/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(enrollmentData)
    });
    
    const result = await response.json();
    
    if (response.ok) {
      return {
        success: true,
        data: result
      };
    } else {
      return {
        success: false,
        errors: result.details || { general: result.error }
      };
    }
  } catch (error) {
    console.error('Network error during enrollment:', error);
    return {
      success: false,
      errors: { network: 'Network error occurred' }
    };
  }
};
```

### **Required Enrollment Data**
```javascript
const enrollmentData = {
  // REQUIRED FIELDS
  first_name: "John",           // String, max 100 chars
  last_name: "Doe",             // String, max 100 chars  
  email: "john@example.com",    // Valid email format
  phone: "+1234567890",         // String, max 20 chars
  
  // OPTIONAL FIELDS
  organization: "Tech Corp",     // String, max 200 chars
  job_title: "Developer"        // String, max 100 chars
};
```

### **Successful Enrollment Response**
```javascript
{
  "message": "Successfully enrolled in course",
  "enrollment": {
    "id": 6,
    "course": 6,
    "course_code": "bio_61",
    "first_name": "John",
    "last_name": "Doe",
    "email": "john@example.com",
    "phone": "+1234567890",
    "organization": "Tech Corp",
    "job_title": "Developer",
    "enrollment_date": "2025-07-31T08:29:17.107845Z",
    "enrollment_token": "b56a0158-0b08-401b-8e89-2272d78e6e53",
    "status": "approved",
    "payment_status": "pending",
    "payment_amount": "0.00",
    "enrollee_name": "John Doe",
    "enrollee_email": "john@example.com",
    "is_guest_enrollment": true
  },
  "enrollment_token": "b56a0158-0b08-401b-8e89-2272d78e6e53",
  "payment_amount": 500.0,
  "next_steps": [
    "Save your enrollment ID for future reference",
    "Check course start date and prepare materials", 
    "Contact support if you have questions"
  ]
}
```

### **Error Response Example**
```javascript
{
  "error": "Invalid enrollment data",
  "details": {
    "first_name": ["First name is required."],
    "last_name": ["Last name is required."],
    "email": ["Email is required."],
    "phone": ["Phone number is required."]
  }
}
```

---

## 🎨 **3. React Component Examples**

### **Course List Component**
```jsx
import React, { useState, useEffect } from 'react';

const CourseList = () => {
  const [courses, setCourses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const loadCourses = async () => {
      try {
        const response = await fetch('http://127.0.0.1:8000/api/training/courses/');
        const data = await response.json();
        setCourses(data.results || []);
      } catch (err) {
        setError('Failed to load courses');
      } finally {
        setLoading(false);
      }
    };

    loadCourses();
  }, []);

  if (loading) return <div>Loading courses...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div className="course-list">
      <h2>Available Courses</h2>
      {courses.map(course => (
        <CourseCard key={course.id} course={course} />
      ))}
    </div>
  );
};
```

### **Course Card Component**
```jsx
const CourseCard = ({ course }) => {
  const [showEnrollment, setShowEnrollment] = useState(false);

  return (
    <div className="course-card">
      <h3>{course.title}</h3>
      <p><strong>Code:</strong> {course.course_code}</p>
      <p><strong>Instructor:</strong> {course.instructor}</p>
      <p><strong>Department:</strong> {course.department_name}</p>
      <p><strong>Duration:</strong> {course.start_date} to {course.end_date}</p>
      <p><strong>Cost:</strong> ${course.cost}</p>
      <p><strong>Enrollment:</strong> {course.current_enrollment}/{course.max_participants}</p>
      
      <div className="enrollment-status">
        {course.is_full ? (
          <span className="status-full">Course Full</span>
        ) : course.can_register ? (
          <button 
            onClick={() => setShowEnrollment(true)}
            className="btn-enroll"
          >
            Enroll Now
          </button>
        ) : (
          <span className="status-closed">Registration Closed</span>
        )}
      </div>

      {showEnrollment && (
        <EnrollmentForm
          course={course}
          onClose={() => setShowEnrollment(false)}
        />
      )}
    </div>
  );
};
```

### **Enrollment Form Component**
```jsx
import React, { useState } from 'react';

const EnrollmentForm = ({ course, onClose }) => {
  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    email: '',
    phone: '',
    organization: '',
    job_title: ''
  });

  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(null);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));

    // Clear error when user starts typing
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: null
      }));
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setErrors({});

    try {
      const response = await fetch(`http://127.0.0.1:8000/api/training/courses/${course.id}/enroll/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData)
      });

      const result = await response.json();

      if (response.ok) {
        setSuccess(result);
        // Store enrollment token for future reference
        localStorage.setItem(`enrollment_${course.id}`, result.enrollment_token);
      } else {
        setErrors(result.details || { general: result.error });
      }
    } catch (error) {
      setErrors({ network: 'Network error occurred. Please try again.' });
    } finally {
      setLoading(false);
    }
  };

  if (success) {
    return (
      <div className="enrollment-success">
        <h3>✅ Enrollment Successful!</h3>
        <p><strong>Course:</strong> {course.title}</p>
        <p><strong>Enrollee:</strong> {success.enrollment.enrollee_name}</p>
        <p><strong>Enrollment Token:</strong> {success.enrollment_token}</p>
        <p><strong>Payment Amount:</strong> ${success.payment_amount}</p>

        <div className="next-steps">
          <h4>Next Steps:</h4>
          <ul>
            {success.next_steps.map((step, index) => (
              <li key={index}>{step}</li>
            ))}
          </ul>
        </div>

        <button onClick={onClose} className="btn-close">Close</button>
      </div>
    );
  }

  return (
    <div className="enrollment-form-overlay">
      <div className="enrollment-form">
        <h3>Enroll in {course.title}</h3>

        <form onSubmit={handleSubmit}>
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="first_name">First Name *</label>
              <input
                type="text"
                id="first_name"
                name="first_name"
                value={formData.first_name}
                onChange={handleChange}
                className={errors.first_name ? 'error' : ''}
                required
              />
              {errors.first_name && (
                <span className="error-message">{errors.first_name[0]}</span>
              )}
            </div>

            <div className="form-group">
              <label htmlFor="last_name">Last Name *</label>
              <input
                type="text"
                id="last_name"
                name="last_name"
                value={formData.last_name}
                onChange={handleChange}
                className={errors.last_name ? 'error' : ''}
                required
              />
              {errors.last_name && (
                <span className="error-message">{errors.last_name[0]}</span>
              )}
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="email">Email Address *</label>
            <input
              type="email"
              id="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              className={errors.email ? 'error' : ''}
              required
            />
            {errors.email && (
              <span className="error-message">{errors.email[0]}</span>
            )}
          </div>

          <div className="form-group">
            <label htmlFor="phone">Phone Number *</label>
            <input
              type="tel"
              id="phone"
              name="phone"
              value={formData.phone}
              onChange={handleChange}
              className={errors.phone ? 'error' : ''}
              required
            />
            {errors.phone && (
              <span className="error-message">{errors.phone[0]}</span>
            )}
          </div>

          <div className="form-group">
            <label htmlFor="organization">Organization</label>
            <input
              type="text"
              id="organization"
              name="organization"
              value={formData.organization}
              onChange={handleChange}
            />
          </div>

          <div className="form-group">
            <label htmlFor="job_title">Job Title</label>
            <input
              type="text"
              id="job_title"
              name="job_title"
              value={formData.job_title}
              onChange={handleChange}
            />
          </div>

          {errors.general && (
            <div className="error-message general-error">{errors.general}</div>
          )}

          {errors.network && (
            <div className="error-message network-error">{errors.network}</div>
          )}

          <div className="form-actions">
            <button
              type="button"
              onClick={onClose}
              className="btn-cancel"
              disabled={loading}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="btn-submit"
              disabled={loading}
            >
              {loading ? 'Enrolling...' : 'Enroll Now'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
```

---

## 🎨 **4. CSS Styling Examples**

### **Basic Styles**
```css
/* Course List Styles */
.course-list {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.course-card {
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
  background: white;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.course-card h3 {
  color: #333;
  margin-bottom: 10px;
}

.course-card p {
  margin: 5px 0;
  color: #666;
}

/* Enrollment Status */
.enrollment-status {
  margin-top: 15px;
}

.btn-enroll {
  background: #007bff;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 5px;
  cursor: pointer;
  font-size: 16px;
}

.btn-enroll:hover {
  background: #0056b3;
}

.status-full {
  color: #dc3545;
  font-weight: bold;
}

.status-closed {
  color: #6c757d;
  font-weight: bold;
}

/* Enrollment Form Styles */
.enrollment-form-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.enrollment-form {
  background: white;
  padding: 30px;
  border-radius: 10px;
  max-width: 500px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
}

.enrollment-form h3 {
  margin-bottom: 20px;
  color: #333;
}

.form-row {
  display: flex;
  gap: 15px;
}

.form-group {
  margin-bottom: 15px;
  flex: 1;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
  color: #333;
}

.form-group input {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 5px;
  font-size: 16px;
}

.form-group input:focus {
  outline: none;
  border-color: #007bff;
  box-shadow: 0 0 0 2px rgba(0,123,255,0.25);
}

.form-group input.error {
  border-color: #dc3545;
}

.error-message {
  color: #dc3545;
  font-size: 14px;
  margin-top: 5px;
  display: block;
}

.general-error, .network-error {
  background: #f8d7da;
  color: #721c24;
  padding: 10px;
  border-radius: 5px;
  margin-bottom: 15px;
}

.form-actions {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
  margin-top: 20px;
}

.btn-cancel {
  background: #6c757d;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 5px;
  cursor: pointer;
}

.btn-submit {
  background: #28a745;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 5px;
  cursor: pointer;
}

.btn-submit:disabled {
  background: #6c757d;
  cursor: not-allowed;
}

/* Success Message */
.enrollment-success {
  background: #d4edda;
  border: 1px solid #c3e6cb;
  color: #155724;
  padding: 20px;
  border-radius: 5px;
}

.enrollment-success h3 {
  margin-bottom: 15px;
}

.next-steps {
  margin: 15px 0;
}

.next-steps ul {
  margin: 10px 0;
  padding-left: 20px;
}

.btn-close {
  background: #007bff;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 5px;
  cursor: pointer;
  margin-top: 15px;
}
```

---

## 🔧 **5. Utility Functions**

### **API Helper Functions**
```javascript
// api.js
const API_BASE_URL = 'http://127.0.0.1:8000/api/training';

export const courseAPI = {
  // Get all courses
  async getCourses(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    const url = `${API_BASE_URL}/courses/${queryString ? `?${queryString}` : ''}`;

    const response = await fetch(url);
    if (!response.ok) {
      throw new Error('Failed to fetch courses');
    }
    return response.json();
  },

  // Get single course
  async getCourse(id) {
    const response = await fetch(`${API_BASE_URL}/courses/${id}/`);
    if (!response.ok) {
      throw new Error('Course not found');
    }
    return response.json();
  },

  // Enroll in course
  async enrollInCourse(courseId, enrollmentData) {
    const response = await fetch(`${API_BASE_URL}/courses/${courseId}/enroll/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(enrollmentData)
    });

    const result = await response.json();

    return {
      success: response.ok,
      data: result,
      errors: response.ok ? null : result.details
    };
  }
};
```

### **Form Validation Helper**
```javascript
// validation.js
export const validateEnrollmentForm = (formData) => {
  const errors = {};

  // Required fields
  if (!formData.first_name?.trim()) {
    errors.first_name = ['First name is required.'];
  }

  if (!formData.last_name?.trim()) {
    errors.last_name = ['Last name is required.'];
  }

  if (!formData.email?.trim()) {
    errors.email = ['Email is required.'];
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
    errors.email = ['Please enter a valid email address.'];
  }

  if (!formData.phone?.trim()) {
    errors.phone = ['Phone number is required.'];
  }

  return {
    isValid: Object.keys(errors).length === 0,
    errors
  };
};
```

### **Local Storage Helper**
```javascript
// storage.js
export const enrollmentStorage = {
  // Save enrollment token
  saveEnrollmentToken(courseId, token) {
    localStorage.setItem(`enrollment_${courseId}`, token);
  },

  // Get enrollment token
  getEnrollmentToken(courseId) {
    return localStorage.getItem(`enrollment_${courseId}`);
  },

  // Check if user is enrolled in course
  isEnrolledInCourse(courseId) {
    return !!this.getEnrollmentToken(courseId);
  },

  // Remove enrollment token
  removeEnrollmentToken(courseId) {
    localStorage.removeItem(`enrollment_${courseId}`);
  },

  // Get all enrollments
  getAllEnrollments() {
    const enrollments = {};
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      if (key.startsWith('enrollment_')) {
        const courseId = key.replace('enrollment_', '');
        enrollments[courseId] = localStorage.getItem(key);
      }
    }
    return enrollments;
  }
};
```

---

## 📱 **6. Mobile Responsive Considerations**

### **Responsive CSS**
```css
/* Mobile Styles */
@media (max-width: 768px) {
  .course-list {
    padding: 10px;
  }

  .course-card {
    padding: 15px;
    margin-bottom: 15px;
  }

  .enrollment-form {
    padding: 20px;
    margin: 10px;
  }

  .form-row {
    flex-direction: column;
    gap: 0;
  }

  .form-actions {
    flex-direction: column;
  }

  .btn-cancel, .btn-submit {
    width: 100%;
    margin-bottom: 10px;
  }
}
```

---

## ⚠️ **7. Error Handling Best Practices**

### **Common Error Scenarios**
```javascript
const handleEnrollmentErrors = (errors) => {
  // Field validation errors
  if (errors.first_name) {
    // Show field-specific error
  }

  // Duplicate enrollment
  if (errors.email && errors.email[0].includes('already enrolled')) {
    // Show "already enrolled" message
  }

  // Course full
  if (errors.general && errors.general.includes('full')) {
    // Show course full message
  }

  // Network errors
  if (errors.network) {
    // Show network error message
  }
};
```

---

## 🚀 **8. Quick Start Checklist**

### **Frontend Implementation Steps**

1. **✅ Set up API calls**
   - Implement course fetching
   - Implement enrollment submission

2. **✅ Create components**
   - Course list component
   - Course card component
   - Enrollment form component

3. **✅ Add form validation**
   - Client-side validation
   - Server error handling

4. **✅ Style the interface**
   - Responsive design
   - Error states
   - Success states

5. **✅ Test enrollment flow**
   - Valid submissions
   - Invalid submissions
   - Error scenarios

### **Testing URLs**
- **Courses API**: `http://127.0.0.1:8000/api/training/courses/`
- **Course Detail**: `http://127.0.0.1:8000/api/training/courses/6/`
- **Enrollment**: `POST http://127.0.0.1:8000/api/training/courses/6/enroll/`

---

## 🎯 **Summary**

This guide provides everything needed to implement a complete course enrollment system:

- ✅ **No authentication required** - Guest enrollment
- ✅ **Required fields**: first_name, last_name, email, phone
- ✅ **Optional fields**: organization, job_title
- ✅ **Real-time validation** with clear error messages
- ✅ **Responsive design** for mobile and desktop
- ✅ **Complete React components** ready to use
- ✅ **Error handling** for all scenarios
- ✅ **Local storage** for enrollment tracking

Your frontend team can use this guide to build a professional, user-friendly course enrollment system! 🚀
```

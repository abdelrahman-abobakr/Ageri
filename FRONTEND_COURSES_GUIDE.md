# Complete Frontend Guide for Course Management

## 📋 **Table of Contents**

1. [API Overview](#api-overview)
2. [Authentication Setup](#authentication-setup)
3. [Basic Course Operations](#basic-course-operations)
4. [Advanced Features](#advanced-features)
5. [React Components Examples](#react-components-examples)
6. [Vanilla JavaScript Examples](#vanilla-javascript-examples)
7. [Error Handling](#error-handling)
8. [Best Practices](#best-practices)

---

## 🌐 **API Overview**

### **Base Configuration**
```javascript
const API_BASE_URL = 'http://localhost:8000/api';
const COURSES_ENDPOINT = `${API_BASE_URL}/training/courses/`;

// Default headers for all requests
const DEFAULT_HEADERS = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
};
```

### **Available Endpoints**
```javascript
const ENDPOINTS = {
    // Public endpoints (no auth required)
    LIST_COURSES: 'GET /api/training/courses/',
    GET_COURSE: 'GET /api/training/courses/{id}/',
    
    // Protected endpoints (auth required)
    CREATE_COURSE: 'POST /api/training/courses/',
    UPDATE_COURSE: 'PUT /api/training/courses/{id}/',
    PARTIAL_UPDATE: 'PATCH /api/training/courses/{id}/',
    DELETE_COURSE: 'DELETE /api/training/courses/{id}/',
    ENROLL_COURSE: 'POST /api/training/courses/{id}/enroll/',
    
    // Special endpoints
    FEATURED_COURSES: 'GET /api/training/courses/featured/',
    UPCOMING_COURSES: 'GET /api/training/courses/upcoming/'
};
```

---

## 🔐 **Authentication Setup**

### **Token Management**
```javascript
class AuthManager {
    constructor() {
        this.accessToken = localStorage.getItem('access_token');
        this.refreshToken = localStorage.getItem('refresh_token');
    }
    
    // Set tokens after login
    setTokens(accessToken, refreshToken) {
        this.accessToken = accessToken;
        this.refreshToken = refreshToken;
        localStorage.setItem('access_token', accessToken);
        localStorage.setItem('refresh_token', refreshToken);
    }
    
    // Get authorization headers
    getAuthHeaders() {
        return {
            ...DEFAULT_HEADERS,
            'Authorization': `Bearer ${this.accessToken}`
        };
    }
    
    // Check if user is authenticated
    isAuthenticated() {
        return !!this.accessToken;
    }
    
    // Refresh access token
    async refreshAccessToken() {
        try {
            const response = await fetch(`${API_BASE_URL}/auth/token/refresh/`, {
                method: 'POST',
                headers: DEFAULT_HEADERS,
                body: JSON.stringify({
                    refresh: this.refreshToken
                })
            });
            
            if (response.ok) {
                const data = await response.json();
                this.setTokens(data.access, data.refresh);
                return true;
            }
            return false;
        } catch (error) {
            console.error('Token refresh failed:', error);
            return false;
        }
    }
    
    // Logout
    logout() {
        this.accessToken = null;
        this.refreshToken = null;
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
    }
}

// Global auth manager instance
const authManager = new AuthManager();
```

### **Auto-Refresh Token Setup**
```javascript
// Auto-refresh token every 50 minutes (before 1-hour expiry)
setInterval(async () => {
    if (authManager.isAuthenticated()) {
        const refreshed = await authManager.refreshAccessToken();
        if (!refreshed) {
            // Redirect to login if refresh fails
            window.location.href = '/login';
        }
    }
}, 50 * 60 * 1000); // 50 minutes
```

---

## 📚 **Basic Course Operations**

### **1. Fetch All Courses**
```javascript
class CourseService {
    // Get all courses with optional filters
    static async getCourses(filters = {}) {
        try {
            const queryParams = new URLSearchParams();
            
            // Add filters to query params
            Object.entries(filters).forEach(([key, value]) => {
                if (value !== null && value !== undefined && value !== '') {
                    queryParams.append(key, value);
                }
            });
            
            const url = queryParams.toString() 
                ? `${COURSES_ENDPOINT}?${queryParams}`
                : COURSES_ENDPOINT;
            
            const response = await fetch(url, {
                method: 'GET',
                headers: DEFAULT_HEADERS
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Error fetching courses:', error);
            throw error;
        }
    }
    
    // Get single course by ID
    static async getCourse(courseId) {
        try {
            const response = await fetch(`${COURSES_ENDPOINT}${courseId}/`, {
                method: 'GET',
                headers: DEFAULT_HEADERS
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Error fetching course:', error);
            throw error;
        }
    }
    
    // Create new course (requires authentication)
    static async createCourse(courseData) {
        try {
            const response = await fetch(COURSES_ENDPOINT, {
                method: 'POST',
                headers: authManager.getAuthHeaders(),
                body: JSON.stringify(courseData)
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(JSON.stringify(errorData));
            }
            
            return await response.json();
        } catch (error) {
            console.error('Error creating course:', error);
            throw error;
        }
    }
    
    // Update course (requires authentication)
    static async updateCourse(courseId, courseData) {
        try {
            const response = await fetch(`${COURSES_ENDPOINT}${courseId}/`, {
                method: 'PUT',
                headers: authManager.getAuthHeaders(),
                body: JSON.stringify(courseData)
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(JSON.stringify(errorData));
            }
            
            return await response.json();
        } catch (error) {
            console.error('Error updating course:', error);
            throw error;
        }
    }
    
    // Partial update course (requires authentication)
    static async patchCourse(courseId, partialData) {
        try {
            const response = await fetch(`${COURSES_ENDPOINT}${courseId}/`, {
                method: 'PATCH',
                headers: authManager.getAuthHeaders(),
                body: JSON.stringify(partialData)
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(JSON.stringify(errorData));
            }
            
            return await response.json();
        } catch (error) {
            console.error('Error patching course:', error);
            throw error;
        }
    }
    
    // Delete course (requires authentication)
    static async deleteCourse(courseId) {
        try {
            const response = await fetch(`${COURSES_ENDPOINT}${courseId}/`, {
                method: 'DELETE',
                headers: authManager.getAuthHeaders()
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return true;
        } catch (error) {
            console.error('Error deleting course:', error);
            throw error;
        }
    }
    
    // Enroll in course (requires authentication)
    static async enrollInCourse(courseId) {
        try {
            const response = await fetch(`${COURSES_ENDPOINT}${courseId}/enroll/`, {
                method: 'POST',
                headers: authManager.getAuthHeaders()
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(JSON.stringify(errorData));
            }
            
            return await response.json();
        } catch (error) {
            console.error('Error enrolling in course:', error);
            throw error;
        }
    }
}
```

### **2. Usage Examples**
```javascript
// Example: Load all courses
async function loadCourses() {
    try {
        const data = await CourseService.getCourses();
        console.log(`Found ${data.count} courses`);
        console.log('Courses:', data.results);
        return data;
    } catch (error) {
        console.error('Failed to load courses:', error);
    }
}

// Example: Load course with filters
async function loadFilteredCourses() {
    const filters = {
        type: 'course',
        status: 'published',
        is_featured: true,
        search: 'python'
    };
    
    try {
        const data = await CourseService.getCourses(filters);
        return data;
    } catch (error) {
        console.error('Failed to load filtered courses:', error);
    }
}

// Example: Create new course
async function createNewCourse() {
    const courseData = {
        course_name: "Advanced JavaScript",
        course_code: "JS201",
        instructor: "John Doe",
        cost: "199.99",
        start_date: "2025-03-01",
        end_date: "2025-03-31",
        registration_deadline: "2025-02-25",
        training_hours: 40,
        description: "Advanced JavaScript concepts and frameworks",
        max_participants: 25,
        type: "course",
        status: "draft"
    };
    
    try {
        const newCourse = await CourseService.createCourse(courseData);
        console.log('Course created:', newCourse);
        return newCourse;
    } catch (error) {
        console.error('Failed to create course:', error);
    }
}
```

---

## 🔍 **Advanced Features**

### **1. Filtering and Search**
```javascript
class CourseFilters {
    constructor() {
        this.filters = {
            search: '',
            type: '',
            status: '',
            is_featured: null,
            is_public: null,
            department: '',
            ordering: '-start_date'
        };
    }
    
    // Set filter value
    setFilter(key, value) {
        this.filters[key] = value;
    }
    
    // Get current filters
    getFilters() {
        return { ...this.filters };
    }
    
    // Clear all filters
    clearFilters() {
        this.filters = {
            search: '',
            type: '',
            status: '',
            is_featured: null,
            is_public: null,
            department: '',
            ordering: '-start_date'
        };
    }
    
    // Apply filters and get courses
    async applyCourses() {
        return await CourseService.getCourses(this.filters);
    }
}

// Usage example
const courseFilters = new CourseFilters();

// Set filters
courseFilters.setFilter('search', 'python');
courseFilters.setFilter('type', 'course');
courseFilters.setFilter('is_featured', true);

// Apply filters
const filteredCourses = await courseFilters.applyCourses();
```

### **2. Pagination Handler**
```javascript
class PaginationHandler {
    constructor(initialData = null) {
        this.currentPage = 1;
        this.totalPages = 1;
        this.totalCount = 0;
        this.pageSize = 20;
        this.nextUrl = null;
        this.previousUrl = null;
        
        if (initialData) {
            this.updateFromResponse(initialData);
        }
    }
    
    // Update pagination info from API response
    updateFromResponse(data) {
        this.totalCount = data.count;
        this.nextUrl = data.next;
        this.previousUrl = data.previous;
        this.totalPages = Math.ceil(this.totalCount / this.pageSize);
    }
    
    // Get next page
    async getNextPage() {
        if (!this.nextUrl) return null;
        
        try {
            const response = await fetch(this.nextUrl, {
                headers: DEFAULT_HEADERS
            });
            const data = await response.json();
            this.updateFromResponse(data);
            this.currentPage++;
            return data;
        } catch (error) {
            console.error('Error fetching next page:', error);
            throw error;
        }
    }
    
    // Get previous page
    async getPreviousPage() {
        if (!this.previousUrl) return null;
        
        try {
            const response = await fetch(this.previousUrl, {
                headers: DEFAULT_HEADERS
            });
            const data = await response.json();
            this.updateFromResponse(data);
            this.currentPage--;
            return data;
        } catch (error) {
            console.error('Error fetching previous page:', error);
            throw error;
        }
    }
    
    // Go to specific page
    async goToPage(pageNumber, filters = {}) {
        const params = new URLSearchParams({
            ...filters,
            page: pageNumber
        });
        
        try {
            const response = await fetch(`${COURSES_ENDPOINT}?${params}`, {
                headers: DEFAULT_HEADERS
            });
            const data = await response.json();
            this.updateFromResponse(data);
            this.currentPage = pageNumber;
            return data;
        } catch (error) {
            console.error('Error fetching page:', error);
            throw error;
        }
    }
    
    // Check if has next page
    hasNext() {
        return !!this.nextUrl;
    }
    
    // Check if has previous page
    hasPrevious() {
        return !!this.previousUrl;
    }
    
    // Get pagination info
    getInfo() {
        return {
            currentPage: this.currentPage,
            totalPages: this.totalPages,
            totalCount: this.totalCount,
            hasNext: this.hasNext(),
            hasPrevious: this.hasPrevious()
        };
    }
}
```

### **3. Course Validation**
```javascript
class CourseValidator {
    static validateCourseData(courseData) {
        const errors = {};
        
        // Required fields validation
        if (!courseData.course_name?.trim()) {
            errors.course_name = 'Course name is required';
        }
        
        if (!courseData.course_code?.trim()) {
            errors.course_code = 'Course code is required';
        }
        
        if (!courseData.instructor?.trim()) {
            errors.instructor = 'Instructor is required';
        }
        
        if (!courseData.start_date) {
            errors.start_date = 'Start date is required';
        }
        
        if (!courseData.end_date) {
            errors.end_date = 'End date is required';
        }
        
        if (!courseData.registration_deadline) {
            errors.registration_deadline = 'Registration deadline is required';
        }
        
        // Date validation
        if (courseData.start_date && courseData.end_date) {
            const startDate = new Date(courseData.start_date);
            const endDate = new Date(courseData.end_date);
            
            if (endDate <= startDate) {
                errors.end_date = 'End date must be after start date';
            }
        }
        
        if (courseData.registration_deadline && courseData.start_date) {
            const regDeadline = new Date(courseData.registration_deadline);
            const startDate = new Date(courseData.start_date);
            
            if (regDeadline >= startDate) {
                errors.registration_deadline = 'Registration deadline must be before start date';
            }
        }
        
        // Numeric validation
        if (courseData.cost && isNaN(parseFloat(courseData.cost))) {
            errors.cost = 'Cost must be a valid number';
        }
        
        if (courseData.training_hours && (!Number.isInteger(Number(courseData.training_hours)) || Number(courseData.training_hours) <= 0)) {
            errors.training_hours = 'Training hours must be a positive integer';
        }
        
        if (courseData.max_participants && (!Number.isInteger(Number(courseData.max_participants)) || Number(courseData.max_participants) <= 0)) {
            errors.max_participants = 'Max participants must be a positive integer';
        }
        
        return {
            isValid: Object.keys(errors).length === 0,
            errors
        };
    }
    
    static formatValidationErrors(errors) {
        return Object.entries(errors).map(([field, message]) => ({
            field,
            message
        }));
    }
}
```

---

## ⚛️ **React Components Examples**

### **1. Course List Component**
```jsx
import React, { useState, useEffect } from 'react';
import { CourseService } from '../services/CourseService';

const CourseList = () => {
    const [courses, setCourses] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [filters, setFilters] = useState({
        search: '',
        type: '',
        status: 'published'
    });
    const [pagination, setPagination] = useState({
        count: 0,
        next: null,
        previous: null
    });

    // Load courses
    const loadCourses = async (newFilters = filters) => {
        try {
            setLoading(true);
            setError(null);
            const data = await CourseService.getCourses(newFilters);
            setCourses(data.results);
            setPagination({
                count: data.count,
                next: data.next,
                previous: data.previous
            });
        } catch (err) {
            setError('Failed to load courses');
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    // Load courses on component mount
    useEffect(() => {
        loadCourses();
    }, []);

    // Handle filter change
    const handleFilterChange = (key, value) => {
        const newFilters = { ...filters, [key]: value };
        setFilters(newFilters);
        loadCourses(newFilters);
    };

    // Handle search
    const handleSearch = (searchTerm) => {
        handleFilterChange('search', searchTerm);
    };

    if (loading) return <div className="loading">Loading courses...</div>;
    if (error) return <div className="error">{error}</div>;

    return (
        <div className="course-list">
            <div className="course-list-header">
                <h2>Available Courses ({pagination.count})</h2>

                {/* Search Bar */}
                <div className="search-bar">
                    <input
                        type="text"
                        placeholder="Search courses..."
                        value={filters.search}
                        onChange={(e) => handleSearch(e.target.value)}
                        className="search-input"
                    />
                </div>

                {/* Filters */}
                <div className="filters">
                    <select
                        value={filters.type}
                        onChange={(e) => handleFilterChange('type', e.target.value)}
                        className="filter-select"
                    >
                        <option value="">All Types</option>
                        <option value="course">Course</option>
                        <option value="workshop">Workshop</option>
                        <option value="seminar">Seminar</option>
                    </select>
                </div>
            </div>

            {/* Course Grid */}
            <div className="course-grid">
                {courses.map(course => (
                    <CourseCard key={course.id} course={course} />
                ))}
            </div>

            {/* Pagination */}
            {(pagination.next || pagination.previous) && (
                <div className="pagination">
                    <button
                        disabled={!pagination.previous}
                        onClick={() => loadPreviousPage()}
                        className="pagination-btn"
                    >
                        Previous
                    </button>
                    <button
                        disabled={!pagination.next}
                        onClick={() => loadNextPage()}
                        className="pagination-btn"
                    >
                        Next
                    </button>
                </div>
            )}
        </div>
    );
};

export default CourseList;
```

### **2. Course Card Component**
```jsx
import React from 'react';
import { formatDate, formatCurrency } from '../utils/formatters';

const CourseCard = ({ course, onEnroll, onEdit, onDelete, showActions = true }) => {
    const handleEnroll = async () => {
        try {
            await CourseService.enrollInCourse(course.id);
            alert('Successfully enrolled in course!');
            // Refresh course data or update UI
        } catch (error) {
            alert('Failed to enroll in course');
            console.error(error);
        }
    };

    return (
        <div className={`course-card ${course.is_featured ? 'featured' : ''}`}>
            {/* Course Image */}
            {course.featured_image && (
                <div className="course-image">
                    <img src={course.featured_image} alt={course.course_name} />
                </div>
            )}

            {/* Course Content */}
            <div className="course-content">
                <div className="course-header">
                    <h3 className="course-title">{course.course_name}</h3>
                    <span className="course-code">{course.course_code}</span>
                </div>

                <div className="course-meta">
                    <p className="instructor">👨‍🏫 {course.instructor}</p>
                    <p className="duration">⏱️ {course.training_hours} hours</p>
                    <p className="dates">
                        📅 {formatDate(course.start_date)} - {formatDate(course.end_date)}
                    </p>
                </div>

                <div className="course-description">
                    <p>{course.description}</p>
                </div>

                <div className="course-stats">
                    <div className="enrollment">
                        <span>👥 {course.current_enrollment}/{course.max_participants}</span>
                        <div className="progress-bar">
                            <div
                                className="progress-fill"
                                style={{ width: `${course.enrollment_percentage}%` }}
                            ></div>
                        </div>
                    </div>
                </div>

                <div className="course-footer">
                    <div className="course-price">
                        {course.is_free ? (
                            <span className="free-badge">FREE</span>
                        ) : (
                            <span className="price">{formatCurrency(course.cost)}</span>
                        )}
                    </div>

                    <div className="course-status">
                        <span className={`status-badge ${course.status}`}>
                            {course.status.toUpperCase()}
                        </span>
                        {course.is_featured && (
                            <span className="featured-badge">⭐ FEATURED</span>
                        )}
                    </div>
                </div>

                {/* Action Buttons */}
                {showActions && (
                    <div className="course-actions">
                        {course.can_register && (
                            <button
                                onClick={handleEnroll}
                                className="btn btn-primary"
                                disabled={course.is_full || !course.is_registration_open}
                            >
                                {course.is_full ? 'Full' : 'Enroll Now'}
                            </button>
                        )}

                        {!course.is_registration_open && (
                            <span className="registration-closed">
                                Registration Closed
                            </span>
                        )}

                        <button
                            onClick={() => window.open(`/courses/${course.id}`, '_blank')}
                            className="btn btn-secondary"
                        >
                            View Details
                        </button>
                    </div>
                )}
            </div>
        </div>
    );
};

export default CourseCard;
```

### **3. Course Form Component**
```jsx
import React, { useState, useEffect } from 'react';
import { CourseValidator } from '../utils/CourseValidator';
import { CourseService } from '../services/CourseService';

const CourseForm = ({ courseId = null, onSuccess, onCancel }) => {
    const [formData, setFormData] = useState({
        course_name: '',
        course_code: '',
        instructor: '',
        cost: '0.00',
        start_date: '',
        end_date: '',
        registration_deadline: '',
        training_hours: '',
        description: '',
        max_participants: '30',
        type: 'course',
        status: 'draft',
        is_featured: false,
        is_public: true,
        prerequisites: '',
        materials_provided: '',
        tags: ''
    });

    const [errors, setErrors] = useState({});
    const [loading, setLoading] = useState(false);
    const [isEditing, setIsEditing] = useState(!!courseId);

    // Load course data for editing
    useEffect(() => {
        if (courseId) {
            loadCourseData();
        }
    }, [courseId]);

    const loadCourseData = async () => {
        try {
            setLoading(true);
            const course = await CourseService.getCourse(courseId);
            setFormData(course);
        } catch (error) {
            console.error('Failed to load course:', error);
        } finally {
            setLoading(false);
        }
    };

    // Handle input change
    const handleChange = (e) => {
        const { name, value, type, checked } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: type === 'checkbox' ? checked : value
        }));

        // Clear error for this field
        if (errors[name]) {
            setErrors(prev => ({
                ...prev,
                [name]: null
            }));
        }
    };

    // Handle form submission
    const handleSubmit = async (e) => {
        e.preventDefault();

        // Validate form data
        const validation = CourseValidator.validateCourseData(formData);
        if (!validation.isValid) {
            setErrors(validation.errors);
            return;
        }

        try {
            setLoading(true);
            setErrors({});

            let result;
            if (isEditing) {
                result = await CourseService.updateCourse(courseId, formData);
            } else {
                result = await CourseService.createCourse(formData);
            }

            onSuccess && onSuccess(result);
        } catch (error) {
            try {
                const errorData = JSON.parse(error.message);
                setErrors(errorData);
            } catch {
                setErrors({ general: 'An error occurred while saving the course' });
            }
        } finally {
            setLoading(false);
        }
    };

    if (loading && isEditing) {
        return <div className="loading">Loading course data...</div>;
    }

    return (
        <form onSubmit={handleSubmit} className="course-form">
            <div className="form-header">
                <h2>{isEditing ? 'Edit Course' : 'Create New Course'}</h2>
            </div>

            {errors.general && (
                <div className="error-message">{errors.general}</div>
            )}

            <div className="form-grid">
                {/* Basic Information */}
                <div className="form-section">
                    <h3>Basic Information</h3>

                    <div className="form-group">
                        <label htmlFor="course_name">Course Name *</label>
                        <input
                            type="text"
                            id="course_name"
                            name="course_name"
                            value={formData.course_name}
                            onChange={handleChange}
                            className={errors.course_name ? 'error' : ''}
                            required
                        />
                        {errors.course_name && (
                            <span className="error-text">{errors.course_name}</span>
                        )}
                    </div>

                    <div className="form-group">
                        <label htmlFor="course_code">Course Code *</label>
                        <input
                            type="text"
                            id="course_code"
                            name="course_code"
                            value={formData.course_code}
                            onChange={handleChange}
                            className={errors.course_code ? 'error' : ''}
                            required
                        />
                        {errors.course_code && (
                            <span className="error-text">{errors.course_code}</span>
                        )}
                    </div>

                    <div className="form-group">
                        <label htmlFor="instructor">Instructor *</label>
                        <input
                            type="text"
                            id="instructor"
                            name="instructor"
                            value={formData.instructor}
                            onChange={handleChange}
                            className={errors.instructor ? 'error' : ''}
                            required
                        />
                        {errors.instructor && (
                            <span className="error-text">{errors.instructor}</span>
                        )}
                    </div>

                    <div className="form-group">
                        <label htmlFor="type">Course Type</label>
                        <select
                            id="type"
                            name="type"
                            value={formData.type}
                            onChange={handleChange}
                        >
                            <option value="course">Course</option>
                            <option value="workshop">Workshop</option>
                            <option value="seminar">Seminar</option>
                            <option value="summer_training">Summer Training</option>
                        </select>
                    </div>
                </div>

                {/* Dates and Duration */}
                <div className="form-section">
                    <h3>Schedule</h3>

                    <div className="form-group">
                        <label htmlFor="start_date">Start Date *</label>
                        <input
                            type="date"
                            id="start_date"
                            name="start_date"
                            value={formData.start_date}
                            onChange={handleChange}
                            className={errors.start_date ? 'error' : ''}
                            required
                        />
                        {errors.start_date && (
                            <span className="error-text">{errors.start_date}</span>
                        )}
                    </div>

                    <div className="form-group">
                        <label htmlFor="end_date">End Date *</label>
                        <input
                            type="date"
                            id="end_date"
                            name="end_date"
                            value={formData.end_date}
                            onChange={handleChange}
                            className={errors.end_date ? 'error' : ''}
                            required
                        />
                        {errors.end_date && (
                            <span className="error-text">{errors.end_date}</span>
                        )}
                    </div>

                    <div className="form-group">
                        <label htmlFor="registration_deadline">Registration Deadline *</label>
                        <input
                            type="date"
                            id="registration_deadline"
                            name="registration_deadline"
                            value={formData.registration_deadline}
                            onChange={handleChange}
                            className={errors.registration_deadline ? 'error' : ''}
                            required
                        />
                        {errors.registration_deadline && (
                            <span className="error-text">{errors.registration_deadline}</span>
                        )}
                    </div>

                    <div className="form-group">
                        <label htmlFor="training_hours">Training Hours *</label>
                        <input
                            type="number"
                            id="training_hours"
                            name="training_hours"
                            value={formData.training_hours}
                            onChange={handleChange}
                            className={errors.training_hours ? 'error' : ''}
                            min="1"
                            required
                        />
                        {errors.training_hours && (
                            <span className="error-text">{errors.training_hours}</span>
                        )}
                    </div>
                </div>

                {/* Pricing and Capacity */}
                <div className="form-section">
                    <h3>Pricing & Capacity</h3>

                    <div className="form-group">
                        <label htmlFor="cost">Cost</label>
                        <input
                            type="number"
                            id="cost"
                            name="cost"
                            value={formData.cost}
                            onChange={handleChange}
                            className={errors.cost ? 'error' : ''}
                            min="0"
                            step="0.01"
                        />
                        {errors.cost && (
                            <span className="error-text">{errors.cost}</span>
                        )}
                    </div>

                    <div className="form-group">
                        <label htmlFor="max_participants">Max Participants</label>
                        <input
                            type="number"
                            id="max_participants"
                            name="max_participants"
                            value={formData.max_participants}
                            onChange={handleChange}
                            className={errors.max_participants ? 'error' : ''}
                            min="1"
                        />
                        {errors.max_participants && (
                            <span className="error-text">{errors.max_participants}</span>
                        )}
                    </div>
                </div>

                {/* Description and Details */}
                <div className="form-section full-width">
                    <h3>Course Details</h3>

                    <div className="form-group">
                        <label htmlFor="description">Description</label>
                        <textarea
                            id="description"
                            name="description"
                            value={formData.description}
                            onChange={handleChange}
                            rows="4"
                            placeholder="Describe the course content, objectives, and what students will learn..."
                        />
                    </div>

                    <div className="form-group">
                        <label htmlFor="prerequisites">Prerequisites</label>
                        <textarea
                            id="prerequisites"
                            name="prerequisites"
                            value={formData.prerequisites}
                            onChange={handleChange}
                            rows="3"
                            placeholder="List any prerequisites or requirements for this course..."
                        />
                    </div>

                    <div className="form-group">
                        <label htmlFor="materials_provided">Materials Provided</label>
                        <textarea
                            id="materials_provided"
                            name="materials_provided"
                            value={formData.materials_provided}
                            onChange={handleChange}
                            rows="3"
                            placeholder="List materials, resources, or tools provided to students..."
                        />
                    </div>

                    <div className="form-group">
                        <label htmlFor="tags">Tags</label>
                        <input
                            type="text"
                            id="tags"
                            name="tags"
                            value={formData.tags}
                            onChange={handleChange}
                            placeholder="Comma-separated tags (e.g., programming, web development, javascript)"
                        />
                    </div>
                </div>

                {/* Settings */}
                <div className="form-section">
                    <h3>Settings</h3>

                    <div className="form-group">
                        <label htmlFor="status">Status</label>
                        <select
                            id="status"
                            name="status"
                            value={formData.status}
                            onChange={handleChange}
                        >
                            <option value="draft">Draft</option>
                            <option value="published">Published</option>
                            <option value="inactive">Inactive</option>
                        </select>
                    </div>

                    <div className="form-group checkbox-group">
                        <label>
                            <input
                                type="checkbox"
                                name="is_featured"
                                checked={formData.is_featured}
                                onChange={handleChange}
                            />
                            Featured Course
                        </label>
                    </div>

                    <div className="form-group checkbox-group">
                        <label>
                            <input
                                type="checkbox"
                                name="is_public"
                                checked={formData.is_public}
                                onChange={handleChange}
                            />
                            Public Course
                        </label>
                    </div>
                </div>
            </div>

            {/* Form Actions */}
            <div className="form-actions">
                <button
                    type="button"
                    onClick={onCancel}
                    className="btn btn-secondary"
                    disabled={loading}
                >
                    Cancel
                </button>
                <button
                    type="submit"
                    className="btn btn-primary"
                    disabled={loading}
                >
                    {loading ? 'Saving...' : (isEditing ? 'Update Course' : 'Create Course')}
                </button>
            </div>
        </form>
    );
};

export default CourseForm;

---

## 🟨 **Vanilla JavaScript Examples**

### **1. Course List with Vanilla JS**
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Course Management</title>
    <style>
        .course-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; }
        .course-card { border: 1px solid #ddd; border-radius: 8px; padding: 16px; }
        .course-card.featured { border-color: #007bff; background: #f8f9ff; }
        .loading { text-align: center; padding: 20px; }
        .error { color: red; padding: 10px; background: #ffe6e6; border-radius: 4px; }
        .filters { margin: 20px 0; display: flex; gap: 10px; align-items: center; }
        .search-input, .filter-select { padding: 8px; border: 1px solid #ddd; border-radius: 4px; }
        .btn { padding: 8px 16px; border: none; border-radius: 4px; cursor: pointer; }
        .btn-primary { background: #007bff; color: white; }
        .btn-secondary { background: #6c757d; color: white; }
        .pagination { text-align: center; margin: 20px 0; }
        .pagination-btn { margin: 0 5px; }
    </style>
</head>
<body>
    <div id="app">
        <h1>Course Management System</h1>

        <!-- Filters -->
        <div class="filters">
            <input type="text" id="searchInput" placeholder="Search courses..." class="search-input">
            <select id="typeFilter" class="filter-select">
                <option value="">All Types</option>
                <option value="course">Course</option>
                <option value="workshop">Workshop</option>
                <option value="seminar">Seminar</option>
            </select>
            <select id="statusFilter" class="filter-select">
                <option value="">All Status</option>
                <option value="published">Published</option>
                <option value="draft">Draft</option>
            </select>
            <button id="clearFilters" class="btn btn-secondary">Clear Filters</button>
        </div>

        <!-- Loading/Error States -->
        <div id="loading" class="loading" style="display: none;">Loading courses...</div>
        <div id="error" class="error" style="display: none;"></div>

        <!-- Course Count -->
        <div id="courseCount" style="margin: 10px 0;"></div>

        <!-- Course Grid -->
        <div id="courseGrid" class="course-grid"></div>

        <!-- Pagination -->
        <div id="pagination" class="pagination" style="display: none;">
            <button id="prevBtn" class="btn btn-secondary pagination-btn">Previous</button>
            <span id="pageInfo"></span>
            <button id="nextBtn" class="btn btn-secondary pagination-btn">Next</button>
        </div>
    </div>

    <script>
        // Course Management Class
        class CourseManager {
            constructor() {
                this.courses = [];
                this.filters = {
                    search: '',
                    type: '',
                    status: 'published'
                };
                this.pagination = {
                    count: 0,
                    next: null,
                    previous: null,
                    currentPage: 1
                };
                this.init();
            }

            init() {
                this.bindEvents();
                this.loadCourses();
            }

            bindEvents() {
                // Search input
                document.getElementById('searchInput').addEventListener('input', (e) => {
                    this.filters.search = e.target.value;
                    this.debounceSearch();
                });

                // Filter selects
                document.getElementById('typeFilter').addEventListener('change', (e) => {
                    this.filters.type = e.target.value;
                    this.loadCourses();
                });

                document.getElementById('statusFilter').addEventListener('change', (e) => {
                    this.filters.status = e.target.value;
                    this.loadCourses();
                });

                // Clear filters
                document.getElementById('clearFilters').addEventListener('click', () => {
                    this.clearFilters();
                });

                // Pagination
                document.getElementById('prevBtn').addEventListener('click', () => {
                    this.loadPreviousPage();
                });

                document.getElementById('nextBtn').addEventListener('click', () => {
                    this.loadNextPage();
                });
            }

            // Debounced search
            debounceSearch() {
                clearTimeout(this.searchTimeout);
                this.searchTimeout = setTimeout(() => {
                    this.loadCourses();
                }, 300);
            }

            async loadCourses() {
                try {
                    this.showLoading(true);
                    this.hideError();

                    const queryParams = new URLSearchParams();
                    Object.entries(this.filters).forEach(([key, value]) => {
                        if (value) queryParams.append(key, value);
                    });

                    const url = `http://localhost:8000/api/training/courses/?${queryParams}`;
                    const response = await fetch(url, {
                        headers: {
                            'Accept': 'application/json',
                            'Content-Type': 'application/json'
                        }
                    });

                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }

                    const data = await response.json();
                    this.courses = data.results;
                    this.pagination = {
                        count: data.count,
                        next: data.next,
                        previous: data.previous,
                        currentPage: 1
                    };

                    this.renderCourses();
                    this.updatePagination();
                    this.updateCourseCount();

                } catch (error) {
                    this.showError('Failed to load courses: ' + error.message);
                } finally {
                    this.showLoading(false);
                }
            }

            async loadNextPage() {
                if (!this.pagination.next) return;
                await this.loadPage(this.pagination.next);
                this.pagination.currentPage++;
            }

            async loadPreviousPage() {
                if (!this.pagination.previous) return;
                await this.loadPage(this.pagination.previous);
                this.pagination.currentPage--;
            }

            async loadPage(url) {
                try {
                    this.showLoading(true);
                    const response = await fetch(url, {
                        headers: {
                            'Accept': 'application/json',
                            'Content-Type': 'application/json'
                        }
                    });

                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }

                    const data = await response.json();
                    this.courses = data.results;
                    this.pagination.next = data.next;
                    this.pagination.previous = data.previous;

                    this.renderCourses();
                    this.updatePagination();

                } catch (error) {
                    this.showError('Failed to load page: ' + error.message);
                } finally {
                    this.showLoading(false);
                }
            }

            renderCourses() {
                const grid = document.getElementById('courseGrid');

                if (this.courses.length === 0) {
                    grid.innerHTML = '<p>No courses found matching your criteria.</p>';
                    return;
                }

                grid.innerHTML = this.courses.map(course => this.createCourseCard(course)).join('');
            }

            createCourseCard(course) {
                const formatDate = (dateString) => {
                    return new Date(dateString).toLocaleDateString();
                };

                const formatCurrency = (amount) => {
                    return new Intl.NumberFormat('en-US', {
                        style: 'currency',
                        currency: 'USD'
                    }).format(amount);
                };

                return `
                    <div class="course-card ${course.is_featured ? 'featured' : ''}">
                        <div class="course-header">
                            <h3>${course.course_name}</h3>
                            <span class="course-code">${course.course_code}</span>
                        </div>

                        <div class="course-meta">
                            <p><strong>Instructor:</strong> ${course.instructor}</p>
                            <p><strong>Duration:</strong> ${course.training_hours} hours</p>
                            <p><strong>Dates:</strong> ${formatDate(course.start_date)} - ${formatDate(course.end_date)}</p>
                            <p><strong>Registration Deadline:</strong> ${formatDate(course.registration_deadline)}</p>
                        </div>

                        <div class="course-description">
                            <p>${course.description || 'No description available.'}</p>
                        </div>

                        <div class="course-stats">
                            <p><strong>Enrollment:</strong> ${course.current_enrollment}/${course.max_participants} (${course.enrollment_percentage.toFixed(1)}%)</p>
                            <div class="progress-bar" style="background: #f0f0f0; height: 8px; border-radius: 4px; overflow: hidden;">
                                <div style="background: #007bff; height: 100%; width: ${course.enrollment_percentage}%; transition: width 0.3s;"></div>
                            </div>
                        </div>

                        <div class="course-footer" style="margin-top: 15px; display: flex; justify-content: space-between; align-items: center;">
                            <div class="course-price">
                                ${course.is_free ?
                                    '<span style="background: #28a745; color: white; padding: 4px 8px; border-radius: 4px; font-size: 12px;">FREE</span>' :
                                    `<span style="font-weight: bold; color: #007bff;">${formatCurrency(course.cost)}</span>`
                                }
                            </div>

                            <div class="course-actions">
                                ${course.can_register ?
                                    `<button class="btn btn-primary" onclick="courseManager.enrollInCourse(${course.id})" ${course.is_full ? 'disabled' : ''}>
                                        ${course.is_full ? 'Full' : 'Enroll'}
                                    </button>` :
                                    '<span style="color: #dc3545; font-size: 12px;">Registration Closed</span>'
                                }
                            </div>
                        </div>

                        ${course.is_featured ? '<div style="position: absolute; top: 10px; right: 10px; background: #ffc107; color: #000; padding: 2px 6px; border-radius: 4px; font-size: 10px;">⭐ FEATURED</div>' : ''}
                    </div>
                `;
            }

            async enrollInCourse(courseId) {
                // Check if user is authenticated
                const accessToken = localStorage.getItem('access_token');
                if (!accessToken) {
                    alert('Please login to enroll in courses');
                    return;
                }

                try {
                    const response = await fetch(`http://localhost:8000/api/training/courses/${courseId}/enroll/`, {
                        method: 'POST',
                        headers: {
                            'Authorization': `Bearer ${accessToken}`,
                            'Content-Type': 'application/json',
                            'Accept': 'application/json'
                        }
                    });

                    if (response.ok) {
                        alert('Successfully enrolled in course!');
                        this.loadCourses(); // Refresh the course list
                    } else {
                        const errorData = await response.json();
                        alert('Failed to enroll: ' + (errorData.error || 'Unknown error'));
                    }
                } catch (error) {
                    alert('Failed to enroll: ' + error.message);
                }
            }

            clearFilters() {
                this.filters = {
                    search: '',
                    type: '',
                    status: 'published'
                };

                document.getElementById('searchInput').value = '';
                document.getElementById('typeFilter').value = '';
                document.getElementById('statusFilter').value = 'published';

                this.loadCourses();
            }

            updateCourseCount() {
                const countElement = document.getElementById('courseCount');
                countElement.textContent = `Found ${this.pagination.count} courses`;
            }

            updatePagination() {
                const paginationElement = document.getElementById('pagination');
                const prevBtn = document.getElementById('prevBtn');
                const nextBtn = document.getElementById('nextBtn');
                const pageInfo = document.getElementById('pageInfo');

                if (this.pagination.next || this.pagination.previous) {
                    paginationElement.style.display = 'block';
                    prevBtn.disabled = !this.pagination.previous;
                    nextBtn.disabled = !this.pagination.next;
                    pageInfo.textContent = `Page ${this.pagination.currentPage}`;
                } else {
                    paginationElement.style.display = 'none';
                }
            }

            showLoading(show) {
                document.getElementById('loading').style.display = show ? 'block' : 'none';
            }

            showError(message) {
                const errorElement = document.getElementById('error');
                errorElement.textContent = message;
                errorElement.style.display = 'block';
            }

            hideError() {
                document.getElementById('error').style.display = 'none';
            }
        }

        // Initialize the course manager when the page loads
        let courseManager;
        document.addEventListener('DOMContentLoaded', () => {
            courseManager = new CourseManager();
        });
    </script>
</body>
</html>

---

## ⚠️ **Error Handling**

### **1. API Error Handler**
```javascript
class APIErrorHandler {
    static handleResponse(response, data) {
        if (!response.ok) {
            switch (response.status) {
                case 400:
                    return this.handleValidationError(data);
                case 401:
                    return this.handleAuthError();
                case 403:
                    return this.handlePermissionError();
                case 404:
                    return this.handleNotFoundError();
                case 500:
                    return this.handleServerError();
                default:
                    return this.handleGenericError(response.status);
            }
        }
        return null;
    }

    static handleValidationError(data) {
        const errors = [];
        if (typeof data === 'object') {
            Object.entries(data).forEach(([field, messages]) => {
                if (Array.isArray(messages)) {
                    messages.forEach(message => {
                        errors.push({ field, message });
                    });
                } else {
                    errors.push({ field, message: messages });
                }
            });
        }
        return {
            type: 'validation',
            message: 'Please check the form for errors',
            errors
        };
    }

    static handleAuthError() {
        // Clear tokens and redirect to login
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');

        return {
            type: 'auth',
            message: 'Authentication required. Please login.',
            action: 'redirect_login'
        };
    }

    static handlePermissionError() {
        return {
            type: 'permission',
            message: 'You do not have permission to perform this action.'
        };
    }

    static handleNotFoundError() {
        return {
            type: 'not_found',
            message: 'The requested resource was not found.'
        };
    }

    static handleServerError() {
        return {
            type: 'server',
            message: 'Server error occurred. Please try again later.'
        };
    }

    static handleGenericError(status) {
        return {
            type: 'generic',
            message: `An error occurred (${status}). Please try again.`
        };
    }
}
```

### **2. Enhanced Course Service with Error Handling**
```javascript
class EnhancedCourseService {
    static async makeRequest(url, options = {}) {
        try {
            const response = await fetch(url, {
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                    ...options.headers
                },
                ...options
            });

            let data = null;
            const contentType = response.headers.get('content-type');

            if (contentType && contentType.includes('application/json')) {
                data = await response.json();
            }

            if (!response.ok) {
                const error = APIErrorHandler.handleResponse(response, data);
                throw new APIError(error.message, error.type, error.errors, response.status);
            }

            return data;
        } catch (error) {
            if (error instanceof APIError) {
                throw error;
            }

            // Network or other errors
            throw new APIError(
                'Network error occurred. Please check your connection.',
                'network',
                [],
                0
            );
        }
    }

    static async getCourses(filters = {}) {
        const queryParams = new URLSearchParams();
        Object.entries(filters).forEach(([key, value]) => {
            if (value !== null && value !== undefined && value !== '') {
                queryParams.append(key, value);
            }
        });

        const url = queryParams.toString()
            ? `${COURSES_ENDPOINT}?${queryParams}`
            : COURSES_ENDPOINT;

        return await this.makeRequest(url);
    }

    static async createCourse(courseData) {
        return await this.makeRequest(COURSES_ENDPOINT, {
            method: 'POST',
            headers: authManager.getAuthHeaders(),
            body: JSON.stringify(courseData)
        });
    }

    // Add other methods with similar error handling...
}

// Custom API Error class
class APIError extends Error {
    constructor(message, type, errors = [], status = 0) {
        super(message);
        this.name = 'APIError';
        this.type = type;
        this.errors = errors;
        this.status = status;
    }
}
```

### **3. React Error Boundary**
```jsx
import React from 'react';

class CourseErrorBoundary extends React.Component {
    constructor(props) {
        super(props);
        this.state = { hasError: false, error: null };
    }

    static getDerivedStateFromError(error) {
        return { hasError: true, error };
    }

    componentDidCatch(error, errorInfo) {
        console.error('Course component error:', error, errorInfo);

        // Log to error reporting service
        if (window.errorReporting) {
            window.errorReporting.captureException(error, {
                extra: errorInfo,
                tags: { component: 'course' }
            });
        }
    }

    render() {
        if (this.state.hasError) {
            return (
                <div className="error-boundary">
                    <h2>Something went wrong</h2>
                    <p>We're sorry, but something went wrong while loading the courses.</p>
                    <button
                        onClick={() => this.setState({ hasError: false, error: null })}
                        className="btn btn-primary"
                    >
                        Try Again
                    </button>
                </div>
            );
        }

        return this.props.children;
    }
}

// Usage
const App = () => (
    <CourseErrorBoundary>
        <CourseList />
    </CourseErrorBoundary>
);
```

---

## 🎯 **Best Practices**

### **1. Performance Optimization**

#### **Debounced Search**
```javascript
class SearchManager {
    constructor(callback, delay = 300) {
        this.callback = callback;
        this.delay = delay;
        this.timeoutId = null;
    }

    search(query) {
        clearTimeout(this.timeoutId);
        this.timeoutId = setTimeout(() => {
            this.callback(query);
        }, this.delay);
    }

    cancel() {
        clearTimeout(this.timeoutId);
    }
}

// Usage
const searchManager = new SearchManager((query) => {
    CourseService.getCourses({ search: query });
}, 300);

// In your component
const handleSearchChange = (e) => {
    searchManager.search(e.target.value);
};
```

#### **Caching Strategy**
```javascript
class CourseCache {
    constructor(ttl = 5 * 60 * 1000) { // 5 minutes TTL
        this.cache = new Map();
        this.ttl = ttl;
    }

    set(key, data) {
        this.cache.set(key, {
            data,
            timestamp: Date.now()
        });
    }

    get(key) {
        const item = this.cache.get(key);
        if (!item) return null;

        if (Date.now() - item.timestamp > this.ttl) {
            this.cache.delete(key);
            return null;
        }

        return item.data;
    }

    clear() {
        this.cache.clear();
    }

    // Generate cache key from filters
    static generateKey(filters) {
        return JSON.stringify(filters);
    }
}

// Enhanced Course Service with caching
class CachedCourseService extends CourseService {
    static cache = new CourseCache();

    static async getCourses(filters = {}) {
        const cacheKey = CourseCache.generateKey(filters);
        const cached = this.cache.get(cacheKey);

        if (cached) {
            return cached;
        }

        const data = await super.getCourses(filters);
        this.cache.set(cacheKey, data);
        return data;
    }

    static clearCache() {
        this.cache.clear();
    }
}
```

### **2. State Management**

#### **Simple State Manager**
```javascript
class CourseStateManager {
    constructor() {
        this.state = {
            courses: [],
            loading: false,
            error: null,
            filters: {
                search: '',
                type: '',
                status: 'published'
            },
            pagination: {
                count: 0,
                next: null,
                previous: null
            }
        };
        this.listeners = [];
    }

    // Subscribe to state changes
    subscribe(listener) {
        this.listeners.push(listener);
        return () => {
            this.listeners = this.listeners.filter(l => l !== listener);
        };
    }

    // Update state and notify listeners
    setState(updates) {
        this.state = { ...this.state, ...updates };
        this.listeners.forEach(listener => listener(this.state));
    }

    // Get current state
    getState() {
        return { ...this.state };
    }

    // Actions
    async loadCourses() {
        this.setState({ loading: true, error: null });

        try {
            const data = await CourseService.getCourses(this.state.filters);
            this.setState({
                courses: data.results,
                pagination: {
                    count: data.count,
                    next: data.next,
                    previous: data.previous
                },
                loading: false
            });
        } catch (error) {
            this.setState({
                error: error.message,
                loading: false
            });
        }
    }

    setFilters(filters) {
        this.setState({
            filters: { ...this.state.filters, ...filters }
        });
        this.loadCourses();
    }
}

// Usage
const courseState = new CourseStateManager();

// Subscribe to changes
const unsubscribe = courseState.subscribe((state) => {
    console.log('State updated:', state);
    // Update UI based on new state
});
```

### **3. Accessibility**

#### **Accessible Course Card**
```jsx
const AccessibleCourseCard = ({ course }) => {
    return (
        <article
            className="course-card"
            role="article"
            aria-labelledby={`course-title-${course.id}`}
        >
            <header>
                <h3 id={`course-title-${course.id}`}>
                    {course.course_name}
                </h3>
                <span className="course-code" aria-label="Course code">
                    {course.course_code}
                </span>
            </header>

            <div className="course-content">
                <dl className="course-details">
                    <dt>Instructor:</dt>
                    <dd>{course.instructor}</dd>

                    <dt>Duration:</dt>
                    <dd>{course.training_hours} hours</dd>

                    <dt>Enrollment:</dt>
                    <dd>
                        <span aria-label={`${course.current_enrollment} out of ${course.max_participants} participants enrolled`}>
                            {course.current_enrollment}/{course.max_participants}
                        </span>
                    </dd>
                </dl>

                <div
                    className="progress-bar"
                    role="progressbar"
                    aria-valuenow={course.enrollment_percentage}
                    aria-valuemin="0"
                    aria-valuemax="100"
                    aria-label="Enrollment progress"
                >
                    <div
                        className="progress-fill"
                        style={{ width: `${course.enrollment_percentage}%` }}
                    />
                </div>
            </div>

            <footer className="course-actions">
                {course.can_register ? (
                    <button
                        className="btn btn-primary"
                        onClick={() => handleEnroll(course.id)}
                        disabled={course.is_full}
                        aria-describedby={`course-status-${course.id}`}
                    >
                        {course.is_full ? 'Course Full' : 'Enroll Now'}
                    </button>
                ) : (
                    <span
                        id={`course-status-${course.id}`}
                        className="registration-closed"
                        role="status"
                    >
                        Registration Closed
                    </span>
                )}
            </footer>
        </article>
    );
};
```

### **4. Security Best Practices**

#### **Secure API Calls**
```javascript
class SecureCourseService {
    static async makeSecureRequest(url, options = {}) {
        // Add CSRF token if available
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;

        const headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            ...(csrfToken && { 'X-CSRFToken': csrfToken }),
            ...options.headers
        };

        // Sanitize URL to prevent injection
        const sanitizedUrl = this.sanitizeUrl(url);

        return await fetch(sanitizedUrl, {
            ...options,
            headers,
            credentials: 'same-origin' // Include cookies for CSRF
        });
    }

    static sanitizeUrl(url) {
        try {
            const urlObj = new URL(url, window.location.origin);
            // Only allow same origin requests
            if (urlObj.origin !== window.location.origin) {
                throw new Error('Cross-origin requests not allowed');
            }
            return urlObj.toString();
        } catch (error) {
            throw new Error('Invalid URL');
        }
    }

    // Sanitize user input
    static sanitizeInput(input) {
        if (typeof input !== 'string') return input;

        return input
            .replace(/[<>]/g, '') // Remove potential HTML tags
            .trim()
            .substring(0, 1000); // Limit length
    }

    static async getCourses(filters = {}) {
        // Sanitize filter inputs
        const sanitizedFilters = {};
        Object.entries(filters).forEach(([key, value]) => {
            sanitizedFilters[key] = this.sanitizeInput(value);
        });

        const queryParams = new URLSearchParams(sanitizedFilters);
        const url = `${COURSES_ENDPOINT}?${queryParams}`;

        return await this.makeSecureRequest(url);
    }
}
```

### **5. Testing Utilities**

#### **Mock Course Service for Testing**
```javascript
class MockCourseService {
    static mockCourses = [
        {
            id: 1,
            course_name: "Test Course 1",
            course_code: "TEST001",
            instructor: "Test Instructor",
            cost: "99.99",
            is_free: false,
            start_date: "2025-03-01",
            end_date: "2025-03-31",
            registration_deadline: "2025-02-25",
            training_hours: 40,
            max_participants: 30,
            current_enrollment: 15,
            enrollment_percentage: 50,
            status: "published",
            is_featured: true,
            can_register: true,
            is_full: false,
            is_registration_open: true
        }
    ];

    static async getCourses(filters = {}) {
        // Simulate API delay
        await new Promise(resolve => setTimeout(resolve, 500));

        let filteredCourses = [...this.mockCourses];

        // Apply filters
        if (filters.search) {
            filteredCourses = filteredCourses.filter(course =>
                course.course_name.toLowerCase().includes(filters.search.toLowerCase())
            );
        }

        if (filters.type) {
            filteredCourses = filteredCourses.filter(course =>
                course.type === filters.type
            );
        }

        return {
            count: filteredCourses.length,
            next: null,
            previous: null,
            results: filteredCourses
        };
    }

    static async createCourse(courseData) {
        await new Promise(resolve => setTimeout(resolve, 500));

        const newCourse = {
            id: Date.now(),
            ...courseData,
            current_enrollment: 0,
            enrollment_percentage: 0,
            can_register: true,
            is_full: false,
            is_registration_open: true
        };

        this.mockCourses.push(newCourse);
        return newCourse;
    }
}

// Test helper
class CourseTestHelper {
    static createMockCourse(overrides = {}) {
        return {
            id: Math.floor(Math.random() * 1000),
            course_name: "Test Course",
            course_code: "TEST001",
            instructor: "Test Instructor",
            cost: "0.00",
            is_free: true,
            start_date: "2025-03-01",
            end_date: "2025-03-31",
            registration_deadline: "2025-02-25",
            training_hours: 20,
            max_participants: 25,
            current_enrollment: 10,
            enrollment_percentage: 40,
            status: "published",
            is_featured: false,
            can_register: true,
            is_full: false,
            is_registration_open: true,
            ...overrides
        };
    }

    static async testCourseService() {
        console.log('Testing Course Service...');

        try {
            // Test getCourses
            const courses = await CourseService.getCourses();
            console.log('✅ getCourses works:', courses);

            // Test with filters
            const filteredCourses = await CourseService.getCourses({
                search: 'test',
                type: 'course'
            });
            console.log('✅ getCourses with filters works:', filteredCourses);

        } catch (error) {
            console.error('❌ Course service test failed:', error);
        }
    }
}
```

---

## 📚 **Summary**

This comprehensive guide covers:

### **✅ Core Features Implemented:**
- **Authentication & Authorization** with JWT tokens
- **CRUD Operations** for courses (Create, Read, Update, Delete)
- **Advanced Filtering** by type, status, featured, department
- **Search Functionality** with debounced input
- **Pagination** with next/previous navigation
- **Course Enrollment** for authenticated users
- **Form Validation** with client-side and server-side checks
- **Error Handling** with user-friendly messages
- **Loading States** and progress indicators

### **🎯 Best Practices Included:**
- **Performance Optimization** with caching and debouncing
- **Security Measures** with input sanitization and CSRF protection
- **Accessibility Support** with ARIA labels and semantic HTML
- **State Management** for complex applications
- **Testing Utilities** for development and QA
- **Error Boundaries** for React applications

### **🚀 Ready-to-Use Components:**
- **React Components** for modern applications
- **Vanilla JavaScript** for traditional web pages
- **Reusable Services** for API communication
- **Utility Classes** for common operations

### **📱 Responsive Design Ready:**
- Mobile-friendly course cards
- Flexible grid layouts
- Touch-friendly buttons and controls
- Accessible navigation

This guide provides everything you need to build a complete course management frontend that integrates seamlessly with your Django REST API! 🎉
```
```

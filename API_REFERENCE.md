# Ageri Research Platform - API Reference

## **Base URL**
```
Development: http://localhost:8000/api
Production: https://your-domain.com/api
```

## **Authentication**
All API requests (except registration and login) require JWT authentication:
```
Authorization: Bearer <your_jwt_token>
```

## **Response Format**
All API responses follow this structure:
```json
{
  "success": true,
  "data": {...},
  "message": "Success message",
  "errors": null
}
```

## **Authentication Endpoints**

### **POST /auth/register/**
Register a new user (requires admin approval)
```json
Request:
{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "securepassword123",
  "password_confirm": "securepassword123",
  "first_name": "John",
  "last_name": "Doe",
  "institution": "University of Science"
}

Response:
{
  "message": "Registration successful. Please wait for admin approval.",
  "user": {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "is_approved": false
  }
}
```

### **POST /auth/login/**
Authenticate user and get JWT tokens
```json
Request:
{
  "username": "john_doe",
  "password": "securepassword123"
}

Response:
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "role": "researcher",
    "is_approved": true
  }
}
```

### **GET /auth/users/me/**
Get current user profile
```json
Response:
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "role": "researcher",
  "institution": "University of Science",
  "is_approved": true,
  "date_joined": "2025-01-01T10:00:00Z"
}
```

## **Research Endpoints**

### **GET /research/publications/**
List publications with pagination and filtering
```
Query Parameters:
- page: Page number (default: 1)
- page_size: Items per page (default: 10)
- search: Search in title, abstract, authors
- status: Filter by status (draft, pending, published, rejected)
- author: Filter by author ID

Response:
{
  "count": 25,
  "next": "http://localhost:8000/api/research/publications/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "Advanced Machine Learning Techniques",
      "abstract": "This paper explores...",
      "status": "published",
      "journal_name": "Journal of AI Research",
      "corresponding_author": {
        "id": 1,
        "name": "John Doe",
        "email": "john@example.com"
      },
      "authors": [
        {"id": 1, "name": "John Doe"},
        {"id": 2, "name": "Jane Smith"}
      ],
      "created_at": "2025-01-01T10:00:00Z",
      "updated_at": "2025-01-02T15:30:00Z"
    }
  ]
}
```

### **POST /research/publications/**
Submit a new publication
```json
Request:
{
  "title": "New Research Paper",
  "abstract": "This paper presents...",
  "journal_name": "Science Journal",
  "corresponding_author": 1,
  "authors": [1, 2, 3],
  "status": "draft"
}

Response:
{
  "id": 2,
  "title": "New Research Paper",
  "status": "draft",
  "created_at": "2025-01-03T09:00:00Z"
}
```

## **Organization Endpoints (Public Access)**

### **GET /organization/departments/**
List all departments (public access)
```json
Response:
{
  "count": 5,
  "results": [
    {
      "id": 1,
      "name": "Computer Science",
      "description": "Department of Computer Science and Engineering",
      "head": {
        "id": 5,
        "full_name": "Dr. Alice Johnson",
        "email": "alice.johnson@ageri.com"
      },
      "researchers_count": 15,
      "labs_count": 3,
      "status": "active",
      "created_at": "2024-01-15T10:00:00Z"
    }
  ]
}
```

### **GET /organization/departments/{id}/**
Get department details (public access)
```json
Response:
{
  "id": 1,
  "name": "Computer Science",
  "description": "Department of Computer Science and Engineering focusing on AI, software engineering, and data science research.",
  "head": {
    "id": 5,
    "full_name": "Dr. Alice Johnson",
    "email": "alice.johnson@ageri.com"
  },
  "researchers_count": 15,
  "labs_count": 3,
  "status": "active",
  "created_at": "2024-01-15T10:00:00Z"
}
```

### **GET /organization/departments/{id}/labs/**
Get labs in a department (public access)
```json
Response:
{
  "count": 3,
  "results": [
    {
      "id": 1,
      "name": "AI Research Lab",
      "description": "Artificial Intelligence and Machine Learning research",
      "department": {
        "id": 1,
        "name": "Computer Science"
      },
      "head": {
        "id": 3,
        "full_name": "Dr. Bob Wilson",
        "email": "bob.wilson@ageri.com"
      },
      "capacity": 20,
      "current_researchers_count": 12,
      "equipment": ["GPU Cluster", "Workstations", "Servers"],
      "status": "active"
    }
  ]
}
```

### **GET /organization/labs/**
List all laboratories (public access)
```json
Response:
{
  "count": 8,
  "results": [
    {
      "id": 1,
      "name": "AI Research Lab",
      "description": "Artificial Intelligence and Machine Learning research",
      "department": {
        "id": 1,
        "name": "Computer Science"
      },
      "head": {
        "id": 3,
        "full_name": "Dr. Bob Wilson",
        "email": "bob.wilson@ageri.com"
      },
      "capacity": 20,
      "current_researchers_count": 12,
      "equipment": ["GPU Cluster", "Workstations", "Servers"],
      "status": "active",
      "created_at": "2024-02-01T14:00:00Z"
    }
  ]
}
```

### **GET /organization/labs/{id}/**
Get laboratory details (public access)
```json
Response:
{
  "id": 1,
  "name": "AI Research Lab",
  "description": "State-of-the-art facility for Artificial Intelligence and Machine Learning research, equipped with high-performance computing resources.",
  "department": {
    "id": 1,
    "name": "Computer Science",
    "description": "Department of Computer Science and Engineering"
  },
  "head": {
    "id": 3,
    "full_name": "Dr. Bob Wilson",
    "email": "bob.wilson@ageri.com"
  },
  "capacity": 20,
  "current_researchers_count": 12,
  "equipment": ["GPU Cluster", "Workstations", "Servers", "High-speed Network"],
  "research_areas": ["Machine Learning", "Deep Learning", "Computer Vision", "NLP"],
  "status": "active",
  "created_at": "2024-02-01T14:00:00Z"
}
```

### **GET /organization/labs/{id}/researchers/**
Get researchers in a lab (public access)
```json
Response:
{
  "count": 12,
  "results": [
    {
      "id": 1,
      "researcher": {
        "id": 10,
        "full_name": "Dr. Sarah Chen",
        "email": "sarah.chen@ageri.com",
        "role": "researcher",
        "specialization": "Machine Learning"
      },
      "lab": {
        "id": 1,
        "name": "AI Research Lab"
      },
      "position": "Senior Researcher",
      "start_date": "2024-01-15",
      "status": "active"
    }
  ]
}
```

### **GET /organization/labs/{id}/head/**
Get lab head researcher (public access)
```json
Response:
{
  "id": 3,
  "full_name": "Dr. Bob Wilson",
  "email": "bob.wilson@ageri.com",
  "role": "researcher",
  "specialization": "Artificial Intelligence",
  "bio": "Leading researcher in AI with 15+ years of experience",
  "research_interests": ["Machine Learning", "Deep Learning", "Computer Vision"],
  "publications_count": 45,
  "joined_date": "2020-03-01"
}
```

## **Training Endpoints**

### **GET /training/courses/**
List available courses
```json
Response:
{
  "results": [
    {
      "id": 1,
      "title": "Introduction to Machine Learning",
      "description": "Basic ML concepts and algorithms",
      "instructor": {
        "id": 2,
        "name": "Dr. Sarah Davis"
      },
      "duration_weeks": 8,
      "max_participants": 30,
      "enrolled_count": 25,
      "start_date": "2025-02-01",
      "end_date": "2025-03-29",
      "status": "open"
    }
  ]
}
```

### **POST /training/courses/{id}/enroll/**
Enroll in a course
```json
Request:
{
  "motivation": "I want to learn ML for my research project"
}

Response:
{
  "message": "Successfully enrolled in course",
  "enrollment": {
    "id": 1,
    "course": 1,
    "student": 1,
    "enrolled_at": "2025-01-15T14:00:00Z",
    "status": "enrolled"
  }
}
```

## **Services Endpoints**

### **GET /services/test-services/**
List available testing services
```json
Response:
{
  "results": [
    {
      "id": 1,
      "name": "Material Testing",
      "description": "Comprehensive material analysis",
      "category": "testing",
      "price": 500.00,
      "duration_days": 5,
      "requirements": ["Sample preparation", "Safety documentation"],
      "available": true
    }
  ]
}
```

### **POST /services/requests/**
Submit a service request
```json
Request:
{
  "service": 1,
  "title": "Steel Sample Analysis",
  "description": "Need to test steel samples for tensile strength",
  "client": {
    "name": "ABC Manufacturing",
    "email": "contact@abc.com",
    "phone": "+1234567890",
    "organization": "ABC Corp"
  },
  "requirements": "Urgent testing needed",
  "expected_completion": "2025-02-15"
}

Response:
{
  "id": 1,
  "request_id": "SR2025-001",
  "status": "pending",
  "estimated_completion": "2025-02-15",
  "created_at": "2025-01-15T10:00:00Z"
}
```

## **Content Endpoints**

### **GET /content/announcements/**
List announcements (includes full content and all attachments)
```json
Response:
{
  "count": 25,
  "next": "http://localhost:8000/api/content/announcements/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "System Maintenance Notice",
      "content": "The system will be under maintenance from 2:00 AM to 6:00 AM EST on January 20th, 2025. During this time, all services will be temporarily unavailable. We apologize for any inconvenience this may cause and appreciate your patience as we work to improve our platform.",
      "summary": "System maintenance scheduled for January 20th from 2:00 AM to 6:00 AM EST",
      "announcement_type": "maintenance",
      "priority": "high",
      "target_audience": "all",
      "status": "published",
      "is_pinned": true,
      "is_featured": false,
      "publish_at": "2025-01-10T09:00:00Z",
      "expires_at": "2025-01-20T23:59:59Z",
      "author": {
        "id": 1,
        "full_name": "Admin User",
        "email": "admin@ageri.com"
      },
      "view_count": 156,
      "is_published": true,
      "is_expired": false,
      "attachment": null,
      "attachment_url": null,
      "images": [
        {
          "id": 1,
          "announcement": 1,
          "image_url": "http://localhost:8000/media/content/announcements/1/images/diagram.jpg",
          "caption": "System architecture diagram",
          "alt_text": "Diagram showing system components and maintenance areas",
          "order": 0,
          "created_at": "2025-01-10T09:15:00Z"
        },
        {
          "id": 2,
          "announcement": 1,
          "image_url": "http://localhost:8000/media/content/announcements/1/images/timeline.png",
          "caption": "Maintenance timeline",
          "alt_text": "Visual timeline of maintenance activities",
          "order": 1,
          "created_at": "2025-01-10T09:20:00Z"
        }
      ],
      "attachments": [
        {
          "id": 1,
          "announcement": 1,
          "file_url": "http://localhost:8000/media/content/announcements/1/schedule.pdf",
          "title": "Detailed Maintenance Schedule",
          "description": "Complete timeline and procedures for the maintenance window",
          "file_size": 245760,
          "file_size_display": "240.00 KB",
          "download_count": 23,
          "created_at": "2025-01-10T09:10:00Z"
        },
        {
          "id": 2,
          "announcement": 1,
          "file_url": "http://localhost:8000/media/content/announcements/1/contact-info.pdf",
          "title": "Emergency Contact Information",
          "description": "Contact details for urgent issues during maintenance",
          "file_size": 102400,
          "file_size_display": "100.00 KB",
          "download_count": 45,
          "created_at": "2025-01-10T09:25:00Z"
        }
      ],
      "created_at": "2025-01-10T09:00:00Z"
    }
  ]
}
```

### **POST /content/announcements/{id}/images/**
Upload images to an announcement
```json
Request (multipart/form-data):
{
  "image": <file>,
  "caption": "System architecture diagram",
  "alt_text": "Diagram showing system components",
  "order": 0
}

Response:
{
  "id": 1,
  "announcement": 1,
  "image_url": "http://localhost:8000/media/content/announcements/1/images/diagram.jpg",
  "caption": "System architecture diagram",
  "alt_text": "Diagram showing system components",
  "order": 0,
  "created_at": "2025-01-15T10:30:00Z"
}
```

### **POST /content/announcements/{id}/attachments/**
Upload attachments to an announcement
```json
Request (multipart/form-data):
{
  "file": <file>,
  "title": "Maintenance Schedule",
  "description": "Detailed maintenance timeline and procedures"
}

Response:
{
  "id": 1,
  "announcement": 1,
  "file_url": "http://localhost:8000/media/content/announcements/1/schedule.pdf",
  "title": "Maintenance Schedule",
  "description": "Detailed maintenance timeline and procedures",
  "file_size": 245760,
  "file_size_display": "240.00 KB",
  "download_count": 0,
  "created_at": "2025-01-15T10:35:00Z"
}
```

### **GET /content/posts/**
List news posts
```json
Response:
{
  "results": [
    {
      "id": 1,
      "title": "New Research Breakthrough",
      "content": "Our team has made significant progress...",
      "author": {
        "id": 2,
        "name": "Dr. Research Lead"
      },
      "tags": ["research", "breakthrough", "ai"],
      "comments_count": 5,
      "created_at": "2025-01-12T14:30:00Z"
    }
  ]
}
```

## **Error Responses**
```json
400 Bad Request:
{
  "success": false,
  "errors": {
    "field_name": ["Error message"]
  },
  "message": "Validation failed"
}

401 Unauthorized:
{
  "success": false,
  "message": "Authentication credentials were not provided"
}

403 Forbidden:
{
  "success": false,
  "message": "You do not have permission to perform this action"
}

404 Not Found:
{
  "success": false,
  "message": "Resource not found"
}
```

## **Pagination**
List endpoints support pagination:
```
?page=2&page_size=20
```

## **Filtering & Search**
Most list endpoints support filtering:
```
?search=machine learning&status=published&author=1
```

## **File Uploads**
For endpoints that accept files, use multipart/form-data:
```javascript
const formData = new FormData();
formData.append('file', fileObject);
formData.append('title', 'Document Title');
```

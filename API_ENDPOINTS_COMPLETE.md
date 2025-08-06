# Ageri Research Platform - Complete API Endpoints

## **Base URL**
```
Development: http://localhost:8000/api
Production: https://your-domain.com/api
```

## **Interactive Documentation**
- **Swagger UI**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/
- **API Schema**: http://localhost:8000/api/schema/

## **Authentication Required**
All endpoints except registration and login require JWT authentication:
```
Authorization: Bearer <your_jwt_token>
```

---

## **🔐 AUTHENTICATION ENDPOINTS**

### **User Authentication**
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `POST` | `/auth/register/` | User registration | ❌ |
| `POST` | `/auth/login/` | User login | ❌ |
| `POST` | `/auth/logout/` | User logout | ✅ |
| `POST` | `/auth/token/refresh/` | Refresh JWT token | ❌ |
| `GET` | `/auth/users/me/` | Get current user profile | ✅ |
| `PUT` | `/auth/users/me/` | Update user profile | ✅ |
| `PATCH` | `/auth/users/me/` | Partial update user profile | ✅ |

### **User Management (Admin Only)**
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/auth/users/` | List all users | ✅ (Admin) |
| `GET` | `/auth/users/{id}/` | Get user details | ✅ (Admin) |
| `PUT` | `/auth/users/{id}/` | Update user | ✅ (Admin) |
| `DELETE` | `/auth/users/{id}/` | Delete user | ✅ (Admin) |
| `POST` | `/auth/users/{id}/approve/` | Approve user | ✅ (Admin) |

---

## **📚 RESEARCH ENDPOINTS**

### **Publications**
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/research/publications/` | List publications | ✅ |
| `POST` | `/research/publications/` | Create publication | ✅ |
| `GET` | `/research/publications/{id}/` | Get publication details | ✅ |
| `PUT` | `/research/publications/{id}/` | Update publication | ✅ |
| `PATCH` | `/research/publications/{id}/` | Partial update publication | ✅ |
| `DELETE` | `/research/publications/{id}/` | Delete publication | ✅ |

### **Publication Authors**
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/research/publications/{id}/authors/` | List publication authors | ✅ |
| `POST` | `/research/publications/{id}/authors/` | Add author to publication | ✅ |
| `DELETE` | `/research/publications/{id}/authors/{author_id}/` | Remove author | ✅ |

---

## **🏢 ORGANIZATION ENDPOINTS**

### **Departments (Public Access)**
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/organization/departments/` | List departments | ❌ |
| `POST` | `/organization/departments/` | Create department | ✅ (Admin) |
| `GET` | `/organization/departments/{id}/` | Get department details | ❌ |
| `GET` | `/organization/departments/{id}/labs/` | Get department labs | ❌ |
| `PUT` | `/organization/departments/{id}/` | Update department | ✅ (Admin) |
| `PATCH` | `/organization/departments/{id}/` | Partial update department | ✅ (Admin) |
| `DELETE` | `/organization/departments/{id}/` | Delete department | ✅ (Admin) |

### **Laboratories (Public Access)**
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/organization/labs/` | List laboratories | ❌ |
| `POST` | `/organization/labs/` | Create laboratory | ✅ (Admin) |
| `GET` | `/organization/labs/{id}/` | Get laboratory details | ❌ |
| `GET` | `/organization/labs/{id}/researchers/` | Get lab researchers | ❌ |
| `GET` | `/organization/labs/{id}/head/` | Get lab head researcher | ❌ |
| `PUT` | `/organization/labs/{id}/` | Update laboratory | ✅ (Admin) |
| `PATCH` | `/organization/labs/{id}/` | Partial update laboratory | ✅ (Admin) |
| `DELETE` | `/organization/labs/{id}/` | Delete laboratory | ✅ (Admin) |

### **Lab Management**
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `POST` | `/organization/labs/{id}/assign-researcher/` | Assign researcher to lab | ✅ (Admin) |
| `POST` | `/organization/labs/{id}/remove-researcher/` | Remove researcher from lab | ✅ (Admin) |
| `GET` | `/organization/labs/{id}/researchers/` | List lab researchers | ✅ |

---

## **🎓 TRAINING ENDPOINTS**

### **Courses**
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/training/courses/` | List courses | ✅ |
| `POST` | `/training/courses/` | Create course | ✅ (Admin/Moderator) |
| `GET` | `/training/courses/{id}/` | Get course details | ✅ |
| `PUT` | `/training/courses/{id}/` | Update course | ✅ (Admin/Moderator) |
| `PATCH` | `/training/courses/{id}/` | Partial update course | ✅ (Admin/Moderator) |
| `DELETE` | `/training/courses/{id}/` | Delete course | ✅ (Admin) |

### **Course Enrollment**
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `POST` | `/training/courses/{id}/enroll/` | Enroll in course | ✅ |
| `POST` | `/training/courses/{id}/unenroll/` | Unenroll from course | ✅ |
| `GET` | `/training/courses/{id}/enrollments/` | List course enrollments | ✅ (Admin/Moderator) |
| `GET` | `/training/my-enrollments/` | Get user's enrollments | ✅ |

### **Summer Training Programs**
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/training/summer-programs/` | List summer programs | ✅ |
| `POST` | `/training/summer-programs/` | Create summer program | ✅ (Admin/Moderator) |
| `GET` | `/training/summer-programs/{id}/` | Get program details | ✅ |
| `PUT` | `/training/summer-programs/{id}/` | Update program | ✅ (Admin/Moderator) |
| `DELETE` | `/training/summer-programs/{id}/` | Delete program | ✅ (Admin) |

### **Public Services**
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/training/public-services/` | List public services | ❌ |
| `POST` | `/training/public-services/` | Request public service | ❌ |
| `GET` | `/training/public-services/{id}/` | Get service details | ❌ |

---

## **⚙️ SERVICES ENDPOINTS**

### **Test Services**
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/services/test-services/` | List available services | ✅ |
| `POST` | `/services/test-services/` | Create service | ✅ (Admin) |
| `GET` | `/services/test-services/{id}/` | Get service details | ✅ |
| `PUT` | `/services/test-services/{id}/` | Update service | ✅ (Admin) |
| `DELETE` | `/services/test-services/{id}/` | Delete service | ✅ (Admin) |

### **Service Requests**
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/services/requests/` | List service requests | ✅ |
| `POST` | `/services/requests/` | Submit service request | ✅ |
| `GET` | `/services/requests/{id}/` | Get request details | ✅ |
| `PUT` | `/services/requests/{id}/` | Update request | ✅ |
| `PATCH` | `/services/requests/{id}/` | Partial update request | ✅ |
| `DELETE` | `/services/requests/{id}/` | Delete request | ✅ |

### **Service Management**
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `POST` | `/services/requests/{id}/assign-technician/` | Assign technician | ✅ (Admin/Moderator) |
| `POST` | `/services/requests/{id}/update-status/` | Update request status | ✅ (Admin/Moderator) |
| `GET` | `/services/my-requests/` | Get user's requests | ✅ |

---

## **📢 CONTENT ENDPOINTS**

### **Announcements**
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/content/announcements/` | List announcements | ✅ |
| `POST` | `/content/announcements/` | Create announcement | ✅ (Admin/Moderator) |
| `GET` | `/content/announcements/{id}/` | Get announcement details | ✅ |
| `PUT` | `/content/announcements/{id}/` | Update announcement | ✅ (Admin/Moderator) |
| `DELETE` | `/content/announcements/{id}/` | Delete announcement | ✅ (Admin/Moderator) |

### **Announcement Media**
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `POST` | `/content/announcements/{id}/images/` | Upload announcement image | ✅ (Admin/Moderator) |
| `GET` | `/content/announcements/{id}/images/` | List announcement images | ✅ |
| `DELETE` | `/content/announcements/{id}/images/{image_id}/` | Delete image | ✅ (Admin/Moderator) |
| `POST` | `/content/announcements/{id}/attachments/` | Upload attachment | ✅ (Admin/Moderator) |
| `GET` | `/content/announcements/{id}/attachments/` | List attachments | ✅ |
| `DELETE` | `/content/announcements/{id}/attachments/{file_id}/` | Delete attachment | ✅ (Admin/Moderator) |

### **Posts**
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/content/posts/` | List posts | ✅ |
| `POST` | `/content/posts/` | Create post | ✅ |
| `GET` | `/content/posts/{id}/` | Get post details | ✅ |
| `PUT` | `/content/posts/{id}/` | Update post | ✅ |
| `DELETE` | `/content/posts/{id}/` | Delete post | ✅ |

### **Comments**
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/content/posts/{id}/comments/` | List post comments | ✅ |
| `POST` | `/content/posts/{id}/comments/` | Add comment | ✅ |
| `PUT` | `/content/comments/{id}/` | Update comment | ✅ |
| `DELETE` | `/content/comments/{id}/` | Delete comment | ✅ |

---

## **📊 QUERY PARAMETERS**

### **Pagination**
```
?page=2&page_size=20
```

### **Filtering**
```
?search=keyword&status=published&author=1
```

### **Ordering**
```
?ordering=-created_at&ordering=title
```

### **Date Filtering**
```
?created_after=2025-01-01&created_before=2025-12-31
```

---

## **📁 FILE UPLOAD ENDPOINTS**

### **Profile Pictures**
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `POST` | `/auth/users/me/avatar/` | Upload profile picture | ✅ |
| `DELETE` | `/auth/users/me/avatar/` | Remove profile picture | ✅ |

### **Publication Files**
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `POST` | `/research/publications/{id}/files/` | Upload publication file | ✅ |
| `GET` | `/research/publications/{id}/files/` | List publication files | ✅ |
| `DELETE` | `/research/publications/{id}/files/{file_id}/` | Delete file | ✅ |

---

## **🔍 SEARCH ENDPOINTS**

### **Global Search**
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/search/` | Global search across all content | ✅ |
| `GET` | `/search/users/` | Search users | ✅ |
| `GET` | `/search/departments/` | Search departments | ❌ |
| `GET` | `/search/labs/` | Search laboratories | ❌ |

---

## **📈 ANALYTICS ENDPOINTS**

### **Statistics**
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/analytics/dashboard/` | Dashboard statistics | ✅ (Admin) |
| `GET` | `/analytics/publications/` | Publication analytics | ✅ (Admin) |
| `GET` | `/analytics/users/` | User analytics | ✅ (Admin) |
| `GET` | `/analytics/services/` | Service analytics | ✅ (Admin) |

---

## **⚡ REAL-TIME ENDPOINTS**

### **Notifications**
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/notifications/` | List user notifications | ✅ |
| `POST` | `/notifications/{id}/mark-read/` | Mark notification as read | ✅ |
| `POST` | `/notifications/mark-all-read/` | Mark all as read | ✅ |

---

## **🔧 ADMIN ENDPOINTS**

### **System Management**
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/admin/system-info/` | Get system information | ✅ (Admin) |
| `POST` | `/admin/clear-cache/` | Clear system cache | ✅ (Admin) |
| `GET` | `/admin/health-check/` | System health check | ✅ (Admin) |

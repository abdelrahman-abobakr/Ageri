# Frontend Integration Guide

## Overview
This guide provides information for integrating a React frontend with the Scientific Research Organization Platform API.

## API Base Configuration

### Base URL
- **Development**: `http://localhost:8000/api/`
- **Production**: Configure via environment variables

### Authentication
The API uses JWT (JSON Web Tokens) for authentication.

#### Authentication Flow
1. **Login**: POST to `/api/auth/login/` with email and password
2. **Response**: Receive `access` and `refresh` tokens
3. **API Calls**: Include `Authorization: Bearer <access_token>` header
4. **Token Refresh**: POST to `/api/auth/token/refresh/` with refresh token

#### Example Login Request
```javascript
const loginResponse = await fetch('http://localhost:8000/api/auth/login/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    email: 'user@example.com',
    password: 'password123'
  })
});

const { access, refresh } = await loginResponse.json();
```

#### Example Authenticated Request
```javascript
const response = await fetch('http://localhost:8000/api/research/publications/', {
  headers: {
    'Authorization': `Bearer ${accessToken}`,
    'Content-Type': 'application/json',
  }
});
```

## API Endpoints Overview

### Authentication (`/api/auth/`)
- `POST /login/` - User login
- `POST /logout/` - User logout
- `POST /register/` - User registration
- `POST /token/refresh/` - Refresh access token
- `GET /users/` - List users (admin only)
- `GET /users/me/` - Current user profile
- `PUT /users/me/` - Update current user profile

### Research (`/api/research/`)
- `GET /publications/` - List publications
- `POST /publications/` - Create publication
- `GET /publications/{id}/` - Get publication details
- `PUT /publications/{id}/` - Update publication
- `DELETE /publications/{id}/` - Delete publication
- `POST /publications/{id}/approve/` - Approve publication (admin)

### Organization (`/api/organization/`)
- `GET /departments/` - List departments
- `GET /labs/` - List labs
- `GET /equipment/` - List equipment
- `GET /staff/` - List staff members

### Content (`/api/content/`)
- `GET /announcements/` - List announcements
- `POST /announcements/` - Create announcement (moderator+)
- `GET /posts/` - List posts
- `POST /posts/` - Create post (moderator+)

### Training (`/api/training/`)
- `GET /courses/` - List courses
- `GET /summer-training/` - List summer training programs
- `GET /public-services/` - List public services
- `POST /enrollments/` - Enroll in course
- `POST /applications/` - Apply for summer training

### Services (`/api/services/`)
- `GET /test-services/` - List test services
- `POST /service-requests/` - Create service request
- `GET /clients/` - List clients (admin/moderator)
- `GET /technician-assignments/` - List technician assignments

## User Roles and Permissions

### Admin
- Full access to all endpoints
- User management and approval
- System configuration

### Moderator
- Content creation (announcements, posts)
- Service management
- User data viewing

### Researcher
- Profile management
- Publication submission
- Service requests
- Course enrollment

## File Uploads

### Supported File Types
- Documents: PDF, DOC, DOCX
- Images: JPG, JPEG, PNG, GIF
- Maximum size: 10MB (configurable)

### Upload Example
```javascript
const formData = new FormData();
formData.append('file', fileInput.files[0]);
formData.append('title', 'Document Title');

const response = await fetch('http://localhost:8000/api/research/publications/', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${accessToken}`,
  },
  body: formData
});
```

## Error Handling

### HTTP Status Codes
- `200` - Success
- `201` - Created
- `400` - Bad Request (validation errors)
- `401` - Unauthorized (authentication required)
- `403` - Forbidden (insufficient permissions)
- `404` - Not Found
- `500` - Internal Server Error

### Error Response Format
```json
{
  "detail": "Error message",
  "field_errors": {
    "email": ["This field is required."],
    "password": ["Password too short."]
  }
}
```

## Pagination

### Request Parameters
- `page` - Page number (default: 1)
- `page_size` - Items per page (default: 20, max: 100)

### Response Format
```json
{
  "count": 150,
  "next": "http://localhost:8000/api/research/publications/?page=2",
  "previous": null,
  "results": [...]
}
```

## Filtering and Search

### Common Query Parameters
- `search` - Text search across relevant fields
- `ordering` - Sort by field (prefix with `-` for descending)
- Field-specific filters (varies by endpoint)

### Example
```
GET /api/research/publications/?search=machine%20learning&ordering=-created_at&status=published
```

## Real-time Features (Future)

### WebSocket Endpoints (Planned)
- `/ws/notifications/` - Real-time notifications
- `/ws/chat/` - Real-time messaging

## Development Tools

### API Documentation
- **Swagger UI**: `http://localhost:8000/api/docs/`
- **OpenAPI Schema**: `http://localhost:8000/api/schema/`

### CORS Configuration
The API is configured to accept requests from:
- `http://localhost:3000` (React development server)
- `http://127.0.0.1:3000`

## Environment Variables for Frontend

Create a `.env` file in your React project:

```env
REACT_APP_API_BASE_URL=http://localhost:8000/api
REACT_APP_MEDIA_BASE_URL=http://localhost:8000/media
REACT_APP_ENVIRONMENT=development
```

## Recommended Frontend Libraries

### Core
- **React Router** - Client-side routing
- **Axios** - HTTP client
- **React Query/TanStack Query** - Data fetching and caching

### UI Components
- **Material-UI** or **Ant Design** - Component library
- **React Hook Form** - Form handling
- **React Dropzone** - File uploads

### State Management
- **Zustand** or **Redux Toolkit** - Global state management
- **React Context** - Authentication state

### Utilities
- **date-fns** or **moment.js** - Date manipulation
- **react-pdf** - PDF viewing
- **react-chartjs-2** - Data visualization

## Sample React Hooks

### Authentication Hook
```javascript
// hooks/useAuth.js
import { useState, useEffect } from 'react';

export const useAuth = () => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (token) {
      // Verify token and get user info
      fetchUserProfile(token);
    } else {
      setLoading(false);
    }
  }, []);

  const login = async (email, password) => {
    // Login implementation
  };

  const logout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    setUser(null);
  };

  return { user, login, logout, loading };
};
```

### API Hook
```javascript
// hooks/useApi.js
import { useState, useEffect } from 'react';

export const useApi = (endpoint) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const token = localStorage.getItem('access_token');
        const response = await fetch(`${process.env.REACT_APP_API_BASE_URL}${endpoint}`, {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          }
        });
        
        if (!response.ok) throw new Error('API request failed');
        
        const result = await response.json();
        setData(result);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [endpoint]);

  return { data, loading, error };
};
```

## Next Steps

1. Set up React project with recommended dependencies
2. Implement authentication flow
3. Create reusable API service layer
4. Build core components (layout, navigation, forms)
5. Implement role-based routing and permissions
6. Add error handling and loading states
7. Implement file upload functionality
8. Add real-time features (notifications, chat)

For detailed API documentation, visit: `http://localhost:8000/api/docs/`

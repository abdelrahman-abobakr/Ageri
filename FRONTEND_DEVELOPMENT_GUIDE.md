# Ageri Research Platform - Frontend Development Guide

## **Project Overview**
You are building a modern, responsive React frontend for the Ageri Research Platform - a comprehensive research management system. The backend is complete with 91/91 tests passing and a custom admin dashboard.

## **Technology Stack Recommendations**

### **Core Framework**
- **React 18+** with TypeScript for type safety
- **Vite** for fast development and building
- **React Router v6** for client-side routing

### **UI Framework & Styling**
- **Ant Design** or **Material-UI (MUI)** for professional components
- **Tailwind CSS** for custom styling and responsive design
- **Styled Components** or **Emotion** for component-level styling

### **State Management**
- **Redux Toolkit (RTK)** with RTK Query for API state management
- **React Context** for simple global state
- **React Hook Form** for form management

### **HTTP & API**
- **Axios** for HTTP requests with interceptors
- **React Query** or **RTK Query** for server state management
- **JWT handling** for authentication

### **Development Tools**
- **ESLint + Prettier** for code quality
- **Husky** for git hooks
- **Jest + React Testing Library** for testing

## **Project Structure**
```
ageri-frontend/
├── public/
├── src/
│   ├── components/           # Reusable UI components
│   │   ├── common/          # Generic components (Button, Modal, etc.)
│   │   ├── forms/           # Form components
│   │   └── layout/          # Layout components (Header, Sidebar, etc.)
│   ├── pages/               # Page components
│   │   ├── auth/            # Login, Register, Profile
│   │   ├── dashboard/       # Dashboard pages
│   │   ├── research/        # Publication management
│   │   ├── organization/    # Departments, Labs
│   │   ├── training/        # Courses, Programs
│   │   ├── services/        # Service requests
│   │   └── content/         # Announcements, Posts
│   ├── hooks/               # Custom React hooks
│   ├── services/            # API service functions
│   ├── store/               # Redux store configuration
│   ├── utils/               # Utility functions
│   ├── types/               # TypeScript type definitions
│   └── constants/           # App constants
├── package.json
└── README.md
```

## **API Integration Details**

### **Base Configuration**
```javascript
// src/services/api.js
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// JWT Token Interceptor
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response Interceptor for token refresh
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // Handle token refresh or redirect to login
    }
    return Promise.reject(error);
  }
);
```

### **Authentication Service**
```javascript
// src/services/authService.js
export const authService = {
  login: (credentials) => apiClient.post('/auth/login/', credentials),
  register: (userData) => apiClient.post('/auth/register/', userData),
  logout: () => apiClient.post('/auth/logout/'),
  getCurrentUser: () => apiClient.get('/auth/users/me/'),
  updateProfile: (data) => apiClient.put('/auth/users/me/', data),
  refreshToken: (refresh) => apiClient.post('/auth/token/refresh/', { refresh }),
};
```

## **Key Features to Implement**

### **1. Authentication System**
**Pages**: Login, Register, Profile, Password Reset

**Features**:
- JWT-based authentication with automatic token refresh
- Role-based navigation (Admin/Moderator/Researcher)
- Protected routes with authentication guards
- User profile management with avatar upload
- Password change and reset functionality

**Components**:
- `LoginForm` - Email/password login
- `RegisterForm` - Multi-step registration
- `ProfilePage` - User profile editing
- `ProtectedRoute` - Route guard component

### **2. Dashboard System**
**Pages**: Main Dashboard, User Dashboard, Admin Dashboard

**Features**:
- Role-specific dashboards with different widgets
- Real-time statistics and charts (Chart.js/Recharts)
- Recent activity feeds
- Quick action buttons
- Responsive grid layout

**Components**:
- `DashboardLayout` - Main dashboard wrapper
- `StatCard` - Statistics display cards
- `ActivityFeed` - Recent activity component
- `QuickActions` - Action buttons panel

### **3. Research Management**
**Pages**: Publications List, Publication Detail, Submit Publication, My Publications

**Features**:
- Publication submission with file upload
- Multi-author management interface
- Advanced search and filtering
- Publication status tracking
- Citation and metrics display

**Components**:
- `PublicationList` - Paginated publication listing
- `PublicationCard` - Individual publication display
- `PublicationForm` - Submission/editing form
- `AuthorManager` - Add/remove authors interface
- `SearchFilters` - Advanced search component

### **4. Organization Management**
**Pages**: Departments, Laboratories, Researchers

**Features**:
- Hierarchical department/lab structure
- Researcher assignment interface
- Capacity and resource tracking
- Interactive organizational charts
- Resource booking system

**Components**:
- `DepartmentTree` - Hierarchical department view
- `LabCard` - Laboratory information display
- `ResearcherAssignment` - Assignment interface
- `CapacityTracker` - Resource utilization display

### **5. Training System**
**Pages**: Course Catalog, My Courses, Course Details, Enrollment

**Features**:
- Course catalog with search and filtering
- Enrollment management
- Progress tracking
- Certificate generation
- Calendar integration

**Components**:
- `CourseCatalog` - Course listing with filters
- `CourseCard` - Individual course display
- `EnrollmentForm` - Course enrollment interface
- `ProgressTracker` - Learning progress display

### **6. Services Management**
**Pages**: Service Catalog, My Requests, Request Details, Submit Request

**Features**:
- Service catalog with detailed descriptions
- Request submission with file attachments
- Status tracking with timeline
- Technician communication
- Invoice and billing integration

**Components**:
- `ServiceCatalog` - Available services listing
- `RequestForm` - Service request submission
- `RequestTracker` - Status tracking component
- `TechnicianChat` - Communication interface

### **7. Content Management**
**Pages**: Announcements, News, Post Details

**Features**:
- **Enhanced Announcements**: Full content, multiple images, and file attachments
- **Rich Media Support**: Image galleries with captions and alt text
- **File Attachments**: PDF, DOC, XLS files with download tracking
- **Comment System**: Threaded discussions on posts
- **Content Categorization**: Filter by type, priority, and audience
- **Search Functionality**: Full-text search across content

**Components**:
- `AnnouncementList` - Enhanced announcements with media preview
- `AnnouncementCard` - Rich announcement display with images/attachments
- `ImageGallery` - Announcement image carousel with captions
- `AttachmentList` - File attachments with download links
- `PostCard` - Individual post component
- `CommentSection` - Comments interface
- `RichTextEditor` - Content creation tool

**Enhanced Announcement Data Structure**:
```typescript
interface Announcement {
  id: number;
  title: string;
  content: string;        // Full content now included in list view
  summary: string;
  announcement_type: 'general' | 'urgent' | 'maintenance' | 'event';
  priority: 'low' | 'medium' | 'high';
  status: 'draft' | 'pending' | 'published' | 'rejected';
  is_pinned: boolean;
  is_featured: boolean;
  author: User;
  images: AnnouncementImage[];     // Multiple images with captions
  attachments: AnnouncementAttachment[];  // Multiple file attachments
  attachment_url?: string;         // Legacy single attachment
  view_count: number;
  created_at: string;
  expires_at?: string;
}

interface AnnouncementImage {
  id: number;
  image_url: string;
  caption: string;
  alt_text: string;
  order: number;
}

interface AnnouncementAttachment {
  id: number;
  file_url: string;
  title: string;
  description: string;
  file_size_display: string;
  download_count: number;
}
```

## **UI/UX Design Guidelines**

### **Design Principles**
- **Professional Academic Look**: Clean, scholarly appearance
- **Accessibility First**: WCAG 2.1 AA compliance
- **Mobile Responsive**: Mobile-first design approach
- **Consistent Branding**: Ageri color scheme and typography
- **Intuitive Navigation**: Clear information architecture

### **Color Scheme**
```css
:root {
  --primary-color: #0d6efd;      /* Primary blue */
  --secondary-color: #6c757d;    /* Secondary gray */
  --success-color: #198754;      /* Success green */
  --warning-color: #ffc107;      /* Warning yellow */
  --danger-color: #dc3545;       /* Danger red */
  --info-color: #0dcaf0;         /* Info cyan */
  --light-color: #f8f9fa;        /* Light background */
  --dark-color: #212529;         /* Dark text */
}
```

### **Typography**
- **Primary Font**: 'Inter' or 'Roboto' for body text
- **Heading Font**: 'Poppins' or 'Montserrat' for headings
- **Code Font**: 'Fira Code' or 'Source Code Pro' for code

### **Component Standards**
- **Buttons**: Consistent sizing, hover states, loading states
- **Forms**: Proper validation, error handling, accessibility
- **Tables**: Sortable, filterable, responsive
- **Modals**: Consistent behavior, escape key handling
- **Navigation**: Breadcrumbs, active states, responsive menu

## **State Management Strategy**

### **Redux Store Structure**
```javascript
// src/store/index.js
{
  auth: {
    user: null,
    token: null,
    isAuthenticated: false,
    loading: false
  },
  research: {
    publications: [],
    currentPublication: null,
    loading: false,
    filters: {}
  },
  organization: {
    departments: [],
    labs: [],
    researchers: []
  },
  training: {
    courses: [],
    enrollments: [],
    progress: {}
  },
  services: {
    services: [],
    requests: [],
    currentRequest: null
  },
  content: {
    announcements: [],
    posts: [],
    comments: {}
  },
  ui: {
    sidebarOpen: false,
    theme: 'light',
    notifications: []
  }
}
```

## **Development Workflow**

### **Phase 1: Foundation (Week 1-2)**
1. **Project Setup**: Create React app with TypeScript
2. **Routing**: Implement React Router with protected routes
3. **Authentication**: Login/register functionality
4. **Layout**: Header, sidebar, main content area
5. **API Integration**: Base API service setup

### **Phase 2: Core Features (Week 3-4)**
1. **Dashboard**: Main dashboard with statistics
2. **User Management**: Profile, settings
3. **Research Module**: Publication listing and submission
4. **Basic Navigation**: Menu system and breadcrumbs

### **Phase 3: Advanced Features (Week 5-6)**
1. **Organization Module**: Departments and labs
2. **Training Module**: Course catalog and enrollment
3. **Services Module**: Service requests
4. **Content Module**: Announcements and posts

### **Phase 4: Polish & Testing (Week 7-8)**
1. **UI/UX Refinement**: Polish design and interactions
2. **Testing**: Unit tests and integration tests
3. **Performance**: Optimization and lazy loading
4. **Documentation**: User guides and API documentation

## **Testing Strategy**
- **Unit Tests**: Component testing with React Testing Library
- **Integration Tests**: API integration testing
- **E2E Tests**: Cypress for critical user flows
- **Accessibility Tests**: Automated a11y testing

## **API Endpoints Reference**

### **Authentication Endpoints**
```
POST /api/auth/register/          # User registration
POST /api/auth/login/             # User login
POST /api/auth/logout/            # User logout
POST /api/auth/token/refresh/     # Refresh JWT token
GET  /api/auth/users/me/          # Get current user
PUT  /api/auth/users/me/          # Update user profile
POST /api/auth/users/{id}/approve/ # Approve user (admin)
```

### **Research Endpoints**
```
GET  /api/research/publications/           # List publications
POST /api/research/publications/           # Create publication
GET  /api/research/publications/{id}/      # Get publication details
PUT  /api/research/publications/{id}/      # Update publication
DELETE /api/research/publications/{id}/    # Delete publication
POST /api/research/publications/{id}/authors/ # Manage authors
```

### **Organization Endpoints (Public Access)**
```
GET  /api/organization/departments/                    # List departments (public)
POST /api/organization/departments/                    # Create department (admin)
GET  /api/organization/departments/{id}/               # Get department details (public)
GET  /api/organization/departments/{id}/labs/          # Get department labs (public)
GET  /api/organization/labs/                           # List laboratories (public)
POST /api/organization/labs/                           # Create laboratory (admin)
GET  /api/organization/labs/{id}/                      # Get lab details (public)
GET  /api/organization/labs/{id}/researchers/          # Get lab researchers (public)
GET  /api/organization/labs/{id}/head/                 # Get lab head researcher (public)
POST /api/organization/labs/{id}/assign-researcher/    # Assign researcher (admin)
```

### **Training Endpoints**
```
GET  /api/training/courses/                # List courses
POST /api/training/courses/                # Create course
GET  /api/training/courses/{id}/           # Get course details
POST /api/training/courses/{id}/enroll/    # Enroll in course
GET  /api/training/summer-programs/        # List summer programs
POST /api/training/public-services/        # Request public training
```

### **Services Endpoints**
```
GET  /api/services/test-services/          # List available services
POST /api/services/requests/               # Submit service request
GET  /api/services/requests/{id}/          # Get request details
PUT  /api/services/requests/{id}/          # Update request
POST /api/services/requests/{id}/assign-technician/ # Assign technician
```

### **Content Endpoints**
```
GET  /api/content/announcements/                    # List announcements (with full content & attachments)
POST /api/content/announcements/                    # Create announcement
GET  /api/content/announcements/{id}/               # Get announcement details
POST /api/content/announcements/{id}/images/        # Upload announcement images
GET  /api/content/announcements/{id}/images/        # List announcement images
DELETE /api/content/announcements/{id}/images/{id}/ # Delete announcement image
POST /api/content/announcements/{id}/attachments/   # Upload announcement attachments
GET  /api/content/announcements/{id}/attachments/   # List announcement attachments
DELETE /api/content/announcements/{id}/attachments/{id}/ # Delete attachment
GET  /api/content/posts/                            # List posts
POST /api/content/posts/                            # Create post
POST /api/content/posts/{id}/comments/              # Add comment
```

## **Sample Component Implementation**

### **Login Component Example**
```jsx
// src/components/auth/LoginForm.jsx
import React, { useState } from 'react';
import { Form, Input, Button, Alert } from 'antd';
import { useDispatch } from 'react-redux';
import { loginUser } from '../store/slices/authSlice';

const LoginForm = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const dispatch = useDispatch();

  const onFinish = async (values) => {
    setLoading(true);
    setError(null);

    try {
      await dispatch(loginUser(values)).unwrap();
      // Redirect handled by Redux middleware
    } catch (err) {
      setError(err.message || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Form onFinish={onFinish} layout="vertical">
      {error && <Alert message={error} type="error" showIcon />}

      <Form.Item
        name="username"
        label="Username"
        rules={[{ required: true, message: 'Please enter your username' }]}
      >
        <Input size="large" />
      </Form.Item>

      <Form.Item
        name="password"
        label="Password"
        rules={[{ required: true, message: 'Please enter your password' }]}
      >
        <Input.Password size="large" />
      </Form.Item>

      <Form.Item>
        <Button
          type="primary"
          htmlType="submit"
          size="large"
          loading={loading}
          block
        >
          Login
        </Button>
      </Form.Item>
    </Form>
  );
};

export default LoginForm;
```

### **Publication List Component Example**
```jsx
// src/components/research/PublicationList.jsx
import React, { useEffect, useState } from 'react';
import { Table, Tag, Button, Input, Select } from 'antd';
import { useSelector, useDispatch } from 'react-redux';
import { fetchPublications } from '../store/slices/researchSlice';

const PublicationList = () => {
  const dispatch = useDispatch();
  const { publications, loading } = useSelector(state => state.research);
  const [filters, setFilters] = useState({
    search: '',
    status: 'all'
  });

  useEffect(() => {
    dispatch(fetchPublications(filters));
  }, [dispatch, filters]);

  const columns = [
    {
      title: 'Title',
      dataIndex: 'title',
      key: 'title',
      render: (text, record) => (
        <a href={`/publications/${record.id}`}>{text}</a>
      ),
    },
    {
      title: 'Authors',
      dataIndex: 'authors',
      key: 'authors',
      render: (authors) => authors.map(author => author.name).join(', '),
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      render: (status) => {
        const colors = {
          draft: 'default',
          pending: 'processing',
          published: 'success',
          rejected: 'error'
        };
        return <Tag color={colors[status]}>{status.toUpperCase()}</Tag>;
      },
    },
    {
      title: 'Created',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (date) => new Date(date).toLocaleDateString(),
    },
  ];

  return (
    <div>
      <div style={{ marginBottom: 16 }}>
        <Input.Search
          placeholder="Search publications..."
          value={filters.search}
          onChange={(e) => setFilters({...filters, search: e.target.value})}
          style={{ width: 300, marginRight: 16 }}
        />
        <Select
          value={filters.status}
          onChange={(value) => setFilters({...filters, status: value})}
          style={{ width: 120 }}
        >
          <Select.Option value="all">All Status</Select.Option>
          <Select.Option value="draft">Draft</Select.Option>
          <Select.Option value="pending">Pending</Select.Option>
          <Select.Option value="published">Published</Select.Option>
        </Select>
      </div>

      <Table
        columns={columns}
        dataSource={publications}
        loading={loading}
        rowKey="id"
        pagination={{
          pageSize: 10,
          showSizeChanger: true,
          showQuickJumper: true,
        }}
      />
    </div>
  );
};

export default PublicationList;
```

## **Deployment Considerations**
- **Build Optimization**: Code splitting and lazy loading
- **Environment Variables**: Different configs for dev/staging/prod
- **CDN Integration**: Static asset optimization
- **Error Monitoring**: Sentry or similar error tracking
- **Analytics**: User behavior tracking

## **🏢 Departments Navigation Structure**

### **Public Access Organization Pages:**
The platform now provides public access to the organizational structure:

```
Navbar: Departments
├── Department List Page
│   ├── Computer Science Department
│   │   ├── AI Research Lab → Researchers + Head
│   │   ├── Software Engineering Lab → Researchers + Head
│   │   └── Data Science Lab → Researchers + Head
│   ├── Biology Department
│   │   ├── Molecular Biology Lab → Researchers + Head
│   │   └── Genetics Lab → Researchers + Head
│   └── Chemistry Department
│       ├── Organic Chemistry Lab → Researchers + Head
│       └── Analytical Chemistry Lab → Researchers + Head
```

### **Navigation Flow:**
1. **Departments Page** (`/departments`) - List all departments
2. **Department Detail** (`/departments/{id}`) - Show department info + labs
3. **Lab Detail** (`/labs/{id}`) - Show lab info + researchers + head

### **API Endpoints for Departments:**
```typescript
// Public API calls (no authentication required)
const departmentsApi = {
  getDepartments: () => GET('/api/organization/departments/'),
  getDepartment: (id) => GET(`/api/organization/departments/${id}/`),
  getDepartmentLabs: (id) => GET(`/api/organization/departments/${id}/labs/`),
  getLab: (id) => GET(`/api/organization/labs/${id}/`),
  getLabResearchers: (id) => GET(`/api/organization/labs/${id}/researchers/`),
  getLabHead: (id) => GET(`/api/organization/labs/${id}/head/`),
};
```

### **Component Structure:**
```
src/pages/organization/
├── DepartmentsPage.tsx      # List all departments
├── DepartmentDetail.tsx     # Department info + labs
├── LabDetail.tsx           # Lab info + researchers
└── components/
    ├── DepartmentCard.tsx   # Department display card
    ├── LabCard.tsx         # Lab display card
    └── ResearcherCard.tsx  # Researcher profile card
```

## **Getting Started Checklist**
- [ ] Set up React project with TypeScript and Vite
- [ ] Install recommended dependencies (Ant Design, Redux Toolkit, etc.)
- [ ] Configure API client with JWT authentication
- [ ] Implement basic routing structure
- [ ] Create authentication flow (login/register)
- [ ] Build main layout components
- [ ] Implement departments navigation (public access)
- [ ] Add error handling and loading states
- [ ] Set up testing framework
- [ ] Configure deployment pipeline

**Note:** Publications are NOT in public pages - they only appear in researcher profiles when authenticated.

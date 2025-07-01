# Scientific Research Organization Platform - Development Plan

## Project Overview
Full-stack platform with Django REST Framework backend and React frontend for scientific research organization management.

## Current Status: ANALYSIS PHASE
**Last Updated**: 2025-07-01
**Current Focus**: Backend Development with SQLite

---

## Phase 1: Analysis & Planning ⏳

### 1.1 Requirements Analysis ✅
**User Types & Permissions:**
- Admin: Full system control, user approval, CRUD operations
- Moderator: Content creation (announcements, events)
- Researcher: Profile management, publication submission

**Core Features:**
- User registration with admin approval
- Profile management with CV uploads, ORCID integration
- Publication submission and approval workflow
- Department/Lab management with cross-assignments
- Training unit (courses, summer training, public service)
- Special services with pricing and technician assignment
- Announcement system

### 1.2 Technology Stack ✅
**Backend:**
- Django 4.2+ with Django REST Framework
- SQLite (development), PostgreSQL (production ready)
- Django packages: django-cors-headers, Pillow, django-extensions

**Authentication:**
- Custom User model with role-based permissions
- Django's built-in authentication system

### 1.3 App Structure Design ✅
**Proposed Django Apps:**
1. `accounts` - User management, authentication, profiles
2. `research` - Publications, researchers, ORCID integration  
3. `organization` - Departments, labs, organizational structure
4. `training` - Courses, summer training, public service
5. `services` - Special tests, client data, technician assignments
6. `content` - Announcements, posts, general content
7. `core` - Shared utilities, base models, common functionality

---

## Phase 2: Environment Setup ✅

### 2.1 Virtual Environment Setup ✅
- [x] Create Python virtual environment
- [x] Activate virtual environment
- [x] Create requirements.txt with initial packages
- [x] Upgrade pip to latest version

### 2.2 Django Project Initialization ✅
- [x] Install all Django packages from requirements.txt
- [x] Create Django project structure (research_platform)
- [x] Configure settings.py with all apps and DRF
- [x] Create all Django apps (core, accounts, research, organization, training, services, content)
- [x] Setup environment variables (.env file)
- [x] Configure CORS, JWT, and API documentation

---

## Phase 3: Core Backend Development (App by App)

### 3.1 Core App ✅
- [x] Base abstract models (TimeStampedModel)
- [x] Common utilities and mixins
- [x] Shared constants and choices (StatusChoices, PriorityChoices)
- [x] File upload utilities

### 3.2 Accounts App ✅
- [x] Custom User model with roles (Admin, Moderator, Researcher)
- [x] User profile models with CV upload and ORCID
- [x] Admin interface with approval workflow
- [x] Authentication views and serializers (JWT-based)
- [x] Permission classes (role-based access control)
- [x] API endpoints for user management
- [x] User registration with admin approval workflow
- [x] Login/logout with JWT tokens
- [x] User profile management
- [x] Admin user approval system
- [x] API documentation endpoints

### 3.3 Organization App ✅
- [x] Department model with head assignment
- [x] Lab model with department relationships and capacity tracking
- [x] ResearcherAssignment through model (many-to-many with metadata)
- [x] Enhanced admin interface with inlines and capacity visualization
- [x] Complete API serializers with validation
- [x] API views with role-based permissions
- [x] URL patterns and endpoint configuration
- [x] Organization statistics endpoint
- [x] Lab availability checking
- [x] User assignment management

**Progress Update:** Organization app is now fully functional with complete CRUD operations, role-based permissions, and advanced features like capacity tracking and assignment management.

### 3.4 Research App 📋
- [ ] Publication model
- [ ] ORCID integration
- [ ] Publication approval workflow
- [ ] File upload for research documents

### 3.5 Content App 📋
- [ ] Announcement model
- [ ] Post model for events/activities
- [ ] Moderator content creation system

### 3.6 Training App 📋
- [ ] Course model
- [ ] Summer training model
- [ ] Public service model
- [ ] Payment integration preparation

### 3.7 Services App 📋
- [ ] Test service model with pricing
- [ ] Client data model
- [ ] Technician assignment system

---

## Database Design

### Core Entities Identified:
1. **User** (Custom with roles: Admin, Moderator, Researcher)
2. **UserProfile** (CV, ORCID, notes, publications)
3. **Department** (Name, description, head)
4. **Lab** (Name, department, equipment, researchers)
5. **Publication** (Title, authors, status, approval)
6. **Announcement** (Title, content, author, date)
7. **Course** (Name, description, price, instructor)
8. **Service** (Name, description, price, technician)
9. **Client** (Contact info, services used)

### Key Relationships:
- User → UserProfile (One-to-One)
- Department → Lab (One-to-Many)
- Lab ↔ Researcher (Many-to-Many through assignment)
- Researcher → Publication (One-to-Many)
- Service ↔ Technician (Many-to-Many)

---

## Security Considerations
- Role-based permissions with Django groups
- Admin deletion protection (ensure at least one admin exists)
- File upload validation and security
- API rate limiting
- Input validation and sanitization

---

## Next Steps
1. **AWAITING APPROVAL**: Environment setup and requirements.txt creation
2. **AWAITING APPROVAL**: Django project structure and initial apps
3. **AWAITING APPROVAL**: Database model design details

---

## Notes
- Focus on backend completion before frontend
- Each app will be developed and tested independently
- Admin interface will be enhanced for better UX
- API documentation will be generated automatically

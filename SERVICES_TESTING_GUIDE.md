
# Frontend Guide: Testing Services API

This guide provides instructions for the frontend team on how to test the services API.

## Base URL

The base URL for all service-related endpoints is `/api/services/`.

---

## 1. Test Services (`/api/services/test-services/`)

This endpoint manages test services offered by the labs.

### 1.1. List Services

- **Endpoint:** `GET /api/services/test-services/`
- **Description:** Retrieves a list of all available test services.
- **Permissions:** Publicly accessible (with some filtering for unauthenticated users).
- **Query Parameters:**
    - `available_only=true`: Filter for services with `status='active'`.
    - `category=<category_name>`: Filter by service category.
    - `department=<department_id>`: Filter by department ID.
    - `lab=<lab_id>`: Filter by lab ID.
    - `status=<status>`: Filter by service status.
    - `is_featured=true`: Filter for featured services.
    - `is_public=true`: Filter for public services.
    - `search=<term>`: Search for a term in the service name, description, code, or tags.
    - `ordering=<field>`: Order the results by a specific field (e.g., `name`, `-base_price`).
- **Response Body (`TestServiceListSerializer`):**
  ```json
  [
      {
          "id": 1,
          "name": "Service Name",
          "short_description": "A brief description.",
          "service_code": "SVC-001",
          "category": "Category Name",
          "department_name": "Department Name",
          "lab_name": "Lab Name",
          "base_price": "100.00",
          "is_free": false,
          "estimated_duration": "2 hours",
          "status": "active",
          "is_featured": true,
          "is_public": true,
          "is_available": true,
          "is_at_capacity": false,
          "availability_percentage": 80,
          "technician_count": 2,
          "current_requests": 1,
          "max_concurrent_requests": 5
      }
  ]
  ```

### 1.2. Retrieve Service Details

- **Endpoint:** `GET /api/services/test-services/{id}/`
- **Description:** Retrieves the full details of a specific service.
- **Permissions:** Publicly accessible.
- **Response Body (`TestServiceDetailSerializer`):**
  ```json
  {
      "id": 1,
      "name": "Service Name",
      "description": "A detailed description of the service.",
      "short_description": "A brief description.",
      "service_code": "SVC-001",
      "category": "Category Name",
      "department": { ... },
      "lab": { ... },
      "technicians": [ ... ],
      "base_price": "100.00",
      "is_free": false,
      "pricing_structure": "...",
      "estimated_duration": "2 hours",
      "sample_requirements": "...",
      "equipment_used": "...",
      "methodology": "...",
      "max_concurrent_requests": 5,
      "current_requests": 1,
      "required_documents": "...",
      "safety_requirements": "...",
      "status": "active",
      "is_featured": true,
      "is_public": true,
      "contact_email": "contact@example.com",
      "contact_phone": "123-456-7890",
      "featured_image": "/media/...",
      "service_brochure": "/media/...",
      "tags": ["tag1", "tag2"],
      "is_available": true,
      "is_at_capacity": false,
      "availability_percentage": 80,
      "request_count": 10,
      "created_at": "...",
      "updated_at": "..."
  }
  ```

### 1.3. Create a Service

- **Endpoint:** `POST /api/services/test-services/`
- **Description:** Creates a new test service.
- **Permissions:** `IsAdminOrReadOnly`
- **Request Body (`TestServiceCreateUpdateSerializer`):**
  ```json
  {
      "name": "New Service",
      "description": "...",
      "short_description": "...",
      "service_code": "SVC-002",
      "category": "...",
      "department": 1,
      "lab": 1,
      "base_price": "150.00",
      ...
  }
  ```

### 1.4. Update a Service

- **Endpoint:** `PUT /api/services/test-services/{id}/` or `PATCH /api/services/test-services/{id}/`
- **Description:** Updates an existing service.
- **Permissions:** `IsAdminOrReadOnly`
- **Request Body (`TestServiceCreateUpdateSerializer`):**
  ```json
  {
      "name": "Updated Service Name",
      ...
  }
  ```

### 1.5. Delete a Service

- **Endpoint:** `DELETE /api/services/test-services/{id}/`
- **Description:** Deletes a service.
- **Permissions:** `IsAdminOrReadOnly`

### 1.6. Custom Actions

- **Assign Technician:**
    - **Endpoint:** `POST /api/services/test-services/{id}/assign_technician/`
    - **Permissions:** `IsModeratorOrAdmin`
    - **Request Body:**
      ```json
      {
          "technician_id": 1,
          "role": "primary"
      }
      ```

- **Remove Technician:**
    - **Endpoint:** `POST /api/services/test-services/{id}/remove_technician/`
    - **Permissions:** `IsModeratorOrAdmin`
    - **Request Body:**
      ```json
      {
          "technician_id": 1
      }
      ```

- **Statistics:**
    - **Endpoint:** `GET /api/services/test-services/statistics/`
    - **Permissions:** Publicly accessible.

---

## 2. Clients (`/api/services/clients/`)

This endpoint manages clients who request services.

### 2.1. List Clients

- **Endpoint:** `GET /api/services/clients/`
- **Permissions:** `IsModeratorOrAdmin`
- **Query Parameters:** `client_type`, `is_active`, `payment_terms`, `search`, `ordering`.
- **Response Body (`ClientListSerializer`):**
  ```json
  [
      {
          "id": 1,
          "name": "Client Name",
          "organization": "Client Org",
          "client_type": "internal",
          "email": "client@example.com",
          ...
      }
  ]
  ```

### 2.2. Retrieve Client Details

- **Endpoint:** `GET /api/services/clients/{id}/`
- **Permissions:** `IsModeratorOrAdmin`
- **Response Body (`ClientDetailSerializer`):**
  ```json
  {
      "id": 1,
      "name": "Client Name",
      ...
      "recent_requests": [ ... ]
  }
  ```

### 2.3. Create, Update, Delete Client

- **Endpoints:** `POST`, `PUT`, `PATCH`, `DELETE` at `/api/services/clients/{id}/`
- **Permissions:** `IsModeratorOrAdmin`
- **Request Body (`ClientCreateUpdateSerializer`):**
  ```json
  {
      "name": "New Client",
      "organization": "New Org",
      ...
  }
  ```

### 2.4. Custom Actions

- **Statistics:**
    - **Endpoint:** `GET /api/services/clients/statistics/`
    - **Permissions:** `IsModeratorOrAdmin`

---

## 3. Service Requests (`/api/services/requests/`)

This endpoint manages requests for services.

### 3.1. List Service Requests

- **Endpoint:** `GET /api/services/requests/`
- **Permissions:** `IsAuthenticated`
- **Query Parameters:** `service`, `client`, `assigned_technician`, `status`, `priority`, `urgency`, `is_paid`, `search`, `ordering`.
- **Response Body (`ServiceRequestListSerializer`):**
  ```json
  [
      {
          "id": 1,
          "request_id": "SR-2023-001",
          "title": "Request Title",
          ...
      }
  ]
  ```

### 3.2. Retrieve Service Request Details

- **Endpoint:** `GET /api/services/requests/{id}/`
- **Permissions:** `IsAuthenticated`
- **Response Body (`ServiceRequestDetailSerializer`):**
  ```json
  {
      "id": 1,
      "request_id": "SR-2023-001",
      ...
  }
  ```

### 3.3. Create, Update, Delete Service Request

- **Endpoints:** `POST`, `PUT`, `PATCH`, `DELETE` at `/api/services/requests/{id}/`
- **Permissions:** `IsAuthenticated`
- **Request Body (`ServiceRequestCreateUpdateSerializer`):**
  ```json
  {
      "service": 1,
      "client": 1,
      "title": "New Request",
      ...
  }
  ```

### 3.4. Custom Actions

- **Assign Technician:**
    - **Endpoint:** `POST /api/services/requests/{id}/assign_technician/`
    - **Permissions:** `IsModeratorOrAdmin`
    - **Request Body:** `{"technician_id": 1}`

- **Start Request:**
    - **Endpoint:** `POST /api/services/requests/{id}/start_request/`
    - **Permissions:** `IsAuthenticated`

- **Complete Request:**
    - **Endpoint:** `POST /api/services/requests/{id}/complete_request/`
    - **Permissions:** `IsAuthenticated`
    - **Request Body:** `{"final_cost": "120.00"}` (optional)

- **Approve Request:**
    - **Endpoint:** `POST /api/services/requests/{id}/approve_request/`
    - **Permissions:** `IsModeratorOrAdmin`
    - **Request Body:** `{"estimated_cost": "110.00", "review_notes": "..."}` (optional)

- **Reject Request:**
    - **Endpoint:** `POST /api/services/requests/{id}/reject_request/`
    - **Permissions:** `IsModeratorOrAdmin`
    - **Request Body:** `{"review_notes": "..."}` (optional)

- **Statistics:**
    - **Endpoint:** `GET /api/services/requests/statistics/`
    - **Permissions:** `IsAuthenticated`

---

## 4. Technician Assignments (`/api/services/technician-assignments/`)

This endpoint manages the assignment of technicians to services.

### 4.1. List Assignments

- **Endpoint:** `GET /api/services/technician-assignments/`
- **Permissions:** `IsModeratorOrAdmin`
- **Query Parameters:** `service`, `technician`, `role`, `is_active`, `search`, `ordering`.
- **Response Body (`TechnicianAssignmentSerializer`):**
  ```json
  [
      {
          "id": 1,
          "service": 1,
          "service_name": "Service Name",
          "technician": { ... },
          "role": "primary",
          ...
      }
  ]
  ```

### 4.2. Create, Update, Delete Assignment

- **Endpoints:** `POST`, `PUT`, `PATCH`, `DELETE` at `/api/services/technician-assignments/{id}/`
- **Permissions:** `IsModeratorOrAdmin`
- **Request Body (`TechnicianAssignmentCreateUpdateSerializer`):**
  ```json
  {
      "service": 1,
      "technician": 1,
      "role": "primary",
      ...
  }
  ```

### 4.3. Custom Actions

- **Workload Report:**
    - **Endpoint:** `GET /api/services/technician-assignments/workload_report/`
    - **Permissions:** `IsModeratorOrAdmin`


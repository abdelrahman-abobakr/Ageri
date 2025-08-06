# User Profile API Endpoints

This document outlines the API endpoints related to user profiles in the Ageri Research Platform.

## 1. Get/Update Current User's Profile

*   **Endpoint:** `/api/accounts/profile/me/`
*   **HTTP Methods:** `GET`, `PUT`, `PATCH`
*   **Description:** Retrieves or updates the profile of the currently authenticated user. When using `PUT` or `PATCH`, the `Content-Type` should be `multipart/form-data` to support file uploads (for the CV).
*   **Permissions:** `IsOwnerOrAdmin` (Only the user themselves or an admin can access this).

### GET Request

*   **Description:** Retrieves the profile of the currently logged-in user.
*   **Response Body:**

```json
{
    "id": 1,
    "user": 1,
    "bio": "A brief biography.",
    "research_interests": "Quantum physics, machine learning.",
    "orcid_id": "0000-0000-0000-0000",
    "cv_file": "/media/cvs/user_cv.pdf",
    "website": "https://example.com",
    "linkedin": "https://linkedin.com/in/user",
    "google_scholar": "https://scholar.google.com/citations?user=userid",
    "researchgate": "https://researchgate.net/profile/user",
    "is_public": true
}
```

### PUT/PATCH Request

*   **Description:** Updates the profile of the currently logged-in user. `PUT` requires all fields, while `PATCH` allows for partial updates.
*   **Request Body (`multipart/form-data`):**

| Field                | Type    | Description                                         |
| -------------------- | ------- | --------------------------------------------------- |
| `bio`                | string  | A brief biography of the user.                      |
| `research_interests` | string  | The user's research interests.                      |
| `orcid_id`           | string  | The user's ORCID iD.                                |
| `cv_file`            | file    | The user's curriculum vitae (CV) file.              |
| `website`            | string  | The user's personal or professional website.        |
| `linkedin`           | string  | A link to the user's LinkedIn profile.              |
| `google_scholar`     | string  | A link to the user's Google Scholar profile.        |
| `researchgate`       | string  | A link to the user's ResearchGate profile.          |
| `is_public`          | boolean | Whether the user's profile is publicly visible.     |

*   **Success Response (200 OK):**

```json
{
    "message": "Profile updated successfully",
    "profile": {
        // ... updated profile data ...
    }
}
```

## 2. View a Public User Profile

*   **Endpoint:** `/api/accounts/profiles/<id>/`
*   **HTTP Method:** `GET`
*   **Description:** Retrieves the public profile of a specific user.
*   **Permissions:** `IsApprovedUser` (Any approved user can view public profiles).

### GET Request

*   **Description:** Retrieves the public profile of the user with the specified ID. If the profile is private, it will only be visible to the owner or an admin.
*   **Success Response (200 OK):**

```json
{
    "id": 2,
    "user": 2,
    "bio": "Another user's biography.",
    "research_interests": "Data science, bioinformatics.",
    // ... other public profile fields ...
    "is_public": true,
    "user_info": {
        "full_name": "Jane Doe",
        "institution": "Example University",
        "role": "RESEARCHER"
    }
}
```

*   **Error Response (403 Forbidden):**

```json
{
    "error": "This profile is private"
}
```

## 3. List Approved Researchers (Public Directory)

*   **Endpoint:** `/api/accounts/researchers/`
*   **HTTP Method:** `GET`
*   **Description:** Provides a paginated list of all approved researchers with public profiles. This can be used as a public directory.
*   **Permissions:** `IsApprovedUser`
*   **Query Parameters:**
    *   `role`: Filter by user role (e.g., `RESEARCHER`).
    *   `institution`: Filter by institution.
    *   `search`: Search by first name, last name, institution, or research interests.
    *   `ordering`: Order by `date_joined` or `last_name`.

### GET Request

*   **Success Response (200 OK):**

```json
{
    "count": 15,
    "next": "http://localhost:8000/api/accounts/researchers/?page=2",
    "previous": null,
    "results": [
        {
            "id": 2,
            "email": "jane.doe@example.com",
            "first_name": "Jane",
            "last_name": "Doe",
            "institution": "Example University",
            "profile": {
                "research_interests": "Data science, bioinformatics."
            }
        },
        // ... other researchers ...
    ]
}
```

## 4. User Profile Statistics

*   **Endpoint:** `/api/accounts/profile-stats/`
*   **HTTP Method:** `GET`
*   **Description:** Retrieves statistics about user profiles.
*   **Permissions:** `IsAdminUser`

### GET Request

*   **Success Response (200 OK):**

```json
{
    "total_users": 50,
    "approved_users": 45,
    "pending_users": 5,
    "users_by_role": {
        "admin": 2,
        "moderator": 5,
        "researcher": 38
    },
    "profiles_complete": 30,
    "public_profiles": 25
}
```

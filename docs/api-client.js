/**
 * API Client for Scientific Research Organization Platform
 * 
 * This is a JavaScript client library for interacting with the Django REST API.
 * It handles authentication, token management, and provides convenient methods
 * for all API endpoints.
 * 
 * Usage:
 * import ApiClient from './api-client.js';
 * const api = new ApiClient('http://localhost:8000/api');
 * 
 * // Login
 * await api.auth.login('user@example.com', 'password');
 * 
 * // Make authenticated requests
 * const publications = await api.research.getPublications();
 */

class ApiClient {
  constructor(baseURL = 'http://localhost:8000/api') {
    this.baseURL = baseURL.replace(/\/$/, ''); // Remove trailing slash
    this.accessToken = localStorage.getItem('access_token');
    this.refreshToken = localStorage.getItem('refresh_token');
    
    // Initialize endpoint groups
    this.auth = new AuthEndpoints(this);
    this.research = new ResearchEndpoints(this);
    this.organization = new OrganizationEndpoints(this);
    this.content = new ContentEndpoints(this);
    this.training = new TrainingEndpoints(this);
    this.services = new ServicesEndpoints(this);
  }

  /**
   * Make an HTTP request with automatic token handling
   */
  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    // Add authorization header if token exists
    if (this.accessToken && !config.headers.Authorization) {
      config.headers.Authorization = `Bearer ${this.accessToken}`;
    }

    try {
      let response = await fetch(url, config);

      // Handle token refresh on 401
      if (response.status === 401 && this.refreshToken && endpoint !== '/auth/token/refresh/') {
        const refreshed = await this.refreshAccessToken();
        if (refreshed) {
          config.headers.Authorization = `Bearer ${this.accessToken}`;
          response = await fetch(url, config);
        }
      }

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new ApiError(response.status, errorData.detail || 'Request failed', errorData);
      }

      // Handle empty responses
      if (response.status === 204) {
        return null;
      }

      return await response.json();
    } catch (error) {
      if (error instanceof ApiError) {
        throw error;
      }
      throw new ApiError(0, 'Network error', { originalError: error });
    }
  }

  /**
   * Refresh the access token
   */
  async refreshAccessToken() {
    if (!this.refreshToken) {
      return false;
    }

    try {
      const response = await fetch(`${this.baseURL}/auth/token/refresh/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ refresh: this.refreshToken }),
      });

      if (response.ok) {
        const data = await response.json();
        this.setTokens(data.access, this.refreshToken);
        return true;
      }
    } catch (error) {
      console.error('Token refresh failed:', error);
    }

    this.clearTokens();
    return false;
  }

  /**
   * Set authentication tokens
   */
  setTokens(accessToken, refreshToken) {
    this.accessToken = accessToken;
    this.refreshToken = refreshToken;
    localStorage.setItem('access_token', accessToken);
    localStorage.setItem('refresh_token', refreshToken);
  }

  /**
   * Clear authentication tokens
   */
  clearTokens() {
    this.accessToken = null;
    this.refreshToken = null;
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  }

  /**
   * Check if user is authenticated
   */
  isAuthenticated() {
    return !!this.accessToken;
  }
}

/**
 * Custom error class for API errors
 */
class ApiError extends Error {
  constructor(status, message, data = {}) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.data = data;
  }
}

/**
 * Authentication endpoints
 */
class AuthEndpoints {
  constructor(client) {
    this.client = client;
  }

  async login(email, password) {
    const data = await this.client.request('/auth/login/', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
    
    this.client.setTokens(data.access, data.refresh);
    return data;
  }

  async logout() {
    try {
      await this.client.request('/auth/logout/', { method: 'POST' });
    } finally {
      this.client.clearTokens();
    }
  }

  async register(userData) {
    return this.client.request('/auth/register/', {
      method: 'POST',
      body: JSON.stringify(userData),
    });
  }

  async getCurrentUser() {
    return this.client.request('/auth/users/me/');
  }

  async updateProfile(userData) {
    return this.client.request('/auth/users/me/', {
      method: 'PUT',
      body: JSON.stringify(userData),
    });
  }

  async getUsers(params = {}) {
    const query = new URLSearchParams(params).toString();
    return this.client.request(`/auth/users/${query ? '?' + query : ''}`);
  }
}

/**
 * Research endpoints
 */
class ResearchEndpoints {
  constructor(client) {
    this.client = client;
  }

  async getPublications(params = {}) {
    const query = new URLSearchParams(params).toString();
    return this.client.request(`/research/publications/${query ? '?' + query : ''}`);
  }

  async getPublication(id) {
    return this.client.request(`/research/publications/${id}/`);
  }

  async createPublication(data) {
    return this.client.request('/research/publications/', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updatePublication(id, data) {
    return this.client.request(`/research/publications/${id}/`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async deletePublication(id) {
    return this.client.request(`/research/publications/${id}/`, {
      method: 'DELETE',
    });
  }

  async approvePublication(id, reviewData) {
    return this.client.request(`/research/publications/${id}/approve/`, {
      method: 'POST',
      body: JSON.stringify(reviewData),
    });
  }
}

/**
 * Organization endpoints
 */
class OrganizationEndpoints {
  constructor(client) {
    this.client = client;
  }

  async getDepartments(params = {}) {
    const query = new URLSearchParams(params).toString();
    return this.client.request(`/organization/departments/${query ? '?' + query : ''}`);
  }

  async getLabs(params = {}) {
    const query = new URLSearchParams(params).toString();
    return this.client.request(`/organization/labs/${query ? '?' + query : ''}`);
  }

  async getEquipment(params = {}) {
    const query = new URLSearchParams(params).toString();
    return this.client.request(`/organization/equipment/${query ? '?' + query : ''}`);
  }

  async getStaff(params = {}) {
    const query = new URLSearchParams(params).toString();
    return this.client.request(`/organization/staff/${query ? '?' + query : ''}`);
  }
}

/**
 * Content endpoints
 */
class ContentEndpoints {
  constructor(client) {
    this.client = client;
  }

  async getAnnouncements(params = {}) {
    const query = new URLSearchParams(params).toString();
    return this.client.request(`/content/announcements/${query ? '?' + query : ''}`);
  }

  async createAnnouncement(data) {
    return this.client.request('/content/announcements/', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async getPosts(params = {}) {
    const query = new URLSearchParams(params).toString();
    return this.client.request(`/content/posts/${query ? '?' + query : ''}`);
  }

  async createPost(data) {
    return this.client.request('/content/posts/', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }
}

/**
 * Training endpoints
 */
class TrainingEndpoints {
  constructor(client) {
    this.client = client;
  }

  async getCourses(params = {}) {
    const query = new URLSearchParams(params).toString();
    return this.client.request(`/training/courses/${query ? '?' + query : ''}`);
  }

  async getSummerTraining(params = {}) {
    const query = new URLSearchParams(params).toString();
    return this.client.request(`/training/summer-training/${query ? '?' + query : ''}`);
  }

  async getPublicServices(params = {}) {
    const query = new URLSearchParams(params).toString();
    return this.client.request(`/training/public-services/${query ? '?' + query : ''}`);
  }

  async enrollInCourse(courseId, data = {}) {
    return this.client.request('/training/enrollments/', {
      method: 'POST',
      body: JSON.stringify({ course: courseId, ...data }),
    });
  }

  async applyForSummerTraining(programId, data = {}) {
    return this.client.request('/training/applications/', {
      method: 'POST',
      body: JSON.stringify({ program: programId, ...data }),
    });
  }
}

/**
 * Services endpoints
 */
class ServicesEndpoints {
  constructor(client) {
    this.client = client;
  }

  async getTestServices(params = {}) {
    const query = new URLSearchParams(params).toString();
    return this.client.request(`/services/test-services/${query ? '?' + query : ''}`);
  }

  async createServiceRequest(data) {
    return this.client.request('/services/service-requests/', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async getServiceRequests(params = {}) {
    const query = new URLSearchParams(params).toString();
    return this.client.request(`/services/service-requests/${query ? '?' + query : ''}`);
  }

  async getClients(params = {}) {
    const query = new URLSearchParams(params).toString();
    return this.client.request(`/services/clients/${query ? '?' + query : ''}`);
  }
}

// Export for use in modules
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { ApiClient, ApiError };
}

// Export for use in browsers
if (typeof window !== 'undefined') {
  window.ApiClient = ApiClient;
  window.ApiError = ApiError;
}

/**
 * File upload helper
 */
class FileUploadHelper {
  constructor(client) {
    this.client = client;
  }

  async uploadFile(endpoint, file, additionalData = {}) {
    const formData = new FormData();
    formData.append('file', file);

    Object.keys(additionalData).forEach(key => {
      formData.append(key, additionalData[key]);
    });

    return this.client.request(endpoint, {
      method: 'POST',
      headers: {
        // Don't set Content-Type, let browser set it with boundary
        Authorization: `Bearer ${this.client.accessToken}`,
      },
      body: formData,
    });
  }
}

// Add file upload helper to ApiClient
ApiClient.prototype.files = function() {
  return new FileUploadHelper(this);
};

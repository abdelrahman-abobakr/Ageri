/**
 * React Examples for API Integration
 * 
 * These examples show how to integrate the API client with React components
 * using hooks and context for state management.
 */

import React, { createContext, useContext, useState, useEffect } from 'react';
import ApiClient from './api-client.js';

// Initialize API client
const api = new ApiClient(process.env.REACT_APP_API_BASE_URL);

// Authentication Context
const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const initAuth = async () => {
      if (api.isAuthenticated()) {
        try {
          const userData = await api.auth.getCurrentUser();
          setUser(userData);
        } catch (error) {
          console.error('Failed to get user data:', error);
          api.clearTokens();
        }
      }
      setLoading(false);
    };

    initAuth();
  }, []);

  const login = async (email, password) => {
    try {
      const response = await api.auth.login(email, password);
      setUser(response.user);
      return { success: true };
    } catch (error) {
      return { success: false, error: error.message };
    }
  };

  const logout = async () => {
    try {
      await api.auth.logout();
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      setUser(null);
    }
  };

  const value = {
    user,
    login,
    logout,
    loading,
    isAuthenticated: !!user,
    isAdmin: user?.role === 'admin',
    isModerator: user?.role === 'moderator' || user?.role === 'admin',
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

// Custom hook for API data fetching
export const useApiData = (endpoint, dependencies = []) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);
        const result = await api.request(endpoint);
        setData(result);
      } catch (err) {
        setError(err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, dependencies);

  const refetch = () => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);
        const result = await api.request(endpoint);
        setData(result);
      } catch (err) {
        setError(err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  };

  return { data, loading, error, refetch };
};

// Login Component
export const LoginForm = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const { login } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    const result = await login(email, password);
    
    if (!result.success) {
      setError(result.error);
    }
    
    setLoading(false);
  };

  return (
    <form onSubmit={handleSubmit}>
      <div>
        <label htmlFor="email">Email:</label>
        <input
          type="email"
          id="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
      </div>
      <div>
        <label htmlFor="password">Password:</label>
        <input
          type="password"
          id="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />
      </div>
      {error && <div style={{ color: 'red' }}>{error}</div>}
      <button type="submit" disabled={loading}>
        {loading ? 'Logging in...' : 'Login'}
      </button>
    </form>
  );
};

// Publications List Component
export const PublicationsList = () => {
  const [publications, setPublications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  useEffect(() => {
    const fetchPublications = async () => {
      try {
        setLoading(true);
        const response = await api.research.getPublications({ page, page_size: 10 });
        setPublications(response.results);
        setTotalPages(Math.ceil(response.count / 10));
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchPublications();
  }, [page]);

  if (loading) return <div>Loading publications...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div>
      <h2>Publications</h2>
      {publications.map((pub) => (
        <div key={pub.id} style={{ border: '1px solid #ccc', margin: '10px', padding: '10px' }}>
          <h3>{pub.title}</h3>
          <p>{pub.abstract}</p>
          <p>Status: {pub.status}</p>
          <p>Authors: {pub.authors.map(a => `${a.first_name} ${a.last_name}`).join(', ')}</p>
        </div>
      ))}
      
      <div>
        <button 
          onClick={() => setPage(p => Math.max(1, p - 1))} 
          disabled={page === 1}
        >
          Previous
        </button>
        <span> Page {page} of {totalPages} </span>
        <button 
          onClick={() => setPage(p => Math.min(totalPages, p + 1))} 
          disabled={page === totalPages}
        >
          Next
        </button>
      </div>
    </div>
  );
};

// File Upload Component
export const FileUpload = ({ onUpload }) => {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState('');

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
    setError('');
  };

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a file');
      return;
    }

    setUploading(true);
    setError('');

    try {
      const result = await api.files().uploadFile('/research/publications/', file, {
        title: file.name,
      });
      onUpload && onUpload(result);
      setFile(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div>
      <input type="file" onChange={handleFileChange} accept=".pdf,.doc,.docx" />
      <button onClick={handleUpload} disabled={!file || uploading}>
        {uploading ? 'Uploading...' : 'Upload'}
      </button>
      {error && <div style={{ color: 'red' }}>{error}</div>}
    </div>
  );
};

// Protected Route Component
export const ProtectedRoute = ({ children, requiredRole = null }) => {
  const { user, loading } = useAuth();

  if (loading) {
    return <div>Loading...</div>;
  }

  if (!user) {
    return <div>Please log in to access this page.</div>;
  }

  if (requiredRole) {
    const hasPermission = 
      requiredRole === 'admin' && user.role === 'admin' ||
      requiredRole === 'moderator' && ['admin', 'moderator'].includes(user.role) ||
      requiredRole === 'researcher' && ['admin', 'moderator', 'researcher'].includes(user.role);

    if (!hasPermission) {
      return <div>You don't have permission to access this page.</div>;
    }
  }

  return children;
};

// Service Request Form Component
export const ServiceRequestForm = () => {
  const [services, setServices] = useState([]);
  const [selectedService, setSelectedService] = useState('');
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [priority, setPriority] = useState('medium');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    const fetchServices = async () => {
      try {
        const response = await api.services.getTestServices();
        setServices(response.results);
      } catch (err) {
        setError('Failed to load services');
      }
    };

    fetchServices();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess(false);

    try {
      await api.services.createServiceRequest({
        service: selectedService,
        title,
        description,
        priority,
      });
      setSuccess(true);
      setTitle('');
      setDescription('');
      setSelectedService('');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <h2>Request a Service</h2>
      
      <div>
        <label htmlFor="service">Service:</label>
        <select
          id="service"
          value={selectedService}
          onChange={(e) => setSelectedService(e.target.value)}
          required
        >
          <option value="">Select a service</option>
          {services.map((service) => (
            <option key={service.id} value={service.id}>
              {service.name} - ${service.base_price}
            </option>
          ))}
        </select>
      </div>

      <div>
        <label htmlFor="title">Title:</label>
        <input
          type="text"
          id="title"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          required
        />
      </div>

      <div>
        <label htmlFor="description">Description:</label>
        <textarea
          id="description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          required
        />
      </div>

      <div>
        <label htmlFor="priority">Priority:</label>
        <select
          id="priority"
          value={priority}
          onChange={(e) => setPriority(e.target.value)}
        >
          <option value="low">Low</option>
          <option value="medium">Medium</option>
          <option value="high">High</option>
          <option value="urgent">Urgent</option>
        </select>
      </div>

      {error && <div style={{ color: 'red' }}>{error}</div>}
      {success && <div style={{ color: 'green' }}>Service request submitted successfully!</div>}

      <button type="submit" disabled={loading}>
        {loading ? 'Submitting...' : 'Submit Request'}
      </button>
    </form>
  );
};

// Main App Component Example
export const App = () => {
  return (
    <AuthProvider>
      <div>
        <h1>Research Platform</h1>
        <LoginForm />
        <ProtectedRoute>
          <PublicationsList />
          <ServiceRequestForm />
        </ProtectedRoute>
      </div>
    </AuthProvider>
  );
};

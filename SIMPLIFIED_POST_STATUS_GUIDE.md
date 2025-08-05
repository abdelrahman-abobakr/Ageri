# 📊 Simplified Post Status Management Guide

## 🎯 **Overview**

The post status system has been simplified to just **2 statuses** and uses the regular PATCH endpoint for updates. No special approval endpoint needed!

---

## 📋 **Simplified Status System**

### **Available Status Values**
```javascript
const POST_STATUSES = {
  PENDING: 'pending',     // Default - Awaiting review
  PUBLISHED: 'published'  // Live and visible to public
};
```

### **Status Configuration**
```javascript
const statusConfig = {
  pending: {
    label: 'Pending',
    description: 'Awaiting review before publication',
    color: '#fd7e14',
    bgColor: '#fff3cd',
    icon: '⏳',
    isVisible: false
  },
  
  published: {
    label: 'Published',
    description: 'Live and visible to public',
    color: '#28a745',
    bgColor: '#d4edda',
    icon: '🌐',
    isVisible: true
  }
};
```

---

## 🔗 **Status Update API**

### **Endpoint (Same as Regular Updates)**
```
PATCH /api/content/posts/{id}/
```

### **Authentication**
- **Required**: Admin or Moderator permissions
- **Headers**: `Authorization: Bearer ACCESS_TOKEN`

### **Request Examples**
```javascript
// Update status only
{
  "status": "published"
}

// Update status with other fields
{
  "title": "Updated Title",
  "status": "published",
  "is_featured": true
}
```

---

## 🔧 **API Helper Functions**

### **Simplified Status API**
```javascript
// api/postStatus.js
const API_BASE_URL = 'http://127.0.0.1:8000/api/content';

const getAccessToken = () => localStorage.getItem('access_token');

export const postStatusAPI = {
  /**
   * Update post status using regular PATCH endpoint
   * @param {number} postId - Post ID
   * @param {string} status - New status ('pending' or 'published')
   * @param {Object} additionalData - Other fields to update
   * @returns {Promise<Object>} Updated post data
   */
  async updateStatus(postId, status, additionalData = {}) {
    try {
      const updateData = {
        status,
        ...additionalData
      };

      const response = await fetch(`${API_BASE_URL}/posts/${postId}/`, {
        method: 'PATCH',
        headers: {
          'Authorization': `Bearer ${getAccessToken()}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(updateData)
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `Failed to update status to ${status}`);
      }

      return await response.json();
    } catch (error) {
      console.error(`Error updating post status to ${status}:`, error);
      throw error;
    }
  },

  /**
   * Publish a post (set status to published)
   * @param {number} postId - Post ID
   * @returns {Promise<Object>} Updated post data
   */
  async publishPost(postId) {
    return this.updateStatus(postId, 'published');
  },

  /**
   * Unpublish a post (set status to pending)
   * @param {number} postId - Post ID
   * @returns {Promise<Object>} Updated post data
   */
  async unpublishPost(postId) {
    return this.updateStatus(postId, 'pending');
  },

  /**
   * Get posts by status
   * @param {string} status - Status to filter by
   * @returns {Promise<Array>} Posts with specified status
   */
  async getPostsByStatus(status) {
    try {
      const response = await fetch(`${API_BASE_URL}/posts/?status=${status}`, {
        headers: {
          'Authorization': `Bearer ${getAccessToken()}`
        }
      });

      if (!response.ok) {
        throw new Error('Failed to fetch posts');
      }

      const data = await response.json();
      return data.results || [];
    } catch (error) {
      console.error(`Error fetching posts with status ${status}:`, error);
      throw error;
    }
  },

  /**
   * Get pending posts
   * @returns {Promise<Array>} Posts awaiting review
   */
  async getPendingPosts() {
    return this.getPostsByStatus('pending');
  },

  /**
   * Get published posts
   * @returns {Promise<Array>} Published posts
   */
  async getPublishedPosts() {
    return this.getPostsByStatus('published');
  }
};
```

---

## ⚛️ **React Components**

### **1. Simple Status Badge**
```jsx
import React from 'react';

const PostStatusBadge = ({ status, size = 'medium' }) => {
  const config = statusConfig[status] || statusConfig.pending;
  
  const sizeStyles = {
    small: { padding: '2px 8px', fontSize: '10px' },
    medium: { padding: '4px 12px', fontSize: '12px' },
    large: { padding: '6px 16px', fontSize: '14px' }
  };

  return (
    <span 
      className={`post-status-badge status-${status}`}
      style={{
        backgroundColor: config.color,
        color: 'white',
        borderRadius: '12px',
        fontWeight: 'bold',
        display: 'inline-flex',
        alignItems: 'center',
        gap: '4px',
        ...sizeStyles[size]
      }}
      title={config.description}
    >
      <span>{config.icon}</span>
      <span>{config.label}</span>
    </span>
  );
};

export default PostStatusBadge;
```

### **2. Status Toggle Component**
```jsx
import React, { useState } from 'react';
import { postStatusAPI } from '../api/postStatus';
import PostStatusBadge from './PostStatusBadge';

const PostStatusToggle = ({ post, onStatusUpdate, currentUser }) => {
  const [updating, setUpdating] = useState(false);
  const [error, setError] = useState(null);

  const isAdmin = currentUser?.is_admin || currentUser?.is_moderator || false;
  const canUpdateStatus = isAdmin;

  const handleStatusToggle = async () => {
    if (!canUpdateStatus) return;

    const newStatus = post.status === 'published' ? 'pending' : 'published';
    const action = newStatus === 'published' ? 'publish' : 'unpublish';
    
    const confirmed = window.confirm(
      `Are you sure you want to ${action} this post?\n\n` +
      `Title: ${post.title}\n` +
      `Current Status: ${post.status} → New Status: ${newStatus}`
    );
    
    if (!confirmed) return;

    setUpdating(true);
    setError(null);

    try {
      const updatedPost = await postStatusAPI.updateStatus(post.id, newStatus);
      onStatusUpdate(updatedPost);
      
      // Show success message
      alert(`Post ${action}ed successfully!`);
      
    } catch (error) {
      setError(error.message);
      console.error('Status update failed:', error);
    } finally {
      setUpdating(false);
    }
  };

  return (
    <div className="post-status-toggle">
      {/* Current Status Display */}
      <div className="current-status" style={{ marginBottom: '10px' }}>
        <strong>Status: </strong>
        <PostStatusBadge status={post.status} />
      </div>

      {/* Status Toggle Button */}
      {canUpdateStatus && (
        <button
          onClick={handleStatusToggle}
          disabled={updating}
          className={`btn-status-toggle ${post.status}`}
          style={{
            padding: '8px 16px',
            border: 'none',
            borderRadius: '4px',
            cursor: updating ? 'not-allowed' : 'pointer',
            opacity: updating ? 0.6 : 1,
            fontSize: '14px',
            fontWeight: '500',
            backgroundColor: post.status === 'published' ? '#dc3545' : '#28a745',
            color: 'white'
          }}
        >
          {updating ? '⏳ Updating...' : 
           post.status === 'published' ? '📤 Unpublish' : '🌐 Publish'}
        </button>
      )}

      {/* Status Information */}
      <div className="status-info" style={{ 
        marginTop: '10px', 
        fontSize: '14px', 
        color: '#666' 
      }}>
        {post.status === 'pending' && (
          <div>⏳ This post is awaiting review before publication.</div>
        )}
        {post.status === 'published' && (
          <div>🌐 This post is live and visible to users.</div>
        )}
        {!canUpdateStatus && (
          <div>ℹ️ Only admins can change post status.</div>
        )}
      </div>

      {/* Error Display */}
      {error && (
        <div 
          className="error-message"
          style={{
            backgroundColor: '#f8d7da',
            color: '#721c24',
            padding: '8px 12px',
            borderRadius: '4px',
            marginTop: '10px',
            border: '1px solid #f5c6cb',
            fontSize: '14px'
          }}
        >
          <strong>Error:</strong> {error}
        </div>
      )}
    </div>
  );
};

export default PostStatusToggle;
```

### **3. Status Filter Tabs**
```jsx
import React from 'react';

const PostStatusTabs = ({ currentFilter, onFilterChange, statusCounts = {} }) => {
  const tabs = [
    { key: 'all', label: 'All Posts', icon: '📋', color: '#6c757d' },
    { key: 'pending', label: 'Pending', icon: '⏳', color: '#fd7e14' },
    { key: 'published', label: 'Published', icon: '🌐', color: '#28a745' }
  ];

  return (
    <div className="post-status-tabs" style={{ marginBottom: '20px' }}>
      <div className="tab-buttons" style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
        {tabs.map(tab => (
          <button
            key={tab.key}
            onClick={() => onFilterChange(tab.key)}
            className={`tab-btn ${currentFilter === tab.key ? 'active' : ''}`}
            style={{
              padding: '10px 16px',
              border: '2px solid #ddd',
              borderRadius: '6px',
              backgroundColor: currentFilter === tab.key ? tab.color : 'white',
              color: currentFilter === tab.key ? 'white' : '#333',
              cursor: 'pointer',
              fontSize: '14px',
              fontWeight: '500',
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              transition: 'all 0.2s ease'
            }}
          >
            <span>{tab.icon}</span>
            <span>{tab.label}</span>
            {statusCounts[tab.key] !== undefined && (
              <span 
                className="count-badge"
                style={{
                  backgroundColor: currentFilter === tab.key ? 'rgba(255,255,255,0.2)' : tab.color,
                  color: 'white',
                  padding: '2px 6px',
                  borderRadius: '10px',
                  fontSize: '11px',
                  fontWeight: 'bold',
                  minWidth: '18px',
                  textAlign: 'center'
                }}
              >
                {statusCounts[tab.key]}
              </span>
            )}
          </button>
        ))}
      </div>
    </div>
  );
};

export default PostStatusTabs;
```

---

## 🚀 **Usage Examples**

### **1. Simple Status Updates**
```javascript
import { postStatusAPI } from './api/postStatus';

// Publish a post
const publishPost = async (postId) => {
  try {
    const updatedPost = await postStatusAPI.publishPost(postId);
    console.log('Post published:', updatedPost);
    alert('Post published successfully!');
  } catch (error) {
    alert('Failed to publish: ' + error.message);
  }
};

// Unpublish a post
const unpublishPost = async (postId) => {
  try {
    const updatedPost = await postStatusAPI.unpublishPost(postId);
    console.log('Post unpublished:', updatedPost);
    alert('Post unpublished successfully!');
  } catch (error) {
    alert('Failed to unpublish: ' + error.message);
  }
};

// Update status with other fields
const updatePostWithStatus = async (postId) => {
  try {
    const updatedPost = await postStatusAPI.updateStatus(postId, 'published', {
      is_featured: true,
      title: 'Updated Title'
    });
    console.log('Post updated:', updatedPost);
  } catch (error) {
    console.error('Update failed:', error);
  }
};
```

### **2. Filter Posts by Status**
```javascript
// Get pending posts for review
const loadPendingPosts = async () => {
  try {
    const pendingPosts = await postStatusAPI.getPendingPosts();
    console.log(`Found ${pendingPosts.length} posts awaiting review`);
    return pendingPosts;
  } catch (error) {
    console.error('Failed to load pending posts:', error);
  }
};

// Get published posts
const loadPublishedPosts = async () => {
  try {
    const publishedPosts = await postStatusAPI.getPublishedPosts();
    console.log(`Found ${publishedPosts.length} published posts`);
    return publishedPosts;
  } catch (error) {
    console.error('Failed to load published posts:', error);
  }
};
```

### **3. Complete Post Management Component**
```jsx
import React, { useState, useEffect } from 'react';
import { postStatusAPI } from '../api/postStatus';
import PostStatusToggle from './PostStatusToggle';
import PostStatusTabs from './PostStatusTabs';

const SimplePostManager = ({ currentUser }) => {
  const [posts, setPosts] = useState([]);
  const [filteredPosts, setFilteredPosts] = useState([]);
  const [currentFilter, setCurrentFilter] = useState('all');
  const [loading, setLoading] = useState(true);
  const [statusCounts, setStatusCounts] = useState({});

  useEffect(() => {
    fetchPosts();
  }, []);

  useEffect(() => {
    filterPosts();
    calculateStatusCounts();
  }, [posts, currentFilter]);

  const fetchPosts = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/content/posts/', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setPosts(data.results || []);
      }
    } catch (error) {
      console.error('Failed to fetch posts:', error);
    } finally {
      setLoading(false);
    }
  };

  const filterPosts = () => {
    if (currentFilter === 'all') {
      setFilteredPosts(posts);
    } else {
      setFilteredPosts(posts.filter(post => post.status === currentFilter));
    }
  };

  const calculateStatusCounts = () => {
    const counts = {
      all: posts.length,
      pending: posts.filter(p => p.status === 'pending').length,
      published: posts.filter(p => p.status === 'published').length
    };
    setStatusCounts(counts);
  };

  const handleStatusUpdate = (updatedPost) => {
    setPosts(prevPosts =>
      prevPosts.map(post =>
        post.id === updatedPost.id ? updatedPost : post
      )
    );
  };

  if (loading) {
    return <div className="loading">Loading posts...</div>;
  }

  return (
    <div className="simple-post-manager">
      <h2>Post Management</h2>

      {/* Status Filter Tabs */}
      <PostStatusTabs
        currentFilter={currentFilter}
        onFilterChange={setCurrentFilter}
        statusCounts={statusCounts}
      />

      {/* Posts List */}
      <div className="posts-list">
        {filteredPosts.map(post => (
          <div
            key={post.id}
            className="post-item"
            style={{
              border: '1px solid #ddd',
              borderRadius: '8px',
              padding: '20px',
              marginBottom: '15px',
              backgroundColor: 'white'
            }}
          >
            <div className="post-header" style={{ marginBottom: '15px' }}>
              <h3 style={{ margin: '0 0 8px 0' }}>{post.title}</h3>
              <div style={{ fontSize: '12px', color: '#666' }}>
                By {post.author?.full_name} • {new Date(post.created_at).toLocaleDateString()}
              </div>
            </div>

            <div className="post-excerpt" style={{
              marginBottom: '15px',
              color: '#555',
              lineHeight: '1.4'
            }}>
              {post.excerpt || post.content?.substring(0, 150) + '...'}
            </div>

            <PostStatusToggle
              post={post}
              onStatusUpdate={handleStatusUpdate}
              currentUser={currentUser}
            />
          </div>
        ))}
      </div>

      {filteredPosts.length === 0 && (
        <div className="no-posts" style={{
          textAlign: 'center',
          padding: '40px',
          color: '#666'
        }}>
          No {currentFilter === 'all' ? '' : currentFilter} posts found.
        </div>
      )}
    </div>
  );
};

export default SimplePostManager;
```

---

## 🎨 **Simple CSS Styling**

```css
/* Simplified Post Status Styles */
.post-status-badge {
  transition: all 0.2s ease;
}

.post-status-badge:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(0,0,0,0.2);
}

.btn-status-toggle {
  transition: all 0.2s ease;
}

.btn-status-toggle:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(0,0,0,0.2);
}

.btn-status-toggle.published:hover:not(:disabled) {
  background-color: #c82333 !important;
}

.btn-status-toggle.pending:hover:not(:disabled) {
  background-color: #218838 !important;
}

.post-status-tabs .tab-btn:hover:not(.active) {
  background-color: #f8f9fa !important;
  border-color: #007bff !important;
}

.post-item {
  transition: all 0.2s ease;
}

.post-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

/* Responsive Design */
@media (max-width: 768px) {
  .post-status-tabs .tab-buttons {
    flex-direction: column;
  }

  .post-item {
    margin: 10px;
    padding: 15px;
  }
}
```

---

## 🔄 **Status Workflow**

### **Simple 2-Status Flow**
```
📝 Create Post → ⏳ Pending → 🌐 Published
                      ↑           ↓
                      ←-----------←
```

### **Status Transitions**
| From | To | Action | Who Can Do |
|------|----|---------| ----------|
| `pending` | `published` | Publish | Admin/Moderator |
| `published` | `pending` | Unpublish | Admin/Moderator |

---

## 📊 **API Integration Summary**

### **✅ What Changed:**
- **Status field added** to `PostCreateUpdateSerializer`
- **Regular PATCH endpoint** used for status updates
- **Default status** changed to `pending`
- **No special approval endpoint** needed

### **✅ Available Endpoints:**
```javascript
// Update status only
PATCH /api/content/posts/15/
{ "status": "published" }

// Update status with other fields
PATCH /api/content/posts/15/
{
  "status": "published",
  "is_featured": true,
  "title": "Updated Title"
}

// Filter by status
GET /api/content/posts/?status=pending
GET /api/content/posts/?status=published
```

---

## 🎯 **Benefits of Simplified System**

### **✅ Advantages:**
1. **Simpler Logic** - Only 2 statuses to manage
2. **Standard API** - Uses regular PATCH endpoint
3. **Easier Frontend** - Less complex state management
4. **Clear Workflow** - Pending → Published
5. **Flexible Updates** - Can update status with other fields
6. **Better UX** - Simple toggle interface

### **✅ Perfect For:**
- Simple content approval workflows
- Small to medium teams
- Clear publish/unpublish needs
- Standard REST API patterns

---

## 🎯 **Summary**

**The simplified post status system provides:**

✅ **2 Simple Statuses**: `pending` (default) and `published`
✅ **Regular PATCH Endpoint**: No special approval endpoint needed
✅ **Flexible Updates**: Update status with other post fields
✅ **Simple Components**: Toggle buttons and status badges
✅ **Clear Workflow**: Pending → Published → Pending
✅ **Admin Control**: Only admins/moderators can change status
✅ **Easy Integration**: Standard REST API patterns

**Much simpler and cleaner than the complex 7-status system!** 🚀✨
```

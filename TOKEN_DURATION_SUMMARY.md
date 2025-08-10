# Current Token Duration Settings

## 📊 **Current Configuration**

Based on your project settings, here are the current token durations:

### **JWT Token Settings**

| Token Type | Duration | Configuration |
|------------|----------|---------------|
| **Access Token** | **60 minutes (1 hour)** | `JWT_ACCESS_TOKEN_LIFETIME=60` |
| **Refresh Token** | **1440 minutes (24 hours)** | `JWT_REFRESH_TOKEN_LIFETIME=1440` |

### **Session Settings**

| Setting | Value | Note |
|---------|-------|------|
| **Session Cookie Age** | **Default (2 weeks)** | Django default: 1209600 seconds |
| **Session Expire on Browser Close** | **False (default)** | Sessions persist after browser close |

## 🔧 **Configuration Details**

### **JWT Configuration (research_platform/settings.py)**

```python
# JWT Settings
from datetime import timedelta
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=config('JWT_ACCESS_TOKEN_LIFETIME', default=60, cast=int)),
    'REFRESH_TOKEN_LIFETIME': timedelta(minutes=config('JWT_REFRESH_TOKEN_LIFETIME', default=1440, cast=int)),
    'ROTATE_REFRESH_TOKENS': True,
}
```

### **Environment Variables (.env)**

```bash
# JWT Settings
JWT_ACCESS_TOKEN_LIFETIME=60      # 60 minutes = 1 hour
JWT_REFRESH_TOKEN_LIFETIME=1440   # 1440 minutes = 24 hours
```

### **Authentication Classes**

```python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',  # JWT tokens
        'rest_framework.authentication.SessionAuthentication',        # Session cookies
    ],
}
```

## ⏰ **Token Lifecycle**

### **Access Token (1 hour)**
- **Purpose:** API authentication
- **Duration:** 60 minutes
- **Usage:** Sent with each API request
- **Expiration:** Must be refreshed after 1 hour

### **Refresh Token (24 hours)**
- **Purpose:** Renew access tokens
- **Duration:** 1440 minutes (24 hours)
- **Usage:** Used to get new access tokens
- **Rotation:** New refresh token issued with each refresh

### **Session Cookie (2 weeks default)**
- **Purpose:** Web interface authentication
- **Duration:** Django default (2 weeks)
- **Usage:** Browser-based authentication
- **Persistence:** Survives browser restarts

## 🔄 **Token Refresh Process**

```mermaid
graph TD
    A[User Login] --> B[Receive Access Token (1h)]
    B --> C[Receive Refresh Token (24h)]
    C --> D[Use Access Token for API calls]
    D --> E{Access Token Expired?}
    E -->|No| D
    E -->|Yes| F[Use Refresh Token]
    F --> G[Get New Access Token (1h)]
    G --> H[Get New Refresh Token (24h)]
    H --> D
    F --> I{Refresh Token Expired?}
    I -->|Yes| J[User Must Login Again]
    I -->|No| G
```

## 🌐 **API Usage Examples**

### **Login and Token Usage**

```python
import requests

# 1. Login to get tokens
login_response = requests.post('http://localhost:8000/api/accounts/login/', {
    'email': 'user@example.com',
    'password': 'password123'
})

tokens = login_response.json()
access_token = tokens['access']
refresh_token = tokens['refresh']

# 2. Use access token for API calls (valid for 1 hour)
headers = {'Authorization': f'Bearer {access_token}'}
response = requests.get('http://localhost:8000/api/accounts/profile/', headers=headers)

# 3. Refresh token when access token expires
refresh_response = requests.post('http://localhost:8000/api/accounts/token/refresh/', {
    'refresh': refresh_token
})

new_tokens = refresh_response.json()
new_access_token = new_tokens['access']
new_refresh_token = new_tokens['refresh']  # New refresh token due to rotation
```

### **JavaScript/Frontend Usage**

```javascript
// Login and store tokens
async function login(email, password) {
    const response = await fetch('/api/accounts/login/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
    });
    
    const tokens = await response.json();
    
    // Store tokens (valid for 1 hour access, 24 hours refresh)
    localStorage.setItem('access_token', tokens.access);
    localStorage.setItem('refresh_token', tokens.refresh);
    
    return tokens;
}

// Auto-refresh tokens before expiry
setInterval(async () => {
    const refreshToken = localStorage.getItem('refresh_token');
    if (refreshToken) {
        try {
            const response = await fetch('/api/accounts/token/refresh/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ refresh: refreshToken })
            });
            
            const tokens = await response.json();
            localStorage.setItem('access_token', tokens.access);
            localStorage.setItem('refresh_token', tokens.refresh);
        } catch (error) {
            // Refresh failed, redirect to login
            window.location.href = '/login/';
        }
    }
}, 50 * 60 * 1000); // Refresh every 50 minutes (before 1-hour expiry)
```

## ⚙️ **How to Change Token Duration**

### **Method 1: Environment Variables (Recommended)**

Edit `.env` file:
```bash
# Increase access token to 2 hours
JWT_ACCESS_TOKEN_LIFETIME=120

# Increase refresh token to 7 days
JWT_REFRESH_TOKEN_LIFETIME=10080
```

### **Method 2: Direct Settings**

Edit `research_platform/settings.py`:
```python
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=2),      # 2 hours
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),      # 7 days
    'ROTATE_REFRESH_TOKENS': True,
}
```

### **Method 3: Session Duration**

Add to `research_platform/settings.py`:
```python
# Session settings
SESSION_COOKIE_AGE = 60 * 60 * 24 * 7  # 7 days in seconds
SESSION_EXPIRE_AT_BROWSER_CLOSE = False  # Keep sessions after browser close
SESSION_SAVE_EVERY_REQUEST = True        # Extend session on each request
```

## 🔒 **Security Considerations**

### **Current Settings Analysis:**

| Aspect | Current | Security Level | Recommendation |
|--------|---------|----------------|----------------|
| **Access Token** | 1 hour | ✅ Good | Appropriate for most use cases |
| **Refresh Token** | 24 hours | ✅ Good | Reasonable for daily usage |
| **Token Rotation** | ✅ Enabled | ✅ Excellent | Prevents token reuse attacks |
| **Session Duration** | 2 weeks | ⚠️ Long | Consider shortening for sensitive data |

### **Recommendations:**

1. **Keep current JWT settings** - They're well-balanced
2. **Consider shorter sessions** for admin users
3. **Implement automatic logout** on inactivity
4. **Add token blacklisting** for logout functionality

## 📊 **Summary**

### **Current Token Durations:**
- ✅ **Access Token:** 60 minutes (1 hour)
- ✅ **Refresh Token:** 1440 minutes (24 hours)
- ✅ **Session Cookie:** ~2 weeks (Django default)

### **Key Features:**
- ✅ **Token rotation enabled** for security
- ✅ **Dual authentication** (JWT + Session)
- ✅ **Configurable via environment variables**
- ✅ **Reasonable security balance**

Your current token configuration provides a good balance between security and user experience! 🔐

# 🌍 Organization Vision & Message API - Complete Guide

## 📍 **API Endpoint**

```
GET http://localhost:8000/api/organization/settings/
```

**Authentication:** ❌ **No authentication required** (Public endpoint)  
**Method:** `GET`  
**Content-Type:** `application/json`

---

## 📊 **API Response Structure**

### **Current Response (Empty Data):**
```json
{
    "name": "Scientific Research Organization",
    "vision": "",
    "mission": "",
    "about": "",
    "email": "",
    "phone": "",
    "address": "",
    "website": "",
    "facebook": "",
    "twitter": "",
    "linkedin": "",
    "instagram": "",
    "logo": null,
    "banner": null,
    "enable_registration": true
}
```

### **Example Response (With Data):**
```json
{
    "name": "مؤسسة أجري للبحث العلمي",
    "vision": "رؤيتنا أن نكون مركزاً رائداً في البحث العلمي والتطوير التكنولوجي في المنطقة",
    "mission": "مهمتنا تقديم حلول بحثية مبتكرة ومتطورة تخدم المجتمع وتساهم في التنمية المستدامة",
    "about": "نحن مؤسسة بحثية متخصصة تضم نخبة من الباحثين والخبراء في مجالات متعددة من العلوم والتكنولوجيا",
    "email": "info@ageri.org",
    "phone": "+20123456789",
    "address": "القاهرة، جمهورية مصر العربية",
    "website": "https://ageri.org",
    "facebook": "https://facebook.com/ageri",
    "twitter": "https://twitter.com/ageri",
    "linkedin": "https://linkedin.com/company/ageri",
    "instagram": "https://instagram.com/ageri",
    "logo": "http://localhost:8000/media/organization/logo.png",
    "banner": "http://localhost:8000/media/organization/banner.jpg",
    "enable_registration": true
}
```

---

## 🚀 **Frontend Integration Examples**

### **1. Vanilla JavaScript (Fetch API)**

```javascript
// Simple fetch request
async function getOrganizationSettings() {
    try {
        const response = await fetch('http://localhost:8000/api/organization/settings/');
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        // Access vision and message
        console.log('Organization Name:', data.name);
        console.log('Vision:', data.vision);
        console.log('Mission:', data.mission);
        console.log('About:', data.about);
        console.log('Logo URL:', data.logo);
        
        return data;
    } catch (error) {
        console.error('Error fetching organization settings:', error);
        return null;
    }
}

// Usage
getOrganizationSettings().then(settings => {
    if (settings) {
        // Update UI with organization data
        document.getElementById('org-name').textContent = settings.name;
        document.getElementById('org-vision').textContent = settings.vision;
        document.getElementById('org-mission').textContent = settings.mission;
        
        if (settings.logo) {
            document.getElementById('org-logo').src = settings.logo;
        }
    }
});
```

### **2. React Hook Implementation**

```jsx
import { useState, useEffect } from 'react';

// Custom hook for organization settings
export const useOrganizationSettings = () => {
    const [settings, setSettings] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchSettings = async () => {
            try {
                setLoading(true);
                const response = await fetch('http://localhost:8000/api/organization/settings/');
                
                if (!response.ok) {
                    throw new Error(`Failed to fetch: ${response.status}`);
                }
                
                const data = await response.json();
                setSettings(data);
                setError(null);
            } catch (err) {
                setError(err.message);
                setSettings(null);
            } finally {
                setLoading(false);
            }
        };

        fetchSettings();
    }, []);

    return { settings, loading, error };
};

// React component using the hook
const OrganizationHeader = () => {
    const { settings, loading, error } = useOrganizationSettings();

    if (loading) return <div>Loading organization info...</div>;
    if (error) return <div>Error: {error}</div>;
    if (!settings) return <div>No organization data available</div>;

    return (
        <header className="organization-header">
            <div className="container">
                <div className="org-info">
                    {settings.logo && (
                        <img 
                            src={settings.logo} 
                            alt="Organization Logo" 
                            className="org-logo"
                        />
                    )}
                    <div className="org-text">
                        <h1>{settings.name}</h1>
                        {settings.vision && (
                            <p className="org-vision">{settings.vision}</p>
                        )}
                        {settings.mission && (
                            <p className="org-mission">{settings.mission}</p>
                        )}
                    </div>
                </div>
            </div>
        </header>
    );
};
```

### **3. Axios Implementation**

```javascript
import axios from 'axios';

// Create axios instance
const api = axios.create({
    baseURL: 'http://localhost:8000/api',
    headers: {
        'Content-Type': 'application/json',
    }
});

// Get organization settings
export const getOrganizationSettings = async () => {
    try {
        const response = await api.get('/organization/settings/');
        return response.data;
    } catch (error) {
        console.error('Error fetching organization settings:', error);
        throw error;
    }
};

// Usage with async/await
async function displayOrganizationInfo() {
    try {
        const settings = await getOrganizationSettings();
        
        // Update page title
        document.title = settings.name;
        
        // Update meta description
        const metaDesc = document.querySelector('meta[name="description"]');
        if (metaDesc && settings.about) {
            metaDesc.setAttribute('content', settings.about);
        }
        
        // Update UI elements
        updateUI(settings);
        
    } catch (error) {
        console.error('Failed to load organization settings:', error);
    }
}

function updateUI(settings) {
    // Update various UI elements
    const elements = {
        'org-name': settings.name,
        'org-vision': settings.vision,
        'org-mission': settings.mission,
        'org-about': settings.about,
        'org-email': settings.email,
        'org-phone': settings.phone,
        'org-address': settings.address
    };
    
    Object.entries(elements).forEach(([id, value]) => {
        const element = document.getElementById(id);
        if (element && value) {
            element.textContent = value;
        }
    });
    
    // Update logo
    if (settings.logo) {
        const logoElements = document.querySelectorAll('.org-logo');
        logoElements.forEach(img => {
            img.src = settings.logo;
            img.alt = `${settings.name} Logo`;
        });
    }
    
    // Update banner
    if (settings.banner) {
        const bannerElements = document.querySelectorAll('.org-banner');
        bannerElements.forEach(img => {
            img.src = settings.banner;
            img.alt = `${settings.name} Banner`;
        });
    }
}
```

### **4. Vue.js Implementation**

```vue
<template>
  <div class="organization-info">
    <div v-if="loading" class="loading">
      Loading organization information...
    </div>
    
    <div v-else-if="error" class="error">
      Error: {{ error }}
    </div>
    
    <div v-else-if="settings" class="org-content">
      <div class="org-header">
        <img 
          v-if="settings.logo" 
          :src="settings.logo" 
          :alt="settings.name + ' Logo'"
          class="org-logo"
        />
        <h1>{{ settings.name }}</h1>
      </div>
      
      <div v-if="settings.vision" class="org-vision">
        <h3>Our Vision</h3>
        <p>{{ settings.vision }}</p>
      </div>
      
      <div v-if="settings.mission" class="org-mission">
        <h3>Our Mission</h3>
        <p>{{ settings.mission }}</p>
      </div>
      
      <div v-if="settings.about" class="org-about">
        <h3>About Us</h3>
        <p>{{ settings.about }}</p>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'OrganizationInfo',
  data() {
    return {
      settings: null,
      loading: true,
      error: null
    };
  },
  async mounted() {
    await this.fetchOrganizationSettings();
  },
  methods: {
    async fetchOrganizationSettings() {
      try {
        this.loading = true;
        const response = await fetch('http://localhost:8000/api/organization/settings/');
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        this.settings = await response.json();
        this.error = null;
      } catch (error) {
        this.error = error.message;
        this.settings = null;
      } finally {
        this.loading = false;
      }
    }
  }
};
</script>
```

---

## 🎯 **Key Points for Frontend Integration**

### **✅ What You Get:**
- **Organization Name** - `data.name`
- **Vision Statement** - `data.vision`
- **Mission Statement** - `data.mission`
- **About Description** - `data.about`
- **Contact Info** - `data.email`, `data.phone`, `data.address`
- **Social Media** - `data.website`, `data.facebook`, `data.twitter`, etc.
- **Media Files** - `data.logo`, `data.banner` (full URLs)
- **Settings** - `data.enable_registration`

### **✅ Best Practices:**
1. **Error Handling** - Always handle network errors and empty responses
2. **Loading States** - Show loading indicators while fetching
3. **Fallback Content** - Provide default content if data is empty
4. **Caching** - Consider caching the response (it doesn't change often)
5. **SEO** - Use the data to update page title and meta tags

### **✅ Common Use Cases:**
- **Website Header** - Display organization name and logo
- **About Page** - Show vision, mission, and about content
- **Footer** - Display contact information and social media links
- **Hero Section** - Use banner image and vision statement
- **Meta Tags** - Update page title and description for SEO

---

## 🚀 **Quick Test**

You can test the API right now:

```bash
curl -X GET "http://localhost:8000/api/organization/settings/" \
     -H "Accept: application/json"
```

Or open in browser: `http://localhost:8000/api/organization/settings/`

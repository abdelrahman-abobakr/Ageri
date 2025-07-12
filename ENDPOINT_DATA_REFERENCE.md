# Vision/Mission Image Upload - Endpoint & Data Reference

## 🌐 API Endpoint

**Base URL**: `/api/organization/settings/`

## 📊 HTTP Methods & Data

### 1. GET Request (Public Access)
**URL**: `GET /api/organization/settings/`
**Authentication**: None required (Public endpoint)
**Content-Type**: `application/json`

#### Response Data Structure:
```json
{
    "id": 1,
    "name": "Scientific Research Organization",
    "vision": "To be a leading research institution driving innovation and scientific excellence by 2030.",
    "vision_image": "http://localhost:8000/media/organization/vision_2030.png",
    "mission": "Our mission is to advance knowledge through cutting-edge research, foster collaboration, and train the next generation of scientists.",
    "mission_image": "http://localhost:8000/media/organization/mission_statement.png",
    "about": "We are a premier research institution...",
    "email": "contact@research.org",
    "phone": "+1-555-0123",
    "address": "123 Research Blvd, Science City, SC 12345",
    "website": "https://research.org",
    "facebook": "https://facebook.com/research",
    "twitter": "https://twitter.com/research",
    "linkedin": "https://linkedin.com/company/research",
    "instagram": "https://instagram.com/research",
    "logo": "http://localhost:8000/media/organization/logo.png",
    "banner": "http://localhost:8000/media/organization/banner.jpg",
    "enable_registration": true,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-07-12T14:45:00Z"
}
```

### 2. PUT Request (Admin Only)
**URL**: `PUT /api/organization/settings/`
**Authentication**: Required (Admin JWT token)
**Content-Type**: `multipart/form-data`

#### Request Data Structure:
```javascript
// FormData object
const formData = new FormData();
formData.append('name', 'Updated Organization Name');
formData.append('vision', 'Our updated vision statement');
formData.append('vision_image', visionImageFile); // File object
formData.append('mission', 'Our updated mission statement');
formData.append('mission_image', missionImageFile); // File object
formData.append('about', 'Updated about text');
formData.append('email', 'newemail@research.org');
// ... other fields
```

#### Response Data Structure:
Same as GET response with updated values.

## 🔧 Field Details

### New Image Fields:
| Field | Type | Description | Validation |
|-------|------|-------------|------------|
| `vision_image` | ImageField | Image for vision statement | JPG, JPEG, PNG only |
| `mission_image` | ImageField | Image for mission statement | JPG, JPEG, PNG only |

### Image Field Behavior:
- **When empty**: Returns `null`
- **When set**: Returns full URL to the image
- **File storage**: Stored in `media/organization/` directory
- **File naming**: Django auto-generates unique names

## 📝 Example API Calls

### JavaScript Fetch Examples:

#### Get Current Settings:
```javascript
const response = await fetch('/api/organization/settings/');
const settings = await response.json();

console.log('Vision:', settings.vision);
console.log('Vision Image URL:', settings.vision_image);
console.log('Mission:', settings.mission);
console.log('Mission Image URL:', settings.mission_image);
```

#### Update Settings with Images:
```javascript
const formData = new FormData();
formData.append('vision', 'New vision statement');
formData.append('mission', 'New mission statement');

// Add image files
const visionImageInput = document.getElementById('vision_image');
const missionImageInput = document.getElementById('mission_image');

if (visionImageInput.files[0]) {
    formData.append('vision_image', visionImageInput.files[0]);
}
if (missionImageInput.files[0]) {
    formData.append('mission_image', missionImageInput.files[0]);
}

const response = await fetch('/api/organization/settings/', {
    method: 'PUT',
    headers: {
        'Authorization': 'Bearer ' + adminToken
    },
    body: formData
});

const updatedSettings = await response.json();
```

### cURL Examples:

#### Get Settings:
```bash
curl -X GET http://localhost:8000/api/organization/settings/
```

#### Update with Images:
```bash
curl -X PUT http://localhost:8000/api/organization/settings/ \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -F "vision=Our new vision for the future" \
  -F "vision_image=@/path/to/vision.jpg" \
  -F "mission=Our updated mission statement" \
  -F "mission_image=@/path/to/mission.png"
```

### Python Requests Examples:

#### Get Settings:
```python
import requests

response = requests.get('http://localhost:8000/api/organization/settings/')
settings = response.json()

print(f"Vision: {settings['vision']}")
print(f"Vision Image: {settings['vision_image']}")
print(f"Mission: {settings['mission']}")
print(f"Mission Image: {settings['mission_image']}")
```

#### Update with Images:
```python
import requests

# Prepare data
data = {
    'vision': 'New vision statement',
    'mission': 'New mission statement'
}

# Prepare files
files = {}
with open('vision.jpg', 'rb') as f:
    files['vision_image'] = f
    with open('mission.png', 'rb') as f2:
        files['mission_image'] = f2
        
        response = requests.put(
            'http://localhost:8000/api/organization/settings/',
            headers={'Authorization': 'Bearer YOUR_ADMIN_TOKEN'},
            data=data,
            files=files
        )

updated_settings = response.json()
```

## 🔒 Authentication & Permissions

### GET Request:
- **Access**: Public (no authentication required)
- **Returns**: All public fields including image URLs

### PUT Request:
- **Access**: Admin users only
- **Authentication**: JWT token required
- **Header**: `Authorization: Bearer <token>`

### Error Responses:

#### 401 Unauthorized (PUT without token):
```json
{
    "detail": "Authentication credentials were not provided."
}
```

#### 403 Forbidden (PUT with non-admin token):
```json
{
    "detail": "You do not have permission to perform this action."
}
```

#### 400 Bad Request (Invalid data):
```json
{
    "vision_image": ["File extension 'txt' is not allowed. Allowed extensions are: jpg, jpeg, png."]
}
```

## 📱 Frontend Integration Examples

### React Hook:
```javascript
const useOrganizationSettings = () => {
    const [settings, setSettings] = useState(null);
    const [loading, setLoading] = useState(true);
    
    useEffect(() => {
        fetch('/api/organization/settings/')
            .then(res => res.json())
            .then(data => {
                setSettings(data);
                setLoading(false);
            });
    }, []);
    
    const updateSettings = async (formData) => {
        const response = await fetch('/api/organization/settings/', {
            method: 'PUT',
            headers: {
                'Authorization': `Bearer ${getAdminToken()}`
            },
            body: formData
        });
        
        if (response.ok) {
            const updated = await response.json();
            setSettings(updated);
            return updated;
        }
        throw new Error('Update failed');
    };
    
    return { settings, loading, updateSettings };
};
```

### Vue Composable:
```javascript
import { ref, onMounted } from 'vue';

export function useOrganizationSettings() {
    const settings = ref(null);
    const loading = ref(true);
    
    const loadSettings = async () => {
        try {
            const response = await fetch('/api/organization/settings/');
            settings.value = await response.json();
        } finally {
            loading.value = false;
        }
    };
    
    const updateSettings = async (formData) => {
        const response = await fetch('/api/organization/settings/', {
            method: 'PUT',
            headers: {
                'Authorization': `Bearer ${getAdminToken()}`
            },
            body: formData
        });
        
        if (response.ok) {
            settings.value = await response.json();
        }
    };
    
    onMounted(loadSettings);
    
    return { settings, loading, updateSettings };
}
```

## 🧪 Testing the Endpoint

### Using the Test File:
The `services/tests.py` file contains comprehensive tests:

```python
# Test API with images
class OrganizationSettingsAPIImageTest(APITestCase):
    def test_organization_settings_api_get_with_images(self):
        # Tests GET endpoint with image data
        
    def test_organization_settings_api_update_with_images(self):
        # Tests PUT endpoint with image uploads
```

### Manual Testing:
1. Open `api_test_page.html` in browser
2. Test GET endpoint (loads current settings)
3. Test PUT endpoint (upload images with admin token)

## 📋 Data Validation

### Image File Validation:
- **Allowed formats**: JPG, JPEG, PNG
- **File size**: Configurable (default Django limits apply)
- **Required**: No (images are optional)

### Text Field Validation:
- **vision**: Optional text field
- **mission**: Optional text field
- **Max length**: No specific limit (TextField)

This endpoint provides a complete solution for managing organization vision and mission statements with optional image support.

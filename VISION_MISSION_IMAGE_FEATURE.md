# Vision and Mission Image Upload Feature

## 🎯 Overview

Added the ability to upload pictures/images for organization vision and mission statements in the research platform. This feature allows administrators to enhance their vision and mission statements with visual content.

## ✨ Features Added

### 1. Database Schema Updates
- **`vision_image`** field in `OrganizationSettings` model
- **`mission_image`** field in `OrganizationSettings` model
- Both fields support JPG, JPEG, and PNG formats
- Images are stored in the `organization/` media directory

### 2. API Enhancements
- **GET** `/api/organization/settings/` - Now includes `vision_image` and `mission_image` URLs
- **PUT** `/api/organization/settings/` - Supports multipart form data for image uploads
- Public access for reading, admin access required for updates
- Proper validation for image file types

### 3. Admin Dashboard Updates
- Enhanced organization settings page with image upload fields
- Side-by-side layout for text and image fields
- Visual feedback showing current uploaded images
- File type validation and user-friendly interface

### 4. Comprehensive Testing
- Model-level tests for image upload functionality
- API tests for image upload and retrieval
- Validation tests for file types
- Permission tests for admin-only updates

## 🔧 Technical Implementation

### Model Changes
```python
# organization/models.py
class OrganizationSettings(TimeStampedModel):
    vision = models.TextField(blank=True, help_text="Organization vision statement")
    vision_image = models.ImageField(
        upload_to=upload_to_organization,
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])],
        help_text="Vision statement image (JPG, PNG)"
    )
    
    mission = models.TextField(blank=True, help_text="Organization mission statement")
    mission_image = models.ImageField(
        upload_to=upload_to_organization,
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])],
        help_text="Mission statement image (JPG, PNG)"
    )
```

### API Serializer Updates
```python
# organization/serializers.py
class OrganizationSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrganizationSettings
        fields = [
            'id', 'name', 'vision', 'vision_image', 'mission', 'mission_image', 
            'about', 'email', 'phone', 'address', 'website', 'facebook', 
            'twitter', 'linkedin', 'instagram', 'logo', 'banner', 
            'enable_registration', 'require_approval', 'maintenance_mode', 
            'maintenance_message', 'created_at', 'updated_at'
        ]
```

### Dashboard Template Updates
```html
<!-- Enhanced Vision & Mission section -->
<div class="settings-section">
    <h3>Vision & Mission</h3>
    <div class="row">
        <div class="col-md-6">
            <label for="vision">Vision Statement</label>
            <textarea class="form-control" id="vision" name="vision" rows="3">{{ settings.vision }}</textarea>
        </div>
        <div class="col-md-6">
            <label for="vision_image">Vision Image</label>
            <input type="file" class="form-control" id="vision_image" name="vision_image" 
                   accept="image/jpeg,image/jpg,image/png">
            {% if settings.vision_image %}
                <small class="text-muted">
                    Current: <a href="{{ settings.vision_image.url }}" target="_blank">{{ settings.vision_image.name }}</a>
                </small>
            {% endif %}
        </div>
    </div>
    <!-- Similar layout for mission -->
</div>
```

## 🚀 Usage Examples

### 1. API Usage (JavaScript)
```javascript
// Get organization settings (public)
const response = await fetch('/api/organization/settings/');
const settings = await response.json();
console.log(settings.vision_image); // URL to vision image
console.log(settings.mission_image); // URL to mission image

// Update settings with images (admin only)
const formData = new FormData();
formData.append('vision', 'Our new vision statement');
formData.append('vision_image', visionImageFile);
formData.append('mission', 'Our new mission statement');
formData.append('mission_image', missionImageFile);

await fetch('/api/organization/settings/', {
    method: 'PUT',
    headers: {
        'Authorization': 'Bearer ' + adminToken
    },
    body: formData
});
```

### 2. Django Model Usage
```python
from organization.models import OrganizationSettings

# Get settings
settings = OrganizationSettings.get_settings()

# Update with images
settings.vision = "Our vision for the future"
settings.vision_image = vision_image_file
settings.mission = "Our mission statement"
settings.mission_image = mission_image_file
settings.save()

# Access image URLs
if settings.vision_image:
    vision_image_url = settings.vision_image.url
if settings.mission_image:
    mission_image_url = settings.mission_image.url
```

### 3. Admin Dashboard
1. Navigate to `/dashboard/organization-settings/`
2. Scroll to "Vision & Mission" section
3. Enter text in vision/mission fields
4. Upload images using the file input fields
5. Click "Save Settings"

## 📁 File Structure
```
organization/
├── models.py              # Added vision_image and mission_image fields
├── serializers.py         # Updated serializers to include image fields
├── admin.py              # Updated admin interface
├── views.py              # API views (no changes needed)
├── migrations/
│   └── 0003_organizationsettings_mission_image_and_more.py
└── ...

dashboard/
├── views.py              # Updated to handle image uploads
├── templates/dashboard/
│   └── organization_settings.html  # Enhanced with image upload fields
└── ...

services/
└── tests.py              # Added comprehensive tests for image functionality
```

## 🧪 Testing

Run the tests to verify functionality:
```bash
# Test model functionality
python manage.py test services.tests.OrganizationSettingsImageTest

# Test API functionality
python manage.py test services.tests.OrganizationSettingsAPIImageTest

# Run demo script
python vision_image_demo.py
```

## 🔒 Security & Validation

- **File Type Validation**: Only JPG, JPEG, and PNG files are allowed
- **Permission Control**: Only admin users can upload/update images
- **File Storage**: Images are stored securely in the media directory
- **API Security**: Proper authentication and authorization checks

## 🌐 Frontend Integration

The API now returns image URLs that can be used directly in frontend applications:

```json
{
    "name": "Scientific Research Organization",
    "vision": "To be a leading research institution...",
    "vision_image": "http://localhost:8000/media/organization/vision_2030.png",
    "mission": "Our mission is to advance knowledge...",
    "mission_image": "http://localhost:8000/media/organization/mission_statement.png",
    "logo": "http://localhost:8000/media/organization/logo.png",
    "banner": "http://localhost:8000/media/organization/banner.png"
}
```

## 📝 Notes

- Images are optional - vision and mission can still be text-only
- Existing vision and mission text functionality remains unchanged
- Images are automatically validated for file type and size
- The feature is fully backward compatible
- All changes are covered by comprehensive tests

This feature enhances the visual appeal of the organization's vision and mission statements while maintaining the existing text-based functionality.

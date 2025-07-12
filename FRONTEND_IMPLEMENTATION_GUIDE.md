# Frontend Implementation Guide for Vision/Mission Images

## 🎯 Quick Answer: What You Need to Do

**The good news**: Most of the work is already done! The backend changes are complete and the Django template is already updated.

**What's working right now**:
- ✅ Database fields added (`vision_image`, `mission_image`)
- ✅ API endpoints updated to include image fields
- ✅ Django admin template updated with image upload fields
- ✅ Django view handles file uploads automatically
- ✅ All tests passing

**What you need to do**: Choose your frontend approach and optionally add enhancements.

## 🚀 Option 1: Use What's Already There (Recommended)

### Current Status
The Django template at `/dashboard/organization-settings/` already includes:

```html
<!-- Vision & Mission section with image uploads -->
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
<!-- Similar for mission -->
```

### How to Test Right Now
1. Go to `/dashboard/organization-settings/`
2. You'll see the new image upload fields
3. Upload JPG/PNG images for vision and mission
4. Click "Save Settings"
5. Images are automatically saved and displayed

**This works immediately with no additional frontend changes needed!**

## 🎨 Option 2: Add JavaScript Enhancements (Optional)

I've created an enhanced JavaScript file that adds:
- Image preview before upload
- File validation
- AJAX form submission
- Better user experience

### Files Created:
- `dashboard/static/dashboard/js/organization-settings.js` - Enhanced JavaScript
- Template already updated to include this script

### Features Added:
- **Image Preview**: See images before uploading
- **File Validation**: Automatic validation of file types and sizes
- **AJAX Submission**: No page reload when saving
- **Better UX**: Loading states, notifications, error handling

## 🌐 Option 3: API Integration for Custom Frontend

If you're building a custom frontend (React, Vue, etc.), use the API:

### API Endpoints:
```javascript
// Get organization settings (public)
GET /api/organization/settings/
// Response includes vision_image and mission_image URLs

// Update settings (admin only)
PUT /api/organization/settings/
// Send multipart/form-data with image files
```

### Example API Usage:
```javascript
// Load current settings
const response = await fetch('/api/organization/settings/');
const settings = await response.json();
console.log(settings.vision_image); // Image URL
console.log(settings.mission_image); // Image URL

// Update with images
const formData = new FormData();
formData.append('vision', 'New vision text');
formData.append('vision_image', imageFile);
formData.append('mission', 'New mission text');
formData.append('mission_image', imageFile);

await fetch('/api/organization/settings/', {
    method: 'PUT',
    headers: {
        'Authorization': 'Bearer ' + adminToken
    },
    body: formData
});
```

## 📱 Frontend Framework Examples

### React Component:
```jsx
const [settings, setSettings] = useState({});
const [visionImage, setVisionImage] = useState(null);
const [missionImage, setMissionImage] = useState(null);

// Load settings
useEffect(() => {
    fetch('/api/organization/settings/')
        .then(res => res.json())
        .then(setSettings);
}, []);

// Update settings
const handleSubmit = async (e) => {
    e.preventDefault();
    const formData = new FormData();
    formData.append('vision', settings.vision);
    formData.append('mission', settings.mission);
    if (visionImage) formData.append('vision_image', visionImage);
    if (missionImage) formData.append('mission_image', missionImage);
    
    await fetch('/api/organization/settings/', {
        method: 'PUT',
        body: formData
    });
};

return (
    <form onSubmit={handleSubmit}>
        <textarea 
            value={settings.vision || ''} 
            onChange={(e) => setSettings({...settings, vision: e.target.value})}
        />
        <input 
            type="file" 
            onChange={(e) => setVisionImage(e.target.files[0])}
            accept="image/*"
        />
        {settings.vision_image && (
            <img src={settings.vision_image} alt="Current vision" />
        )}
        {/* Similar for mission */}
        <button type="submit">Save</button>
    </form>
);
```

### Vue Component:
```vue
<template>
    <form @submit.prevent="updateSettings">
        <textarea v-model="settings.vision"></textarea>
        <input type="file" @change="onVisionImageChange" accept="image/*">
        <img v-if="settings.vision_image" :src="settings.vision_image" alt="Current vision">
        
        <textarea v-model="settings.mission"></textarea>
        <input type="file" @change="onMissionImageChange" accept="image/*">
        <img v-if="settings.mission_image" :src="settings.mission_image" alt="Current mission">
        
        <button type="submit">Save Settings</button>
    </form>
</template>

<script>
export default {
    data() {
        return {
            settings: {},
            visionImage: null,
            missionImage: null
        }
    },
    async mounted() {
        const response = await fetch('/api/organization/settings/');
        this.settings = await response.json();
    },
    methods: {
        onVisionImageChange(e) {
            this.visionImage = e.target.files[0];
        },
        onMissionImageChange(e) {
            this.missionImage = e.target.files[0];
        },
        async updateSettings() {
            const formData = new FormData();
            formData.append('vision', this.settings.vision);
            formData.append('mission', this.settings.mission);
            if (this.visionImage) formData.append('vision_image', this.visionImage);
            if (this.missionImage) formData.append('mission_image', this.missionImage);
            
            await fetch('/api/organization/settings/', {
                method: 'PUT',
                body: formData
            });
        }
    }
}
</script>
```

## 🔧 Testing Your Implementation

### 1. Test the Django Template (Already Working)
- Visit: `http://localhost:8000/dashboard/organization-settings/`
- Upload images and save
- Check that images appear in the form

### 2. Test the API
- Use the provided `api_test_page.html`
- Or use curl:
```bash
# Get settings
curl http://localhost:8000/api/organization/settings/

# Update with images (need admin token)
curl -X PUT http://localhost:8000/api/organization/settings/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "vision=New vision" \
  -F "vision_image=@image.jpg"
```

### 3. Test JavaScript Enhancements
- The enhanced JavaScript is automatically included
- Upload images to see preview functionality
- Form submission uses AJAX with loading states

## 📁 File Structure Summary

```
dashboard/
├── templates/dashboard/
│   └── organization_settings.html     # ✅ Updated with image fields
├── static/dashboard/js/
│   └── organization-settings.js       # ✅ New: Enhanced JavaScript
└── views.py                          # ✅ Updated to handle image uploads

organization/
├── models.py                         # ✅ Added vision_image, mission_image
├── serializers.py                    # ✅ Updated to include image fields
├── admin.py                          # ✅ Updated admin interface
└── migrations/
    └── 0003_*.py                     # ✅ Database migration applied

# Testing files
├── api_test_page.html                # ✅ New: API testing page
├── frontend_admin_integration.md     # ✅ New: Integration guide
└── FRONTEND_IMPLEMENTATION_GUIDE.md  # ✅ New: This guide
```

## 🎯 Recommended Next Steps

1. **Test the current implementation**: Visit `/dashboard/organization-settings/` and try uploading images
2. **Choose your approach**: 
   - Keep the Django template (works now)
   - Add JavaScript enhancements (better UX)
   - Build custom frontend with API (most flexible)
3. **Customize styling**: Adjust CSS to match your design
4. **Add validation**: Client-side validation for better UX

## 🔒 Security Notes

- Only admin users can upload/update images
- File type validation (JPG, JPEG, PNG only)
- File size limits can be configured
- Images stored securely in media directory
- API requires proper authentication for updates

The implementation is complete and ready to use! Choose the approach that best fits your current frontend architecture.

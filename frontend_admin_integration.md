# Frontend Admin Dashboard Integration Guide

## 🎯 Overview

This guide shows you how to handle the new vision and mission image upload functionality in your frontend admin dashboard. You have several options depending on your frontend architecture.

## 🔧 Option 1: Enhanced Django Template (Recommended for existing setup)

The Django template has already been updated to include the image upload fields. Here's how it works:

### Current Template Structure
```html
<!-- Vision & Mission Section -->
<div class="settings-section">
    <h3>Vision & Mission</h3>
    <div class="row">
        <div class="col-md-6">
            <div class="form-group">
                <label for="vision">Vision Statement</label>
                <textarea class="form-control" id="vision" name="vision" rows="3">{{ settings.vision }}</textarea>
            </div>
        </div>
        <div class="col-md-6">
            <div class="form-group">
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
    </div>
    <!-- Similar structure for mission -->
</div>
```

### Form Submission
The form already uses `enctype="multipart/form-data"` and the Django view handles the file uploads automatically.

## 🚀 Option 2: JavaScript/AJAX Enhancement

Add JavaScript to enhance the user experience with preview functionality and AJAX submission:

### Enhanced Template with JavaScript
```html
<!-- Add to the template -->
<script>
// Image preview functionality
function setupImagePreview() {
    const visionInput = document.getElementById('vision_image');
    const missionInput = document.getElementById('mission_image');
    
    if (visionInput) {
        visionInput.addEventListener('change', function(e) {
            previewImage(e.target, 'vision-preview');
        });
    }
    
    if (missionInput) {
        missionInput.addEventListener('change', function(e) {
            previewImage(e.target, 'mission-preview');
        });
    }
}

function previewImage(input, previewId) {
    const file = input.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            let preview = document.getElementById(previewId);
            if (!preview) {
                preview = document.createElement('img');
                preview.id = previewId;
                preview.style.maxWidth = '200px';
                preview.style.maxHeight = '150px';
                preview.style.marginTop = '10px';
                preview.style.border = '1px solid #ddd';
                preview.style.borderRadius = '4px';
                input.parentNode.appendChild(preview);
            }
            preview.src = e.target.result;
        };
        reader.readAsDataURL(file);
    }
}

// AJAX form submission
function setupAjaxSubmission() {
    const form = document.querySelector('form[enctype="multipart/form-data"]');
    if (form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            submitFormWithAjax(form);
        });
    }
}

function submitFormWithAjax(form) {
    const formData = new FormData(form);
    const submitBtn = form.querySelector('button[type="submit"]');
    
    // Show loading state
    const originalText = submitBtn.textContent;
    submitBtn.textContent = 'Saving...';
    submitBtn.disabled = true;
    
    fetch(form.action || window.location.pathname, {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        }
    })
    .then(response => {
        if (response.ok) {
            showNotification('Settings updated successfully!', 'success');
            return response.text();
        } else {
            throw new Error('Failed to update settings');
        }
    })
    .then(html => {
        // Optionally reload the page or update specific sections
        window.location.reload();
    })
    .catch(error => {
        showNotification('Error updating settings: ' + error.message, 'error');
    })
    .finally(() => {
        submitBtn.textContent = originalText;
        submitBtn.disabled = false;
    });
}

function showNotification(message, type) {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type === 'success' ? 'success' : 'danger'}`;
    notification.textContent = message;
    notification.style.position = 'fixed';
    notification.style.top = '20px';
    notification.style.right = '20px';
    notification.style.zIndex = '9999';
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.remove();
    }, 5000);
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', function() {
    setupImagePreview();
    setupAjaxSubmission();
});
</script>
```

## 🌐 Option 3: Pure API Integration

If you want to use the REST API directly instead of Django forms:

### API-Based Frontend
```javascript
class OrganizationSettingsManager {
    constructor() {
        this.apiUrl = '/api/organization/settings/';
        this.csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
    }
    
    async loadSettings() {
        try {
            const response = await fetch(this.apiUrl);
            if (response.ok) {
                const settings = await response.json();
                this.populateForm(settings);
                return settings;
            }
        } catch (error) {
            console.error('Error loading settings:', error);
        }
    }
    
    populateForm(settings) {
        // Populate text fields
        document.getElementById('vision').value = settings.vision || '';
        document.getElementById('mission').value = settings.mission || '';
        
        // Show current images
        this.showCurrentImage('vision_image', settings.vision_image);
        this.showCurrentImage('mission_image', settings.mission_image);
    }
    
    showCurrentImage(fieldName, imageUrl) {
        if (imageUrl) {
            const container = document.getElementById(fieldName).parentNode;
            let currentImageDiv = container.querySelector('.current-image');
            
            if (!currentImageDiv) {
                currentImageDiv = document.createElement('div');
                currentImageDiv.className = 'current-image';
                container.appendChild(currentImageDiv);
            }
            
            currentImageDiv.innerHTML = `
                <small class="text-muted">Current image:</small><br>
                <img src="${imageUrl}" style="max-width: 150px; max-height: 100px; margin-top: 5px; border: 1px solid #ddd; border-radius: 4px;">
                <br><a href="${imageUrl}" target="_blank" class="text-primary">View full size</a>
            `;
        }
    }
    
    async saveSettings(formData) {
        try {
            const response = await fetch(this.apiUrl, {
                method: 'PUT',
                body: formData,
                headers: {
                    'X-CSRFToken': this.csrfToken
                }
            });
            
            if (response.ok) {
                const updatedSettings = await response.json();
                this.showNotification('Settings updated successfully!', 'success');
                this.populateForm(updatedSettings);
                return updatedSettings;
            } else {
                const errorData = await response.json();
                throw new Error(JSON.stringify(errorData));
            }
        } catch (error) {
            this.showNotification('Error updating settings: ' + error.message, 'error');
            throw error;
        }
    }
    
    showNotification(message, type) {
        // Same notification function as above
        const notification = document.createElement('div');
        notification.className = `alert alert-${type === 'success' ? 'success' : 'danger'}`;
        notification.textContent = message;
        notification.style.position = 'fixed';
        notification.style.top = '20px';
        notification.style.right = '20px';
        notification.style.zIndex = '9999';
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 5000);
    }
}

// Usage
const settingsManager = new OrganizationSettingsManager();

// Load settings when page loads
document.addEventListener('DOMContentLoaded', async function() {
    await settingsManager.loadSettings();
    
    // Setup form submission
    const form = document.querySelector('form');
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const formData = new FormData(form);
        await settingsManager.saveSettings(formData);
    });
});
```

## 📱 Option 4: React/Vue Component (if using modern frontend)

### React Component Example
```jsx
import React, { useState, useEffect } from 'react';

const OrganizationSettings = () => {
    const [settings, setSettings] = useState({});
    const [loading, setLoading] = useState(false);
    const [visionImage, setVisionImage] = useState(null);
    const [missionImage, setMissionImage] = useState(null);
    
    useEffect(() => {
        loadSettings();
    }, []);
    
    const loadSettings = async () => {
        try {
            const response = await fetch('/api/organization/settings/');
            const data = await response.json();
            setSettings(data);
        } catch (error) {
            console.error('Error loading settings:', error);
        }
    };
    
    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        
        const formData = new FormData();
        formData.append('vision', settings.vision || '');
        formData.append('mission', settings.mission || '');
        
        if (visionImage) formData.append('vision_image', visionImage);
        if (missionImage) formData.append('mission_image', missionImage);
        
        try {
            const response = await fetch('/api/organization/settings/', {
                method: 'PUT',
                body: formData
            });
            
            if (response.ok) {
                const updatedSettings = await response.json();
                setSettings(updatedSettings);
                alert('Settings updated successfully!');
            }
        } catch (error) {
            alert('Error updating settings');
        } finally {
            setLoading(false);
        }
    };
    
    return (
        <form onSubmit={handleSubmit}>
            <div className="row">
                <div className="col-md-6">
                    <label>Vision Statement</label>
                    <textarea
                        value={settings.vision || ''}
                        onChange={(e) => setSettings({...settings, vision: e.target.value})}
                        rows="3"
                        className="form-control"
                    />
                </div>
                <div className="col-md-6">
                    <label>Vision Image</label>
                    <input
                        type="file"
                        accept="image/jpeg,image/jpg,image/png"
                        onChange={(e) => setVisionImage(e.target.files[0])}
                        className="form-control"
                    />
                    {settings.vision_image && (
                        <img src={settings.vision_image} alt="Current vision" style={{maxWidth: '150px', marginTop: '10px'}} />
                    )}
                </div>
            </div>
            
            <div className="row">
                <div className="col-md-6">
                    <label>Mission Statement</label>
                    <textarea
                        value={settings.mission || ''}
                        onChange={(e) => setSettings({...settings, mission: e.target.value})}
                        rows="3"
                        className="form-control"
                    />
                </div>
                <div className="col-md-6">
                    <label>Mission Image</label>
                    <input
                        type="file"
                        accept="image/jpeg,image/jpg,image/png"
                        onChange={(e) => setMissionImage(e.target.files[0])}
                        className="form-control"
                    />
                    {settings.mission_image && (
                        <img src={settings.mission_image} alt="Current mission" style={{maxWidth: '150px', marginTop: '10px'}} />
                    )}
                </div>
            </div>
            
            <button type="submit" disabled={loading} className="btn btn-primary">
                {loading ? 'Saving...' : 'Save Settings'}
            </button>
        </form>
    );
};

export default OrganizationSettings;
```

## 🎯 Recommended Approach

For your existing Django-based admin dashboard, I recommend **Option 1** (the enhanced Django template) which is already implemented, plus **Option 2** (JavaScript enhancement) for better user experience.

The template is already updated and working. You just need to:

1. ✅ **Already Done**: Template updated with image upload fields
2. ✅ **Already Done**: Django view handles file uploads
3. ✅ **Already Done**: API endpoints support image fields
4. **Optional**: Add JavaScript enhancements for image preview and AJAX submission

The current implementation works out of the box with traditional form submission. The JavaScript enhancements are optional but provide a better user experience.

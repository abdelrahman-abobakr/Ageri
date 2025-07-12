/**
 * Organization Settings JavaScript Enhancement
 * Provides image preview, AJAX submission, and better UX for vision/mission image uploads
 */

class OrganizationSettingsManager {
    constructor() {
        this.apiUrl = '/api/organization/settings/';
        this.form = document.querySelector('form[enctype="multipart/form-data"]');
        this.csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
        this.init();
    }

    init() {
        this.setupImagePreviews();
        this.setupFormSubmission();
        this.setupImageValidation();
        this.loadCurrentImages();
    }

    /**
     * Setup image preview functionality
     */
    setupImagePreviews() {
        const visionInput = document.getElementById('vision_image');
        const missionInput = document.getElementById('mission_image');

        if (visionInput) {
            visionInput.addEventListener('change', (e) => {
                this.previewImage(e.target, 'vision-preview');
                this.validateImageFile(e.target);
            });
        }

        if (missionInput) {
            missionInput.addEventListener('change', (e) => {
                this.previewImage(e.target, 'mission-preview');
                this.validateImageFile(e.target);
            });
        }
    }

    /**
     * Preview selected image
     */
    previewImage(input, previewId) {
        const file = input.files[0];
        if (file) {
            // Validate file type
            if (!this.isValidImageType(file)) {
                this.showNotification('Please select a valid image file (JPG, JPEG, PNG)', 'error');
                input.value = '';
                return;
            }

            // Validate file size (max 5MB)
            if (file.size > 5 * 1024 * 1024) {
                this.showNotification('Image file size must be less than 5MB', 'error');
                input.value = '';
                return;
            }

            const reader = new FileReader();
            reader.onload = (e) => {
                this.createOrUpdatePreview(input, previewId, e.target.result, file.name);
            };
            reader.readAsDataURL(file);
        } else {
            this.removePreview(previewId);
        }
    }

    /**
     * Create or update image preview
     */
    createOrUpdatePreview(input, previewId, imageSrc, fileName) {
        let previewContainer = document.getElementById(previewId);
        
        if (!previewContainer) {
            previewContainer = document.createElement('div');
            previewContainer.id = previewId;
            previewContainer.className = 'image-preview-container mt-2';
            input.parentNode.appendChild(previewContainer);
        }

        previewContainer.innerHTML = `
            <div class="image-preview">
                <img src="${imageSrc}" alt="Preview" style="max-width: 200px; max-height: 150px; border: 1px solid #ddd; border-radius: 4px;">
                <div class="mt-1">
                    <small class="text-muted">Selected: ${fileName}</small>
                    <button type="button" class="btn btn-sm btn-outline-danger ms-2" onclick="organizationSettings.removeImageSelection('${input.id}', '${previewId}')">
                        <i class="fas fa-times"></i> Remove
                    </button>
                </div>
            </div>
        `;
    }

    /**
     * Remove image preview
     */
    removePreview(previewId) {
        const preview = document.getElementById(previewId);
        if (preview) {
            preview.remove();
        }
    }

    /**
     * Remove image selection
     */
    removeImageSelection(inputId, previewId) {
        const input = document.getElementById(inputId);
        if (input) {
            input.value = '';
        }
        this.removePreview(previewId);
    }

    /**
     * Validate image file type
     */
    isValidImageType(file) {
        const validTypes = ['image/jpeg', 'image/jpg', 'image/png'];
        return validTypes.includes(file.type);
    }

    /**
     * Setup image validation
     */
    validateImageFile(input) {
        const file = input.files[0];
        if (file && !this.isValidImageType(file)) {
            this.showNotification('Only JPG, JPEG, and PNG files are allowed', 'error');
            input.value = '';
            return false;
        }
        return true;
    }

    /**
     * Setup enhanced form submission with AJAX
     */
    setupFormSubmission() {
        if (this.form) {
            this.form.addEventListener('submit', (e) => {
                e.preventDefault();
                this.submitForm();
            });
        }
    }

    /**
     * Submit form with AJAX
     */
    async submitForm() {
        const formData = new FormData(this.form);
        const submitBtn = this.form.querySelector('button[type="submit"]');
        
        // Show loading state
        const originalText = submitBtn.innerHTML;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Saving...';
        submitBtn.disabled = true;

        try {
            const response = await fetch(this.form.action || window.location.pathname, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': this.csrfToken
                }
            });

            if (response.ok) {
                this.showNotification('Organization settings updated successfully!', 'success');
                
                // Reload current images to show updated ones
                setTimeout(() => {
                    this.loadCurrentImages();
                }, 1000);
            } else {
                const errorText = await response.text();
                throw new Error(`Server error: ${response.status}`);
            }
        } catch (error) {
            console.error('Error updating settings:', error);
            this.showNotification('Error updating settings. Please try again.', 'error');
        } finally {
            submitBtn.innerHTML = originalText;
            submitBtn.disabled = false;
        }
    }

    /**
     * Load and display current images
     */
    async loadCurrentImages() {
        try {
            const response = await fetch(this.apiUrl);
            if (response.ok) {
                const settings = await response.json();
                this.displayCurrentImage('vision_image', settings.vision_image);
                this.displayCurrentImage('mission_image', settings.mission_image);
            }
        } catch (error) {
            console.error('Error loading current images:', error);
        }
    }

    /**
     * Display current image
     */
    displayCurrentImage(fieldName, imageUrl) {
        const input = document.getElementById(fieldName);
        if (!input || !imageUrl) return;

        const container = input.parentNode;
        let currentImageDiv = container.querySelector('.current-image-display');

        if (!currentImageDiv) {
            currentImageDiv = document.createElement('div');
            currentImageDiv.className = 'current-image-display mt-2';
            container.appendChild(currentImageDiv);
        }

        currentImageDiv.innerHTML = `
            <div class="current-image">
                <small class="text-muted">Current image:</small><br>
                <img src="${imageUrl}" alt="Current image" style="max-width: 150px; max-height: 100px; margin-top: 5px; border: 1px solid #ddd; border-radius: 4px;">
                <br>
                <a href="${imageUrl}" target="_blank" class="text-primary small">
                    <i class="fas fa-external-link-alt"></i> View full size
                </a>
            </div>
        `;
    }

    /**
     * Show notification message
     */
    showNotification(message, type = 'info') {
        // Remove existing notifications
        const existingNotifications = document.querySelectorAll('.settings-notification');
        existingNotifications.forEach(n => n.remove());

        const notification = document.createElement('div');
        notification.className = `alert alert-${type === 'success' ? 'success' : type === 'error' ? 'danger' : 'info'} settings-notification`;
        notification.style.position = 'fixed';
        notification.style.top = '20px';
        notification.style.right = '20px';
        notification.style.zIndex = '9999';
        notification.style.minWidth = '300px';
        notification.innerHTML = `
            <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
            ${message}
            <button type="button" class="btn-close float-end" onclick="this.parentElement.remove()"></button>
        `;

        document.body.appendChild(notification);

        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 5000);
    }

    /**
     * Reset form to original state
     */
    resetForm() {
        this.form.reset();
        this.removePreview('vision-preview');
        this.removePreview('mission-preview');
        this.loadCurrentImages();
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Make it globally accessible for button onclick handlers
    window.organizationSettings = new OrganizationSettingsManager();
});

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = OrganizationSettingsManager;
}

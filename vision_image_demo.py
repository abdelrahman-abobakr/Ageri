#!/usr/bin/env python
"""
Vision and Mission Image Upload Demo

This script demonstrates how to use the new vision and mission image upload functionality
in the Organization Settings.

Features added:
1. vision_image field - Upload images for vision statements
2. mission_image field - Upload images for mission statements
3. API support for image upload and retrieval
4. Admin dashboard support for image management
5. Proper validation for image file types (JPG, JPEG, PNG)

Usage:
    python vision_image_demo.py
"""

import os
import sys
import django
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
import io

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'research_platform.settings')
django.setup()

from organization.models import OrganizationSettings


def create_sample_image(text, color='blue', size=(400, 200)):
    """Create a sample image with text"""
    from PIL import Image, ImageDraw, ImageFont
    
    # Create image
    image = Image.new('RGB', size, color=color)
    draw = ImageDraw.Draw(image)
    
    # Try to use a font, fallback to default if not available
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
    except:
        font = ImageFont.load_default()
    
    # Calculate text position (center)
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (size[0] - text_width) // 2
    y = (size[1] - text_height) // 2
    
    # Draw text
    draw.text((x, y), text, fill='white', font=font)
    
    return image


def image_to_uploaded_file(image, filename):
    """Convert PIL Image to Django UploadedFile"""
    image_file = io.BytesIO()
    image.save(image_file, format='PNG')
    image_file.seek(0)
    
    return SimpleUploadedFile(
        name=filename,
        content=image_file.getvalue(),
        content_type='image/png'
    )


def demo_vision_mission_images():
    """Demonstrate vision and mission image upload functionality"""
    print("🌟 Vision and Mission Image Upload Demo")
    print("=" * 50)
    
    # Get or create organization settings
    settings = OrganizationSettings.get_settings()
    print(f"📋 Organization: {settings.name}")
    
    # Create sample images
    print("\n🎨 Creating sample images...")
    vision_image = create_sample_image("VISION 2030", color='darkblue')
    mission_image = create_sample_image("OUR MISSION", color='darkgreen')
    
    # Convert to uploaded files
    vision_file = image_to_uploaded_file(vision_image, 'vision_2030.png')
    mission_file = image_to_uploaded_file(mission_image, 'mission_statement.png')
    
    # Update organization settings
    print("\n📝 Updating organization settings...")
    settings.vision = "To be a leading research institution driving innovation and scientific excellence by 2030."
    settings.vision_image = vision_file
    
    settings.mission = "Our mission is to advance knowledge through cutting-edge research, foster collaboration, and train the next generation of scientists."
    settings.mission_image = mission_file
    
    settings.save()
    print("✅ Settings updated successfully!")
    
    # Display results
    print("\n📊 Current Settings:")
    print(f"Vision: {settings.vision}")
    print(f"Vision Image: {settings.vision_image.name if settings.vision_image else 'None'}")
    print(f"Mission: {settings.mission}")
    print(f"Mission Image: {settings.mission_image.name if settings.mission_image else 'None'}")
    
    # API endpoint information
    print("\n🌐 API Access:")
    print("GET /api/organization/settings/ - Public access to view settings")
    print("PUT /api/organization/settings/ - Admin access to update settings")
    print("\nExample API response will now include:")
    print("- vision_image: URL to vision image")
    print("- mission_image: URL to mission image")
    
    # Dashboard information
    print("\n🎛️  Admin Dashboard:")
    print("Visit /dashboard/organization-settings/ to manage images through the web interface")
    print("- Upload new vision images")
    print("- Upload new mission images")
    print("- View current images")
    print("- Supported formats: JPG, JPEG, PNG")
    
    print("\n✨ Demo completed successfully!")


def show_api_example():
    """Show example API usage"""
    print("\n🔌 API Usage Examples:")
    print("=" * 30)
    
    print("\n1. Get organization settings (Public):")
    print("   GET http://localhost:8000/api/organization/settings/")
    print("   Response includes vision_image and mission_image URLs")
    
    print("\n2. Update settings with images (Admin only):")
    print("   PUT http://localhost:8000/api/organization/settings/")
    print("   Content-Type: multipart/form-data")
    print("   Body:")
    print("   - vision: 'New vision text'")
    print("   - vision_image: [image file]")
    print("   - mission: 'New mission text'")
    print("   - mission_image: [image file]")
    
    print("\n3. Frontend JavaScript example:")
    print("""
   const formData = new FormData();
   formData.append('vision', 'Our new vision');
   formData.append('vision_image', visionImageFile);
   formData.append('mission', 'Our new mission');
   formData.append('mission_image', missionImageFile);
   
   fetch('/api/organization/settings/', {
       method: 'PUT',
       headers: {
           'Authorization': 'Bearer ' + adminToken
       },
       body: formData
   });
   """)


if __name__ == "__main__":
    try:
        demo_vision_mission_images()
        show_api_example()
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

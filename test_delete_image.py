#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'research_platform.settings')
django.setup()

from organization.models import OrganizationSettings

def test_delete_image():
    """Test deleting an image from OrganizationSettings"""
    try:
        # Get the settings instance
        settings = OrganizationSettings.get_settings()
        
        print("=== قبل الحذف ===")
        print(f"About image: {settings.about_image}")
        print(f"Vision image: {settings.vision_image}")
        print(f"Mission image: {settings.mission_image}")
        
        # Check if about_image exists
        if settings.about_image:
            print(f"\nحذف الصورة: {settings.about_image.name}")
            
            # Delete the image file
            settings.about_image.delete(save=False)
            
            # Clear the field
            settings.about_image = None
            settings.save()
            
            print("✅ تم حذف الصورة بنجاح!")
        else:
            print("❌ لا توجد صورة about_image للحذف")
        
        print("\n=== بعد الحذف ===")
        print(f"About image: {settings.about_image}")
        
        # Refresh from database
        settings.refresh_from_db()
        print(f"About image (after refresh): {settings.about_image}")
        
    except Exception as e:
        print(f"❌ خطأ: {e}")

if __name__ == "__main__":
    test_delete_image()

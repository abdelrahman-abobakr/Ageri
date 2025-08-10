#!/usr/bin/env python
"""
Fix translation encoding issues by creating a simple .mo file
"""

import os
import struct

def create_simple_mo_file():
    """Create a simple .mo file with basic translations"""
    
    # Basic translations that work
    translations = {
        "Dashboard": "لوحة التحكم",
        "Users": "المستخدمون", 
        "Publications": "المنشورات",
        "Services": "الخدمات",
        "Management": "الإدارة",
        "Analytics": "التحليلات",
        "Settings": "الإعدادات",
        "Search": "بحث",
        "Filter": "تصفية",
        "Save": "حفظ",
        "Cancel": "إلغاء",
        "Edit": "تحرير",
        "Delete": "حذف",
        "Status": "الحالة",
        "Actions": "الإجراءات",
        "Active": "نشط",
        "Inactive": "غير نشط",
        "Pending": "معلق",
        "Approved": "موافق عليه",
        "Name": "الاسم",
        "Email": "البريد الإلكتروني",
        "Role": "الدور",
        "Admin": "مدير",
        "Moderator": "مشرف",
        "Researcher": "باحث",
        "Guest": "ضيف",
        "Organization": "المؤسسة",
        "Training": "التدريب",
        "Content": "المحتوى",
        "Departments": "الأقسام",
        "Laboratories": "المختبرات",
        "Courses": "الدورات",
        "Announcements": "الإعلانات"
    }
    
    mo_file_path = "locale/ar/LC_MESSAGES/django.mo"
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(mo_file_path), exist_ok=True)
    
    keys = list(translations.keys())
    values = [translations[k] for k in keys]
    
    # Calculate string table
    koffsets = []
    voffsets = []
    
    # Start after header and offset tables
    offset = 28 + len(keys) * 16
    
    for key in keys:
        key_bytes = key.encode('utf-8')
        koffsets.append((len(key_bytes), offset))
        offset += len(key_bytes) + 1
    
    for value in values:
        value_bytes = value.encode('utf-8')
        voffsets.append((len(value_bytes), offset))
        offset += len(value_bytes) + 1
    
    # Write .mo file
    with open(mo_file_path, 'wb') as f:
        # Magic number
        f.write(struct.pack('<I', 0x950412de))
        # Version
        f.write(struct.pack('<I', 0))
        # Number of entries
        f.write(struct.pack('<I', len(keys)))
        # Offset of key table
        f.write(struct.pack('<I', 28))
        # Offset of value table  
        f.write(struct.pack('<I', 28 + len(keys) * 8))
        # Hash table size
        f.write(struct.pack('<I', 0))
        # Hash table offset
        f.write(struct.pack('<I', 0))
        
        # Write key offsets
        for length, offset in koffsets:
            f.write(struct.pack('<I', length))
            f.write(struct.pack('<I', offset))
        
        # Write value offsets
        for length, offset in voffsets:
            f.write(struct.pack('<I', length))
            f.write(struct.pack('<I', offset))
        
        # Write keys
        for key in keys:
            f.write(key.encode('utf-8') + b'\x00')
        
        # Write values
        for value in values:
            f.write(value.encode('utf-8') + b'\x00')
    
    print(f"✅ Created simple .mo file with {len(translations)} translations")
    print(f"📁 File: {mo_file_path}")
    
    return mo_file_path

def test_mo_file():
    """Test if the .mo file works"""
    try:
        import gettext
        
        mo_file = "locale/ar/LC_MESSAGES/django.mo"
        
        with open(mo_file, 'rb') as f:
            catalog = gettext.GNUTranslations(f)
        
        # Test some translations
        test_strings = ["Dashboard", "Users", "Publications", "Settings"]
        
        print("\n🧪 Testing .mo file:")
        for string in test_strings:
            translated = catalog.gettext(string)
            print(f"✅ '{string}' -> '{translated}'")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing .mo file: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Fixing Translation Encoding Issues")
    print("=" * 50)
    
    # Create simple .mo file
    mo_file = create_simple_mo_file()
    
    # Test it
    if test_mo_file():
        print("\n🎉 Translation file created successfully!")
        print("✅ Django server should now start without Unicode errors")
        print("\n🚀 Try running: python manage.py runserver")
    else:
        print("\n❌ There's still an issue with the .mo file")
        print("🔧 You may need to remove the .mo file temporarily:")
        print("   rm locale/ar/LC_MESSAGES/django.mo")

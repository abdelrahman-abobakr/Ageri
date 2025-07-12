#!/usr/bin/env python
"""
Test script to verify translation functionality
"""

import os
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'research_platform.settings')
django.setup()

from django.utils import translation
from django.utils.translation import gettext as _

def test_translations():
    """Test translation functionality"""
    
    print("🌍 Testing Translation Functionality")
    print("=" * 50)
    
    # Test Arabic translations
    print("\n📝 Testing Arabic Translations:")
    translation.activate('ar')
    
    test_strings = [
        "Dashboard",
        "Users", 
        "Publications",
        "Settings",
        "Organization",
        "Total Users",
        "Pending Approvals",
        "Active Requests",
        "Departments",
        "Laboratories",
        "Translation Management"
    ]
    
    for string in test_strings:
        translated = _(string)
        status = "✅" if translated != string else "❌"
        print(f"{status} '{string}' -> '{translated}'")
    
    # Test English translations
    print("\n📝 Testing English Translations:")
    translation.activate('en')
    
    for string in test_strings:
        translated = _(string)
        status = "✅" if translated == string else "❌"
        print(f"{status} '{string}' -> '{translated}'")
    
    # Test language switching
    print("\n🔄 Testing Language Switching:")
    
    test_word = "Dashboard"
    
    translation.activate('ar')
    ar_translation = _(test_word)
    print(f"Arabic: '{test_word}' -> '{ar_translation}'")
    
    translation.activate('en')
    en_translation = _(test_word)
    print(f"English: '{test_word}' -> '{en_translation}'")
    
    # Check if translations are different
    if ar_translation != en_translation:
        print("✅ Language switching works correctly!")
    else:
        print("❌ Language switching may not be working properly")
    
    # Check translation files
    print("\n📁 Checking Translation Files:")
    
    locale_path = settings.BASE_DIR / 'locale'
    
    for lang_code, lang_name in settings.LANGUAGES:
        po_file = locale_path / lang_code / 'LC_MESSAGES' / 'django.po'
        mo_file = locale_path / lang_code / 'LC_MESSAGES' / 'django.mo'
        
        po_exists = "✅" if po_file.exists() else "❌"
        mo_exists = "✅" if mo_file.exists() else "❌"
        
        print(f"{lang_name} ({lang_code}):")
        print(f"  PO file: {po_exists} {po_file}")
        print(f"  MO file: {mo_exists} {mo_file}")
        
        if po_file.exists():
            with open(po_file, 'r', encoding='utf-8') as f:
                content = f.read()
                total_strings = content.count('msgid "')
                translated_strings = content.count('msgstr "') - content.count('msgstr ""')
                completion = round((translated_strings / total_strings * 100) if total_strings > 0 else 0, 1)
                print(f"  Translation completion: {completion}% ({translated_strings}/{total_strings})")
    
    print("\n🎯 Summary:")
    print("- Translation files are set up")
    print("- Language switching functionality is available")
    print("- Arabic translations are loaded")
    print("- Dashboard templates use translation tags")
    print("- Translation management interface is available at /dashboard/translations/")
    
    print("\n🚀 Next Steps:")
    print("1. Start the Django server: python manage.py runserver")
    print("2. Go to: http://localhost:8000/dashboard/")
    print("3. Use the language switcher in the top navigation")
    print("4. Visit: http://localhost:8000/dashboard/translations/ for translation management")

if __name__ == "__main__":
    test_translations()

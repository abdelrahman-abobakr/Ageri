#!/usr/bin/env python
"""
Compile translation files manually
"""

import os
import struct
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'research_platform.settings')
django.setup()

def parse_po_file(po_file_path):
    """Parse .po file and extract translations"""
    translations = {}
    
    with open(po_file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split into entries
    entries = content.split('\n\n')
    
    for entry in entries:
        lines = entry.strip().split('\n')
        msgid = None
        msgstr = None
        
        for line in lines:
            line = line.strip()
            if line.startswith('msgid "') and line.endswith('"'):
                msgid = line[7:-1]  # Remove 'msgid "' and '"'
            elif line.startswith('msgstr "') and line.endswith('"'):
                msgstr = line[8:-1]  # Remove 'msgstr "' and '"'
            elif line.startswith('"') and line.endswith('"') and msgid is not None and msgstr is None:
                # Continuation of msgid
                msgid += line[1:-1]
            elif line.startswith('"') and line.endswith('"') and msgstr is not None:
                # Continuation of msgstr
                msgstr += line[1:-1]
        
        if msgid and msgstr and msgid != '':
            # Unescape strings
            msgid = msgid.replace('\\"', '"').replace('\\n', '\n').replace('\\t', '\t')
            msgstr = msgstr.replace('\\"', '"').replace('\\n', '\n').replace('\\t', '\t')
            translations[msgid] = msgstr
    
    return translations

def create_mo_file(translations, mo_file_path):
    """Create .mo file from translations dictionary"""
    
    # Filter out empty translations
    filtered_translations = {k: v for k, v in translations.items() if v.strip()}
    
    keys = list(filtered_translations.keys())
    values = [filtered_translations[k] for k in keys]
    
    # Calculate offsets
    key_offsets = []
    value_offsets = []
    
    # Start after header and offset tables
    offset = 28 + len(keys) * 16
    
    # Calculate key offsets
    for key in keys:
        key_bytes = key.encode('utf-8')
        key_offsets.append((len(key_bytes), offset))
        offset += len(key_bytes) + 1  # +1 for null terminator
    
    # Calculate value offsets
    for value in values:
        value_bytes = value.encode('utf-8')
        value_offsets.append((len(value_bytes), offset))
        offset += len(value_bytes) + 1  # +1 for null terminator
    
    # Write .mo file
    with open(mo_file_path, 'wb') as f:
        # Write header
        f.write(struct.pack('<I', 0x950412de))  # Magic number
        f.write(struct.pack('<I', 0))           # Version
        f.write(struct.pack('<I', len(keys)))   # Number of entries
        f.write(struct.pack('<I', 28))          # Offset of key table
        f.write(struct.pack('<I', 28 + len(keys) * 8))  # Offset of value table
        f.write(struct.pack('<I', 0))           # Hash table size
        f.write(struct.pack('<I', 0))           # Hash table offset
        
        # Write key table
        for length, offset in key_offsets:
            f.write(struct.pack('<I', length))
            f.write(struct.pack('<I', offset))
        
        # Write value table
        for length, offset in value_offsets:
            f.write(struct.pack('<I', length))
            f.write(struct.pack('<I', offset))
        
        # Write keys
        for key in keys:
            f.write(key.encode('utf-8') + b'\x00')
        
        # Write values
        for value in values:
            f.write(value.encode('utf-8') + b'\x00')

def compile_translations():
    """Compile all translation files"""
    
    print("🌍 Compiling Translation Files")
    print("=" * 50)
    
    locale_path = settings.BASE_DIR / 'locale'
    
    for lang_code, lang_name in settings.LANGUAGES:
        po_file = locale_path / lang_code / 'LC_MESSAGES' / 'django.po'
        mo_file = locale_path / lang_code / 'LC_MESSAGES' / 'django.mo'
        
        if po_file.exists():
            print(f"\n📝 Processing {lang_name} ({lang_code})...")
            
            try:
                # Parse .po file
                translations = parse_po_file(str(po_file))
                
                # Create .mo file
                create_mo_file(translations, str(mo_file))
                
                print(f"✅ Successfully compiled {po_file.name}")
                print(f"   Translations: {len(translations)}")
                print(f"   Output: {mo_file}")
                
            except Exception as e:
                print(f"❌ Error compiling {po_file.name}: {e}")
        else:
            print(f"⚠️  {lang_name} ({lang_code}): PO file not found")
    
    print(f"\n🎯 Translation compilation complete!")
    print(f"📁 Files location: {locale_path}")

def test_translations():
    """Test if translations are working"""
    from django.utils import translation
    from django.utils.translation import gettext as _
    
    print("\n🧪 Testing Translations...")
    print("-" * 30)
    
    test_strings = [
        "Dashboard",
        "User Management", 
        "Publications",
        "Service Requests",
        "Create Department",
        "All Users",
        "Pending Approval",
        "Search",
        "Filter"
    ]
    
    # Test Arabic
    translation.activate('ar')
    print(f"\n🇸🇦 Arabic Translations:")
    for string in test_strings:
        translated = _(string)
        status = "✅" if translated != string else "❌"
        print(f"{status} '{string}' -> '{translated}'")
    
    # Test English
    translation.activate('en')
    print(f"\n🇺🇸 English Translations:")
    for string in test_strings:
        translated = _(string)
        status = "✅" if translated == string else "❌"
        print(f"{status} '{string}' -> '{translated}'")

if __name__ == "__main__":
    compile_translations()
    test_translations()
    
    print(f"\n🚀 Next Steps:")
    print(f"1. Restart Django server: python manage.py runserver")
    print(f"2. Visit: http://localhost:8000/dashboard/")
    print(f"3. Switch language using the dropdown in navigation")
    print(f"4. All dashboard content should now be in Arabic! 🎉")

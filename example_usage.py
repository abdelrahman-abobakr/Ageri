"""
Example: How to Access Organization Vision and Message

This file shows different ways to access the organization settings
including vision and message in your Django application.
"""

# Method 1: In Django Views
from organization.models import OrganizationSettings

def my_view(request):
    # Get organization settings (creates if doesn't exist)
    org_settings = OrganizationSettings.get_settings()
    
    # Access vision and message
    vision = org_settings.vision  # Arabic version (default)
    mission = org_settings.mission  # Arabic version (default)
    
    # Access specific language versions
    vision_ar = org_settings.vision_ar  # Arabic explicitly
    vision_en = org_settings.vision_en  # English explicitly
    mission_ar = org_settings.mission_ar  # Arabic explicitly
    mission_en = org_settings.mission_en  # English explicitly
    
    context = {
        'org_name': org_settings.name,
        'vision': vision,
        'mission': mission,
        'logo': org_settings.logo,
        'banner': org_settings.banner,
    }
    return render(request, 'my_template.html', context)


# Method 2: In Django Templates
"""
In your template:

{% load i18n %}

<!-- Display organization info -->
<h1>{{ org_settings.name }}</h1>

<!-- Vision (current language) -->
{% if org_settings.vision %}
    <p><strong>{% trans "Vision" %}:</strong> {{ org_settings.vision }}</p>
{% endif %}

<!-- Mission (current language) -->
{% if org_settings.mission %}
    <p><strong>{% trans "Mission" %}:</strong> {{ org_settings.mission }}</p>
{% endif %}

<!-- Logo -->
{% if org_settings.logo %}
    <img src="{{ org_settings.logo.url }}" alt="Logo">
{% endif %}
"""


# Method 3: Via API (Frontend/JavaScript)
"""
// Get organization settings via API
fetch('/api/organization/settings/')
    .then(response => response.json())
    .then(data => {
        console.log('Organization Name:', data.name);
        console.log('Vision:', data.vision);
        console.log('Mission:', data.mission);
        console.log('Logo URL:', data.logo);
        console.log('Banner URL:', data.banner);
    });

// For specific language (if using language parameter)
fetch('/api/organization/settings/?lang=ar')
    .then(response => response.json())
    .then(data => {
        // Arabic versions
        console.log('Arabic Vision:', data.vision);
        console.log('Arabic Mission:', data.mission);
    });
"""


# Method 4: In Django Management Commands or Scripts
"""
from django.core.management.base import BaseCommand
from organization.models import OrganizationSettings

class Command(BaseCommand):
    def handle(self, *args, **options):
        settings = OrganizationSettings.get_settings()
        
        # Set initial values
        settings.name = "مؤسسة أجري للبحث العلمي"
        settings.vision = "رؤيتنا أن نكون مركزاً رائداً في البحث العلمي والتطوير التكنولوجي"
        settings.mission = "مهمتنا تقديم حلول بحثية مبتكرة تخدم المجتمع والتنمية المستدامة"
        settings.about = "نحن مؤسسة بحثية متخصصة في مجالات متعددة من العلوم والتكنولوجيا"
        settings.email = "info@ageri.org"
        settings.phone = "+20123456789"
        settings.save()
        
        self.stdout.write("Organization settings updated successfully!")
"""


# Method 5: Quick Setup Function
def setup_organization_settings():
    """
    Quick function to set up initial organization settings
    Call this once to initialize your organization data
    """
    settings = OrganizationSettings.get_settings()
    
    # Set Arabic content
    settings.name = "مؤسسة أجري للبحث العلمي"
    settings.vision = "رؤيتنا أن نكون مركزاً رائداً في البحث العلمي والتطوير التكنولوجي في المنطقة"
    settings.mission = "مهمتنا تقديم حلول بحثية مبتكرة ومتطورة تخدم المجتمع وتساهم في التنمية المستدامة"
    settings.about = "نحن مؤسسة بحثية متخصصة تضم نخبة من الباحثين والخبراء في مجالات متعددة من العلوم والتكنولوجيا"
    
    # Contact information
    settings.email = "info@ageri.org"
    settings.phone = "+20123456789"
    settings.address = "القاهرة، جمهورية مصر العربية"
    
    # Social media
    settings.website = "https://ageri.org"
    settings.facebook = "https://facebook.com/ageri"
    settings.twitter = "https://twitter.com/ageri"
    
    # System settings
    settings.enable_registration = True
    settings.require_approval = True
    
    settings.save()
    print("Organization settings have been set up successfully!")
    return settings


# Method 6: Context Processor (Global Access)
"""
Create a context processor to make organization settings available globally:

# In your_app/context_processors.py
from organization.models import OrganizationSettings

def organization_settings(request):
    return {
        'org_settings': OrganizationSettings.get_settings()
    }

# Add to settings.py TEMPLATES context_processors:
'OPTIONS': {
    'context_processors': [
        # ... other processors
        'your_app.context_processors.organization_settings',
    ],
},

# Now available in all templates as {{ org_settings }}
"""

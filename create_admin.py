#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'research_platform.settings')
django.setup()

from accounts.models import User

# Create admin user
try:
    admin_user = User.objects.create_superuser(
        username='admin',
        email='admin@research.com',
        password='admin123',
        first_name='Admin',
        last_name='User',
        role='admin',
        is_approved=True
    )
    print(f"Admin user created successfully: {admin_user.email}")
except Exception as e:
    print(f"Error creating admin user: {e}")

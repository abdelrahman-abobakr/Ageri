"""
Django settings for testing
"""

from .settings import *

# Override database configuration for testing
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
        'ATOMIC_REQUESTS': False,
    }
}

# Disable migrations for faster testing
class DisableMigrations:
    def __contains__(self, item):
        return True
    
    def __getitem__(self, item):
        return None

MIGRATION_MODULES = DisableMigrations()

# Speed up password hashing for tests
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Disable logging during tests
LOGGING_CONFIG = None

# Use a simple cache backend for tests
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

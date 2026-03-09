"""Project package init.

Ensure the custom admin site is imported early so model admin
registrations attach to the overridden `admin.site` instance.
"""
# Import custom_admin to replace django.contrib.admin.site early
from . import custom_admin  # noqa: F401

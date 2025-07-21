from modeltranslation.translator import register, TranslationOptions
from .models import Department, Lab, OrganizationSettings


@register(Department)
class DepartmentTranslationOptions(TranslationOptions):
    fields = ('name', 'description', 'location')


@register(Lab)
class LabTranslationOptions(TranslationOptions):
    fields = ('name', 'description', 'equipment', 'location')


@register(OrganizationSettings)
class OrganizationSettingsTranslationOptions(TranslationOptions):
    fields = (
        'name', 'vision', 'mission', 'about', 'address', 
        'maintenance_message'
    )

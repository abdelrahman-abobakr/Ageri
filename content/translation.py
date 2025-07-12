from modeltranslation.translator import register, TranslationOptions
from .models import Announcement, Post


@register(Announcement)
class AnnouncementTranslationOptions(TranslationOptions):
    fields = ('title', 'content', 'summary')


@register(Post)
class PostTranslationOptions(TranslationOptions):
    fields = ('title', 'content', 'excerpt', 'event_location')

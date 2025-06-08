from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache

from .models import Course, Module


@receiver([post_save, post_delete], sender=Course)
def clear_course_cache(sender, instance, **kwargs):
    """Invalidate cached course listings when a course changes."""
    cache.delete('all_courses')
    cache.delete('all_subjects')
    cache.delete(f'subject_{instance.subject.id}_courses')


@receiver([post_save, post_delete], sender=Module)
def clear_module_cache(sender, instance, **kwargs):
    """Invalidate cached course lists when a module changes."""
    subject_id = instance.course.subject.id
    cache.delete('all_courses')
    cache.delete('all_subjects')
    cache.delete(f'subject_{subject_id}_courses')

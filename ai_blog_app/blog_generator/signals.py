# blog_generator/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Author

@receiver(post_save, sender=User)
def create_or_update_author_profile(sender, instance, created, **kwargs):
    if created:
        Author.objects.create(user=instance)
    else:
        if hasattr(instance, 'author_profile'):
            instance.author_profile.save()

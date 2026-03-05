from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Resident

@receiver(post_save, sender=User)
def create_resident_for_user(sender, instance, created, **kwargs):
    if created:
        Resident.objects.create(
            user=instance,
            firstname=instance.username,
            lastname="",
            email=instance.email
        )

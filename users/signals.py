import os

from django.conf import settings
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Profile
from .utils import create_avatar_image


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        # TODO Think about rnd profile image without the need to store it
        abs_img = "".join([os.path.join(settings.AVATARS, str(instance.pk)), ".svg"])
        rel_img = "".join(["avatars/", str(instance.pk), ".svg"])
        create_avatar_image(abs_img)
        Profile.objects.create(user=instance, image=rel_img)


@receiver(post_save, sender=User)
def save_profile(sender, instance, created, **kwargs):
    instance.profile.save()

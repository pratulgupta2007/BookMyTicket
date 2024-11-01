from django.dispatch import receiver
from django.db.models.signals import pre_save, post_save
import uuid
from .models import User, user, wallet


@receiver(post_save, sender=User, dispatch_uid='user.create_user_profile')
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        n=wallet.objects.create()
        user.objects.create(user=instance, walletid=n)
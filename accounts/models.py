from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = (
        ('brand', 'Brand'),
        ('influencer', 'Influencer'),
    )
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    phone = models.CharField(max_length=15, blank=True)

from django.db.models.signals import post_save
from django.dispatch import receiver
from brands.models import BrandProfile
from influencers.models import InfluencerProfile

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        if instance.role == 'brand':
            BrandProfile.objects.create(user=instance, name=instance.username)
        elif instance.role == 'influencer':
            InfluencerProfile.objects.create(user=instance, full_name=instance.username)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if instance.role == 'brand':
        instance.brandprofile.save()
    elif instance.role == 'influencer':
        instance.influencerprofile.save()
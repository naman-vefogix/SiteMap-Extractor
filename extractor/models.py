from django.db import models
from django.contrib.auth.models import AbstractUser, Permission
from django.conf import settings
from django.utils import timezone


# Create your models here.

class User(AbstractUser):
    username=models.CharField(max_length=255, null=True, blank=True,default="Disco", unique=True)
    email =models.EmailField(unique=True)
    email_is_verify=models.BooleanField(default=False)

class SitemapExtraction(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    
    ip_address = models.CharField(blank=True)

    domain = models.URLField()

    urls = models.JSONField()

    total_urls = models.IntegerField()

    created_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField()

    status = models.CharField(
        max_length=20,
        default="completed"
    )
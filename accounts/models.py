from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
import secrets


class User(AbstractUser):
    # "Admin" (not Django admin site "staff")
    is_platform_admin = models.BooleanField(default=False)

    def clean(self):
        # GOD vs Admin exclusivity
        if self.is_superuser and self.is_platform_admin:
            raise ValidationError("User cannot be both GOD (superuser) and Admin (platform admin).")

    def save(self, *args, **kwargs):
        # enforce exclusivity automatically
        if self.is_superuser:
            self.is_platform_admin = False
            self.is_staff = True
        if self.is_platform_admin:
            self.is_superuser = False
            self.is_staff = True
        super().save(*args, **kwargs)

class Invite(models.Model):
    email = models.EmailField()
    token = models.CharField(max_length=64, unique=True, editable=False)
    invited_by = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField(null=True, blank=True)
    used_at = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = secrets.token_urlsafe(32)
        super().save(*args, **kwargs)

    @property
    def is_used(self) -> bool:
        return self.used_at is not None

    @property
    def is_expired(self) -> bool:
        return self.expires_at is not None and timezone.now() > self.expires_at
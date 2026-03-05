from django.db import models
import uuid as _uuid


class Asset(models.Model):
    uuid = models.UUIDField(default=_uuid.uuid4, editable=False, unique=True, primary_key=True)
    organization = models.ForeignKey("organizations.Organization", on_delete=models.CASCADE, related_name="assets")
    name = models.CharField(max_length=200)
    asset_type = models.CharField(max_length=80, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["organization", "name"], name="uniq_asset_per_org")
        ]

    def __str__(self):
        return f"{self.organization} / {self.name}"

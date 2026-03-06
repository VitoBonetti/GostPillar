from django.db import models
import uuid as _uuid


class Market(models.Model):
    uuid = models.UUIDField(default=_uuid.uuid4, editable=False, unique=True, primary_key=True)
    region = models.ForeignKey("regions.Regions", on_delete=models.CASCADE, related_name="markets")
    market = models.CharField(max_length=120)
    code = models.CharField(max_length=15, blank=True, null=True)
    language = models.CharField(max_length=15, blank=True, null=True, default="English")
    active = models.BooleanField(default=True)
    description = models.TextField(blank=True, null=True)
    key_market = models.BooleanField(default=False)
    flag_icons = models.ImageField(blank=True, null=True, upload_to="market_icons")
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)


    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["region", "market"], name="uniq_market_per_region")
        ]

    def __str__(self):
        return f"{self.region} / {self.market}"

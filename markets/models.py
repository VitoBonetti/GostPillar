from django.db import models
import uuid as _uuid


class Market(models.Model):
    uuid = models.UUIDField(default=_uuid.uuid4, editable=False, unique=True, primary_key=True)
    region = models.ForeignKey("regions.Regions", on_delete=models.CASCADE, related_name="markets")
    name = models.CharField(max_length=120)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["region", "name"], name="uniq_market_per_region")
        ]

    def __str__(self):
        return f"{self.region} / {self.name}"

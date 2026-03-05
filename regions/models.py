from django.db import models
import uuid as _uuid

class Regions(models.Model):
    uuid = models.UUIDField(default=_uuid.uuid4, editable=False, unique=True, primary_key=True)
    name = models.CharField(max_length=120, unique=True)

    def __str__(self):
        return self.name
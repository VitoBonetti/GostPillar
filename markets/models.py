from django.db import models
from django.core.files.base import ContentFile
import uuid as _uuid
from management.validators import validate_file_size
from io import BytesIO
from PIL import Image


class Market(models.Model):
    uuid = models.UUIDField(default=_uuid.uuid4, editable=False, unique=True, primary_key=True)
    region = models.ForeignKey("regions.Regions", on_delete=models.CASCADE, related_name="markets")
    market = models.CharField(max_length=120)
    code = models.CharField(max_length=15, blank=True, null=True)
    language = models.CharField(max_length=15, blank=True, null=True, default="English")
    active = models.BooleanField(default=True)
    description = models.TextField(blank=True, null=True)
    key_market = models.BooleanField(default=False)
    flag_icons = models.ImageField(blank=True, null=True, upload_to="market_icons", validators=[validate_file_size])
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)


    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["region", "market"], name="uniq_market_per_region")
        ]

    def __str__(self):
        return f"{self.region} / {self.market}"

    def save(self, *args, **kwargs):
        if self.flag_icons and not self.flag_icons._committed:
            try:
                # Open the image with Pillow
                img = Image.open(self.flag_icons)

                # Check if it has EXIF data (mostly applies to JPEGs/TIFFs)
                if img.getexif():
                    # Safest way to strip all metadata is to copy the raw pixel data into a brand new image
                    data = list(img.getdata())
                    clean_img = Image.new(img.mode, img.size)
                    clean_img.putdata(data)

                    # Save the clean image to memory
                    output = BytesIO()
                    # Default to PNG to preserve transparency if format is missing
                    img_format = img.format if img.format else 'PNG'
                    clean_img.save(output, format=img_format)

                    # Overwrite the uploaded file with our clean, EXIF-free version
                    self.flag_icons.save(self.flag_icons.name, ContentFile(output.getvalue()), save=False)
            except Exception as e:
                # If Pillow fails (e.g., corrupted file), we just pass and let Django's standard validation handle it
                pass

            super().save(*args, **kwargs)


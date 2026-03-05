from django.contrib import admin
from .models import Market

@admin.register(Market)
class MarketAdmin(admin.ModelAdmin):
    list_display = ("name", "region")
    list_filter = ("region",)
    search_fields = ("name",)
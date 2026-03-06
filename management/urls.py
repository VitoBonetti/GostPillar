from django.urls import path
from .views import (
    ManagementHomeView,
    RegionView
)

urlpatterns = [
    path('', ManagementHomeView.as_view(), name='management'),
    path('regions/', RegionView.as_view(), name='regions'),
]
from django.urls import path
from .views import (
    ManagementHomeView,
    RegionView,
    MarketListView,
    MarketFormView,
)

urlpatterns = [
    path('', ManagementHomeView.as_view(), name='management'),
    path('regions/', RegionView.as_view(), name='regions'),
    path('markets/', MarketListView.as_view(), name='markets'),
    path('markets/form/', MarketFormView.as_view(), name='market_form'),
]
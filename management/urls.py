from django.urls import path
from .views import (
    ManagementHomeView,
    RegionView,
    MarketListView,
    MarketFormView,
    OrganizationListView,
    OrganizationFormView,
    UserListView,
    UserFormView,
    UserRoleView,
)

urlpatterns = [
    path('', ManagementHomeView.as_view(), name='management'),
    path('regions/', RegionView.as_view(), name='regions'),
    path('markets/', MarketListView.as_view(), name='markets'),
    path('markets/form/', MarketFormView.as_view(), name='market_form'),
    path('organizations/', OrganizationListView.as_view(), name='organizations'),
    path('organizations/form/', OrganizationFormView.as_view(), name='organization_form'),
    path('users/', UserListView.as_view(), name='users'),
    path('users/form/', UserFormView.as_view(), name='user_form'),
    path('users/<int:user_id>/roles/', UserRoleView.as_view(), name='user_roles'),
]
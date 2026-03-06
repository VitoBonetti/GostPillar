from django.forms import ModelForm
from regions.models import Regions
from markets.models import Market
from organizations.models import Organization

class RegionsForm(ModelForm):
    class Meta:
        model = Regions
        fields = ['region', 'active']


class MarketForm(ModelForm):
    class Meta:
        model = Market
        fields = [
            'region', 'market', 'code', 'language',
            'active', 'key_market', 'description', 'flag_icons'
        ]


class OrganizationForm(ModelForm):
    class Meta:
        model = Organization
        fields = ['market', 'name']
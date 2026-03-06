from django.forms import ModelForm
from regions.models import Regions
from markets.models import Market

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
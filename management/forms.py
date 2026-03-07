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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # show only the market name and force alphabetic order
        self.fields['market'].label_from_instance = lambda obj: obj.market
        self.fields['market'].queryset = Market.objects.filter(active=True).order_by('market')
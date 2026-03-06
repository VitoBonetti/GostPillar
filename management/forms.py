from django.forms import ModelForm
from regions.models import Regions


class RegionsForm(ModelForm):
    class Meta:
        model = Regions
        fields = ['region', 'active']
from django.urls import reverse_lazy
from django.views.generic import TemplateView, ListView, CreateView, UpdateView, DeleteView
from management.mixins import ManagementAccessMixin, ManagementWriteMixin, ManagementDeleteMixin
from regions.models import Regions
from .forms import RegionsForm
from django.views import View
from django.shortcuts import (
    render,
    get_object_or_404,
    reverse
)

class ManagementHomeView(ManagementAccessMixin, TemplateView):
    template_name = "management/home.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        try:
            ctx["active_regions_count"] = Regions.objects.filter(active=True).count()
            ctx["total_regions_count"] = Regions.objects.count()
        except Exception:
            ctx["active_regions_count"] = 0
            ctx["total_regions_count"] = 0
        return ctx

class RegionView(ManagementAccessMixin, View):
    def get(self, request, *args, **kwargs):
        region_id = request.GET.get("region_id", None)
        if region_id:
            region = get_object_or_404(Regions, uuid=region_id)
            form_region = RegionsForm(instance=region)
        else:
            form_region = RegionsForm()

        regions = Regions.objects.all().order_by("region")

        context = {
            "regions": regions,
            "form_region": form_region,
        }

        return render(request, "management/regions.html", context=context)

    def post(self, request, *args, **kwargs):
        region_id = request.GET.get("region_id", None)
        if region_id:
            region = get_object_or_404(Regions, uuid=region_id)
            form_region = RegionsForm(request.POST, instance=region)
        else:
            form_region = RegionsForm(request.POST)

        if form_region.is_valid():
            instance = form_region.save(commit=False)
            form_region = RegionsForm()

        regions = Regions.objects.all().order_by("region")

        context = {
            "regions": regions,
            "form_region": form_region,
        }

        return render(request, "management/regions.html", context=context)
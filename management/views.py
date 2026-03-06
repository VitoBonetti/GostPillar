from django.db.models import Count
from django.views.generic import TemplateView
from django.core.paginator import Paginator
from management.mixins import ManagementAccessMixin
from rbac.management_policy import admin_can_write, admin_can_delete
from regions.models import Regions
from markets.models import Market
from .forms import RegionsForm, MarketForm
from django.views import View
from django.contrib import messages
from django.shortcuts import (
    render,
    get_object_or_404,
    redirect
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
    template_name = "management/regions.html"

    def get(self, request, *args, **kwargs):
        region_id = request.GET.get("region_id")
        if region_id:
            region = get_object_or_404(Regions, uuid=region_id)
            form_region = RegionsForm(instance=region)
        else:
            form_region = RegionsForm()

        return self._render_page(request, form_region, region_id)

    def post(self, request, *args, **kwargs):
        # 1. Handle Delete Action
        if "delete_id" in request.POST:
            if not admin_can_delete(request.user):
                messages.error(request, "You do not have permission to delete regions.")
                return redirect("regions")

            region = get_object_or_404(Regions, uuid=request.POST["delete_id"])
            region.delete()
            messages.success(request, "Region deleted successfully.")
            return redirect("regions")

        # 2. Handle Create / Update Action
        if not admin_can_write(request.user):
            messages.error(request, "You do not have permission to modify regions.")
            return redirect("regions")

        region_id = request.GET.get("region_id")
        if region_id:
            region = get_object_or_404(Regions, uuid=region_id)
            form_region = RegionsForm(request.POST, instance=region)
        else:
            form_region = RegionsForm(request.POST)

        if form_region.is_valid():
            form_region.save()
            msg = "Region updated successfully." if region_id else "Region created successfully."
            messages.success(request, msg)
            return redirect("regions")

        # If form is invalid, re-render the page with errors
        return self._render_page(request, form_region, region_id)

    def _render_page(self, request, form_region, region_id=None):
        # Gather data for the table and statistics
        regions = Regions.objects.annotate(market_count=Count('markets')).order_by("region")
        active_count = regions.filter(active=True).count()
        total_count = regions.count()

        context = {
            "regions": regions,
            "form_region": form_region,
            "active_regions_count": active_count,
            "total_regions_count": total_count,
            "editing": bool(region_id),  # Boolean flag to toggle template titles
            "can_write": admin_can_write(request.user),
            "can_delete": admin_can_delete(request.user),
        }
        return render(request, self.template_name, context)


class MarketListView(ManagementAccessMixin, View):
    template_name = "management/markets.html"

    def get(self, request, *args, **kwargs):
        # Base queryset, using select_related for efficiency since we display Region
        queryset = Market.objects.select_related('region').all()

        # 1. Filtering by market name
        search_query = request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(market__icontains=search_query)

        # 2. Sorting
        sort_by = request.GET.get('sort', 'market')
        valid_sorts = ['market', '-market', 'region__region', '-region__region', 'created_at', '-created_at']
        if sort_by in valid_sorts:
            queryset = queryset.order_by(sort_by)
        else:
            queryset = queryset.order_by('market')

        # 3. Stats (calculate before pagination so it reflects overall data)
        # You could also apply search_query to stats if you want them to be contextual
        total_count = Market.objects.count()
        active_count = Market.objects.filter(active=True).count()
        key_count = Market.objects.filter(key_market=True).count()

        # 4. Pagination
        paginator = Paginator(queryset, 10)  # 10 items per page
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context = {
            'page_obj': page_obj,
            'search_query': search_query,
            'sort_by': sort_by,
            'total_count': total_count,
            'active_count': active_count,
            'key_count': key_count,
            'can_write': admin_can_write(request.user),
            'can_delete': admin_can_delete(request.user),
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        # Handle Deletion
        if "delete_id" in request.POST:
            if not admin_can_delete(request.user):
                messages.error(request, "You do not have permission to delete markets.")
                return redirect("markets")

            market = get_object_or_404(Market, uuid=request.POST["delete_id"])
            market_name = market.market
            market.delete()
            messages.success(request, f"Market '{market_name}' deleted successfully.")
        return redirect("markets")


class MarketFormView(ManagementAccessMixin, View):
    template_name = "management/market_form.html"

    def get(self, request, *args, **kwargs):
        if not admin_can_write(request.user):
            messages.error(request, "You do not have permission to modify markets.")
            return redirect("markets")

        market_id = request.GET.get("market_id")
        if market_id:
            market = get_object_or_404(Market, uuid=market_id)
            form = MarketForm(instance=market)
            editing = True
        else:
            form = MarketForm()
            editing = False

        return render(request, self.template_name, {'form': form, 'editing': editing, 'market_id': market_id})

    def post(self, request, *args, **kwargs):
        if not admin_can_write(request.user):
            messages.error(request, "You do not have permission to modify markets.")
            return redirect("markets")

        market_id = request.GET.get("market_id")
        if market_id:
            market = get_object_or_404(Market, uuid=market_id)
            # request.FILES is required because of the flag_icons ImageField!
            form = MarketForm(request.POST, request.FILES, instance=market)
        else:
            form = MarketForm(request.POST, request.FILES)

        if form.is_valid():
            form.save()
            msg = "Market updated successfully." if market_id else "Market created successfully."
            messages.success(request, msg)
            return redirect("markets")

        return render(request, self.template_name, {'form': form, 'editing': bool(market_id), 'market_id': market_id})
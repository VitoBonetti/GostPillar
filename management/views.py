from django.db.models import Count
from django.db import IntegrityError
from django.views.generic import TemplateView
from django.core.paginator import Paginator
from management.mixins import ManagementAccessMixin
from rbac.management_policy import admin_can_write, admin_can_delete
from regions.models import Regions
from markets.models import Market
from organizations.models import Organization
from accounts.models import User
from .forms import RegionsForm, MarketForm, OrganizationForm
from django.views import View
from django.contrib import messages
from django.shortcuts import (
    render,
    get_object_or_404,
    redirect
)
import json
import jsonschema


# Define the expected structure of the JSON
ORG_JSON_SCHEMA = {
    "type": "object",
    "patternProperties": {
        "^[a-zA-Z0-9_.-]+$": {
            "type": "array",
            "items": {"type": "string", "minLength": 1, "maxLength": 200}
        }
    },
    "additionalProperties": False
}

class ManagementHomeView(ManagementAccessMixin, TemplateView):
    template_name = "management/home.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        try:
            # Regions Stats
            ctx["active_regions_count"] = Regions.objects.filter(active=True).count()
            ctx["total_regions_count"] = Regions.objects.count()

            # Markets Stats
            ctx["total_markets_count"] = Market.objects.count()
            ctx["active_markets_count"] = Market.objects.filter(active=True).count()

            # Organizations Stats
            ctx["total_orgs_count"] = Organization.objects.count()

            # Users Stats
            ctx["total_users_count"] = User.objects.count()
            ctx["admin_users_count"] = User.objects.filter(is_platform_admin=True).count()

        except Exception:
            # Fallback if tables don't exist yet
            ctx["active_regions_count"] = 0
            ctx["total_regions_count"] = 0
            ctx["total_markets_count"] = 0
            ctx["active_markets_count"] = 0
            ctx["total_orgs_count"] = 0
            ctx["total_users_count"] = 0
            ctx["admin_users_count"] = 0

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
        # Base Queryset
        queryset = Regions.objects.annotate(market_count=Count('markets'))

        # 1. Search Filter
        search_query = request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(region__icontains=search_query)

        # 2. Sorting
        sort_by = request.GET.get('sort', 'region')
        valid_sorts = ['region', '-region', '-created_at', 'created_at']
        if sort_by in valid_sorts:
            queryset = queryset.order_by(sort_by)
        else:
            queryset = queryset.order_by('region')

        # 3. Stats
        active_count = queryset.filter(active=True).count()
        total_count = queryset.count()

        # 4. Pagination
        paginator = Paginator(queryset, 10)  # 10 items per page
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context = {
            "page_obj": page_obj,
            "search_query": search_query,  # Pass search back to template
            "sort_by": sort_by,  # Pass sort back to template
            "form_region": form_region,
            "active_regions_count": active_count,
            "total_regions_count": total_count,
            "editing": bool(region_id),
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
            market_instance = form.save(commit=False)

            if request.POST.get('flag_icons-clear') == 'on':
                if market_instance.flag_icons:
                    market_instance.flag_icons.delete(save=False)
            market_instance.save()

            msg = "Market updated successfully." if market_id else "Market created successfully."
            messages.success(request, msg)

            if 'save_and_add' in request.POST:
                return redirect("market_form")
            else:
                return redirect("markets")

        return render(request, self.template_name, {'form': form, 'editing': bool(market_id), 'market_id': market_id})


class OrganizationListView(ManagementAccessMixin, View):
    template_name = "management/organizations.html"

    def get(self, request, *args, **kwargs):
        queryset = Organization.objects.select_related('market__region').all()

        # 1. Search Filter
        search_query = request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(name__icontains=search_query)

        # 2. Market Filter (NEW)
        market_filter = request.GET.get('market', '')
        if market_filter:
            queryset = queryset.filter(market__uuid=market_filter)

        # 3. Sorting
        sort_by = request.GET.get('sort', 'name')
        valid_sorts = ['name', '-name', 'market__market', '-market__market']
        if sort_by in valid_sorts:
            queryset = queryset.order_by(sort_by)
        else:
            queryset = queryset.order_by('name')

        total_count = queryset.count()

        # 4. Pagination
        paginator = Paginator(queryset, 15)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        # 5. Get all markets for the dropdown filter
        markets = Market.objects.all().order_by('market')

        context = {
            'page_obj': page_obj,
            'search_query': search_query,
            'market_filter': market_filter,
            'markets': markets,
            'sort_by': sort_by,
            'total_count': total_count,
            'can_write': admin_can_write(request.user),
            'can_delete': admin_can_delete(request.user),
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        if "delete_id" in request.POST:
            if not admin_can_delete(request.user):
                messages.error(request, "Permission denied.")
                return redirect("organizations")

            org = get_object_or_404(Organization, uuid=request.POST["delete_id"])
            org.delete()
            messages.success(request, f"Organization '{org.name}' deleted.")
        return redirect("organizations")


class OrganizationFormView(ManagementAccessMixin, View):
    template_name = "management/organization_form.html"

    def get(self, request, *args, **kwargs):
        if not admin_can_write(request.user):
            messages.error(request, "Permission denied.")
            return redirect("organizations")

        org_id = request.GET.get("org_id")
        if org_id:
            org = get_object_or_404(Organization, uuid=org_id)
            form = OrganizationForm(instance=org)
            editing = True
        else:
            form = OrganizationForm()
            editing = False

        return render(request, self.template_name, {'form': form, 'editing': editing, 'org_id': org_id})

    def post(self, request, *args, **kwargs):
        if not admin_can_write(request.user):
            messages.error(request, "Permission denied.")
            return redirect("organizations")

        submission_type = request.POST.get('submission_type', 'single')
        org_id = request.GET.get("org_id")

        # 1. Handle Single Form Submission
        if submission_type == 'single':
            if org_id:
                org = get_object_or_404(Organization, uuid=org_id)
                form = OrganizationForm(request.POST, instance=org)
            else:
                form = OrganizationForm(request.POST)

            if form.is_valid():
                form.save()
                messages.success(request, "Organization saved successfully.")
                if 'save_and_add' in request.POST:
                    return redirect("organization_form")
                return redirect("organizations")
            return render(request, self.template_name, {'form': form, 'editing': bool(org_id), 'org_id': org_id})

        # 2. Handle JSON Bulk Submissions
        json_data = None
        try:
            if submission_type == 'json_text':
                json_data = json.loads(request.POST.get('json_text', '{}'))
            elif submission_type == 'json_file':
                file = request.FILES.get('json_file')
                if file:
                    # SECURE: Check file size before reading into memory (e.g., limit to 2MB)
                    if file.size > 2 * 1024 * 1024:
                        messages.error(request, "JSON file is too large. Maximum size is 2MB.")
                        return redirect("organization_form")

                    json_data = json.loads(file.read().decode('utf-8'))
                else:
                    raise ValueError("No file uploaded.")

            # SECURE: Validate the JSON structure to prevent deeply nested or malformed injections
            if json_data:
                jsonschema.validate(instance=json_data, schema=ORG_JSON_SCHEMA)

        except json.JSONDecodeError:
            messages.error(request, "Invalid JSON formatting.")
            return redirect("organization_form")
        except jsonschema.exceptions.ValidationError as e:
            messages.error(request, f"JSON Schema validation failed: {e.message}")
            return redirect("organization_form")
        except Exception as e:
            messages.error(request, f"Error processing file: {str(e)}")
            return redirect("organization_form")

        # 3. Process the parsed JSON
        if json_data:
            created_count = 0
            skipped_count = 0
            missing_markets = set()

            for market_code, org_list in json_data.items():
                # Find market by code
                market = Market.objects.filter(code=market_code).first()
                if not market:
                    missing_markets.add(market_code)
                    continue

                # Create organizations
                for org_name in org_list:
                    obj, created = Organization.objects.get_or_create(market=market, name=org_name)
                    if created:
                        created_count += 1
                    else:
                        skipped_count += 1

            # Provide feedback
            if created_count > 0:
                messages.success(request, f"Successfully created {created_count} organizations.")
            if skipped_count > 0:
                messages.info(request, f"Skipped {skipped_count} organizations (already existed in that market).")
            if missing_markets:
                messages.warning(request,
                                 f"Skipped organizations for unknown market codes: {', '.join(missing_markets)}")

        return redirect("organizations")
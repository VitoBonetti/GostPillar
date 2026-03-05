from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from rbac.policy import is_god, is_admin
from rbac.models import ROLE_MANAGER, ROLE_OPERATOR, ROLE_REGIONAL_VIEWER

@login_required
def home(request):
    u = request.user

    if is_god(u):
        role_text = "You are GOD (superuser). Full access."
    elif is_admin(u):
        role_text = "You are Admin. Full access (except creating God/Admin)."
    else:
        # list scoped roles
        ras = u.role_assignments.select_related("scope_content_type").all()

        if not ras:
            role_text = "You have no scoped roles yet."

        else:
            lines = []
            for ra in ras:
                scope_label = f"{ra.scope_content_type.model}:{ra.scope_object_id}"
                if ra.role == ROLE_REGIONAL_VIEWER:
                    lines.append(f"Regional Viewer on {scope_label}")
                elif ra.role == ROLE_MANAGER:
                    lines.append(f"Manager on {scope_label}")
                elif ra.role == ROLE_OPERATOR:
                    lines.append(f"Operator on {scope_label}")
            role_text = " / ".join(lines)

    return render(request, "accounts/home.html", {"role_text": role_text})
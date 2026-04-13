"""Listado administrativo de usuarios."""

from django.shortcuts import render

from apps.core.presentation.dashboard import build_dashboard_base_context
from apps.core.utils.decorators import role_required
from apps.users.forms import AdminUserFilterForm
from apps.users.selectors import get_admin_dashboard_summary, get_admin_user_list


@role_required("admin")
def admin_user_list_view(request):
    """Renderiza una lista basica de usuarios para el panel de admin."""

    filter_form = AdminUserFilterForm(request.GET or None)
    filter_data = filter_form.cleaned_data if filter_form.is_valid() else None
    managed_users = get_admin_user_list(filters=filter_data)
    context = build_dashboard_base_context(
        request.user,
        "admin",
        request=request,
        active_section="users",
        extra_context={
            **get_admin_dashboard_summary(),
            "managed_users": managed_users,
            "managed_users_count": len(managed_users),
            "filter_form": filter_form,
        },
    )
    return render(request, "users/pages/admin/user_list.html", context)

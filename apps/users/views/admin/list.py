"""Listado administrativo de usuarios."""

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.shortcuts import redirect, render

from apps.core.presentation.dashboard import build_dashboard_base_context
from apps.core.presentation.pagination import paginate_dashboard_list
from apps.core.utils.decorators import role_required
from apps.users.forms import AdminUserCreateForm, AdminUserFilterForm
from apps.users.selectors import get_admin_dashboard_summary, get_admin_user_list
from apps.users.services.admin.management import create_admin_user


def _merge_validation_errors(form, exc):
    """Traspasa errores de validacion al formulario del modal."""

    message_dict = getattr(exc, "message_dict", None)
    if message_dict:
        for field, errors in message_dict.items():
            for error in errors:
                form.add_error(field if field in form.fields else None, error)
        return

    messages_list = getattr(exc, "messages", None) or [str(exc)]
    for error in messages_list:
        form.add_error(None, error)


def _build_admin_users_context(request, *, create_user_form=None):
    """Prepara el contexto comun del listado y del modal de alta rapida."""

    filter_form = AdminUserFilterForm(request.GET or None)
    filter_data = filter_form.cleaned_data if filter_form.is_valid() else None
    managed_users = get_admin_user_list(filters=filter_data)
    managed_users_page = paginate_dashboard_list(request, managed_users)
    return build_dashboard_base_context(
        request.user,
        "admin",
        request=request,
        active_section="users",
        extra_context={
            **get_admin_dashboard_summary(),
            "managed_users": managed_users_page["items"],
            "managed_users_count": managed_users_page["total_count"],
            "page_obj": managed_users_page["page_obj"],
            "pagination_context": managed_users_page["pagination_context"],
            "filter_form": filter_form,
            "create_user_form": create_user_form or AdminUserCreateForm(),
            "create_user_action": request.get_full_path(),
            "create_user_close_url": request.get_full_path(),
        },
    )


@role_required("admin")
def admin_user_list_view(request):
    """Renderiza y gestiona el listado basico de usuarios del panel de admin."""

    create_user_form = AdminUserCreateForm()

    if request.method == "POST":
        create_user_form = AdminUserCreateForm(request.POST)
        if create_user_form.is_valid():
            try:
                user = create_admin_user(
                    acting_user=request.user,
                    email=create_user_form.cleaned_data["email"],
                    dni=create_user_form.cleaned_data["dni"],
                )
            except ValidationError as exc:
                _merge_validation_errors(create_user_form, exc)
            except IntegrityError:
                create_user_form.add_error(
                    None,
                    "No se ha podido crear el usuario. Revisa los datos e inténtalo de nuevo.",
                )
            else:
                messages.success(
                    request,
                    f"Se ha creado la cuenta de {user.email} y se ha enviado su enlace de activación.",
                )
                return redirect(request.get_full_path())

    context = _build_admin_users_context(request, create_user_form=create_user_form)
    return render(request, "users/pages/admin/user_list.html", context)

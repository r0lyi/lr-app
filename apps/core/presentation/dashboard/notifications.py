"""Fragmentos de contexto relacionados con el inbox del dashboard."""

from apps.notifications.selectors import (
    get_unread_notifications_count,
    get_user_inbox_notifications_page,
)


def build_notifications_page_url(request, page_number):
    """Construye una URL que conserva filtros actuales y cambia de pagina."""

    if request is None:
        return ""

    query_params = request.GET.copy()
    query_params["notifications_page"] = page_number
    encoded_query = query_params.urlencode()
    return f"{request.path}?{encoded_query}" if encoded_query else request.path


def get_dashboard_notifications_context(user, *, request=None):
    """Devuelve el contexto visual del inbox compartido del dashboard."""

    notifications_page_number = 1
    if request is not None:
        notifications_page_number = request.GET.get("notifications_page", 1)

    notifications_page = get_user_inbox_notifications_page(
        user,
        page_number=notifications_page_number,
        page_size=10,
    )

    return {
        "notifications_page_obj": notifications_page,
        "recent_notifications": list(notifications_page.object_list),
        "notifications_next_page_url": (
            build_notifications_page_url(
                request,
                notifications_page.next_page_number(),
            )
            if notifications_page.has_next()
            else ""
        ),
        "notifications_previous_page_url": (
            build_notifications_page_url(
                request,
                notifications_page.previous_page_number(),
            )
            if notifications_page.has_previous()
            else ""
        ),
        "notifications_return_path": (
            request.get_full_path() if request is not None else ""
        ),
        "unread_notifications_count": get_unread_notifications_count(user),
    }

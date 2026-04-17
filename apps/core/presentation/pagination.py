"""Helpers de presentacion para paginar listados del dashboard."""

from django.core.paginator import Paginator


DEFAULT_DASHBOARD_PAGE_SIZE = 10


def paginate_dashboard_list(
    request,
    items,
    *,
    page_size=DEFAULT_DASHBOARD_PAGE_SIZE,
    page_parameter="page",
):
    """Pagina una lista o queryset preservando los filtros GET actuales."""

    paginator = Paginator(items, page_size)
    page_obj = paginator.get_page(request.GET.get(page_parameter) or 1)

    return {
        "items": page_obj.object_list,
        "page_obj": page_obj,
        "pagination_context": build_pagination_links(
            request,
            page_obj,
            page_parameter=page_parameter,
        ),
        "total_count": paginator.count,
    }


def build_pagination_links(request, page_obj, *, page_parameter="page"):
    """Genera enlaces de paginacion manteniendo los parametros de filtro."""

    if page_obj.paginator.num_pages <= 1:
        return {
            "pages": [],
            "previous_url": "",
            "next_url": "",
        }

    def build_page_url(page_number):
        querydict = request.GET.copy()
        querydict[page_parameter] = page_number
        return f"?{querydict.urlencode()}"

    pages = [
        {
            "number": page_number,
            "url": build_page_url(page_number),
            "current": page_number == page_obj.number,
        }
        for page_number in range(1, page_obj.paginator.num_pages + 1)
    ]

    return {
        "pages": pages,
        "previous_url": build_page_url(page_obj.previous_page_number())
        if page_obj.has_previous()
        else "",
        "next_url": build_page_url(page_obj.next_page_number())
        if page_obj.has_next()
        else "",
    }
